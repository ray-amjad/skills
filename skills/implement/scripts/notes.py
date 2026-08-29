#!/usr/bin/env python3
"""Append-only log for implementation notes, rendered as one self-contained HTML page.

The page stores its notes as JSON inside a <script type="application/json"> block and
renders them client-side, so appending a note never means rewriting markup by hand.

  notes.py init    --file implementation-notes.html [--title T] [--spec S]
  notes.py add     --file F --type decision|deviation|tradeoff|question --title T [...]
  notes.py resolve --file F --id n3 [--body "how it was settled"]
  notes.py list    --file F [--json]

--body accepts "-" to read the body from stdin, which avoids shell quoting problems
with multi-line text.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

TYPES = ("decision", "deviation", "tradeoff", "question")
IMPACTS = ("high", "medium", "low")

DATA_RE = re.compile(
    r'(<script id="notes-data" type="application/json">)(.*?)(</script>)', re.DOTALL
)


# --------------------------------------------------------------------------- io


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def embed(payload):
    """JSON safe to sit inside a <script> block: no raw '<' can close the tag."""
    return json.dumps(payload, ensure_ascii=False, indent=2).replace("<", "\\u003c")


def load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    match = DATA_RE.search(html)
    if not match:
        sys.exit(
            f"{path} exists but has no notes-data block. Move it aside or pick another "
            "filename; refusing to overwrite a file this script did not write."
        )
    return json.loads(match.group(2))


def save(path, payload):
    """Always re-render the shell so template improvements reach existing files."""
    payload["meta"]["updated"] = now()
    html = TEMPLATE.replace("__TITLE__", esc(payload["meta"]["title"]))
    html = DATA_RE.sub(
        lambda m: m.group(1) + "\n" + embed(payload) + "\n" + m.group(3), html, count=1
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)


def esc(text):
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def read_body(value):
    if value == "-":
        return sys.stdin.read().strip()
    return value or ""


def fresh(title, spec):
    return {
        "meta": {
            "title": title,
            "spec": spec,
            "created": now(),
            "updated": now(),
        },
        "notes": [],
    }


# ---------------------------------------------------------------------- actions


def cmd_init(args):
    if load(args.file) is not None and not args.force:
        print(f"{args.file} already exists; leaving its notes intact.")
        return
    save(args.file, fresh(args.title, args.spec))
    print(f"Created {args.file}")


def cmd_add(args):
    payload = load(args.file)
    if payload is None:
        payload = fresh(args.title_page or "Implementation notes", args.spec_page)
    note = {
        "id": f"n{len(payload['notes']) + 1}",
        "type": args.type,
        "title": args.title,
        "body": read_body(args.body),
        "spec": args.spec or "",
        "where": [w.strip() for w in (args.where or "").split(",") if w.strip()],
        "impact": args.impact,
        "status": "open" if args.type == "question" else "settled",
        "ts": now(),
        "resolution": "",
    }
    payload["notes"].append(note)
    save(args.file, payload)
    print(f"{note['id']}  {note['type']}: {note['title']}")


def cmd_resolve(args):
    payload = load(args.file)
    if payload is None:
        sys.exit(f"No such notes file: {args.file}")
    for note in payload["notes"]:
        if note["id"] == args.id:
            note["status"] = "resolved"
            note["resolution"] = read_body(args.body)
            save(args.file, payload)
            print(f"{note['id']} resolved")
            return
    sys.exit(f"No note with id {args.id}")


def cmd_list(args):
    payload = load(args.file)
    if payload is None:
        sys.exit(f"No such notes file: {args.file}")
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    for note in payload["notes"]:
        flag = " [OPEN]" if note["status"] == "open" else ""
        print(f"{note['id']}  {note['type']:<9} {note['title']}{flag}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("--file", required=True)
    p.add_argument("--title", default="Implementation notes")
    p.add_argument("--spec", default="")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("add")
    p.add_argument("--file", required=True)
    p.add_argument("--type", required=True, choices=TYPES)
    p.add_argument("--title", required=True)
    p.add_argument("--body", default="", help='note body, or "-" to read stdin')
    p.add_argument("--spec", default="", help="the spec clause this relates to")
    p.add_argument("--where", default="", help="comma-separated file:line refs")
    p.add_argument("--impact", default="medium", choices=IMPACTS)
    p.add_argument("--title-page", default="", help="page title if file is new")
    p.add_argument("--spec-page", default="", help="spec ref if file is new")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("resolve")
    p.add_argument("--file", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--body", default="")
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("list")
    p.add_argument("--file", required=True)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root {
    --bg: #fbfaf8; --panel: #ffffff; --ink: #16151a; --muted: #6b6a73;
    --rule: #e6e3dd; --shadow: 0 1px 2px rgba(20,18,16,.05);
    --decision: #2563eb; --deviation: #c2620a; --tradeoff: #7c3aed; --question: #d61f4e;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #131316; --panel: #1a1a1f; --ink: #edecea; --muted: #9b99a3;
      --rule: #2c2c33; --shadow: none;
      --decision: #7ba6ff; --deviation: #f0a44a; --tradeoff: #b494ff; --question: #ff7a97;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font: 16px/1.6 ui-sans-serif, -apple-system, "Segoe UI", Inter, system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: 820px; margin: 0 auto; padding: 56px 24px 120px; }
  header { border-bottom: 1px solid var(--rule); padding-bottom: 24px; margin-bottom: 8px; }
  h1 { font-size: 30px; line-height: 1.2; margin: 0 0 10px; letter-spacing: -.02em; }
  .meta { color: var(--muted); font-size: 13px; display: flex; gap: 16px; flex-wrap: wrap; }
  .meta code {
    font: 12px ui-monospace, SFMono-Regular, Menlo, monospace;
    background: var(--panel); border: 1px solid var(--rule);
    border-radius: 4px; padding: 1px 6px;
  }
  .bar { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin: 24px 0 28px; }
  .chip {
    border: 1px solid var(--rule); background: var(--panel); color: var(--ink);
    border-radius: 999px; padding: 5px 13px; font-size: 13px; cursor: pointer;
    font-family: inherit; transition: background .12s, border-color .12s;
  }
  .chip:hover { border-color: var(--muted); }
  .chip[aria-pressed="true"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }
  .chip .n { opacity: .55; margin-left: 6px; font-variant-numeric: tabular-nums; }
  .spacer { flex: 1; }
  .ghost { border: 1px solid var(--rule); background: none; color: var(--muted);
           border-radius: 6px; padding: 5px 11px; font-size: 13px; cursor: pointer; font-family: inherit; }
  .ghost:hover { color: var(--ink); border-color: var(--muted); }
  .alert {
    border: 1px solid var(--rule); border-left: 3px solid var(--question);
    background: var(--panel); border-radius: 8px; padding: 14px 18px;
    margin-bottom: 28px; font-size: 14px;
  }
  .alert b { color: var(--question); }
  .note {
    background: var(--panel); border: 1px solid var(--rule); border-left: 3px solid var(--rule);
    border-radius: 8px; padding: 18px 20px; margin-bottom: 14px; box-shadow: var(--shadow);
  }
  .note.decision  { border-left-color: var(--decision); }
  .note.deviation { border-left-color: var(--deviation); }
  .note.tradeoff  { border-left-color: var(--tradeoff); }
  .note.question  { border-left-color: var(--question); }
  .note h2 { font-size: 17px; margin: 0 0 8px; line-height: 1.35; letter-spacing: -.01em; }
  .tags { display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
          font-size: 11px; letter-spacing: .07em; text-transform: uppercase;
          color: var(--muted); margin-bottom: 9px; }
  .kind { font-weight: 650; }
  .decision .kind  { color: var(--decision); }
  .deviation .kind { color: var(--deviation); }
  .tradeoff .kind  { color: var(--tradeoff); }
  .question .kind  { color: var(--question); }
  .open { color: var(--question); font-weight: 650; }
  .body p { margin: 0 0 10px; }
  .body ul { margin: 0 0 10px; padding-left: 20px; }
  .body li { margin-bottom: 3px; }
  .body code, .refs code {
    font: 13px ui-monospace, SFMono-Regular, Menlo, monospace;
    background: var(--bg); border: 1px solid var(--rule); border-radius: 4px; padding: 1px 5px;
  }
  .foot { margin-top: 12px; padding-top: 10px; border-top: 1px dashed var(--rule);
          font-size: 13px; color: var(--muted); display: flex; gap: 18px; flex-wrap: wrap; }
  .resolution { margin-top: 10px; padding-left: 12px; border-left: 2px solid var(--rule);
                font-size: 14px; color: var(--muted); }
  .empty { color: var(--muted); text-align: center; padding: 60px 0; font-size: 15px; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1 id="pageTitle"></h1>
    <div class="meta" id="pageMeta"></div>
  </header>
  <div class="bar" id="filters"></div>
  <div id="alert"></div>
  <div id="notes"></div>
</div>

<script id="notes-data" type="application/json">
{"meta": {"title": "Implementation notes", "spec": "", "created": "", "updated": ""}, "notes": []}
</script>

<script>
(function () {
  var data = JSON.parse(document.getElementById('notes-data').textContent);
  var notes = data.notes || [];
  var meta = data.meta || {};
  var active = 'all';

  var LABEL = {
    decision: 'Design decision', deviation: 'Deviation',
    tradeoff: 'Tradeoff', question: 'Open question'
  };

  function esc(s) {
    return String(s).replace(/[&<>]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c];
    });
  }

  // Deliberately small: paragraphs, dash bullets, `code`, **bold**. Notes are prose,
  // not documents, so a full markdown parser would be more surface than it is worth.
  function fmt(text) {
    if (!text) return '';
    var out = '', list = null;
    esc(text).split('\n').forEach(function (line) {
      var t = line.trim();
      if (/^[-*]\s+/.test(t)) {
        list = (list || '') + '<li>' + inline(t.replace(/^[-*]\s+/, '')) + '</li>';
        return;
      }
      if (list) { out += '<ul>' + list + '</ul>'; list = null; }
      if (t) out += '<p>' + inline(t) + '</p>';
    });
    if (list) out += '<ul>' + list + '</ul>';
    return out;
  }

  function inline(s) {
    return s.replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  }

  function when(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    return isNaN(d) ? iso : d.toLocaleString(undefined,
      { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  }

  document.title = meta.title || 'Implementation notes';
  document.getElementById('pageTitle').textContent = meta.title || 'Implementation notes';

  var bits = [];
  if (meta.spec) bits.push('Spec: <code>' + esc(meta.spec) + '</code>');
  bits.push(notes.length + (notes.length === 1 ? ' note' : ' notes'));
  if (meta.updated) bits.push('Updated ' + esc(when(meta.updated)));
  document.getElementById('pageMeta').innerHTML = bits.map(function (b) {
    return '<span>' + b + '</span>';
  }).join('');

  function count(kind) {
    return kind === 'all' ? notes.length
      : notes.filter(function (n) { return n.type === kind; }).length;
  }

  var bar = document.getElementById('filters');
  ['all', 'decision', 'deviation', 'tradeoff', 'question'].forEach(function (kind) {
    if (kind !== 'all' && !count(kind)) return;
    var b = document.createElement('button');
    b.className = 'chip';
    b.setAttribute('aria-pressed', kind === 'all');
    b.innerHTML = (kind === 'all' ? 'All' : LABEL[kind] + 's') +
                  '<span class="n">' + count(kind) + '</span>';
    b.onclick = function () {
      active = kind;
      [].forEach.call(bar.querySelectorAll('.chip'), function (c) {
        c.setAttribute('aria-pressed', c === b);
      });
      render();
    };
    bar.appendChild(b);
  });

  var spacer = document.createElement('span');
  spacer.className = 'spacer';
  bar.appendChild(spacer);

  var copy = document.createElement('button');
  copy.className = 'ghost';
  copy.textContent = 'Copy as markdown';
  copy.onclick = function () {
    var md = '# ' + (meta.title || 'Implementation notes') + '\n\n' +
      notes.map(function (n) {
        var s = '## ' + LABEL[n.type] + ': ' + n.title + '\n\n' + (n.body || '');
        if (n.spec) s += '\n\nSpec: ' + n.spec;
        if (n.where && n.where.length) s += '\n\nWhere: ' + n.where.join(', ');
        if (n.resolution) s += '\n\nResolved: ' + n.resolution;
        return s;
      }).join('\n\n');
    navigator.clipboard.writeText(md).then(function () {
      copy.textContent = 'Copied';
      setTimeout(function () { copy.textContent = 'Copy as markdown'; }, 1600);
    });
  };
  bar.appendChild(copy);

  var open = notes.filter(function (n) { return n.status === 'open'; });
  document.getElementById('alert').innerHTML = open.length
    ? '<div class="alert"><b>' + open.length + ' open question' +
      (open.length === 1 ? '' : 's') + '</b> waiting on you — ' +
      open.map(function (n) { return esc(n.title); }).join(' · ') + '</div>'
    : '';

  function render() {
    var list = active === 'all'
      ? notes : notes.filter(function (n) { return n.type === active; });
    var host = document.getElementById('notes');
    if (!list.length) {
      host.innerHTML = '<div class="empty">Nothing logged yet.</div>';
      return;
    }
    host.innerHTML = list.map(function (n) {
      var tags = '<span class="kind">' + LABEL[n.type] + '</span>';
      if (n.impact && n.impact !== 'medium') tags += '<span>' + esc(n.impact) + ' impact</span>';
      if (n.status === 'open') tags += '<span class="open">needs your call</span>';
      if (n.ts) tags += '<span>' + esc(when(n.ts)) + '</span>';

      var foot = [];
      if (n.spec) foot.push('Spec: <code>' + esc(n.spec) + '</code>');
      if (n.where && n.where.length) {
        foot.push('Where: ' + n.where.map(function (w) {
          return '<code>' + esc(w) + '</code>';
        }).join(' '));
      }

      return '<article class="note ' + esc(n.type) + '" id="' + esc(n.id) + '">' +
        '<div class="tags">' + tags + '</div>' +
        '<h2>' + esc(n.title) + '</h2>' +
        '<div class="body">' + fmt(n.body) + '</div>' +
        (n.resolution ? '<div class="resolution">' + fmt(n.resolution) + '</div>' : '') +
        (foot.length ? '<div class="foot refs">' +
          foot.map(function (f) { return '<span>' + f + '</span>'; }).join('') +
          '</div>' : '') +
        '</article>';
    }).join('');
  }

  render();
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
