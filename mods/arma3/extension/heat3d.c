/*
 * heat3d: the file writer of the Heat3D recorder for Arma 3 servers.
 *
 * SQF cannot write files, so the recorder (addons/heat3d_recorder) hands its
 * lines to this extension through callExtension. The extension does two
 * things only:
 *
 *   - during the mission, appends the lines to a journal,
 *     <dir>/<date>_<mission>.heat3d.part, flushed on every call, so a crash
 *     loses at most the lines of the call that was being written;
 *   - when the mission ends (or, after a crash, when the next mission starts),
 *     turns the journal into <dir>/<date>_<mission>.json, a recording in OCAP's
 *     JSON layout, which 3DHeat reads as it is (and OCAP's web player too).
 *
 * Journal lines, one record each, fields separated by a tab:
 *   H <json object>        the recording's header (missionName, worldName, captureDelay...)
 *   N <frame>              a frame begins
 *   E <id> <json object>   an entity (without its positions)
 *   P <id> <json array>    the entity's state in the current frame
 *   F <id> <json array>    a shot: [frame, [x, y, z]]
 *   V <json array>         an event: [frame, kind, ...]
 *   T <json object>        a time mark: {frameNum, time, systemTimeUTC}
 *
 * Commands (callExtension ["command", [args]]):
 *   "open"  [mission]   finishes journals left over from a crash, starts a new
 *                       one; answers its base name
 *   "write" [text]      appends text (lines separated by \n)
 *   "close" []          finishes the journal; answers the recording's path
 *
 * Files go to the folder named by the environment variable HEAT3D_DIR, else to
 * a folder "recordings" beside this library.
 *
 * Build (64-bit, which is what Arma 3's 64-bit server loads):
 *   Windows (MSVC):  cl /nologo /O2 /LD heat3d.c /Fe:heat3d_x64.dll
 *   Linux (gcc):     gcc -O2 -shared -fPIC -o heat3d_x64.so heat3d.c -ldl
 *
 * MIT licence, see the repository's LICENSE.
 */

#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS /* fopen and strcpy are used with sizes checked */
#else
#define _GNU_SOURCE /* dladdr */
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#include <direct.h>
#define EXPORT __declspec(dllexport)
#define MKDIR(p) _mkdir(p)
#else
#include <dlfcn.h>
#include <dirent.h>
#include <libgen.h>
#include <sys/stat.h>
#include <unistd.h>
#define EXPORT __attribute__((visibility("default")))
#define MKDIR(p) mkdir(p, 0755)
#endif

#define HEAT3D_VERSION "0.1.0"
#define PART ".heat3d.part"

static FILE *journal = NULL;
static char journal_path[2048];

/* ---------------------------------------------------------------- folders */

/** The folder recordings go to, created when missing. */
static void recordings_dir(char *out, size_t n) {
  const char *env = getenv("HEAT3D_DIR");
  if (env && *env) {
    snprintf(out, n, "%s", env);
  } else {
    char lib[2048] = "";
#ifdef _WIN32
    HMODULE h = NULL;
    if (GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT, (LPCSTR)&recordings_dir, &h))
      GetModuleFileNameA(h, lib, sizeof lib);
    char *slash = strrchr(lib, '\\');
    if (!slash) slash = strrchr(lib, '/');
    if (slash) *slash = 0;
    else strcpy(lib, ".");
#else
    Dl_info info;
    if (dladdr((void *)&recordings_dir, &info) && info.dli_fname) snprintf(lib, sizeof lib, "%s", info.dli_fname);
    char *slash = strrchr(lib, '/');
    if (slash) *slash = 0;
    else strcpy(lib, ".");
#endif
    snprintf(out, n, "%s/recordings", lib);
  }
  MKDIR(out);
}

/* ---------------------------------------------------------------- arguments */

/**
 * An argument as SQF meant it: Arma passes a string argument in quotes with
 * the quotes inside it doubled ("say ""hi"""), numbers as they are.
 */
static char *unquote(const char *a) {
  size_t n = strlen(a);
  char *out = (char *)malloc(n + 1);
  if (!out) return NULL;
  if (n >= 2 && a[0] == '"' && a[n - 1] == '"') {
    size_t k = 0;
    for (size_t i = 1; i + 1 < n; i++) {
      out[k++] = a[i];
      if (a[i] == '"' && a[i + 1] == '"') i++;
    }
    out[k] = 0;
  } else {
    memcpy(out, a, n + 1);
  }
  return out;
}

/** Letters, digits, - and _ only: the mission's name made safe for a file name. */
static void safe_name(const char *in, char *out, size_t n) {
  size_t k = 0;
  for (const char *p = in; *p && k + 1 < n && k < 80; p++) {
    char c = *p;
    int ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '-' || c == '_';
    out[k++] = ok ? c : '_';
  }
  if (k == 0 && n > 7) {
    strcpy(out, "mission");
    return;
  }
  out[k] = 0;
}

/* ---------------------------------------------------------------- finishing */

typedef struct {
  long id;
  long seq;
  const char *text;
  size_t len;
} Rec;

typedef struct {
  Rec *at;
  size_t n, cap;
} Recs;

