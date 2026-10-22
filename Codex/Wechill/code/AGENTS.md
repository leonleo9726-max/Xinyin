# Wechill 代码工作区规则

继承 `E:\Codex\Wechill\AGENTS.md`。本文件适用于 `code/` 下的 26 个独立 Git 仓库；仓库内若有更具体的 `AGENTS.md`，以仓库规则为准。仓库职责和依赖关系见 `ARCHITECTURE.md`。

## 工作区边界

- 只在用户指定的仓库内修改业务代码；跨仓接口变更先核对调用方、服务端和共享契约。
- `app-parent` 的 Maven 模块指向同级的 `app-commons`、`app-bases`、`admin-content`、`app-user`、`app-chat`、`app-live`、`app-home`、`app-payer`、`app-game`、`app-act`、`app-state` 和 `app-pusher`。在 `app-parent` 所在目录执行聚合构建时保留这些同级目录。
- `im-parent` 独立聚合 `im-bases`、`im-chat`、`im-live`、`im-pusher`。两组父 POM 使用不同的 Spring Boot 基线，分别验证。
- `app-commons` 放通用基础设施能力，`app-bases` 放业务基础能力。常见业务仓库以 `*-data`、`*-client`、`*-service` 划分持久化对象、跨模块契约和业务实现；`app-user` README 要求核心用户服务不依赖边缘服务接口。
- BD 组织、政策、薪资资格与团队结算由 `admin-content` 负责；`app-user` 的 BD/BDM 接口通过 `content-client` 契约访问。`env/test` 的新组织模型与旧模型并存，团队成员范围按组织模型版本解析。
- `h5-app-act` 和 `app-h5` 是独立 Umi H5 项目。路由由各自 `config/routes.ts` 管理，请求和环境配置分别在各仓库内核对。
- `config-domain`、`alarm-collect` 使用 Kotlin/Quarkus 和 Gradle；`app-gateway`、`kts-container`、`delegateaccess`、`xxl-job` 分别按自身 Maven 工程验证。不要将这些项目误纳入两组父 POM。

## Git 与同步

1. 拉取前确认目录、`origin`、当前分支、跟踪分支及未提交改动；新目录先确认不存在，再克隆到 `code/<仓库名>`。
2. 已有仓库只在可确认目标分支和本地改动安全的情况下更新；保留用户的本地修改。记录拉取前后完整提交。
3. 同步后逐仓核对 `HEAD`、远端跟踪提交和工作区状态。失败仓库单独报告，不把部分成功当作全部成功。

## 同步后文档审查

每次成功拉取或更新 `code/` 下任一仓库后，在结束任务前完成：

1. 记录每个仓库的前后提交；检查完整新增提交范围的代码、配置、迁移、测试和仓库文档。新克隆仓库以完整工作树为审查基线。
2. 检查本文件是否遗漏稳定的模块归属、入口、接口约束或验证要求；必要时更新。
3. 检查 `ARCHITECTURE.md` 的仓库职责、依赖方向、数据归属、外部集成和执行入口；必要时更新。暂时性的提交内容不要写进长期文档。
4. 结果中逐仓说明同步状态，并分别说明两份文档“更新”或“保持有效”的依据。

## 验证入口

- `app-parent` 和 `im-parent` 的成员变更：先运行相关模块的聚焦测试，再在对应父 reactor 验证模块依赖；涉及 SQL 时检查迁移与数据访问契约。
- `h5-app-act`、`app-h5`：运行适用的 `package.json` 测试及目标环境构建脚本；核对路由、请求协议、App bridge 和环境配置。`app-h5` 的 `APP_TYPE` 变体有单独脚本。
- `config-domain`、`alarm-collect`：使用仓库自带 Gradle wrapper 和聚焦 Kotlin 测试。
- 其余独立 Maven 项目按各自 POM 和受影响模块运行聚焦测试；`xxl-job` 区分 `core` 与 `admin`。
