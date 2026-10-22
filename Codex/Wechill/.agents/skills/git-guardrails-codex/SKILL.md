---
name: git-guardrails-codex
description: Set up Codex hooks to block dangerous git commands such as push, reset --hard, clean, branch -D, checkout ., and restore . before they execute. 设置 Codex hooks，在执行前阻断危险 git 命令。Use when preventing destructive git operations or adding Codex git safety hooks.
---

# 设置 Git 防护栏

设置 Codex `PreToolUse` hook，在 Codex 执行危险 git 命令前阻断。

## 阻断内容

- `git push` including force variants
- `git reset --hard`
- `git clean -f`, `git clean -fd`, and similar force clean variants
- `git branch -D`
- `git checkout .`
- `git restore .`

## 步骤

### 1. 确认范围

询问用户安装范围：

- **仅当前项目**：`.codex/hooks.json` 和 `.codex/hooks/block-dangerous-git.ps1`
- **所有项目**：如果当前 Codex 安装文档说明了全局 hooks 路径，则使用 Codex home config

默认使用项目范围。

### 2. 复制 Hook 脚本

内置脚本位于 [scripts/block-dangerous-git.ps1](scripts/block-dangerous-git.ps1)。

项目范围安装时，将它复制到 `.codex/hooks/block-dangerous-git.ps1`。目录缺失时先创建。

### 3. 添加 Hook 配置

解析项目根目录，并将下方 `<hook-script-absolute-path>` 替换为刚复制脚本的绝对路径。将内容合并到 `.codex/hooks.json`；不要覆盖已有 hooks：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "functions.shell_command",
        "hooks": [
          {
            "type": "command",
            "command": "pwsh -NoProfile -ExecutionPolicy Bypass -File \"<hook-script-absolute-path>\""
          }
        ]
      }
    ]
  }
}
```

项目级配置不得引用 `E:\\Codex\\.codex\\...` 等全局固定路径。若本地 Codex 环境使用不同的 shell tool matcher，保留解析后的 hook command，只把 `matcher` 替换为实际观察到的 shell tool 名称。

### 4. 确认可定制项

询问用户是否要新增或移除阻断 pattern，并相应编辑复制后的脚本。

### 5. 验证

运行以下 PowerShell smoke test：

```powershell
'{"tool_input":{"command":"git push origin main"}}' | pwsh -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/block-dangerous-git.ps1
```

预期退出码为 2，并向 stderr 打印 `BLOCKED` 消息。
