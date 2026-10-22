---
name: to-issues
description: Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. 将计划、spec 或 PRD 拆成可独立领取的纵切 issues。Use when converting a plan into issues, creating implementation tickets, or breaking work into issues.
---

# To Issues

用 vertical slices（tracer bullets）把计划拆成可独立领取的 issues。

发布前需要 issue tracker 和 triage label vocabulary。配置缺失时，展示已拆分的 slices 并等待用户指定 tracker；不得创建外部 issue。

## 流程

### 1. 收集上下文

基于当前对话上下文工作。如果用户传入 issue reference（issue number、URL 或 path），从 issue tracker 获取并读取完整 body 和 comments。

### 2. 探索代码库（可选）

如果尚未探索代码库，先了解当前代码状态。Issue titles 和 descriptions 应使用项目 domain glossary vocabulary，并尊重相关区域的 ADRs。

### 3. 起草 vertical slices

将计划拆成 **tracer bullet** issues。每个 issue 都是贯穿所有 integration layers 的细纵切，而不是某一层的 horizontal slice。

Slices 可标记为 'HITL' 或 'AFK'。HITL slices 需要人工交互，如 architectural decision 或 design review。AFK slices 可在无人工交互情况下实现并合并。能选 AFK 时优先 AFK。

<vertical-slice-rules>
- 每个 slice 都交付一条窄但完整的跨层路径（schema, API, UI, tests）
- 完成的 slice 可独立 demo 或验证
- 优先许多薄 slices，而不是少数厚 slices
</vertical-slice-rules>

### 4. 询问用户

用编号列表展示拆分方案。每个 slice 展示：

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)

询问用户：

- 粒度是否合适？（too coarse / too fine）
- 依赖关系是否正确？
- 是否应合并或进一步拆分某些 slices？
- HITL 和 AFK 标记是否正确？

迭代直到用户认可拆分。

### 5. 发布 issues 到 issue tracker

对每个已认可 slice，在 issue tracker 发布新 issue。使用下方 issue body template。除非另有指示，这些 issues 视为 ready for AFK agents，因此发布时加上正确 triage label。

按依赖顺序发布 issues（blockers 优先），这样可以在 "Blocked by" 字段引用真实 issue identifiers。

<issue-template>
## Parent

父 issue 在 issue tracker 上的引用（如果源材料是现有 issue；否则省略此部分）。

## What to build

对这个 vertical slice 的简明描述。描述端到端行为，不描述逐层实现。

避免具体文件路径或代码片段，它们很快会过期。例外：如果 prototype 产出的 snippet 比 prose 更精确地编码了决策（state machine、reducer、schema、type shape），可内联在此处，并简要说明它来自 prototype。只保留决策密集部分，不放完整 demo。

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- blocking ticket 的引用（如有）

无 blockers 时写 "None - can start immediately"。

</issue-template>

不要关闭或修改任何 parent issue。
