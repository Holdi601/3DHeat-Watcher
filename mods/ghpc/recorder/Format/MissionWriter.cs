// The recorder's writing thread. The game thread only fills pooled rows and hands
// them over; this thread writes them to the spool, flushes it every second, and
// when the mission ends turns the spool into the `.3dheat` file. Nothing on the
// game thread touches the disk.

using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;

namespace Heat3D.Ghpc.Format
{
    public sealed class MissionWriter
    {
        readonly object _lock = new object();
        List<Row> _pending = new List<Row>(4096);
        List<Row> _swap = new List<Row>(4096);
        readonly Stack<Row> _pool = new Stack<Row>();
        readonly List<KeyValuePair<string, string>> _meta = new List<KeyValuePair<string, string>>();
        readonly List<KeyValuePair<string, string>> _metaSwap = new List<KeyValuePair<string, string>>();
        readonly Thread _thread;
        readonly AutoResetEvent _wake = new AutoResetEvent(false);
        readonly string _spoolPath, _folder, _version;
        readonly Action<string> _log;
        volatile bool _finish;
        volatile bool _abandon;

        /// The finished file, once the thread is done (null until then, or when it failed).
        public string Output { get; private set; }
        public string Error { get; private set; }
        public bool Done { get; private set; }
        public long Written { get; private set; }

        public MissionWriter(string spoolPath, string folder, string version, Action<string> log)
        {
            _spoolPath = spoolPath;
            _folder = folder;
            _version = version;
            _log = log ?? (s => { });
            Directory.CreateDirectory(Path.GetDirectoryName(spoolPath));
            _thread = new Thread(Run) { IsBackground = true, Name = "3DHeat GHPC writer", Priority = ThreadPriority.BelowNormal };
            _thread.Start();
        }

        /// A row to fill; hand it back with `Commit`.
        public Row Rent()
        {
            lock (_lock)
            {
                if (_pool.Count > 0) return _pool.Pop();
            }
            return new Row();
        }

        public void Commit(Row r)
        {
            lock (_lock) _pending.Add(r);
        }

        /// A match-document entry (see Container.MatchDocument for the key scheme).
        public void Meta(string key, string json)
        {
            lock (_lock) _meta.Add(new KeyValuePair<string, string>(key, json));
        }

        /// Ends the mission: the rest is written and the file built on this writer's thread.
        public void Finish()
        {
            _finish = true;
            _wake.Set();
        }

        /// Stops without building a file (the spool stays, and is built at the next start).
        public void Abandon()
        {
            _abandon = true;
            _finish = true;
            _wake.Set();
        }

        /// Waits for the thread (the game is closing). True when it ended in time.
        public bool Join(int ms) => _thread.Join(ms);

        void Drain(SpoolWriter spool)
        {
            lock (_lock)
            {
                var t = _pending;
                _pending = _swap;
                _swap = t;
                _metaSwap.AddRange(_meta);
                _meta.Clear();
            }
            foreach (var kv in _metaSwap) spool.Meta(kv.Key, kv.Value);
            _metaSwap.Clear();
            foreach (var r in _swap)
            {
                spool.Write(r);
                r.Reset();
            }
            Written += _swap.Count;
            lock (_lock)
            {
                foreach (var r in _swap)
                    if (_pool.Count < 8192) _pool.Push(r);
            }
            _swap.Clear();
        }

        void Run()
        {
            try
            {
                using (var spool = new SpoolWriter(_spoolPath))
                {
                    while (!_finish)
                    {
                        _wake.WaitOne(1000);
                        Drain(spool);
                        spool.Flush();
                    }
                    Drain(spool);
                }
                if (_abandon) return;
                var res = Container.Build(_spoolPath, _folder, _version);
                File.Delete(_spoolPath);
                Output = res.Path;
                _log($"wrote {res.Path} ({res.Rows} rows)");
            }
            catch (Exception e)
            {
                Error = e.GetType().Name + ": " + e.Message;
                _log("writing the mission failed, the spool is kept for the next start: " + Error);
            }
            finally
            {
                Done = true;
            }
        }

        /// Spools left by a game that stopped mid-mission: each is built into its file.
        public static List<string> Recover(string spoolFolder, string folder, string version, Action<string> log)
        {
            var done = new List<string>();
            if (!Directory.Exists(spoolFolder)) return done;
            foreach (var p in Directory.GetFiles(spoolFolder, "*.spool"))
            {
                try
                {
                    var res = Container.Build(p, folder, version);
                    File.Delete(p);
                    done.Add(res.Path);
                    log?.Invoke($"recovered {res.Path} from a mission that did not end");
                }
                catch (Exception e)
                {
                    log?.Invoke($"could not recover {p}: {e.GetType().Name}: {e.Message}");
                    try
                    {
                        File.Move(p, p + ".bad");
                    }
                    catch (Exception)
                    {
                    }
                }
            }
            return done;
        }
    }
}
