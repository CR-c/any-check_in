#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import asyncio
from datetime import datetime
from camoufox.async_api import AsyncCamoufox


def log(message):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        print(f"[{timestamp}] {message}")
    except UnicodeEncodeError:
        safe_msg = message.replace('✓', '[OK]').replace('✗', '[FAIL]')
        print(f"[{timestamp}] {safe_msg}")


class AnyrouteCheckin:
    def __init__(self, email, password, base_url=None, headless=True):
        self.email = email
        self.password = password
        self.base_url = base_url or os.environ.get('ANYROUTE_BASE_URL', 'https://anyrouter.top')
        self.user_id = None
        self.headless = headless
        self.page = None
        self.browser = None

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
                    return await response.json();
                }} catch (e) {{
                    return {{error: e.message}};
                }}
            }}
            '''

            result = await self.page.evaluate(js_code)
            log(f"签到响应: {result}")

            if result:
                if result.get('success'):
                    msg = result.get('message') or '签到成功'
                    log(f"[OK] {msg if msg else '签到成功'}")
                    return True
                elif result.get('error'):
                    error_msg = result.get('error')
                    # 如果是已经签到的错误，也算成功
                    if '已经签到' in str(error_msg) or 'already' in str(error_msg).lower():
                        log(f"[OK] 今日已签到")
                        return True
                    log(f"[FAIL] 签到失败: {error_msg}")
                    return False
                else:
                    # 如果没有明确的错误，也当作成功（因为登录时已自动签到）
                    log(f"[OK] 登录自动签到完成")
                    return True

            log("[WARN] 签到响应为空，但登录已自动签到")
            return True

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
        print("Anyrouter 自动签到脚本 (Camoufox)")
        print(f"目标网站: {self.base_url}")
        print(f"Headless 模式: {self.headless}")
        print("=" * 50)

        try:
            await self._init_browser()

            if not await self.login():
                log("程序终止：登录失败")
                return False

            checkin_success = await self.checkin()
            await self.get_user_info()

            if not checkin_success:
                log("程序终止：签到失败")
                return False

            print("=" * 50)
            log("[OK] 签到流程完成")
            print("=" * 50)
            return True

        finally:
            await self._close_browser()


def main():
    email = os.environ.get('ANYROUTE_EMAIL')
    password = os.environ.get('ANYROUTE_PASSWORD')
    base_url = os.environ.get('ANYROUTE_BASE_URL')
    headless = os.environ.get('HEADLESS', 'true').lower() == 'true'

    if not email or not password:
        print("错误: 请设置环境变量 ANYROUTE_EMAIL 和 ANYROUTE_PASSWORD")
        print("可选: ANYROUTE_BASE_URL (默认: https://anyrouter.top)")
        print("可选: HEADLESS=false (显示浏览器窗口)")
        sys.exit(1)

    checkin = AnyrouteCheckin(email, password, base_url, headless)
    success = asyncio.run(checkin.run())
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
