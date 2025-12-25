#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import asyncio
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from camoufox.async_api import AsyncCamoufox


def log(message):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        print(f"[{timestamp}] {message}")
    except UnicodeEncodeError:
        safe_msg = message.replace('✓', '[OK]').replace('✗', '[FAIL]')
        print(f"[{timestamp}] {safe_msg}")


def check_today_success():
    """检查今天是否已经成功签到过"""
    github_token = os.environ.get('GITHUB_TOKEN')
    github_repository = os.environ.get('GITHUB_REPOSITORY')

    # 如果不在 GitHub Actions 环境中，跳过检查
    if not github_token or not github_repository:
        log("未在 GitHub Actions 环境中，跳过今日签到检查")
        return False

    try:
        today = datetime.now().strftime('%Y-%m-%d')

        # 使用 GitHub API 获取 repository variable
        api_url = f"https://api.github.com/repos/{github_repository}/actions/variables/LAST_SUCCESS_DATE"
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            last_success_date = data.get('value', '')

            if last_success_date == today:
                log(f"[INFO] 今日 ({today}) 已经成功签到，跳过本次执行")
                return True
            else:
                log(f"[INFO] 上次成功签到日期: {last_success_date}，继续执行")
                return False
        elif response.status_code == 404:
            log("[INFO] 未找到签到记录，首次执行")
            return False
        else:
            log(f"[WARN] 获取签到记录失败: {response.status_code}")
            return False

    except Exception as e:
        log(f"[WARN] 检查今日签到状态异常: {str(e)}")
        return False


def update_success_date():
    """更新今日签到成功的日期"""
    github_token = os.environ.get('GITHUB_TOKEN')
    github_repository = os.environ.get('GITHUB_REPOSITORY')

    # 如果不在 GitHub Actions 环境中，跳过更新
    if not github_token or not github_repository:
        log("未在 GitHub Actions 环境中，跳过更新签到日期")
        return False

    try:
        today = datetime.now().strftime('%Y-%m-%d')

        # 检查 variable 是否存在
        api_url = f"https://api.github.com/repos/{github_repository}/actions/variables/LAST_SUCCESS_DATE"
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        # 先尝试获取
        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            # Variable 存在，更新
            patch_url = api_url
            data = {'value': today}
            response = requests.patch(patch_url, json=data, headers=headers, timeout=10)

            if response.status_code == 204:
                log(f"[OK] 已更新签到日期: {today}")
                return True
            else:
                log(f"[WARN] 更新签到日期失败: {response.status_code}")
                return False

        elif response.status_code == 404:
            # Variable 不存在，创建
            create_url = f"https://api.github.com/repos/{github_repository}/actions/variables"
            data = {
                'name': 'LAST_SUCCESS_DATE',
                'value': today
            }
            response = requests.post(create_url, json=data, headers=headers, timeout=10)

            if response.status_code == 201:
                log(f"[OK] 已创建签到日期记录: {today}")
                return True
            else:
                log(f"[WARN] 创建签到日期记录失败: {response.status_code}")
                return False
        else:
            log(f"[WARN] 检查签到日期状态失败: {response.status_code}")
            return False

    except Exception as e:
        log(f"[WARN] 更新签到日期异常: {str(e)}")
        return False


