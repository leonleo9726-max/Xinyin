# 核心业务规则与 env/test 实现差异核对（2026-10-14）

对照基线：[核心业务规则-master实现对照版.md](../核心业务规则-master实现对照版.md)。此次只核对源码及分支差异，未查询运行时政策、人员或薪资数据。

**结论：存在差异。** Payroll 档位、比例、结算公式所依赖的 `SalaryV2Extension.kt` 与 `salary/v2` 实现没有分支差异。master 已通过 BDM 员工自挂将本人 BD 有效流水纳入团队；test 新组织模型进一步纳入全部有效后代。其余差异涉及资格、快照有效性、月结并发保护及提现边界。原文与 master 的其他待决策差异不能因此视为已经解决。

## 业务差异

| Rule Name | 合并文档（master 基线） | env/test 实现 | 影响与证据 |
|---|---|---|---|
| 团队有效流水成员 | BDM 本人自挂，汇总本人及直属在职 BD 的个人有效流水 | 旧模型保持本人加直属成员；新模型汇总管理者本人和全部有效后代的**个人 BD 有效流水**，再用其团队政策比档，不叠加下级管理者的团队薪资 | **本人参与没有分支差异**；只有存在间接有效后代时，团队底薪、Bonus 和展示等级才可能变化。见 [员工自挂](admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdStaffServiceImpl.kt)、[团队成员解析](admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdTeamMemberResolverImpl.kt) 与 [月结聚合](admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdStaffMonthlySalarySettlementServiceImpl.kt) |
| 薪资资格及政策类型 | 以 `role_bd`、`role_bdm` 和在职状态说明双轨薪资 | 新模型要求 `management_status=ACTIVE`、有效管理等级和个人政策；A-D 另需对应的 TEAM_A-D 团队政策，E 只领个人薪资。旧模型仍按原角色和政策资格判定 | 新模型的员工准入、团队角色及政策不能只按两个 role 字段复算；见 [资格服务](admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdStaffEligibilityServiceImpl.kt)、[等级映射](admin-content/content-client/src/main/kotlin/com/dy/admin/content/type/bd/BdManagementLevel.kt) |
| 当前月薪资快照 | 当前月读取 `bd_realtime_staff_salary` 的角色行 | 后台 SQL 对新模型额外核对员工组织版本、组织全局 revision、政策 ID 和 revision；旧模型有兼容分支。服务读取快照也校验版本，不匹配时不直接沿用旧值 | 组织或政策变更后，旧实时行可从列表消失，服务可能改走实时计算；见 [后台 SQL](admin-content/content-service/src/main/resources/mapper/BdRealtimeStaffSalaryDao.xml)、[快照校验](admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdRealtimeSalarySnapshotServiceImpl.kt) |
| BD/BDM 月结冲突 | BD 月结后汇总已落库的成员流水；缺失 BD 行通常按 0 处理并留问题单 | 月结前后复核组织与政策版本；明确的版本冲突最多重读重算 3 次；成员个人月结仍有版本冲突时暂缓团队月结，普通缺失仍按 0 并记问题单 | 变更期间的发薪时点及问题单处理不同；见 [月结服务](admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdStaffMonthlySalarySettlementServiceImpl.kt) |
| 已入账工资提现 | 独立 `bd_staff_balance` 余额，文档未定义解散后的提现资格 | 新模型档案仍正常但团队状态为 `CLEARED` 时，可提取既有余额；不因此恢复新增薪资资格 | 解散不自动没收已入账工资；见 [资格服务](admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdStaffEligibilityServiceImpl.kt)、[提现余额服务](admin-content/content-service/src/main/kotlin/com/dy/admin/content/service/service/bd/impl/BdSalaryWithdrawBalanceServiceImpl.kt) |
| BD 现金提现日期边界 | 每月 3-7 日，未写时区 | 仍为每月 3-7 日，但按提现用户区域时区判定；master 固定使用中东时区 | 跨地区用户在月初/月末边界时可能得到不同判定；见 [提现服务](app-payer/payer-service/src/main/kotlin/com/dy/app/payer/service/service/withdraw/impl/SalaryWithdrawServiceImpl.kt) |

## 同步记录

22 个仓库已同步到 `origin/env/test`，`HEAD` 与跟踪分支一致且工作区干净。另 4 个仓库远端未发现名称含 test 的分支，因此保留 `master`，未以其他分支替代。表中“同步前”为本次操作前的 master 提交，“同步后”为当前工作区提交。

