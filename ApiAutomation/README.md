# EastPoint API 自动化测试

基于 Python、pytest 和 requests 的接口自动化项目，覆盖手机号登录/注册、红包、直播礼物及批量业务操作。测试分为离线单元测试和真实接口测试；真实接口调用必须显式传入 `--run-api`。

## 项目结构

```text
ApiAutomation/
├── common/
│   ├── api_client.py       # 业务接口统一请求入口
│   ├── api_paths.py        # API 路径常量
│   ├── auth_utils.py       # 登录、凭证读写和认证信息
│   ├── business_utils.py   # 批处理共用逻辑
│   ├── http_utils.py       # requests 连接池、传输和重试
│   ├── live_gift.py        # 直播批量送礼载荷与明文请求
│   ├── live_heartbeat.py   # 直播心跳与保活循环
│   ├── response_utils.py   # 成功判断和响应字段提取
│   └── sign_utils.py       # 空值过滤、签名和 AES-CBC 加密
├── config/settings.py      # 环境配置和请求头构造
├── tests/                  # pytest 接口测试与离线单元测试
├── data/                   # CSV 测试数据及本地凭证缓存
├── batch_*.py              # 批量登录、注册、红包和送礼脚本
├── conftest.py             # pytest 选项和 fixtures
└── pytest.ini              # pytest 默认参数及 marker
```

## 请求架构

业务测试和批量脚本通过 `common.api_client.EastPointClient` 调用接口。它组合基础 URL、通用请求头、用户 token/user id，并将请求交给 `HttpUtils`。默认业务传输由 `SignUtils` 过滤空值、转换 `stay*` 签名字段、生成 SHA-256 签名，并使用 AES-CBC 加密载荷。

`HttpUtils` 使用线程本地的 `requests.Session` 和共享连接适配器。它对业务响应码 `980003000` 做最多两次、间隔 0.5 至 1.5 秒的抖动重试；此外连接适配器也配置了 HTTP 状态码重试。响应统一使用 `common.response_utils.is_api_success()` 判定，响应中同时出现的成功指标必须一致。

直播批量送礼和直播心跳经 `common.live_gift.post_live_gift()`、`common.live_heartbeat.post_live_heartbeat()` 发送明文 JSON；这两个路径是受控例外。其他业务接口应保持加密与签名。

## 环境配置

使用项目根目录 `.env` 或进程环境变量提供配置。`.env` 已加入 Git 忽略；不要提交密钥或本地凭证。至少配置测试加密密钥：

```dotenv
EASTPOINT_BASE_URL=https://api.eastpointtest.com
EASTPOINT_TEST_ENCRYPT_KEY=<测试环境密钥>
```

`EASTPOINT_BASE_URL` 和 `EASTPOINT_TEST_ENCRYPT_KEY` 分别控制 API 地址和加密密钥。未设置密钥时，加密请求会失败，不会自动退化为明文。直播服务默认地址为 `EASTPOINT_LIVE_BASE_URL` 对应的内部地址；仅在环境提供替代地址时覆盖它。

安装依赖并进入本目录：

```powershell
E:\python\work\.venv\Scripts\python.exe -m pip install -r requirements.txt
Set-Location E:\python\work\ApiAutomation
```

## 运行测试

离线单元测试不调用真实接口：

```powershell
E:\python\work\.venv\Scripts\python.exe -m pytest -m unit -p no:cacheprovider -o addopts=''
```

运行真实接口测试前，确认测试环境地址、密钥、账号和测试数据均已准备好：

```powershell
E:\python\work\.venv\Scripts\python.exe -m pytest -m api --run-api
```

单文件调试示例：

```powershell
E:\python\work\.venv\Scripts\python.exe -m pytest tests/test_login_phone.py --run-api -s
```

`conftest.py` 提供 `--run-api`、`--login-mode`、`--phone`、`--code`、`--area` 和 `--password` 选项，以及 `base_url`、`default_headers`、`encrypt_key` fixtures。`pytest.ini` 默认开启详细输出和 HTML 报告；离线单测命令通过 pytest 选项覆盖默认报告参数。

## 凭证和测试数据

- `data/login_phone.csv`、`data/register_phone.csv` 保存登录和注册测试手机号；`data/device_ids.csv` 保存设备标识。
- `data/login_credentials.json`、`data/batch_login_credentials.json` 保存本机登录凭证，已由 `.gitignore` 忽略，不应加入版本控制。
- 批量业务脚本通常读取上述凭证文件。可先按 `README_BATCH_LOGIN.md` 的流程生成凭证，再执行目标批处理脚本。
- `reports/` 中的 pytest HTML 报告也已忽略。

## 维护约定与当前限制

- 新增业务路径优先放入 `common/api_paths.py`，共用传输和响应逻辑放入对应 `common/` 模块；测试和脚本应聚焦业务载荷及流程。
- 只有批量送礼、直播心跳允许按项目约定使用明文 JSON。当前 `EastPointClient.post(..., plain_json=True)` 是通用开关，传输层没有强制校验路径白名单；新增调用时必须限制在上述两个受控封装内。可进一步将例外校验下沉到客户端，避免误用。
- `ConnectionPool` 的 HTTP 适配器对 POST 也启用部分状态码重试。对会创建或扣减业务资源的接口，重试可能造成重复操作；调整重试策略时应按接口幂等性评估，并避免与业务响应重试叠加。
- 自动化测试不得默认触发真实接口；批量脚本也应使用隔离的测试账号和测试环境运行。
