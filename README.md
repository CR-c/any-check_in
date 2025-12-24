# Anyrouter 自动签到

自动签到 anyrouter.top 的工具，支持邮箱账号密码登录，使用 Camoufox 实现自动化。

## 功能特性

- ✅ 自动每日签到（每4小时执行一次）
- ✅ 邮箱密码登录（非 OAuth）
- ✅ 支持多账号签到
- ✅ 邮件通知签到结果
- ✅ GitHub Actions 自动执行
- ✅ 支持手动触发
- ✅ 登录失败自动重试（最多3次）
- ✅ 显示账户余额信息
- ✅ 支持本地调试模式

## 快速开始

### 方式一：使用 GitHub Actions（推荐）

#### 1. Fork 此仓库

点击右上角的 **Fork** 按钮，将此仓库 fork 到你的账号下。

#### 2. 配置 GitHub Secrets

在你 fork 的仓库中，进入 **Settings** → **Secrets and variables** → **Actions**，添加 secrets。

##### 选项一：多账号模式（推荐）

| Secret 名称 | 说明 | 必填 | 示例 |
|------------|------|------|------|
| `ACCOUNTS` | 多个账号的 JSON 数组配置 | ✅ 是 | 见下方示例 |
| `ANYROUTE_BASE_URL` | 网站地址 | ❌ 否 | `https://anyrouter.top` (默认值) |

**ACCOUNTS 格式示例：**
```json
[
  {
    "name": "主账号",
    "email": "user1@example.com",
    "password": "password1"
  },
  {
    "name": "备用账号",
    "email": "user2",
    "password": "password2"
  }
]
```

**说明：**
- `name`：账号名称（可选），用于日志显示，不填则默认使用 email
- `email`：anyrouter.top 登录邮箱或用户名
- `password`：anyrouter.top 登录密码

##### 选项二：单账号模式（兼容模式）

| Secret 名称 | 说明 | 必填 | 示例 |
|------------|------|------|------|
| `ANYROUTE_EMAIL` | anyrouter.top 登录邮箱或用户名 | ✅ 是 | `your-email@example.com` 或 `username` |
| `ANYROUTE_PASSWORD` | anyrouter.top 登录密码 | ✅ 是 | `your-password` |
| `ANYROUTE_BASE_URL` | 网站地址 | ❌ 否 | `https://anyrouter.top` (默认值) |

##### 选项三：邮件通知配置（可选）

如果需要接收签到结果的邮件通知，添加以下 secrets：

| Secret 名称 | 说明 | 必填 | 示例 |
|------------|------|------|------|
| `SMTP_SERVER` | SMTP 服务器地址 | ✅ 是 | `smtp.gmail.com` / `smtp.qq.com` |
| `SMTP_PORT` | SMTP 端口 | ✅ 是 | `587` (TLS) / `465` (SSL) |
| `SMTP_USER` | 发件人邮箱 | ✅ 是 | `your_email@gmail.com` |
| `SMTP_PASSWORD` | 邮箱授权码 | ✅ 是 | 见下方说明 |
| `EMAIL_TO` | 收件人邮箱 | ✅ 是 | `recipient@example.com` |

**常用邮箱 SMTP 配置：**

| 邮箱服务商 | SMTP 服务器 | 端口 | 说明 |
|-----------|------------|------|------|
| Gmail | smtp.gmail.com | 587 | 需要开启"两步验证"并生成"应用专用密码" |
| QQ 邮箱 | smtp.qq.com | 587 | 需要在设置中开启 SMTP 服务并获取授权码 |
| 163 邮箱 | smtp.163.com | 465 | 需要在设置中开启 SMTP 服务并获取授权码 |
| Outlook | smtp-mail.outlook.com | 587 | 直接使用账号密码 |

**如何获取邮箱授权码：**
- **Gmail**: Settings → Security → 2-Step Verification → App passwords
- **QQ 邮箱**: 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务 → 开启 SMTP 服务 → 生成授权码
- **163 邮箱**: 设置 → POP3/SMTP/IMAP → 开启 SMTP 服务 → 设置授权密码

**邮件通知内容包括：**
- ✅ 签到执行时间
- ✅ 账号签到结果（成功/失败）
- ✅ 每个账号的余额信息
- ✅ 签到统计汇总

**添加步骤（多账号模式）：**
1. 进入仓库的 **Settings** 页面
2. 在左侧菜单选择 **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 在 **Name** 中输入 `ACCOUNTS`
5. 在 **Secret** 中输入 JSON 数组（格式见上方示例）
6. 点击 **Add secret**

**添加步骤（单账号模式）：**
1. 进入仓库的 **Settings** 页面
2. 在左侧菜单选择 **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 在 **Name** 中输入 `ANYROUTE_EMAIL`
5. 在 **Secret** 中输入你的邮箱或用户名
6. 点击 **Add secret**
7. 重复以上步骤添加 `ANYROUTE_PASSWORD`

#### 3. 启用 GitHub Actions

