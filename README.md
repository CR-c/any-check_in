# Anyrouter 自动签到

自动签到 anyrouter.top 的 GitHub Actions 工具，支持邮箱账号密码登录。

## 功能特性

- 自动每日签到（每8小时执行一次）
- 邮箱密码登录（非 OAuth）
- GitHub Actions 自动执行
- 支持手动触发
- 显示账户余额信息

## 快速开始

### 1. Fork 此仓库

点击右上角的 Fork 按钮，将此仓库 fork 到你的账号下。

### 2. 配置 GitHub Secrets

在你 fork 的仓库中，进入 **Settings** → **Secrets and variables** → **Actions**，添加以下 secrets：

| Secret 名称 | 说明 | 必填 |
|------------|------|------|
| `ANYROUTE_EMAIL` | anyrouter.top 登录邮箱 | 是 |
| `ANYROUTE_PASSWORD` | anyrouter.top 登录密码 | 是 |
| `ANYROUTE_BASE_URL` | 网站地址（默认 https://anyrouter.top） | 否 |

**添加步骤：**
1. 点击 **New repository secret**
2. 在 **Name** 中输入 `ANYROUTE_EMAIL`
3. 在 **Secret** 中输入你的邮箱
4. 点击 **Add secret**
5. 重复以上步骤添加 `ANYROUTE_PASSWORD`

### 3. 启用 GitHub Actions

1. 进入你的仓库
2. 点击 **Actions** 标签
3. 点击 **I understand my workflows, go ahead and enable them**

### 4. 测试运行

你可以手动触发一次签到来测试配置是否正确：

1. 进入 **Actions** 标签
2. 点击左侧的 **Anyroute Daily Check-in**
3. 点击右侧的 **Run workflow**
4. 点击绿色的 **Run workflow** 按钮
5. 等待执行完成，查看日志

## 自动执行时间

脚本每 **8 小时** 自动执行一次：
- 北京时间 8:00（UTC 0:00）
- 北京时间 16:00（UTC 8:00）
- 北京时间 0:00（UTC 16:00）

如需修改执行时间，编辑 `.github/workflows/checkin.yml` 文件中的 cron 表达式。

## 本地测试

如果想在本地测试脚本：

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量（Linux/Mac）
export ANYROUTE_EMAIL="your-email@example.com"
export ANYROUTE_PASSWORD="your-password"

# 设置环境变量（Windows PowerShell）
$env:ANYROUTE_EMAIL="your-email@example.com"
$env:ANYROUTE_PASSWORD="your-password"

# 运行脚本
python checkin.py
```

或者复制 `.env.example` 为 `.env` 并填写配置后使用 python-dotenv 加载。

## 注意事项

1. **保护你的密码**：请务必使用 GitHub Secrets 存储敏感信息，不要直接写在代码中
2. **API 调整**：如果网站的登录或签到接口发生变化，可能需要修改 `checkin.py` 中的相关代码
3. **执行频率**：GitHub Actions 的 cron 可能会有几分钟的延迟，这是正常现象
4. **保持活跃**：如果仓库长期没有活动，GitHub 可能会禁用 Actions，建议定期检查

## 故障排查

### Actions 没有自动执行

- 检查 Actions 是否已启用
- 查看仓库是否有近期活动
- Fork 的仓库可能需要有至少一次提交才能触发 Actions

### 签到失败

1. 检查 Secrets 是否正确配置
2. 查看 Actions 日志了解具体错误
3. 尝试手动登录 anyrouter.top 确认账号密码正确
4. 网站可能更新了接口，需要调整脚本

## API 说明

本脚本使用以下 API 端点：

- 登录：`POST /api/user/login`
- 签到：`POST /api/user/sign_in/{user_id}`
- 用户信息：`GET /api/user/self`

## License

MIT License