static int recs_push(Recs *r, long id, long seq, const char *text, size_t len) {
  if (r->n == r->cap) {
    size_t cap = r->cap ? r->cap * 2 : 1024;
    Rec *at = (Rec *)realloc(r->at, cap * sizeof(Rec));
    if (!at) return 0;
    r->at = at;
    r->cap = cap;
  }
  r->at[r->n].id = id;
  r->at[r->n].seq = seq;
  r->at[r->n].text = text;
  r->at[r->n].len = len;
  r->n++;
  return 1;
}

static int by_id_then_seq(const void *a, const void *b) {
  const Rec *x = (const Rec *)a;
  const Rec *y = (const Rec *)b;
  if (x->id != y->id) return x->id < y->id ? -1 : 1;
  return x->seq < y->seq ? -1 : x->seq > y->seq;
}

/** Writes a JSON object without its closing brace; answers whether it had members. */
static int open_object(FILE *out, const char *text, size_t len) {
  while (len && (text[len - 1] == ' ' || text[len - 1] == '\r')) len--;
  if (len && text[len - 1] == '}') len--;
  fwrite(text, 1, len, out);
  for (size_t i = 0; i < len; i++)
    if (text[i] != '{' && text[i] != ' ') return 1;
  return 0;
}

/** Writes the records of one id, comma-separated, from the list sorted by id. */
static void write_run(FILE *out, const Recs *r, long id) {
  size_t lo = 0, hi = r->n;
  while (lo < hi) {
    size_t mid = (lo + hi) / 2;
    if (r->at[mid].id < id) lo = mid + 1;
    else hi = mid;
  }
  int first = 1;
  for (size_t from = lo; from < r->n && r->at[from].id == id; from++) {
    if (!first) fputc(',', out);
    fwrite(r->at[from].text, 1, r->at[from].len, out);
    first = 0;
  }
}

/** Turns a journal into the OCAP JSON recording beside it. Answers 0 on success. */
static int finish(const char *part, char *result, size_t rn) {
  FILE *in = fopen(part, "rb");
  if (!in) return 1;
  fseek(in, 0, SEEK_END);
  long size = ftell(in);
  fseek(in, 0, SEEK_SET);
  char *buf = (char *)malloc((size_t)size + 1);
  if (!buf) {
    fclose(in);
    return 2;
  }
  size_t got = fread(buf, 1, (size_t)size, in);
  fclose(in);
  buf[got] = 0;

  const char *header = "{\"missionName\":\"\",\"captureDelay\":1}";
  size_t header_len = strlen(header);
  long end_frame = 0;
  Recs ents = {0}, pos = {0}, fired = {0}, events = {0}, times = {0};
  long seq = 0;
  int ok = 1;
  for (char *line = buf; line && *line && ok;) {
    char *nl = strchr(line, '\n');
    if (nl) *nl = 0;
    size_t len = strlen(line);
    if (len && line[len - 1] == '\r') line[--len] = 0;
    if (len > 2 && line[1] == '\t') {
      char kind = line[0];
      char *rest = line + 2;
      if (kind == 'H') {
        header = rest;
        header_len = strlen(rest);
      } else if (kind == 'N') {
        long f = strtol(rest, NULL, 10);
        if (f > end_frame) end_frame = f;
      } else if (kind == 'V') {
        ok = recs_push(&events, 0, seq++, rest, strlen(rest));
      } else if (kind == 'T') {
        ok = recs_push(&times, 0, seq++, rest, strlen(rest));
      } else if (kind == 'E' || kind == 'P' || kind == 'F') {
        char *tab = strchr(rest, '\t');
        if (tab) {
          long id = strtol(rest, NULL, 10);
          Recs *r = kind == 'E' ? &ents : kind == 'P' ? &pos : &fired;
          ok = recs_push(r, id, seq++, tab + 1, strlen(tab + 1));
        }
      }
    }
    line = nl ? nl + 1 : NULL;
  }
  if (!ok) {
    free(buf);
    return 3;
  }
  qsort(pos.at, pos.n, sizeof(Rec), by_id_then_seq);
  qsort(fired.at, fired.n, sizeof(Rec), by_id_then_seq);

  char out_path[2048], tmp_path[2100];
  snprintf(out_path, sizeof out_path, "%.*s.json", (int)(strlen(part) - strlen(PART)), part);
  snprintf(tmp_path, sizeof tmp_path, "%s.tmp", out_path);
  FILE *out = fopen(tmp_path, "wb");
  if (!out) {
    free(buf);
    return 4;
  }
  if (open_object(out, header, header_len)) fputc(',', out);
  fprintf(out, "\"endFrame\":%ld,\"entities\":[", end_frame);
  for (size_t i = 0; i < ents.n; i++) {
    if (i) fputc(',', out);
    if (open_object(out, ents.at[i].text, ents.at[i].len)) fputc(',', out);
    fputs("\"positions\":[", out);
    write_run(out, &pos, ents.at[i].id);
    fputs("],\"framesFired\":[", out);
    write_run(out, &fired, ents.at[i].id);
    fputs("]}", out);
  }
  fputs("],\"events\":[", out);
  for (size_t i = 0; i < events.n; i++) {
    if (i) fputc(',', out);
    fwrite(events.at[i].text, 1, events.at[i].len, out);
  }
  fputs("],\"times\":[", out);
  for (size_t i = 0; i < times.n; i++) {
    if (i) fputc(',', out);
    fwrite(times.at[i].text, 1, times.at[i].len, out);
  }
  fputs("],\"Markers\":[]}\n", out);
  int bad = ferror(out);
  fclose(out);
  free(ents.at);
  free(pos.at);
  free(fired.at);
  free(events.at);
  free(times.at);
  free(buf);
  if (bad) return 5;
  remove(out_path);
  if (rename(tmp_path, out_path) != 0) return 6;
  remove(part);
  if (result) snprintf(result, rn, "%s", out_path);
  return 0;
}