| 仓库 | 当前分支 | 同步前完整提交 | 同步后完整提交 |
|---|---|---|---|
| `admin-content` | `env/test` | `cdcb3cbf719a518c1ed3ca729a015004bb2b3391` | `87ac470a3467c9f63142cbaef371e3f7610a4536` |
| `alarm-collect` | `env/test` | `cb506a655440632c3dd3be9053c5867e5d8d50f5` | `ebf3bd3ce1cac4e8b848c1a391931d6419dd3405` |
| `app-act` | `env/test` | `b0ca1098fcd2b9eb5705b1ddfea010b9f8adf857` | `3239df5c2620f0ce653e02bb6a7bfd83f04bc61a` |
| `app-bases` | `env/test` | `8f71109a5dc39b00d06977f9ce912ebcbaeabf93` | `39e8cc220e0956072bb2a684f410407394d5e3a4` |
| `app-chat` | `env/test` | `5986ac4d5f714b766a28f486dbc32071da75e4cc` | `428738d46a86ecea5bbb6233be6f6f85110b0774` |
| `app-commons` | `env/test` | `087c4b4b746ef3739cae602c3e4c63bb7979e537` | `9e6b143dd6bde4c561cda86e8db0fe62115246a2` |
| `app-game` | `env/test` | `abfa33a041cfd1fc13d47e0219608f92ef9c13df` | `7a7ddbb09db89f2520165dfe66d04d4a77ed9992` |
| `app-gateway` | `env/test` | `166e24653045140408fa62052cca788506b12218` | `dad5df906d292c64cd383ed9f2c5fecd1d2620ee` |
| `app-h5` | `env/test` | `4cb2a917d5c5eea89b6858282a10da48cd81792e` | `f386fb295ffb2b1278ac4888aa6c3d457baa4cb7` |
| `app-home` | `env/test` | `990eb409240138136d6458c6f7d3a9c62cf46e0f` | `806ae85ec1fd2ca5a3ce6c235c62cb55ffb70625` |
| `app-live` | `env/test` | `5261fdc31b8245b8874134218028fcb8779e8aba` | `8727a712ba1957adbc5f5af10f00711e65e4eab8` |
| `app-parent` | `env/test` | `bd8eaaafe06ae75e20eacb5dc4da95c618110974` | `47015906c0679864dd4cdef8ef65ef7290441115` |
| `app-payer` | `env/test` | `6ff233d23b3e8626ab9a0809c19f341eece78df6` | `102111c2f3556bda17af1e11702bdfe9839513f9` |
| `app-pusher` | `env/test` | `c24197440ac1f9668ad1d8b74206296e739beea4` | `9e869ddff7a2af61e59d09459953e1992f5329bf` |
| `app-state` | `env/test` | `3385eac3df3f6fd9cc3277441f71adc72ed751ec` | `2033bc408b61c3df91230856584e05b04e8c0f3c` |
| `app-user` | `env/test` | `7120c543dd1f734dd824ff0dc9dc53b835b9bf47` | `f84a5eb514e23eb145e7b46105ffd4c607b2fb9b` |
| `config-domain` | `env/test` | `c6990345cffcdbb4a6f7225cdc7a0e6549881acc` | `560e96bad4bb622435fe4b7c97b5bc6e2e6b8fee` |
| `im-bases` | `env/test` | `94b755ad8b51bf2667b64be515f6986d54f45d20` | `3fc097c32110f6aa935678c877ca3b72578f39d8` |
| `im-chat` | `env/test` | `59be513b497684924cd5a98b7d3433aafd78a3a4` | `247a5722b1ccd37b8e95f57dd87264cd6967e729` |
| `im-live` | `env/test` | `0a2a1bf397ffdb49d155e9d36891cc4e9cb73276` | `bc145817437d884ecb53b9f4208c321a30cdd58d` |
| `im-parent` | `env/test` | `ef352ba202042c6b01793b3abea9e11e23a1809e` | `79313af7bec6d17b8d08de69d625a50118a7f057` |
| `im-pusher` | `env/test` | `b1a38d406cdbe2d8bab6cf89bfe957a6b2d3336c` | `31ab0929422026d99cfc622f27e3db2f77f51cd0` |
| `delegateaccess` | `master` | `e6c87e76aba8b4c4528a8e3f70b4065b1ed867f4` | `e6c87e76aba8b4c4528a8e3f70b4065b1ed867f4` |
| `h5-app-act` | `master` | `78eaa37d960c62d61eb3da75c2238ae6f46a6038` | `78eaa37d960c62d61eb3da75c2238ae6f46a6038` |
| `kts-container` | `master` | `eef4c832397f7797dc63ad0b135470073ef50bb9` | `eef4c832397f7797dc63ad0b135470073ef50bb9` |
| `xxl-job` | `master` | `021a4992e2d8e051964bd46cb86a6a3163212df4` | `021a4992e2d8e051964bd46cb86a6a3163212df4` |

## 文档审查

[AGENTS.md](AGENTS.md) 和 [ARCHITECTURE.md](ARCHITECTURE.md) 已补充 test 的 BD 组织模型与跨仓职责。其余仓库分支差异未改变现有 reactor 成员、仓库归属或验证入口；两份文档的其余结构说明保持有效。

**核验范围：** 静态源码与分支差异；未运行构建、数据库验算或薪资结算。
