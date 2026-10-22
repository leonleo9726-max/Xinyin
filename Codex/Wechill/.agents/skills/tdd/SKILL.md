---
name: tdd
description: Test-driven development with red-green-refactor loop. 使用 red-green-refactor 循环进行测试驱动开发。Use when building features or fixing bugs with TDD, when the user mentions "red-green-refactor", wants integration tests, or asks for test-first development.
---

# 测试驱动开发

## 理念

**核心原则**：Tests 应通过 public interfaces 验证 behavior，而不是 implementation details。代码可以完全变化，tests 不应跟着坏。

**Good tests** 是 integration-style：通过 public APIs 运行真实 code paths。它们描述系统做_什么_，而不是_如何_做。好 test 像 specification："user can checkout with valid cart" 直接说明存在什么能力。这类 tests 能经受 refactors，因为它们不关心内部结构。

**Bad tests** 与 implementation 耦合。它们 mock internal collaborators、测试 private methods，或通过外部手段验证（比如绕过 interface 直接查数据库）。警告信号：refactor 后 behavior 没变，但 test 坏了。如果只是重命名内部函数 tests 就失败，那些 tests 测的是 implementation，不是 behavior。

示例见 [tests.md](tests.md)，mocking 指南见 [mocking.md](mocking.md)。

## 反模式：Horizontal Slices

**不要先写完所有 tests，再写所有 implementation。** 这是 "horizontal slicing"：把 RED 当成 "write all tests"，把 GREEN 当成 "write all code"。

这会产生**糟糕 tests**：

- 批量写出的 tests 测的是_想象中_的 behavior，不是_实际_ behavior
- 最终会测试事物的_shape_（data structures、function signatures），而不是 user-facing behavior
- Tests 对真实变化不敏感：behavior 坏了它们可能通过，behavior 没坏它们可能失败
- 你会超前太多，在理解 implementation 前就承诺 test structure

**正确方式**：通过 tracer bullets 做 vertical slices。一个 test → 一个 implementation → 重复。每个 test 都响应上一轮学到的信息。因为刚写过代码，你更清楚什么 behavior 重要、如何验证。

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
  ...
```

## 工作流

### 1. 规划

探索代码库时，使用项目 domain glossary，使 test names 和 interface vocabulary 与项目语言一致，并尊重相关区域的 ADRs。

写任何代码前：

- [ ] 从请求与现有接口确定 interface changes；仅在 public interface 存在多种合理选择时向用户确认
- [ ] 从风险与用户请求确定要测试的 behaviors（优先级）；仅在优先级会实质改变实现范围时向用户确认
- [ ] 识别 [deep modules](deep-modules.md) 机会（small interface, deep implementation）
- [ ] 为 [testability](interface-design.md) 设计 interfaces
- [ ] 列出要测试的 behaviors（不是 implementation steps）
- [ ] 记录接口与测试范围的假设；高风险或范围不明确时获得用户认可

询问："What should the public interface look like? Which behaviors are most important to test?"

**不可能测试一切。** 与用户确认哪些 behaviors 最重要。把测试精力放在 critical paths 和 complex logic，而不是每个可能 edge case。

### 2. Tracer Bullet

写一个 test，只确认系统的一件事：

```
RED:   Write test for first behavior → test fails
GREEN: Write minimal code to pass → test passes
```

这是 tracer bullet，用来证明路径端到端可行。

### 3. 增量循环

对每个剩余 behavior：

```
RED:   Write next test → fails
GREEN: Minimal code to pass → passes
```

规则：

- 一次只写一个 test
- 只写足够通过当前 test 的代码
- 不预判未来 tests
- 保持 tests 聚焦 observable behavior

### 4. Refactor

所有 tests 通过后，寻找 [refactor candidates](refactoring.md)：

- [ ] 提取 duplication
- [ ] Deepen modules（把 complexity 移到 simple interfaces 后面）
- [ ] 在自然处应用 SOLID principles
- [ ] 思考新代码暴露了哪些现有代码问题
- [ ] 每个 refactor step 后运行 tests

**RED 时永不 refactor。** 先到 GREEN。

## 每轮 Checklist

```
[ ] Test describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```
