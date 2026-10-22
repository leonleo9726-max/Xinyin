---
name: write-a-skill
description: Create new agent skills with proper structure, progressive disclosure, and bundled resources. 创建或更新结构正确、渐进披露、带必要资源的 Codex agent skill。Use when the user wants to create, write, build, or update a skill.
---

# 编写 Skills

系统 `skill-creator` skill 可用时，以它为准。本地 skill 是精简 fallback，应保持与系统指南一致。

## 流程

1. **Gather requirements** - 向用户确认：
   - skill 覆盖什么任务/领域？
   - 需要处理哪些具体用例？
   - 需要 executable scripts，还是只需要 instructions？
   - 是否有 reference materials 需要包含？

2. **Draft the skill** - 创建：
   - 包含精简 instructions 的 SKILL.md
   - `agents/openai.yaml` with `display_name`, `short_description`, and `default_prompt`
   - 如 SKILL.md 接近 500 行或有可选深层细节，在 `references/` 下添加额外文件
   - 如果需要确定性操作，添加 utility scripts

3. **Review with user** - 展示草稿并询问：
   - 是否覆盖你的用例？
   - 是否有遗漏或不清楚的地方？
   - 哪些部分需要更详细或更精简？

## Skill 结构

```
skill-name/
├── SKILL.md              # Main instructions（必需）
├── agents/
│   └── openai.yaml       # UI metadata（推荐）
├── references/           # Detailed docs（如需要）
└── scripts/              # Utility scripts（如需要）
    └── helper.js
```

## SKILL.md Template

```md
---
name: skill-name
description: Brief description of capability. Use when [specific triggers].
---

# Skill Name

## Quick start

[Minimal working example]

## Workflows

[Step-by-step processes with checklists for complex tasks]

## Advanced features

[Link to separate files under references/ when needed.]
```

## Description 要求

`description` 是 agent 决定是否加载 skill 时看到的**唯一内容**。它会和所有已安装 skill 一起出现在系统提示中。agent 会读取这些 descriptions，并基于用户请求选择相关 skill。

**目标**：给 agent 足够信息，使其知道：

1. 这个 skill 提供什么能力
2. 何时/为何触发它（具体关键词、上下文、文件类型）

**格式**：

- Max 1024 chars
- 使用第三人称
- 第一句：说明它做什么
- 第二句：`Use when [specific triggers]`

**Good example**:

```
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Bad example**:

```
Helps with documents.
```

坏例子无法让 agent 区分它和其他 document skills。

## 何时添加 Scripts

以下情况添加 utility scripts：

- 操作是确定性的（validation、formatting）
- 同样代码会被反复生成
- 错误需要显式处理

相比临时生成代码，scripts 节省 token 且更可靠。

## 何时拆分文件

以下情况拆分到独立文件：

- SKILL.md approaches 500 lines
- 内容有不同领域（finance vs sales schemas）
- 高级功能很少需要

## Review Checklist

草稿完成后验证：

- [ ] Description 包含触发条件（"Use when..."）
- [ ] Frontmatter 只包含 `name` 和 `description`
- [ ] `agents/openai.yaml` 存在且与 skill 匹配
- [ ] SKILL.md 保持精简，并链接到可选 references
- [ ] 没有时效性信息
- [ ] 术语一致
- [ ] 包含具体示例
- [ ] References 只深一层
