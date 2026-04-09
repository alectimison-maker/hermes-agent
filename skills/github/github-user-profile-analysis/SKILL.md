---
name: github-user-profile-analysis
description: 深度分析 GitHub 用户的公开信息（仓库、Stars、关注关系、活动轨迹、研究领域与关系树），支持以该用户为中心的树状扩散剖析。
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, profile-analysis, social-graph, research-domain, stars, repos, activity]
    related_skills: [codebase-inspection, github-repo-management, github-repo-seo-pack]
prerequisites:
  commands: [python3]
---

# GitHub 用户深度画像（树状扩散版）

用于回答：
- “分析一下这个 GitHub 用户是怎样的人”
- “除了仓库和 star，再看关注关系、研究方向、社交图谱”
- “以此人为中心做树状扩散深度剖析”

本技能只使用公开信息，不推断隐私数据。

## 分析范围（公开信息）

一级（用户本人）：
1) Profile 基础信息：bio、location、website、followers/following
2) Repos：数量、语言分布、更新频率、仓库主题、工程化程度
3) Starred：兴趣偏好、技术栈倾向、学习路线
4) Events：Push/Create/Watch 等行为分布
5) README / pinned / about 信息：自我定位、关键叙事

二级（关系网络）：
6) Following 列表：关注对象类型（个人/组织）
7) Following 的研究/项目领域聚类
8) 与本人方向的重叠度（关键词与技术栈）

三级（可选扩散，默认限制）：
9) 对 Top-N 关键关注对象再做轻量一层扩散（N 建议 3~5）
10) 构建“以用户为中心”的领域树状图（文本树）

## 执行模式

- 默认模式：Depth=1（只分析本人）
- 增强模式：Depth=2（本人 + 关键关注对象）
- 深度模式：Depth=3（谨慎，成本高，需明确用户同意）

建议默认：Depth=2, TopFollowing=10, ExpandTop=3。

## 数据获取策略（API-first + Fallback）

### A. GitHub API（优先）
- `GET /users/{username}`
- `GET /users/{username}/repos?per_page=100`
- `GET /users/{username}/starred?per_page=100`
- `GET /users/{username}/events/public?per_page=100`
- `GET /users/{username}/following?per_page=100`
- 对关键关注对象重复轻量采样：`/users/{x}`, `/repos`, `/starred`（可选）

### B. 浏览器回退（API 限流或受限时）
- 读取 profile 页面可见信息
- 读取 repositories/stars/following 标签页可见条目
- 记录“可见样本”并显式标注置信度下降

## 领域识别方法（Research Domain Inference）

从以下来源提取关键词并聚类：
- 用户 bio + 个人 README 文案
- 仓库名 / description / topics / README 首段
- Starred 仓库名 / description / language
- Following 用户 bio 与代表仓库

聚类输出建议：
- 机器人与视觉（robotics / cv / detection / rm）
- AI Agent 与自动化（agent / workflow / orchestration）
- 大模型训练与微调（finetuning / unsloth / trl）
- 教学与理论工具（logic / education / theorem proving）

## 树状分析输出格式（必须）

```text
用户中心画像树
└─ @username
   ├─ 身份叙事: ...
   ├─ 核心领域
   │  ├─ 领域A（证据：repo1, star1, bio关键词）
   │  ├─ 领域B（证据：repo2, star2）
   │  └─ 领域C（证据：...）
   ├─ 工程风格
   │  ├─ 迭代节奏: ...
   │  ├─ 项目组织: ...
   │  └─ 开源成熟度: ...
   ├─ 关注网络（Top N）
   │  ├─ @userA → 领域: ... → 与本人重叠: ...
   │  ├─ @orgB  → 领域: ... → 与本人重叠: ...
   │  └─ ...
   └─ 扩散观察（可选）
      ├─ 从 @userA 扩散出的子方向: ...
      └─ 从 @orgB 扩散出的子方向: ...
```

## 结论写作规范

1) 所有判断都要附“证据来源”
2) 区分“事实”与“推断”
3) 给出置信度：高 / 中 / 低
4) 避免人格定性过度，使用“更像是…”“倾向于…”
5) 输出同时包含：
   - 优势画像
   - 短板画像
   - 下一步建议（可执行）

## 实战补充（经验更新）

1) 用户名歧义时先从“用户自己的 following 列表”确认目标
- 场景：用户说“分析我关注的人 moyuin”，搜索可能返回多个近似账号（如 `moyinNUHS`、`Moyuin-aka`）。
- 做法：优先打开 `/<requester>?tab=following`，在其关注列表中定位目标账号，再进入目标主页分析。
- 收益：避免误判对象，显著提高结论可信度。

2) API 限流时的最低可交付数据面
- 至少采集 4 个页面：Overview / Repositories / Stars / Following。
- Repositories：记录仓库名、描述、语言、topic、star/fork（可见即采）。
- Stars：至少采样前 20 个可见仓库名，用于兴趣方向聚类。
- Following：至少采样前 10~20 个可见账号，用于关系网络聚类。
- 若 Events 无法稳定获取，明确标注“活动轨迹使用页面可见信号替代”。

3) 浏览器解析优先“稳健选择器”
- 首选抓取 `h3 a` 的仓库/星标名称，再辅助抓 `p` 作为描述。
- Following 页面优先用 `href` 正则匹配 `/用户名` 做去重采样。
- 避免依赖过深 CSS 类名（GitHub 页面结构经常变化）。

4) 输出时必须声明样本范围
- 例如："本次受 API 匿名限流影响，基于网页可见样本（repos=16, stars可见样本=30, following可见样本=20）进行分析。"
- 并将置信度从“高”调整为“中高/中”。

## 常见问题与修复

1) API 限流（403 rate limit exceeded）
- 处理：切换浏览器可见信息 + 降采样
- 标注：结论置信度下降，说明样本范围

2) `python` 不存在
- 处理：使用 `python3`

3) `NoneType` 文本字段报错
- 处理：全部字段使用 `repo.get('description') or ''` 兜底

4) Following 过大导致成本高
- 处理：只分析最近活跃或最相关 Top-N

5) 网页抓取信息不全
- 处理：先 snapshot 可见条目，再补 API；若都受限明确说明

## 推荐默认参数

- Depth: 2
- TopFollowing: 10
- ExpandTop: 3
- RepoSample: 最近更新前 15
- StarSample: 最近 Star 前 20
- EventWindow: 最近 100 条 public events

## 交付模板

1) 数据摘要（repo/star/following/activity）
2) 领域聚类（3~6 类）
3) 树状扩散图（文本）
4) 人设与工作风格（证据绑定）
5) 风险与短板
6) 30 天改进路线（如用户需要）

## 安全与边界

- 仅使用公开信息
- 不输出私人推断（家庭、财务、政治倾向等）
- 不进行攻击性画像或标签化贬损
- 用户若要求更深层扩散，先说明成本与不确定性
