#!/usr/bin/env python3
import argparse, pathlib, yaml, re, datetime


def slug(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9\-\s_]+', '', s)
    s = re.sub(r'[\s_]+', '-', s).strip('-')
    return s or 'auto-skill'


def make_skill(step, category='custom'):
    base = slug(step.get('name','step'))
    if base == 'auto-skill':
        base = f"step-{step.get('id','x')}"
    name = f"auto-{base}"
    desc = step.get('prompt','').strip()[:80] or f"Auto skill for step {step.get('id','')}"
    today = datetime.date.today().isoformat()
    body = f"""---
name: {name}
description: {desc}
version: 0.1.0
author: Hermes Agent
license: MIT
---

# {step.get('name','Auto Step')}

自动生成技能草稿（{today}）。

## 触发条件
- 当工作流中遇到该类步骤且缺少可复用 skill 时

## 建议步骤
1. 阅读步骤目标：{step.get('prompt','')}
2. 执行并记录成功命令/策略
3. 将稳定做法沉淀为可复用 checklist

## 输出
- {step.get('output','(未指定输出)')}

## 待完善
- 补充失败案例与排错路径
- 补充验证命令
"""
    return name, category, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    args = ap.parse_args()

    wf = yaml.safe_load(pathlib.Path(args.inp).read_text(encoding='utf-8'))
    skills_root = pathlib.Path.home() / '.hermes' / 'skills'
    created = []

    for s in wf.get('steps', []):
        if s.get('skills'):
            continue
        name, cat, body = make_skill(s)
        d = skills_root / cat / name
        d.mkdir(parents=True, exist_ok=True)
        p = d / 'SKILL.md'
        if not p.exists():
            p.write_text(body, encoding='utf-8')
            created.append(str(p))

    print('created_skills:', len(created))
    for x in created:
        print(x)


if __name__ == '__main__':
    main()
