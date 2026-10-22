---
name: to-prd
description: Turn the current conversation context into a PRD draft, and publish it to the project issue tracker only with explicit user approval. 将当前对话上下文综合成 PRD 草稿；仅在用户明确要求时发布到 issue tracker。Use when the user wants to create a PRD from the current context.
---

这个 skill 基于当前对话上下文和代码库理解生成 PRD。信息足够时直接起草，不进行采访；信息不足时记录明确假设和待确认项。

发布前需要 issue tracker 和 triage label vocabulary。配置缺失时，只交付本地 PRD 草稿，不创建外部 issue。

## 流程

1. 如果尚未探索 repo，先了解当前代码库状态。PRD 全文使用项目 domain glossary vocabulary，并尊重相关区域的 ADRs。

2. 勾勒完成实现需要新增或修改的主要 modules。主动寻找可抽取为 deep modules、并能隔离测试的机会。

deep module（相对于 shallow module）是在简单、可测试且很少变化的 interface 后封装大量功能的 module。

将 modules 与测试决策写入草稿。只有现有对话无法确定、且该决策会实质改变范围时，才单独询问用户。

3. 使用下方模板编写 PRD 草稿。仅在用户明确要求发布且 tracker 配置存在时，发布到项目 issue tracker，并应用 `ready-for-agent` triage label。

<prd-template>

## Problem Statement

从用户视角描述用户面临的问题。

## Solution

从用户视角描述问题的解决方案。

## User Stories

一份很长的编号 user stories 列表。每条 user story 使用以下格式：

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

这份 user stories 列表应足够全面，覆盖 feature 的所有方面。

## Implementation Decisions

列出已经形成的 implementation decisions。可包括：

- 将新增/修改的 modules
- 将修改的 module interfaces
- 来自 developer 的技术澄清
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

不要包含具体文件路径或代码片段。它们可能很快过期。

例外：如果 prototype 产出的 snippet 比 prose 更精确地编码了决策（state machine、reducer、schema、type shape），可内联到相关 decision，并简要说明它来自 prototype。只保留决策密集部分，不放完整 demo。

## Testing Decisions

列出已经形成的 testing decisions。包括：

- 什么是 good test（只测试 external behavior，不测试 implementation details）
- 哪些 modules 会被测试
- tests 的 prior art（即代码库中类似类型的 tests）

## Out of Scope

描述这个 PRD 明确不包含的事项。

## Further Notes

关于 feature 的其他备注。

</prd-template>
