#!/usr/bin/env python3
import argparse, pathlib, yaml


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def to_mermaid(wf):
    lines = ["flowchart TD"]
    steps = wf.get('steps', [])
    for s in steps:
        sid = s['id']
        label = f"{s['name']}\\n[{s.get('model','')}]"
        lines.append(f"  {sid}[\"{label}\"]")
    for s in steps:
        for dep in s.get('depends_on', []):
            lines.append(f"  {dep} --> {s['id']}")
    return "\n".join(lines) + "\n"


def to_text_tree(wf):
    by_id = {s['id']: s for s in wf.get('steps', [])}
    children = {k: [] for k in by_id}
    roots = []
    for sid, s in by_id.items():
        deps = s.get('depends_on', [])
        if not deps:
            roots.append(sid)
        for d in deps:
            if d in children:
                children[d].append(sid)

    out = [f"Workflow: {wf.get('name','unnamed')}"]

    def walk(sid, depth=0, seen=None):
        if seen is None:
            seen = set()
        if sid in seen:
            out.append("  " * depth + f"- {sid} (cycle)")
            return
        seen.add(sid)
        s = by_id[sid]
        out.append("  " * depth + f"- {sid}: {s.get('name','')} | model={s.get('model','')} | skills={','.join(s.get('skills',[]))}")
        out.append("  " * (depth + 1) + f"prompt: {s.get('prompt','')}")
        out.append("  " * (depth + 1) + f"output: {s.get('output','')}")
        for c in children.get(sid, []):
            walk(c, depth + 1, set(seen))

    for r in roots:
        walk(r)
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True, help='workflow.yaml path')
    ap.add_argument('--mmd', default='diagram.mmd')
    ap.add_argument('--txt', default='diagram.txt')
    args = ap.parse_args()

    wf = load(args.inp)
    pathlib.Path(args.mmd).write_text(to_mermaid(wf), encoding='utf-8')
    pathlib.Path(args.txt).write_text(to_text_tree(wf), encoding='utf-8')
    print(f"Rendered: {args.mmd}, {args.txt}")


if __name__ == '__main__':
    main()