def send_email(results):
    """发送签到结果邮件通知"""
    # 读取邮件配置
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT') or '587')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    email_to = os.environ.get('EMAIL_TO')

    # 如果没有配置邮件，则跳过
    if not all([smtp_server, smtp_user, smtp_password, email_to]):
        log("未配置邮件发送，跳过邮件通知")
        return False

    try:
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 构建邮件内容
        subject = f"Anyrouter 签到报告 - {current_time}"

        # HTML 邮件正文
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .summary {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .success {{ color: #28a745; }}
                .fail {{ color: #dc3545; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h2>Anyrouter 自动签到报告</h2>
            <div class="summary">
                <p><strong>执行时间：</strong>{current_time}</p>
                <p><strong>总计账号：</strong>{len(results)} 个</p>
                <p class="success"><strong>✓ 成功：</strong>{success_count} 个</p>
                <p class="fail"><strong>✗ 失败：</strong>{fail_count} 个</p>
            </div>

            <h3>详细结果</h3>
            <table>
                <tr>
                    <th>账号名称</th>
                    <th>签到结果</th>
                    <th>账户余额</th>
                </tr>
        """

        for result in results:
            status_color = "success" if result['success'] else "fail"
            status_text = "✓ 成功" if result['success'] else "✗ 失败"
            quota_info = result.get('quota_info', '')

            html_body += f"""
                <tr>
                    <td>{result['name']}</td>
                    <td class="{status_color}">{status_text}</td>
                    <td>{quota_info}</td>
                </tr>
            """

        html_body += """
            </table>
            <hr>
            <p style="color: #666; font-size: 12px;">
                此邮件由 Anyrouter 自动签到脚本自动发送
            </p>
        </body>
        </html>
        """

        # 创建邮件
        message = MIMEMultipart('alternative')
        message['From'] = Header(f"Anyrouter 签到 <{smtp_user}>", 'utf-8')
        message['To'] = Header(email_to, 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')

        # 添加 HTML 内容
        html_part = MIMEText(html_body, 'html', 'utf-8')
        message.attach(html_part)

        # 发送邮件
        log(f"正在发送邮件到 {email_to}...")

        # 根据端口选择连接方式
        if smtp_port == 465:
            # SSL
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            # TLS (587) 或其他
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()

        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, email_to.split(','), message.as_string())
        server.quit()

        log("[OK] 邮件发送成功")
        return True

    except Exception as e:
        log(f"[FAIL] 邮件发送失败: {str(e)}")
        return False


class AnyrouteCheckin:
    def __init__(self, email, password, base_url=None, headless=True, account_name=None):
        self.email = email
        self.password = password
        self.base_url = base_url or os.environ.get('ANYROUTE_BASE_URL', 'https://anyrouter.top')
        self.user_id = None
        self.headless = headless
        self.page = None
        self.browser = None
        self.account_name = account_name or email

    async def _init_browser(self):
        """初始化浏览器"""
        log("初始化浏览器...")
        self.browser = await AsyncCamoufox(
            headless=self.headless,
            humanize=True,
            locale='zh-CN',
            geoip=False,
        ).__aenter__()
        self.page = await self.browser.new_page()

    async def _close_browser(self):
        """关闭浏览器"""
        if self.browser:
            try:
                await self.browser.__aexit__(None, None, None)
            except:
                pass

    async def login(self):
        """登录到 anyrouter.top（支持重试）"""
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            log(f"开始登录 (尝试 {attempt}/{max_retries})...")
            success = await self._try_login_once()

            if success:
                return True

            if attempt < max_retries:
                log(f"登录失败，刷新页面并重试...")
                await self.page.wait_for_timeout(2000)
            else:
                log(f"登录失败，已尝试 {max_retries} 次")

        return False

    async def _try_login_once(self):
        """尝试一次登录"""
        try:
            # 访问登录页面
            login_page_url = f"{self.base_url}/login"
            log(f"访问登录页面: {login_page_url}")
            await self.page.goto(login_page_url, wait_until='networkidle', timeout=60000)

            # 等待页面渲染
            log("等待页面渲染...")
            await self.page.wait_for_timeout(3000)

            # 关闭可能存在的弹窗
            log("检查并关闭弹窗...")
            for _ in range(3):
                await self.page.keyboard.press('Escape')
                await self.page.wait_for_timeout(500)

            # 打印当前页面所有可点击元素，用于调试
            log("分析页面元素...")
            page_info = await self.page.evaluate('''() => {
                const result = { buttons: [], links: [], inputs: [] };

                document.querySelectorAll('button').forEach(el => {
                    result.buttons.push(el.innerText.trim());
                });

                document.querySelectorAll('a, span[role="button"], div[role="button"]').forEach(el => {
                    const text = el.innerText.trim();
                    if (text && text.length < 50) result.links.push(text);
                });

                document.querySelectorAll('input').forEach(el => {
                    result.inputs.push({
                        type: el.type,
                        id: el.id,
                        placeholder: el.placeholder
                    });
                });

                return result;
            }''')

            log(f"按钮: {page_info.get('buttons', [])}")
            log(f"链接: {page_info.get('links', [])[:10]}")  # 只显示前10个
            log(f"输入框: {page_info.get('inputs', [])}")

            # 步骤1: 点击"使用 邮箱或用户名 登录"
            log("步骤1: 切换到邮箱登录模式...")

            # 检查是否已经有输入框了
            existing_inputs = await self.page.query_selector_all('input#username, input[type="text"]')
            if len(existing_inputs) > 0:
                log("页面已经在邮箱登录模式")
            else:
                # 尝试点击邮箱登录按钮
                email_login_clicked = False
                try:
                    # 方法1: 使用文本选择器
                    email_btn = await self.page.query_selector('text=/.*邮箱.*登.*/')
                    if email_btn:
                        await email_btn.click()
                        email_login_clicked = True
                        log("已点击邮箱登录按钮(方法1)")
                except:
                    pass

                if not email_login_clicked:
                    # 方法2: JavaScript 查找并点击
                    clicked_text = await self.page.evaluate('''() => {
                        const elements = document.querySelectorAll('span, div, a, button, p');
                        for (const el of elements) {
                            const text = el.innerText || '';
                            if (text.includes('邮箱') && text.includes('登')) {
                                console.log('Found email login button:', text);
                                el.click();
                                return text;
                            }
                        }
                        return null;
                    }''')
                    if clicked_text:
                        log(f"已点击: {clicked_text}")
                        email_login_clicked = True

                if email_login_clicked:
                    await self.page.wait_for_timeout(2000)
                else:
                    log("未找到邮箱登录切换按钮，假设已经在邮箱登录模式")

            # 再次检查页面状态
            log("检查切换后的页面状态...")
            inputs_after = await self.page.query_selector_all('input')
            log(f"切换后找到 {len(inputs_after)} 个输入框")

            for inp in inputs_after:
                inp_type = await inp.get_attribute('type') or ''
                inp_id = await inp.get_attribute('id') or ''
                inp_placeholder = await inp.get_attribute('placeholder') or ''
                log(f"  输入框: type={inp_type}, id={inp_id}, placeholder={inp_placeholder}")

            # 步骤2: 填写用户名
            log("步骤2: 填写用户名...")
            username_input = await self.page.query_selector('input#username, input[placeholder*="用户名"], input[placeholder*="邮箱"], input[type="text"]')
            if username_input:
                await username_input.click()
                await self.page.wait_for_timeout(200)
                await username_input.fill(self.email)
                log(f"已填写用户名: {self.email}")
            else:
                log("[FAIL] 找不到用户名输入框")
                return False

            # 步骤3: 填写密码
            log("步骤3: 填写密码...")
            password_input = await self.page.query_selector('input#password, input[type="password"]')
            if password_input:
                await password_input.click()
                await self.page.wait_for_timeout(200)
                await password_input.fill(self.password)
                log("已填写密码")
            else:
                log("[FAIL] 找不到密码输入框")
                return False

            await self.page.wait_for_timeout(500)

            # 步骤4: 点击"继续"按钮
            log("步骤4: 点击继续按钮...")
            continue_btn = await self.page.query_selector('button:has-text("继续")')
            if continue_btn:
                await continue_btn.click()
                log("已点击继续按钮")
            else:
                # 尝试其他方式
                clicked = await self.page.evaluate('''() => {
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        const text = btn.innerText.trim();
                        if (text === '继续' || text.includes('继续')) {
                            btn.click();
                            return text;
                        }
                    }
                    return null;
                }''')
                if clicked:
                    log(f"已点击: {clicked}")
                else:
                    log("[FAIL] 找不到继续按钮")
                    return False

            # 等待登录完成
            log("等待登录响应...")
            await self.page.wait_for_timeout(5000)

            # 检查页面是否有错误提示
            error_msg = await self.page.evaluate('''() => {
                const errorElements = document.querySelectorAll('.error, .alert, [role="alert"], .toast, .message');
                for (const el of errorElements) {
                    const text = el.innerText.trim();
                    if (text && text.length > 0 && text.length < 200) {
                        return text;
                    }
                }
                return null;
            }''')

            if error_msg:
                log(f"页面错误提示: {error_msg}")

            # 检查登录结果
            current_url = self.page.url
            log(f"当前 URL: {current_url}")

            # 检查是否登录成功 - 通过 localStorage 获取用户信息
            try:
                user_str = await self.page.evaluate('() => localStorage.getItem("user")')
                if user_str:
                    user_data = json.loads(user_str)
                    self.user_id = user_data.get('id')
                    username = user_data.get('username', self.email)
                    log(f"[OK] 登录成功 (用户: {username}, ID: {self.user_id})")
                    return True
            except Exception as e:
                log(f"获取用户信息异常: {e}")

            # 检查 URL 是否跳转
            current_url = self.page.url
            if '/login' not in current_url:
                log(f"[OK] 登录成功 (已跳转到: {current_url})")
                await self.page.wait_for_timeout(2000)
                try:
                    user_str = await self.page.evaluate('() => localStorage.getItem("user")')
                    if user_str:
                        user_data = json.loads(user_str)
                        self.user_id = user_data.get('id')
                except:
                    pass
                return True

            log("登录失败，仍在登录页面")
            return False

        except Exception as e:
            log(f"登录异常: {str(e)}")
            return False

    async def checkin(self):
        """执行签到（登录后自动签到）"""
        try:
            log("检查签到状态...")

            # 签到是登录时自动完成的，直接调用API确认
            checkin_url = f"{self.base_url}/api/user/sign_in"
            log(f"签到 URL: {checkin_url}")

            js_code = f'''
            async () => {{
                try {{
                    const response = await fetch("{checkin_url}", {{
                        method: "POST",
                        headers: {{
                            "Content-Type": "application/json"
                        }}
                    }});
                    const data = await response.json();
                    return {{
                        status: response.status,
                        data: data
                    }};
                }} catch (e) {{
                    return {{error: e.message}};
                }}
            }}
            '''

            result = await self.page.evaluate(js_code)
            log(f"签到响应: {result}")

            # 检查是否有网络错误
            if result and result.get('error'):
                error_msg = result.get('error')
                log(f"[FAIL] 网络请求失败: {error_msg}")
                return False

            # 检查 HTTP 状态码
            status = result.get('status') if result else None
            data = result.get('data') if result else None

            if not data:
                log("[FAIL] API 响应为空，签到状态未知")
                return False

            # 判断 API 返回的 success 字段
            if data.get('success') is True:
                msg = data.get('message', '签到成功')
                log(f"[OK] {msg}")
                return True
            elif data.get('success') is False:
                # API 明确返回失败
                msg = data.get('message', '未知错误')
                # 检查是否是"已经签到"的错误
                if '已经签到' in str(msg) or 'already' in str(msg).lower():
                    log(f"[OK] 今日已签到")
                    return True
                log(f"[FAIL] 签到失败: {msg}")
                return False
            else:
                # success 字段不存在或不是布尔值
                log(f"[WARN] API 响应格式异常: {data}")
                log("[FAIL] 无法确认签到状态")
                return False

        except Exception as e:
            log(f"[FAIL] 签到异常: {str(e)}")
            return False

    async def get_user_info(self):
        """获取用户信息"""
        try:
            log("获取用户信息...")

            user_info_url = f"{self.base_url}/api/user/self"

            js_code = f'''
            async () => {{
                try {{
                    const response = await fetch("{user_info_url}", {{
                        method: "GET",
                        headers: {{
                            "Content-Type": "application/json",
                            "new-api-user": "{self.user_id or ''}"
                        }}
                    }});
                    return await response.json();
                }} catch (e) {{
                    return {{error: e.message}};
                }}
            }}
            '''

            result = await self.page.evaluate(js_code)

            if result and result.get('success'):
                user_data = result.get('data', {})
                quota = round(user_data.get('quota', 0) / 500000, 2)
                used_quota = round(user_data.get('used_quota', 0) / 500000, 2)
                bonus_quota = round(user_data.get('bonus_quota', 0) / 500000, 2)

                log(f"  当前余额: ${quota}")
                log(f"  已使用: ${used_quota}")
                log(f"  奖励余额: ${bonus_quota}")

                return {
                    'quota': quota,
                    'used_quota': used_quota,
                    'bonus_quota': bonus_quota
                }
            else:
                error_msg = result.get('message', '未知错误') if result else '无响应'
                log(f"[FAIL] 获取用户信息失败: {error_msg}")
                return None

        except Exception as e:
            log(f"[FAIL] 获取用户信息异常: {str(e)}")
            return None

    async def run(self):
        """运行签到流程"""
        print("=" * 50)
        print(f"账号: {self.account_name}")
        print(f"目标网站: {self.base_url}")
        print(f"Headless 模式: {self.headless}")
        print("=" * 50)

        try:
            await self._init_browser()

            if not await self.login():
                log("程序终止：登录失败")
                return False, None

            checkin_success = await self.checkin()
            user_info = await self.get_user_info()

            if not checkin_success:
                log("程序终止：签到失败")
                return False, None

            print("=" * 50)
            log("[OK] 签到流程完成")
            print("=" * 50)
            return True, user_info

        finally:
            await self._close_browser()


def load_accounts():
    """从环境变量加载账号配置"""
    # 优先使用 ACCOUNTS 配置（支持多账号）
    accounts_json = os.environ.get('ACCOUNTS')
    if accounts_json:
        try:
            accounts = json.loads(accounts_json)
            if not isinstance(accounts, list):
                print("错误: ACCOUNTS 必须是 JSON 数组格式")
                return None

            # 验证每个账号的格式
            for i, account in enumerate(accounts):
                if not isinstance(account, dict):
                    print(f"错误: ACCOUNTS[{i}] 必须是对象")
                    return None
                if 'email' not in account or 'password' not in account:
                    print(f"错误: ACCOUNTS[{i}] 缺少 email 或 password 字段")
                    return None

                # 设置默认 name
                if 'name' not in account:
                    account['name'] = account['email']

            return accounts
        except json.JSONDecodeError as e:
            print(f"错误: ACCOUNTS JSON 解析失败: {e}")
            return None

    # 兼容单账号模式
    email = os.environ.get('ANYROUTE_EMAIL')
    password = os.environ.get('ANYROUTE_PASSWORD')

    if email and password:
        return [{
            'name': email,
            'email': email,
            'password': password
        }]

    return None


async def run_account_checkin(account, default_base_url, headless):
    """运行单个账号的签到"""
    # 优先使用账号自己的 url，否则使用默认 url
    account_url = account.get('url') or default_base_url

    checkin = AnyrouteCheckin(
        email=account['email'],
        password=account['password'],
        base_url=account_url,
        headless=headless,
        account_name=account['name']
    )
    return await checkin.run()


async def main_async():
    """异步主函数"""
    # 注释掉当日签到检查，因为网站签到重置时间不确定
    # 每次执行都尝试签到，依靠网站 API 返回"已签到"来判断
    # if check_today_success():
    #     print("\n" + "=" * 50)
    #     print("今日已成功签到，跳过本次执行")
    #     print("=" * 50)
    #     return True  # 返回 True 表示无需执行（而非失败）

    # 加载账号配置
    accounts = load_accounts()
    if not accounts:
        print("错误: 请设置环境变量 ACCOUNTS 或 ANYROUTE_EMAIL 和 ANYROUTE_PASSWORD")
        print("\n多账号模式（ACCOUNTS）:")
        print('  ACCOUNTS=\'[{"name":"账号1","email":"user1","password":"pass1"},{"name":"账号2","email":"user2","password":"pass2"}]\'')
        print("\n单账号模式（兼容模式）:")
        print("  ANYROUTE_EMAIL=your_email")
        print("  ANYROUTE_PASSWORD=your_password")
        print("\n可选配置:")
        print("  ANYROUTE_BASE_URL (默认: https://anyrouter.top)")
        print("  HEADLESS=false (显示浏览器窗口)")
        print("\n邮件通知配置（可选）:")
        print("  SMTP_SERVER=smtp.gmail.com")
        print("  SMTP_PORT=587")
        print("  SMTP_USER=your_email@gmail.com")
        print("  SMTP_PASSWORD=your_app_password")
        print("  EMAIL_TO=recipient@example.com")
        return False

    base_url = os.environ.get('ANYROUTE_BASE_URL') or 'https://anyrouter.top'
    headless = os.environ.get('HEADLESS', 'true').lower() == 'true'

    # 执行签到
    print("\n" + "=" * 50)
    print("Anyrouter 自动签到脚本 (Camoufox)")
    print(f"共 {len(accounts)} 个账号")
    print("=" * 50 + "\n")

    results = []
    for i, account in enumerate(accounts, 1):
        print(f"\n开始处理第 {i}/{len(accounts)} 个账号...")
        try:
            success, user_info = await run_account_checkin(account, base_url, headless)

            # 格式化余额信息
            quota_info = ""
            if user_info:
                quota_info = f"${user_info.get('quota', 0)}"

            results.append({
                'name': account['name'],
                'success': success,
                'quota_info': quota_info
            })
        except Exception as e:
            log(f"账号 {account['name']} 处理异常: {e}")
            results.append({
                'name': account['name'],
                'success': False,
                'quota_info': ''
            })

        # 账号之间等待一段时间，避免请求过快
        if i < len(accounts):
            await asyncio.sleep(3)

    # 打印汇总结果
    print("\n" + "=" * 50)
    print("签到汇总")
    print("=" * 50)

    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count

    for result in results:
        status = "[OK] 成功" if result['success'] else "[FAIL] 失败"
        quota_text = f" - 余额: {result['quota_info']}" if result['quota_info'] else ""
        print(f"  {result['name']}: {status}{quota_text}")

    print(f"\n总计: {len(results)} 个账号")
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print("=" * 50)

    # 全部成功时更新今日签到日期（已禁用，因为不再检查当日签到）
    all_success = (fail_count == 0)
    # if all_success:
    #     log("所有账号签到成功，更新今日签到记录")
    #     update_success_date()

    # 发送邮件通知（失败不影响整体结果）
    if success_count > 0:  # 只有成功的签到才发送邮件
        try:
            print("\n" + "=" * 50)
            send_email(results)
            print("=" * 50)
        except Exception as e:
            log(f"[WARN] 邮件发送失败: {str(e)}")
            print("=" * 50)

    return all_success


def main():
    success = asyncio.run(main_async())
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
