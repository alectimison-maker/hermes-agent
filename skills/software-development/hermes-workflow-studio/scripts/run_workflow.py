#!/usr/bin/env python3
import argparse, pathlib, subprocess, yaml, shlex, json, datetime


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def topo_steps(steps):
    by_id = {s['id']: s for s in steps}
    indeg = {s['id']: 0 for s in steps}
    g = {s['id']: [] for s in steps}
    for s in steps:
        for d in s.get('depends_on', []):
            if d in by_id:
                g[d].append(s['id'])
                indeg[s['id']] += 1
    q = [k for k, v in indeg.items() if v == 0]
    out = []
    while q:
        n = q.pop(0)
        out.append(by_id[n])
        for nxt in g[n]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    if len(out) != len(steps):
        raise ValueError('workflow has cycle or invalid dependencies')
    return out


def parse_model(m):
    if ':' in m:
        p, model = m.split(':', 1)
        return p, model
    return None, m


def log_step(step, cmd, executed):
    log = pathlib.Path.home() / '.hermes' / 'workflow-step-log.jsonl'
    log.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        'ts': datetime.datetime.utcnow().isoformat() + 'Z',
        'id': step.get('id'),
        'name': step.get('name'),
        'model': step.get('model'),
        'skills': step.get('skills', []),
        'prompt': step.get('prompt', ''),
        'output': step.get('output', ''),
        'cmd': cmd,
        'executed': executed,
    }
    with log.open('a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True, help='workflow.yaml path')
    ap.add_argument('--execute', action='store_true', help='actually run hermes commands')
    ap.add_argument('--workdir', default='.', help='working directory')
    args = ap.parse_args()

    wf = load(args.inp)
    steps = topo_steps(wf.get('steps', []))

    for s in steps:
        provider, model = parse_model(s.get('model', ''))
        skills = ','.join(s.get('skills', []))
        prompt = s.get('prompt', '')
        output = s.get('output', '')

        full_prompt = prompt
        if output:
            full_prompt += f"\n\n请将本步骤结果写入文件: {output}"

        cmd = ['hermes', 'chat', '-q', full_prompt]
        if model:
            cmd += ['-m', model]
        if provider:
            cmd += ['--provider', provider]
        if skills:
            cmd += ['-s', skills]

        print(f"\n[STEP] {s['id']} {s.get('name','')}")
        cmd_str = ' '.join(shlex.quote(x) for x in cmd)
        print('[CMD] ' + cmd_str)
        log_step(s, cmd_str, args.execute)

        if args.execute:
            subprocess.run(cmd, cwd=args.workdir, check=False)


if __name__ == '__main__':
    main()
