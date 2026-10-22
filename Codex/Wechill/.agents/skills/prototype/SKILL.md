---
name: prototype
description: Build a throwaway prototype to flesh out a design before committing to it. 构建一次性 prototype，用于验证逻辑/状态模型或比较多个 UI 方案。Use when the user wants to prototype, sanity-check a data model or state machine, mock up a UI, explore design options, or says "prototype this", "let me play with it", "try a few designs".
---

# Prototype

prototype 是**用于回答问题的一次性代码**。问题决定形态。

## 选择分支

根据用户提示、周边代码，或在用户在线时直接询问，判断要回答的问题：

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md)。构建一个小型交互式 terminal app，用难以纸面推理的 case 推动 state machine。
- **"What should this look like?"** → [UI.md](UI.md)。在单一路由上生成几个差异明显的 UI variations，通过 URL search param 和 floating bottom bar 切换。

两个分支会产生完全不同的 artifact，选错会浪费整个 prototype。如果问题确实模糊且用户不可联系，默认选择更匹配周边代码的分支（backend module → logic；page/component → UI），并在 prototype 顶部说明假设。

## 通用规则

1. **从第一天起就是一次性代码，并清楚标注。** 将 prototype code 放在实际会使用它的位置附近（紧邻要验证的 module 或 page），让上下文明显；但命名要让普通读者一眼看出这是 prototype，不是 production。一次性 UI routes 遵守项目已有 routing convention，不要发明新的顶层结构。
2. **一个命令即可运行。** 使用项目现有 task runner 支持的形式，如 `pnpm <name>`、`python <path>`、`bun <path>` 等。用户应能不思考就启动。
3. **默认不持久化。** State 放在内存中。Persistence 是 prototype 要检查的东西，不应成为依赖。如果问题明确涉及数据库，使用 scratch DB 或带清楚 "PROTOTYPE — wipe me" 名称的本地文件。
4. **跳过打磨。** 不写 tests，不做超出 runnable 所需的 error handling，不抽象。目标是快速学习然后删除。
5. **暴露 state。** 每次 action（logic）或 variant switch（UI）后，打印或渲染完整相关 state，让用户看到变化。
6. **完成后删除或吸收。** 当 prototype 回答完问题后，要么删除它，要么把验证过的决策合并进真实代码；不要让它在 repo 里腐烂。

## 完成后

prototype 中唯一值得保留的是_答案_。把答案和它回答的问题记录到持久位置（commit message、ADR、issue，或 prototype 旁的 `NOTES.md`）。如果用户在线，通过简短对话记录；如果不在线，留下占位内容，方便用户或下一轮处理人在删除 prototype 前补上结论。
