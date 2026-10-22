---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up. 将当前对话压缩为交接文档，供另一个 agent 继续处理。Use when the user asks for a handoff, continuation summary, or next-agent brief.
---

编写一份交接文档，总结当前对话，使新的 agent 能继续工作。保存到临时 Markdown 路径：

- Windows PowerShell：在 `$env:TEMP` 下创建唯一路径，例如 `handoff-<timestamp>.md`。
- Unix shell：使用 `mktemp -t handoff-XXXXXX.md`。

如果目标已存在，先读取再写入；否则直接创建。

建议下一会话应使用的 skills（如有）。

不要重复已经记录在其他 artifact 中的内容（PRDs、plans、ADRs、issues、commits、diffs）。改用路径或 URL 引用。

如果用户传入参数，将其视为下一会话的关注点描述，并据此调整文档。
