---
name: query-bd
description: Query BD/BDM staff, guild, salary, or commission data from the test MySQL database. 默认按 user_number 解析身份；用户明确要求生产库时才使用 mysql_prod。
---

# BD/BDM 数据查询
默认使用测试库 MCP `mysql`（`stay` 库）。只有用户明确要求生产库时使用 `mysql_prod`。数字身份输入默认是 `user_number`；解析身份后，可使用已验证的 `user_id` 作为业务表关联键。

## 步骤
0. 将任务限定为 `BDM/` 规则范围。涉及薪资或佣金时，读取 `BDM/AGENTS.md` 和 `BDM/rules/BDM业务规则.md`；无需为当前工作目录另行询问。
1. **枚举门禁**：先 read `BDM/rules/数据库表结构.md` 确认涉及字段的枚举映射（`SHOW COLUMNS` 只能看到 `tinyint`，看不到语义）。跳过此步会误判枚举值。
2. 每张表首次查询前，先执行 `SHOW COLUMNS FROM <table>`。
3. 从 `app_user.user_number` 解析用户身份。只有用户明确说输入是 `user_id` 时，才跳过该解析；后续业务表按已验证的关联键查询。
4. 得出用户不存在结论前，同时检查基础表和审核/扩展用户表（`app_user`、`app_user_flag`，以及 BDM 文档指定的其他表）。
5. 用正确枚举过滤查询相关表（见下方）。
6. 从权威表查询相关薪资/佣金记录。
7. 结论前预览查询结构：输出列名和前 3 行。
8. 如出现空值、格式非法、枚举不匹配或数据偏移，在结论前增加 **异常声明**。
9. 以结构化表格展示所有相关字段。
10. 发现新映射时更新 `数据库表结构.md`。

## 查询表
- `bd_staff` — BD/BDM 员工主表（employment_status, job_title_type, role_bd/bdm）
- `app_user` — 用户基础信息（通过 user_id 关联 phone_number 等）
- `app_user_agency` — 公会/agency 数据（需要公会上下文时）
- 按上下文查询所需薪资/佣金表

## 关键规则
- 身份入口：**始终**按 `user_number` 查询，除非用户明确输入 `user_id`；业务关联使用已验证的 `user_id`，不把未说明的数字当作 `id`
- **枚举字段禁止猜测**：`employment_status` (0=试用期, 1=已转正, 2=离职)、`job_title_type` (0=BD, 1=BDM, 2=双角色) 等枚举值必须从文档获取，`SHOW COLUMNS` 只显示 `tinyint` 无法区分语义
- 用 `app_user_flag` 交叉核验审核状态
