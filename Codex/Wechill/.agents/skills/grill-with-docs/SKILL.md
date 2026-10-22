---
name: grill-with-docs
description: Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. 基于现有领域模型和已记录决策压力测试计划，并同步更新 CONTEXT.md/ADRs。Use when stress-testing a plan against project language and documented decisions.
---

<what-to-do>

围绕计划的每个方面持续追问，直到达成共同理解。沿设计树逐个分支推进，逐一解决决策之间的依赖关系。每个问题都给出你的推荐答案。

一次只问一个问题，并在继续前等待该问题的反馈。

如果某个问题可以通过探索代码库回答，就先探索代码库。

</what-to-do>

<supporting-info>

## 领域意识

探索代码库时，同时查找已有文档：

### 文件结构

多数 repos 只有一个 context：

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

如果根目录存在 `CONTEXT-MAP.md`，说明 repo 有多个 contexts。该 map 指向每个 context 的位置：

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

惰性创建文件：只有有内容要写时才创建。若没有 `CONTEXT.md`，在第一个术语被确认时创建。若没有 `docs/adr/`，在第一个 ADR 需要时创建。

## 会话中

### 对照 glossary 挑战

当用户使用的术语与 `CONTEXT.md` 中已有语言冲突时，立即指出。"Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### 收紧模糊语言

当用户使用模糊或过载术语时，提出精确 canonical term。"You're saying 'account' — do you mean the Customer or the User? Those are different things."

### 讨论具体场景

讨论 domain relationships 时，用具体场景压力测试。构造能触及 edge cases 的场景，迫使用户明确概念边界。

### 与代码交叉验证

当用户说明某事如何工作时，检查代码是否一致。如发现矛盾，直接指出："Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### 内联更新 CONTEXT.md

术语被确认后，立即更新 `CONTEXT.md`。不要攒到最后，边确认边记录。使用 [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md) 格式。

不要让 `CONTEXT.md` 绑定实现细节。只包含 domain experts 也认为有意义的术语。

### 谨慎提出 ADRs

只有同时满足以下三点时，才提出创建 ADR：

1. **Hard to reverse** — 之后改变主意的成本明显
2. **Surprising without context** — 未来读者会疑惑 "why did they do it this way?"
3. **The result of a real trade-off** — 确实存在备选方案，并基于具体原因选择了其中一个

只要缺少任意一点，就跳过 ADR。使用 [ADR-FORMAT.md](./ADR-FORMAT.md) 格式。

</supporting-info>
