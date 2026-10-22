---
name: improve-codebase-architecture
description: Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions in docs/adr/. 基于 CONTEXT.md 和 ADRs 发现代码库中的 deepening/refactoring 机会。Use when improving architecture, finding refactoring opportunities, consolidating tightly-coupled modules, or making a codebase more testable and AI-navigable.
---

# 改进代码库架构

暴露 architectural friction，并提出 **deepening opportunities**：把 shallow modules 转成 deep ones 的 refactors。目标是 testability 和 AI-navigability。

## 术语表

每条建议都严格使用这些术语。语言一致性就是重点；不要漂移到 "component"、"service"、"API" 或 "boundary"。完整定义见 [LANGUAGE.md](LANGUAGE.md)。

- **Module** — 拥有 interface 和 implementation 的任何东西（function、class、package、slice）。
- **Interface** — caller 使用 module 必须知道的一切：types、invariants、error modes、ordering、config。不只是 type signature。
- **Implementation** — 内部代码。
- **Depth** — interface 上的 leverage：小 interface 背后有大量 behavior。**Deep** = high leverage。**Shallow** = interface 几乎和 implementation 一样复杂。
- **Seam** — interface 所在处；无需原地修改即可改变 behavior 的位置。（使用这个词，不用 "boundary"。）
- **Adapter** — 在 seam 处满足 interface 的具体实现。
- **Leverage** — callers 从 depth 获得的东西。
- **Locality** — maintainers 从 depth 获得的东西：change、bugs、knowledge 集中在一处。

关键原则（完整列表见 [LANGUAGE.md](LANGUAGE.md)）：

- **Deletion test**：想象删除该 module。如果 complexity 消失了，它只是 pass-through。如果 complexity 在 N 个 callers 中重新出现，它就在创造价值。
- **The interface is the test surface.**
- **One adapter = hypothetical seam. Two adapters = real seam.**

该 skill 受项目 domain model 指导。domain language 为好的 seams 命名；ADRs 记录不应重复争论的 decisions。

## 流程

### 1. 探索

先读取项目 domain glossary 以及所触及区域的 ADRs。若不存在，使用 `AGENTS.md` 和代码中稳定的领域术语，并将缺失文档作为发现报告；不要为了完成本次审查创建它们。

然后用 `rg`、文件读取，以及当前环境可用的 subagent tools 直接探索代码库。不要死套启发式；自然探索并记录你感受到 friction 的地方：

- 哪些概念需要在许多小 modules 之间来回跳转才能理解？
- 哪些 modules 是 **shallow**：interface 几乎和 implementation 一样复杂？
- 哪里只是为了 testability 抽出了 pure functions，但真正 bugs 藏在调用方式中（没有 **locality**）？
- 哪里 tightly-coupled modules 越过 seams 泄漏？
- 哪些代码未测试，或很难通过当前 interface 测试？

对任何疑似 shallow 的东西应用 **deletion test**：删除它会集中 complexity，还是只是移动 complexity？"yes, concentrates" 是你要找的信号。

### 2. 展示候选项

用编号列表展示 deepening opportunities。每个 candidate 包含：

- **Files** — 涉及哪些 files/modules
- **Problem** — 当前 architecture 为什么造成 friction
- **Solution** — 用 plain English 描述要改变什么
- **Benefits** — 用 locality 和 leverage 解释，同时说明 tests 会如何改善

**领域用 CONTEXT.md vocabulary，架构用 [LANGUAGE.md](LANGUAGE.md) vocabulary。** 如果 `CONTEXT.md` 定义了 "Order"，就说 "the Order intake module"，不要说 "the FooBarHandler"，也不要说 "the Order service"。

**ADR conflicts**：如果 candidate 与已有 ADR 冲突，只有当 friction 真实到值得重开 ADR 时才提出。清楚标记（如 _"contradicts ADR-0007 — but worth reopening because…"_）。不要列出 ADR 理论上禁止的每个 refactor。

此时不要提出 interfaces。询问用户："Which of these would you like to explore?"

### 3. Grilling loop

用户选择 candidate 后，进入 grilling conversation。与用户一起走设计树：constraints、dependencies、deepened module 的形状、seam 背后的内容、哪些 tests 能保留。

当 decisions 明确时，内联处理副作用：

- **用 `CONTEXT.md` 中不存在的概念命名 deepened module？** 将该术语加入 `CONTEXT.md`，遵循 `$grill-with-docs` 的同样纪律（见 [CONTEXT-FORMAT.md](../grill-with-docs/CONTEXT-FORMAT.md)）。文件不存在时惰性创建。
- **对话中收紧了模糊术语？** 立即更新 `CONTEXT.md`。
- **用户用承重理由拒绝 candidate？** 提议创建 ADR，表达为：_"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ 只有当该理由确实能帮助未来 explorer 避免重复建议同一事项时才提议。跳过临时理由（"not worth it right now"）和显而易见理由。见 [ADR-FORMAT.md](../grill-with-docs/ADR-FORMAT.md)。
- **想探索 deepened module 的替代 interfaces？** 见 [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md)。
