---
name: diagnose
description: Disciplined diagnosis loop for hard bugs and performance regressions. 面向复杂 bug 和性能回归的诊断流程：Reproduce → minimise → hypothesise → instrument → fix → regression-test。Use when the user says "diagnose this" / "debug this", reports broken/failing behavior, or describes a performance regression.
---

# Diagnose

复杂 bug 的纪律化流程。只有明确说明理由时才跳过阶段。

探索代码库时，使用项目 domain glossary 建立相关 modules 的清晰心智模型，并检查所触及区域的 ADRs。若这些文档不存在，改用 `AGENTS.md`、代码与测试建立模型，并在诊断记录中声明文档缺失；不要为诊断任务创建领域文档。

## Phase 1 — 建立 feedback loop

**这就是本 skill 的核心。** 其他都只是机械执行。只要有一个快速、确定、agent 可运行的 bug pass/fail 信号，就能找到原因：bisection、hypothesis-testing、instrumentation 都只是消费这个信号。没有它，盯代码看也救不了。

在这里投入不成比例的精力。**积极、创造性地构建它，不要轻易放弃。**

### 构建方式 — 大致按此顺序尝试

1. **Failing test**，放在能触达 bug 的 seam：unit、integration、e2e。
2. **Curl / HTTP script**，打到正在运行的 dev server。
3. **CLI invocation**，使用 fixture input，并将 stdout 与 known-good snapshot diff。
4. **Headless browser script** (Playwright / Puppeteer)，驱动 UI，并断言 DOM/console/network。
5. **Replay a captured trace.** 保存真实 network request / payload / event log 到磁盘，并在隔离代码路径中 replay。
6. **Throwaway harness.** 启动系统最小子集（一个 service、mocked deps），用单个 function call 触发 bug code path。
7. **Property / fuzz loop.** 如果 bug 是 "sometimes wrong output"，运行 1000 个随机输入寻找 failure mode。
8. **Bisection harness.** 如果 bug 出现在两个已知状态（commit、dataset、version）之间，自动化 "boot at state X, check, repeat"，以便 `git bisect run`。
9. **Differential loop.** 用同一输入跑 old-version vs new-version（或两个 configs），并 diff outputs。
10. **HITL shell script.** 最后手段。如果必须人工点击，用 `scripts/hitl-loop.template.sh` 或 PowerShell 等价脚本驱动人，使 loop 仍然结构化。捕获的输出回流给你。

建立正确 feedback loop，bug 就已经修好 90%。

### 迭代 loop 本身

把 loop 当产品。一旦有了一个 loop，继续问：

- 能否更快？（缓存 setup、跳过无关 init、缩小 test scope）
- 信号能否更尖锐？（断言具体 symptom，而不是 "didn't crash"）
- 能否更确定？（固定时间、seed RNG、隔离 filesystem、冻结 network）

30 秒且 flaky 的 loop 比没有 loop 好不了多少。2 秒确定性 loop 是调试超能力。

### 非确定性 bugs

目标不是 clean repro，而是**更高复现率**。把 trigger 循环 100 次、并行化、加压、缩小 timing windows、注入 sleeps。50% flake 可调试；1% 不可调试。持续提高复现率直到可调试。

### 确实无法建立 loop 时

停下来并明确说明。列出已尝试内容。向用户请求：(a) 能复现问题的环境访问；(b) captured artifact（HAR file、log dump、core dump、带时间戳的 screen recording）；或 (c) 添加临时 production instrumentation 的许可。没有 loop 时，**不要**继续 hypothesise。

在拥有可信 loop 前，不进入 Phase 2。

## Phase 2 — 复现

运行 loop，观察 bug 出现。

确认：

- [ ] loop 产生的是**用户**描述的 failure mode，而不是附近的另一个 failure。Wrong bug = wrong fix。
- [ ] failure 可跨多次运行复现；非确定性 bugs 也要达到足够高的复现率。
- [ ] 已捕获精确 symptom（error message、wrong output、slow timing），后续阶段可验证 fix 是否真正解决它。

复现 bug 前不要继续。

## Phase 3 — 提出假设

测试前先生成 **3–5 个排序假设**。单假设会锚定在第一个看似合理的想法上。

每个 hypothesis 必须**可证伪**：写出它预测什么。

> Format: "If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse."

如果说不出预测，这只是感觉。丢弃或收紧它。

**测试前把排序列表展示给用户。** 用户常有能立刻重排的领域知识（"we just deployed a change to #3"），或知道哪些假设已排除。这个 checkpoint 成本低、节省时间。不要阻塞等待；用户 AFK 时按你的排序继续。

## Phase 4 — Instrument

每个 probe 必须对应 Phase 3 的具体预测。**一次只改变一个变量。**

工具优先级：

1. 环境支持时使用 **Debugger / REPL inspection**。一个 breakpoint 胜过十条 logs。
2. 在区分 hypotheses 的边界打 **Targeted logs**。
3. 永远不要 "log everything and search later"。

**每条 debug log** 都用唯一前缀标记，例如 `[DEBUG-a4f2]`。最终 cleanup 只需一次 `rg` 搜索。未标记 logs 容易残留；已标记 logs 必须删除。

**Perf branch.** 对性能回归，logs 通常不是正确工具。应先建立 baseline measurement（timing harness、`performance.now()`、profiler、query plan），再 bisect。先测量，再修复。

## Phase 5 — Fix + regression test

在 fix 前写 regression test，但前提是存在**正确 seam**。

正确 seam 是 test 能按 call site 中出现的方式覆盖**真实 bug pattern**。如果唯一 seam 太浅（bug 需要多个 callers，却只测单 caller；unit test 无法复现触发 bug 的调用链），那里写 regression test 会产生虚假信心。

**如果没有正确 seam，这本身就是发现。** 记录它。说明代码库架构阻碍了 bug 被锁定。把它标记给下一阶段。

如果存在正确 seam：

1. 将最小化 repro 转成该 seam 上的 failing test。
2. 看它失败。
3. 应用 fix。
4. 看它通过。
5. 用原始（未最小化）场景重跑 Phase 1 feedback loop。

## Phase 6 — Cleanup + post-mortem

宣布完成前必须：

- [ ] 原始 repro 不再复现（重跑 Phase 1 loop）
- [ ] Regression test 通过（或已记录没有 seam）
- [ ] 所有 `[DEBUG-...]` instrumentation 已删除（`rg` prefix）
- [ ] Throwaway prototypes 已删除（或移到清楚标记的 debug location）
- [ ] 在 commit / PR message 中说明最终正确的 hypothesis，方便下一个 debugger 学习

**然后问：什么能预防这个 bug？** 如果答案涉及架构变化（没有好的 test seam、callers 缠绕、hidden coupling），带着具体信息交给 `$improve-codebase-architecture` skill。建议必须在 fix 完成后提出，而不是之前，因为此时信息更多。
