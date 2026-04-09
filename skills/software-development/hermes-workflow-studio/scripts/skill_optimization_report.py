#!/usr/bin/env python3
import json, pathlib, collections


def main():
    log = pathlib.Path.home() / '.hermes' / 'workflow-step-log.jsonl'
    if not log.exists():
        print('No logs found:', log)
        return

    rows = []
    for line in log.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass

    by_name = collections.defaultdict(list)
    for r in rows:
        by_name[r.get('name','unknown')].append(r)

    print('=== Workflow Skill Optimization Report ===')
    for name, items in sorted(by_name.items(), key=lambda kv: len(kv[1]), reverse=True):
        latest = items[-1]
        skills = latest.get('skills') or []
        print(f"\nStep: {name}")
        print(f"  Runs: {len(items)}")
        print(f"  Model(last): {latest.get('model')}")
        print(f"  Skills(last): {', '.join(skills) if skills else '(none)'}")
        if not skills and len(items) >= 2:
            print('  Suggestion: frequently repeated without skill -> create/refine reusable skill')
        if len(items) >= 3:
            print('  Suggestion: compare prompt variants for this step and consolidate best template')


if __name__ == '__main__':
    main()