1. 进入你 fork 的仓库
2. 点击 **Actions** 标签
3. 如果看到提示 "Workflows aren't being run on this forked repository"，点击 **I understand my workflows, go ahead and enable them**

#### 4. 测试运行

你可以手动触发一次签到来测试配置是否正确：

1. 进入 **Actions** 标签
2. 点击左侧的 **Anyroute Daily Check-in**
3. 点击右侧的 **Run workflow** 下拉按钮
4. 选择 **main** 分支
5. 点击绿色的 **Run workflow** 按钮
6. 等待执行完成（约30-60秒），查看运行日志

**查看日志：**
- 点击刚刚运行的 workflow
- 点击 **checkin** 任务
- 展开各个步骤查看详细日志
- 成功时会显示 "✓ Check-in completed successfully"

## 自动执行时间

脚本每 **4 小时** 自动执行一次：
- 🕗 **北京时间 08:00**（UTC 0:00）
- 🕛 **北京时间 12:00**（UTC 4:00）
- 🕓 **北京时间 16:00**（UTC 8:00）
- 🕗 **北京时间 20:00**（UTC 12:00）
- 🕛 **北京时间 00:00**（UTC 16:00）
- 🕓 **北京时间 04:00**（UTC 20:00）

### 自定义执行时间

如需修改执行时间，编辑 `.github/workflows/checkin.yml` 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'   # UTC 0:00 = 北京时间 8:00
  - cron: '0 4 * * *'   # UTC 4:00 = 北京时间 12:00
  - cron: '0 8 * * *'   # UTC 8:00 = 北京时间 16:00
  - cron: '0 12 * * *'  # UTC 12:00 = 北京时间 20:00
  - cron: '0 16 * * *'  # UTC 16:00 = 北京时间 0:00
  - cron: '0 20 * * *'  # UTC 20:00 = 北京时间 4:00
```

**Cron 表达式说明：**
- 格式：`分钟 小时 日 月 星期`
- 时区：UTC（比北京时间晚8小时）
- 示例：
  - `0 0 * * *` = 每天 UTC 00:00（北京时间 08:00）
  - `30 2 * * *` = 每天 UTC 02:30（北京时间 10:30）
  - `0 */6 * * *` = 每6小时执行一次

**时区转换：**
- 北京时间（UTC+8） - 8小时 = UTC 时间
- 例如：北京时间 14:00 → UTC 06:00 → cron: `0 6 * * *`

## 方式二：本地测试

如果想在本地测试脚本：

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync
uv run camoufox fetch

# 或使用 pip
pip install -r requirements.txt
```

### 2. 配置环境变量

**多账号模式（Linux/Mac）：**
```bash
export ACCOUNTS='[{"name":"账号1","email":"user1@example.com","password":"pass1"},{"name":"账号2","email":"user2","password":"pass2"}]'

# 可选：显示浏览器窗口（用于调试）
export HEADLESS="false"
```

**多账号模式（Windows PowerShell）：**
```powershell
$env:ACCOUNTS='[{"name":"账号1","email":"user1@example.com","password":"pass1"},{"name":"账号2","email":"user2","password":"pass2"}]'

# 可选：显示浏览器窗口（用于调试）
$env:HEADLESS="false"
```

**单账号模式（Linux/Mac）：**
```bash
export ANYROUTE_EMAIL="your-email@example.com"
export ANYROUTE_PASSWORD="your-password"

# 可选：显示浏览器窗口（用于调试）
export HEADLESS="false"
```

**单账号模式（Windows PowerShell）：**
```powershell
$env:ANYROUTE_EMAIL="your-email@example.com"
$env:ANYROUTE_PASSWORD="your-password"

# 可选：显示浏览器窗口（用于调试）
$env:HEADLESS="false"
```

**邮件通知配置（可选）：**
```bash
# Linux/Mac
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your_email@gmail.com"
export SMTP_PASSWORD="your_app_password"
export EMAIL_TO="recipient@example.com"

# Windows PowerShell
$env:SMTP_SERVER="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="your_email@gmail.com"
$env:SMTP_PASSWORD="your_app_password"
$env:EMAIL_TO="recipient@example.com"
```

### 3. 运行脚本

```bash
# 使用 pip 安装的环境
python checkin.py

# 使用 uv
uv run python checkin.py

# 显示浏览器窗口（调试模式）
HEADLESS=false python checkin.py
```

## 注意事项

### 安全性

1. **保护你的密码**：请务必使用 GitHub Secrets 存储敏感信息，**不要直接写在代码中**
2. **不要提交 .env 文件**：`.env` 文件已在 `.gitignore` 中，不会被提交到仓库
3. **定期更换密码**：建议定期更换密码并更新 GitHub Secrets

### 使用建议

1. **API 调整**：如果网站的登录或签到接口发生变化，可能需要修改 `checkin.py` 中的相关代码
2. **执行频率**：GitHub Actions 的 cron 可能会有几分钟的延迟，这是正常现象
3. **保持活跃**：如果仓库长期没有活动，GitHub 可能会禁用 Actions，建议定期检查
4. **Fork 更新**：原仓库更新后，需要手动同步更新到你的 fork

