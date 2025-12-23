# Anyrouter 自动签到

自动签到 anyrouter.top 的工具，支持邮箱账号密码登录，使用 Playwright 实现自动化。

## 功能特性

- ✅ 自动每日签到（每8小时执行一次）
- ✅ 邮箱密码登录（非 OAuth）
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

在你 fork 的仓库中，进入 **Settings** → **Secrets and variables** → **Actions**，添加以下 secrets：

| Secret 名称 | 说明 | 必填 | 示例 |
|------------|------|------|------|
| `ANYROUTE_EMAIL` | anyrouter.top 登录邮箱或用户名 | ✅ 是 | `your-email@example.com` 或 `username` |
| `ANYROUTE_PASSWORD` | anyrouter.top 登录密码 | ✅ 是 | `your-password` |
| `ANYROUTE_BASE_URL` | 网站地址 | ❌ 否 | `https://anyrouter.top` (默认值) |

**添加步骤：**
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

脚本每 **8 小时** 自动执行一次：
- 🕗 **北京时间 08:00**（UTC 0:00）
- 🕓 **北京时间 16:00**（UTC 8:00）
- 🕛 **北京时间 00:00**（UTC 16:00）

### 自定义执行时间

如需修改执行时间，编辑 `.github/workflows/checkin.yml` 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'   # UTC 0:00 = 北京时间 8:00
  - cron: '0 8 * * *'   # UTC 8:00 = 北京时间 16:00
  - cron: '0 16 * * *'  # UTC 16:00 = 北京时间 0:00
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
# 使用 pip
pip install -r requirements.txt
playwright install chromium

# 或使用 uv（更快）
uv sync
uv run playwright install chromium
```

### 2. 配置环境变量

**Linux/Mac：**
```bash
export ANYROUTE_EMAIL="your-email@example.com"
export ANYROUTE_PASSWORD="your-password"

# 可选：显示浏览器窗口（用于调试）
export HEADLESS="false"
```

**Windows PowerShell：**
```powershell
$env:ANYROUTE_EMAIL="your-email@example.com"
$env:ANYROUTE_PASSWORD="your-password"

# 可选：显示浏览器窗口（用于调试）
$env:HEADLESS="false"
```

**或使用 .env 文件：**
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的账号密码
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

- 程序使用 Playwright 模拟浏览器登录
- 支持邮箱或用户名登录
- 登录失败时自动重试（最多3次）
- 第一次登录可能触发网站的防护机制，重试后通常可成功

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

1. **Playwright 未安装**
   ```bash
   playwright install chromium
   playwright install-deps  # Linux 需要
   ```

2. **环境变量未设置**
   ```bash
   # 检查环境变量
   echo $ANYROUTE_EMAIL
   echo $ANYROUTE_PASSWORD
   ```

3. **依赖问题**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt --force-reinstall
   ```

## API 说明

本脚本使用以下操作：

- **登录**：访问 `/login` 页面，使用 Playwright 自动填写表单并提交
- **签到**：`POST /api/user/sign_in/{user_id}`
- **用户信息**：`GET /api/user/self`

## 技术栈

- Python 3.11+
- Playwright（浏览器自动化）
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
A: 建议每天2-3次，过于频繁可能被限制。默认配置是每8小时一次。

**Q: 可以同时管理多个账号吗？**
A: 可以。fork 多个仓库，每个仓库配置不同的 Secrets 即可。

**Q: GitHub Actions 有使用限制吗？**
A: 公开仓库的 GitHub Actions 是免费的，每月有 2000 分钟的免费额度（私有仓库）。

**Q: 如何停止自动签到？**
A: 进入 Settings → Actions → General，选择 "Disable actions"。

## 贡献

欢迎提交 Issues 和 Pull Requests！

## License

MIT License