/** Finishes the journals a crash or a restart left behind. */
static void finish_leftovers(const char *dir) {
#ifdef _WIN32
  char pattern[2100];
  snprintf(pattern, sizeof pattern, "%s\\*" PART, dir);
  WIN32_FIND_DATAA fd;
  HANDLE h = FindFirstFileA(pattern, &fd);
  if (h == INVALID_HANDLE_VALUE) return;
  do {
    char path[2400];
    snprintf(path, sizeof path, "%s\\%s", dir, fd.cFileName);
    finish(path, NULL, 0);
  } while (FindNextFileA(h, &fd));
  FindClose(h);
#else
  DIR *d = opendir(dir);
  if (!d) return;
  struct dirent *e;
  size_t pl = strlen(PART);
  while ((e = readdir(d))) {
    size_t n = strlen(e->d_name);
    if (n > pl && strcmp(e->d_name + n - pl, PART) == 0) {
      char path[2400];
      snprintf(path, sizeof path, "%s/%s", dir, e->d_name);
      finish(path, NULL, 0);
    }
  }
  closedir(d);
#endif
}

/* ---------------------------------------------------------------- commands */

static int cmd_open(char *output, unsigned int size, const char *mission) {
  if (journal) {
    fclose(journal);
    journal = NULL;
    finish(journal_path, NULL, 0);
  }
  char dir[2048];
  recordings_dir(dir, sizeof dir);
  finish_leftovers(dir);
  time_t now = time(NULL);
  struct tm local;
#ifdef _WIN32
  localtime_s(&local, &now);
#else
  localtime_r(&now, &local);
#endif
  char safe[96];
  safe_name(mission, safe, sizeof safe);
  // OCAP's own naming, which the viewer reads the date from.
  char base[256];
  snprintf(base, sizeof base, "%04d_%02d_%02d__%02d_%02d_%s", local.tm_year + 1900, local.tm_mon + 1, local.tm_mday, local.tm_hour, local.tm_min, safe);
  snprintf(journal_path, sizeof journal_path, "%s/%s" PART, dir, base);
  journal = fopen(journal_path, "wb");
  if (!journal) {
    snprintf(output, size, "error: cannot write %s", journal_path);
    return 1;
  }
  snprintf(output, size, "%s", base);
  return 0;
}

static int cmd_write(char *output, unsigned int size, const char *text) {
  if (!journal) {
    snprintf(output, size, "error: no recording open");
    return 1;
  }
  size_t n = strlen(text);
  fwrite(text, 1, n, journal);
  if (n && text[n - 1] != '\n') fputc('\n', journal);
  fflush(journal);
  snprintf(output, size, "ok");
  return 0;
}

static int cmd_close(char *output, unsigned int size) {
  if (!journal) {
    snprintf(output, size, "error: no recording open");
    return 1;
  }
  fclose(journal);
  journal = NULL;
  int r = finish(journal_path, output, size);
  if (r) snprintf(output, size, "error %d finishing %s", r, journal_path);
  return r;
}

/* ---------------------------------------------------------------- Arma's entry points */

#ifdef __cplusplus
extern "C" {
#endif

EXPORT void RVExtensionVersion(char *output, unsigned int outputSize) {
  snprintf(output, outputSize, "heat3d " HEAT3D_VERSION);
}

EXPORT void RVExtension(char *output, unsigned int outputSize, const char *function) {
  if (strcmp(function, "version") == 0) snprintf(output, outputSize, HEAT3D_VERSION);
  else if (strcmp(function, "close") == 0) cmd_close(output, outputSize);
  else snprintf(output, outputSize, "error: unknown command %s", function);
}

EXPORT int RVExtensionArgs(char *output, unsigned int outputSize, const char *function, const char **argv, unsigned int argc) {
  char *a0 = argc > 0 ? unquote(argv[0]) : NULL;
  int r;
  if (strcmp(function, "open") == 0) r = cmd_open(output, outputSize, a0 ? a0 : "");
  else if (strcmp(function, "write") == 0) r = a0 ? cmd_write(output, outputSize, a0) : 1;
  else if (strcmp(function, "close") == 0) r = cmd_close(output, outputSize);
  else {
    snprintf(output, outputSize, "error: unknown command %s", function);
    r = 1;
  }
  free(a0);
  return r;
}

#ifdef __cplusplus
}
#endif