### 登录机制

- 程序使用 Camoufox（增强的反检测浏览器）模拟登录
- 支持邮箱或用户名登录
- 登录失败时自动重试（最多3次）
- 签到在登录时自动完成

## 故障排查

### Actions 没有自动执行

- ✅ 检查 Actions 是否已启用（Settings → Actions → General）
- ✅ 查看仓库是否有近期活动
- ✅ Fork 的仓库需要至少一次提交才能触发 Actions
- ✅ 检查 workflow 文件语法是否正确

### 签到失败

1. **检查 Secrets 配置**
   - 进入 Settings → Secrets and variables → Actions
   - 确认 `ANYROUTE_EMAIL` 和 `ANYROUTE_PASSWORD` 已正确配置
   - 密码中的特殊字符需要正确填写

2. **查看 Actions 日志**
   - 进入 Actions 标签
   - 点击失败的 workflow run
   - 查看详细的错误信息

3. **验证账号密码**
   - 尝试手动登录 anyrouter.top 确认账号密码正确
   - 检查账号是否被锁定或需要验证

4. **网站更新**
   - 网站可能更新了登录接口
   - 查看 Issues 了解是否有其他用户遇到相同问题
   - 需要时更新 `checkin.py` 脚本

### 本地测试失败

1. **Camoufox 未安装**
   ```bash
   uv run camoufox fetch
   # 或者使用 pip
   python -m camoufox fetch
   ```

2. **环境变量未设置**
   ```bash
   # 检查环境变量
   echo $ANYROUTE_EMAIL
   echo $ANYROUTE_PASSWORD
   # 或者检查多账号配置
   echo $ACCOUNTS
   ```

3. **依赖问题**
   ```bash
   # 使用 uv 重新同步
   uv sync
   # 或使用 pip 重新安装
   pip install -r requirements.txt --force-reinstall
   ```

## API 说明

本脚本使用以下操作：

- **登录**：访问 `/login` 页面，使用 Camoufox 自动填写表单并提交
- **签到**：`POST /api/user/sign_in`（登录时自动完成）
- **用户信息**：`GET /api/user/self`

## 技术栈

- Python 3.11+
- Camoufox（反检测浏览器自动化）
- GitHub Actions（CI/CD）

## 项目结构

```
.
├── .github/
│   └── workflows/
│       └── checkin.yml        # GitHub Actions 配置
├── checkin.py                 # 主程序脚本
├── requirements.txt           # Python 依赖
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略文件
└── README.md                 # 项目文档
```

## 更新日志

### v1.2.0 (2025-12-24)
- ✨ 新增邮件通知功能
- ✨ 调整执行频率为每4小时一次
- ✅ 邮件显示签到结果和余额信息
- ✅ 支持多种邮箱服务（Gmail、QQ、163 等）

### v1.1.0 (2025-12-24)
- ✨ 新增多账号签到支持
- ✨ 迁移到 Camoufox 浏览器自动化（增强反检测）
- ✨ 优化签到 API 调用
- ✅ 保持向后兼容单账号模式

### v1.0.0 (2025-12-23)
- ✨ 初始版本发布
- ✅ 支持邮箱密码登录
- ✅ 自动签到功能
- ✅ GitHub Actions 定时执行
- ✅ 登录失败自动重试

## 常见问题

**Q: 为什么第一次运行可能失败？**
A: 网站有防护机制，第一次登录可能触发验证。程序会自动重试，通常第2-3次可成功。

**Q: 多久签到一次比较好？**
A: 建议每天4-6次，过于频繁可能被限制。默认配置是每4小时一次。

**Q: 可以同时管理多个账号吗？**
A: 可以！使用 `ACCOUNTS` secret 配置多个账号的 JSON 数组即可。程序会自动依次为每个账号签到。

**Q: 如何设置邮件通知？**
A: 在 GitHub Secrets 中添加 `SMTP_SERVER`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASSWORD` 和 `EMAIL_TO` 即可。支持 Gmail、QQ 邮箱、163 邮箱等常见邮箱服务。

**Q: 邮件通知发送失败怎么办？**
A:
1. 检查 SMTP 配置是否正确（服务器地址、端口）
2. 确认使用的是邮箱授权码，而不是登录密码
3. Gmail 用户需要开启"两步验证"并生成"应用专用密码"
4. QQ/163 邮箱需要在设置中开启 SMTP 服务并获取授权码

**Q: GitHub Actions 有使用限制吗？**
A: 公开仓库的 GitHub Actions 是免费的，每月有 2000 分钟的免费额度（私有仓库）。

**Q: 如何停止自动签到？**
A: 进入 Settings → Actions → General，选择 "Disable actions"。

## 贡献

欢迎提交 Issues 和 Pull Requests！

## License

MIT License
