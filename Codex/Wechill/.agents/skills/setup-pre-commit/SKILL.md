---
name: setup-pre-commit
description: Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. 为当前 repo 设置 Husky、lint-staged、Prettier、typecheck 和 test 的 pre-commit hooks。Use when adding pre-commit hooks or commit-time formatting/typechecking/testing.
---

# 设置 Pre-Commit Hooks

## 设置内容

- **Husky** pre-commit hook
- **lint-staged** 对所有 staged files 运行 Prettier
- **Prettier** config（如缺失）
- pre-commit hook 中的 **typecheck** 和 **test** scripts

## 步骤

### 1. 检测 package manager

检查 `package-lock.json` (npm)、`pnpm-lock.yaml` (pnpm)、`yarn.lock` (yarn)、`bun.lockb` (bun)。使用已存在的工具；不明确时默认 npm。

### 2. 安装依赖

作为 devDependencies 安装：

```
husky lint-staged prettier
```

安装包可能需要网络访问。在受限环境中运行前先请求批准。

### 3. 初始化 Husky

```bash
npx husky init
```

这会创建 `.husky/` 目录，并向 package.json 添加 `prepare: "husky"`。

### 4. 创建 `.husky/pre-commit`

写入以下内容（Husky v9+ 不需要 shebang）：

```
npx lint-staged
npm run typecheck
npm run test
```

**适配**：用检测到的 package manager 替换 `npm`。如果 package.json 没有 `typecheck` 或 `test` script，省略对应行并告知用户。

### 5. 创建 `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. 创建 `.prettierrc`（如缺失）

仅当不存在 Prettier config 时创建。使用以下默认值：

```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```

### 7. 验证

- [ ] `.husky/pre-commit` 存在且可执行
- [ ] `.lintstagedrc` 存在
- [ ] package.json 中 `prepare` script 为 `"husky"`
- [ ] `prettier` config 存在
- [ ] 运行 `npx lint-staged` 验证可用

### 8. Commit

只有用户明确要求 commit 时才 stage 和 commit。如需提交，使用 message：`Add pre-commit hooks (husky + lint-staged + prettier)`

这会跑一遍新的 pre-commit hooks，是确认配置有效的 smoke test。

## 备注

- Husky v9+ hook 文件不需要 shebang
- `prettier --ignore-unknown` 会跳过 Prettier 无法解析的文件（图片等）
- pre-commit 先运行 lint-staged（快，只处理 staged files），再运行完整 typecheck 和 tests
