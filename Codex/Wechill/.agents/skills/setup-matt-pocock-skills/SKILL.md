---
name: setup-matt-pocock-skills
description: Sets up an `## Agent skills` block in AGENTS.md and `docs/agents/` so tracker-writing skills know this repo's issue tracker, triage label vocabulary, and domain doc layout. 在 AGENTS.md 和 docs/agents/ 中配置 issue tracker、triage labels 与领域文档布局。Use before publishing with `to-issues`, `to-prd`, or `triage`, or when configuring those integrations.
---

# 设置 Agent Skills

搭建会写入 issue tracker 的 engineering skills 所需的 per-repo configuration：

- **Issue tracker** — issues 所在位置（默认 GitHub；也支持 local markdown）
- **Triage labels** — 五个 canonical triage roles 使用的字符串
- **Domain docs** — `CONTEXT.md` 和 ADRs 的位置，以及读取规则

这是 prompt-driven skill，不是 deterministic script。先探索、展示发现、与用户确认，然后写入。未完成此配置时，`diagnose`、`tdd`、`improve-codebase-architecture` 与 `zoom-out` 仍可基于 `AGENTS.md` 和代码工作；tracker-writing skills 只能生成草稿。

## 流程

### 1. 探索

查看当前 repo，理解初始状态。读取已存在内容，不要假设：

- `git remote -v` 和 `.git/config` — 这是 GitHub repo 吗？是哪一个？
- repo 根目录的 `AGENTS.md` — 是否存在？是否已有 `## Agent skills` section？
- `CONTEXT.md` and `CONTEXT-MAP.md` at the repo root
- `docs/adr/` 以及任何 `src/*/docs/adr/` directories
- `docs/agents/` — 此 skill 以前的输出是否已存在？
- `.scratch/` — 表明可能已经使用 local-markdown issue tracker convention

### 2. 展示发现并询问

总结已有内容和缺失内容。然后带用户逐个处理三个 decisions：展示一个 section，得到用户回答，再进入下一个。不要一次性抛出三个。

假设用户不知道这些术语含义。每个 section 先给简短解释（它是什么、为什么 skills 需要它、不同选择会改变什么），再展示选项和默认值。

**Section A — Issue tracker.**

> Explainer: "issue tracker" 是这个 repo 存放 issues 的地方。`to-issues`、`triage`、`to-prd`、`qa` 等 skills 会读写它，因此需要知道是调用 `gh issue create`、写 `.scratch/` 下的 markdown 文件，还是遵循你描述的其他 workflow。选择你实际跟踪工作的地方。

默认姿态：这些 skills 最初面向 GitHub。若 `git remote` 指向 GitHub，推荐 GitHub。若 `git remote` 指向 GitLab（`gitlab.com` 或 self-hosted host），推荐 GitLab。否则（或用户偏好其他方式），提供：

- **GitHub** — issues 位于 repo 的 GitHub Issues（使用 `gh` CLI）
- **GitLab** — issues 位于 repo 的 GitLab Issues（使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI）
- **Local markdown** — issues 作为文件位于本 repo 的 `.scratch/<feature>/` 下（适合个人项目或无 remote 的 repo）
- **Other** (Jira, Linear, etc.) — 让用户用一段话描述 workflow；skill 将其记录为 freeform prose

**Section B — Triage label vocabulary.**

> Explainer: `triage` skill 处理新 issue 时，会让它通过一个 state machine：needs evaluation、waiting on reporter、ready for an AFK agent、ready for a human、或 won't fix。为此，它需要应用与你*实际配置*匹配的 labels（或 issue tracker 中等价物）。如果 repo 已使用不同 label names（如 `bug:triage` 而不是 `needs-triage`），在这里映射，避免 skill 创建重复标签。

五个 canonical roles：

- `needs-triage` — maintainer 需要评估
- `needs-info` — 等待 reporter
- `ready-for-agent` — 已完整说明，AFK-ready（agent 可在没有人工上下文时领取）
- `ready-for-human` — 需要人工实现
- `wontfix` — 不会处理

默认：每个 role 的字符串等于其名称。询问用户是否要覆盖任何项。如果 issue tracker 没有现有 labels，默认值即可。

**Section C — Domain docs.**

> Explainer: 一些 skills（`improve-codebase-architecture`、`diagnose`、`tdd`）会读取 `CONTEXT.md` 学习项目 domain language，并读取 `docs/adr/` 了解历史 architectural decisions。它们需要知道 repo 是一个 global context，还是多个 contexts（如 frontend/backend 分离的 monorepo），以便查找正确位置。

确认 layout：

- **Single-context** — repo 根目录一个 `CONTEXT.md` + `docs/adr/`。多数 repo 如此。
- **Multi-context** — 根目录 `CONTEXT-MAP.md` 指向每个 context 的 `CONTEXT.md`（通常是 monorepo）。

### 3. 确认并编辑

向用户展示草稿：

- 要添加到 `AGENTS.md` 的 `## Agent skills` block
- `docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md`、`docs/agents/domain.md` 的内容

写入前允许用户修改。

### 4. 写入

**选择要编辑的文件：**

- 如果 `AGENTS.md` 存在，编辑它。
- 如果不存在，创建前先询问，除非用户已经要求端到端完成 setup。

如果选中文件里已有 `## Agent skills` block，原地更新其内容，不追加重复 block。不要覆盖周边 sections 的用户编辑。

The block:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs

[one-line summary of layout — "single-context" or "multi-context"]. See `docs/agents/domain.md`.
```

然后使用此 skill folder 中的 seed templates 作为起点，写入三个 docs files：

- [issue-tracker-github.md](./issue-tracker-github.md) — GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md) — GitLab issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md) — local-markdown issue tracker
- [triage-labels.md](./triage-labels.md) — label mapping
- [domain.md](./domain.md) — domain doc consumer rules + layout

对于 "other" issue trackers，基于用户描述从零编写 `docs/agents/issue-tracker.md`。

### 5. 完成

告知用户 setup 已完成，以及哪些 engineering skills 会读取这些文件。说明之后可直接编辑 `docs/agents/*.md`；只有要切换 issue tracker 或从头重建时才需要重新运行此 skill。
