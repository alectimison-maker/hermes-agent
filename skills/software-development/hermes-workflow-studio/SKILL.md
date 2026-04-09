---
name: hermes-workflow-studio
description: 在终端内用模板化方式设计可视化工作流：每步可配置 model、skills、prompt，并生成可读流程图（Mermaid + 文本树）供用户微调。
version: 0.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [workflow, terminal, visualization, model-routing, skills, orchestration]
    related_skills: [writing-plans, subagent-driven-development, hermes-agent]
---

# Hermes Workflow Studio（终端版）

目标：
- 把复杂任务拆成清晰步骤
- 每一步都可配置：`model`、`skills`、`prompt`
- 自动生成初版流程图，用户只需微调

## 适用场景
- 多阶段任务（研究 -> 方案 -> 实施 -> 验证）
- 需要在“质量与速度”间按步骤动态调模
- 需要复用 skill 组合并做 A/B 优化

## 核心产物
1) `workflow.yaml`：工作流规范
2) `diagram.mmd`：Mermaid 流程图
3) `diagram.txt`：终端可读树状图

## 快速开始

1. 复制模板：`templates/workflow.template.yaml` -> `workflow.yaml`
2. 填写每个步骤的 `model` / `skills` / `prompt`
3. 运行渲染脚本（生成 mmd + txt）
4. 先审阅图，再执行流程

## workflow.yaml 约定
每个 step 字段：
- `id`: 唯一 ID
- `name`: 步骤名
- `depends_on`: 依赖步骤 ID 列表
- `model`: 例如 `openrouter:anthropic/claude-sonnet-4`
- `skills`: 例如 `["github-repo-seo-pack"]`
- `prompt`: 该步骤简要提示词
- `output`: 输出物路径或说明

## 推荐执行策略
- 先由 Hermes 自动生成初版 workflow
- 用户只改 3 件事：
  1) 哪几步用高质量模型
  2) 哪几步加载 skill
  3) 哪几步提示词要更严格

## 可视化策略（终端友好 + 点击编辑）
- `diagram.txt`：文本树（终端直接看）
- `diagram.mmd`：Mermaid 图（可在 VSCode/GitHub 渲染）
- `scripts/workflow_ui_server.py` + `assets/workflow-studio.html`：本地 Web UI（点击步骤直接改 model/skills/prompt）

### 启动点击式编辑器
```bash
python3 ~/.hermes/skills/software-development/hermes-workflow-studio/scripts/workflow_ui_server.py
# 浏览器打开 http://127.0.0.1:8765
```

### 渲染流程图
```bash
python3 ~/.hermes/skills/software-development/hermes-workflow-studio/scripts/render_workflow.py --in workflow.yaml
```

### 执行工作流（步骤级 model/skill）
```bash
python3 ~/.hermes/skills/software-development/hermes-workflow-studio/scripts/run_workflow.py --in workflow.yaml
python3 ~/.hermes/skills/software-development/hermes-workflow-studio/scripts/run_workflow.py --in workflow.yaml --execute
```

### 自动补全缺失 skill（首轮草稿）
```bash
python3 ~/.hermes/skills/software-development/hermes-workflow-studio/scripts/auto_skill_bootstrap.py --in workflow.yaml
```
当某步骤 `skills: []` 时，会在 `~/.hermes/skills/custom/` 自动生成草稿 skill，供后续迭代优化。

### 运行日志驱动的 skill 优化建议
执行工作流时会记录步骤日志到 `~/.hermes/workflow-step-log.jsonl`，然后可生成优化报告：
```bash
python3 ~/.hermes/skills/software-development/hermes-workflow-studio/scripts/skill_optimization_report.py
```
用于发现“高频但无 skill”的步骤，并提示沉淀/升级 skill。

## 注意
- 终端内原生拖拽式可视编辑较弱，不建议追求自由布局
- 使用模板化自动布局可保证复杂任务下清晰可读
- 点击式编辑通过本地 Web UI 实现（终端启动，浏览器交互）
- 真正“每步独立模型执行”建议走 wrapper 脚本或子 agent 调度
