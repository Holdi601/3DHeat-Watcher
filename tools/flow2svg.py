"""Column flow diagram -> SVG, at most 3 columns a row (wraps into further rows), <= ~860 px wide,
main labels 16 px, sub lines 14 px; role=img + aria-label. usage: python -I flow2svg2.py spec.json out.svg [--per-row 3]
spec: {"title": "...", "cols": [[{"t": "title", "s": "sub line|second line", "c": "blue"}...], ...], "legend": [["blue","meaning"],...]}"""
import json, sys, html
spec = json.load(open(sys.argv[1], encoding="utf-8"))
per = int(sys.argv[sys.argv.index("--per-row") + 1]) if "--per-row" in sys.argv else 3
C = {"blue": ("#e8f0fe", "#3b6fd8"), "green": ("#e6f4ea", "#2e8b57"), "orange": ("#fff1e0", "#d9822b"),
     "grey": ("#f1f3f4", "#80868b"), "purple": ("#f3e8fd", "#8a4fd0")}
cols = spec["cols"]; bw, gx, gy, pad, top, lh, rowgap = 236, 46, 16, 24, 60, 19, 46
def lines(b): return [b["t"]] + [x for x in b.get("s", "").split("|") if x]
for col in cols:
    for b in col: b["h"] = 22 + lh * len(lines(b))
rows = [cols[i:i + per] for i in range(0, len(cols), per)]
ncol = min(per, len(cols)); W = pad * 2 + ncol * bw + (ncol - 1) * gx
o = []; y0 = top
for r, row in enumerate(rows):
    colh = [sum(b["h"] for b in c) + gy * (len(c) - 1) for c in row]; rh = max(colh)
    for i, col in enumerate(row):
        x = pad + i * (bw + gx); y = y0 + (rh - colh[i]) / 2
        for b in col:
            b["x"], b["y"] = x, y
            fill, stroke = C.get(b.get("c", "blue"), C["blue"])
            o.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{b["h"]}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
            ls = lines(b); ty = y + 11 + 15
            for k, l in enumerate(ls):
                st = 'font-weight="600" font-size="16" fill="#202124"' if k == 0 else 'font-size="14" fill="#3c4043"'
                o.append(f'<text x="{x + bw/2}" y="{ty + k*lh}" text-anchor="middle" {st}>{html.escape(l)}</text>')
            y += b["h"] + gy
    for i in range(len(row) - 1):
        a, b = row[i], row[i + 1]
        pairs = [(p, q) for p in a for q in b] if (len(a) == 1 or len(b) == 1) else list(zip(a, b))
        for p, q in pairs:
            o.append(f'<line x1="{p["x"]+bw}" y1="{p["y"]+p["h"]/2}" x2="{q["x"]-2}" y2="{q["y"]+q["h"]/2}" stroke="#5f6368" stroke-width="1.5" marker-end="url(#a)"/>')
    row[-1].append  # noqa
    y0 += rh + rowgap
    if r + 1 < len(rows):
        last = row[-1][-1]; nxt = rows[r + 1][0][0]
        sx, sy = last["x"] + bw / 2, last["y"] + last["h"]; my = y0 - rowgap / 2
        # next row's first column top is placed later; aim at y0 (row top) and fix after layout
        o.append(("ELBOW", sx, sy, my, nxt))
H0 = y0 - rowgap + pad
leg = spec.get("legend", [])
H = H0 + (30 if leg else 0)
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI,Helvetica,Arial,sans-serif" role="img" aria-label="{html.escape(spec.get("title", ""))}">',
       '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#5f6368"/></marker></defs>',
       f'<rect width="{W}" height="{H}" rx="10" fill="#ffffff" stroke="#dadce0"/>',
       f'<text x="{pad}" y="36" font-size="18" font-weight="600" fill="#202124">{html.escape(spec.get("title", ""))}</text>']
for e in o:
    if isinstance(e, tuple):
        _, sx, sy, my, n = e; tx = n["x"] + bw / 2; ty = n["y"] - 2
        out.append(f'<path d="M{sx},{sy} V{my} H{tx} V{ty}" fill="none" stroke="#5f6368" stroke-width="1.5" marker-end="url(#a)"/>')
    else:
        out.append(e)
x = pad
for c, t in leg:
    fill, stroke = C[c]
    out.append(f'<rect x="{x}" y="{H0 - 4}" width="18" height="18" rx="3" fill="{fill}" stroke="{stroke}"/>')
    out.append(f'<text x="{x + 24}" y="{H0 + 10}" font-size="14" fill="#3c4043">{html.escape(t)}</text>')
    x += 34 + len(t) * 7.5
out.append("</svg>")
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n"); print(sys.argv[2], W, H)
