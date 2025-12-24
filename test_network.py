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
        # 移除不可打印字符
        safe_msg = message.encode('ascii', 'ignore').decode('ascii')
        print(f"[{timestamp}] {safe_msg}")


async def test_login_with_network_monitor():
    """测试登录并监听网络请求"""
    email = "evacc"
    password = "Any192102-"
    base_url = "https://anyrouter.top"

    log("初始化浏览器...")
    browser = await AsyncCamoufox(
        headless=False,
        humanize=True,
        locale='zh-CN',
        geoip=False,
    ).__aenter__()

    page = await browser.new_page()

    # 记录所有网络请求
    network_requests = []

    async def log_request(request):
        req_info = {
            'url': request.url,
            'method': request.method,
            'headers': dict(request.headers),
            'post_data': request.post_data
        }
        network_requests.append(req_info)
        log(f"[REQ] {request.method} {request.url}")

    async def log_response(response):
        try:
            # 只记录 API 相关的响应
            if '/api/' in response.url:
                content_type = response.headers.get('content-type', '')
                log(f"[RES] {response.status} {response.url}")

                if 'application/json' in content_type:
                    try:
                        body = await response.text()
                        log(f"   JSON: {body[:200]}...")  # 只显示前200字符
                    except:
                        pass
        except Exception as e:
            log(f"   获取响应失败: {e}")

    # 监听网络事件
    page.on("request", log_request)
    page.on("response", log_response)

    try:
        # 访问登录页面
        login_page_url = f"{base_url}/login"
        log(f"访问登录页面: {login_page_url}")
        await page.goto(login_page_url, wait_until='networkidle', timeout=60000)

        # 等待页面渲染
        log("等待页面渲染...")
        await page.wait_for_timeout(3000)

        # 关闭可能存在的弹窗
        log("检查并关闭弹窗...")
        for _ in range(3):
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(500)

        # 填写用户名
        log("填写用户名...")
        username_input = await page.query_selector('input#username, input[placeholder*="用户名"], input[placeholder*="邮箱"], input[type="text"]')
        if username_input:
            await username_input.click()
            await page.wait_for_timeout(200)
            await username_input.fill(email)
            log(f"已填写用户名: {email}")

        # 填写密码
        log("填写密码...")
        password_input = await page.query_selector('input#password, input[type="password"]')
        if password_input:
            await password_input.click()
            await page.wait_for_timeout(200)
            await password_input.fill(password)
            log("已填写密码")

        await page.wait_for_timeout(500)

        # 点击继续按钮
        log("点击继续按钮...")
        continue_btn = await page.query_selector('button:has-text("继续")')
        if continue_btn:
            await continue_btn.click()
            log("已点击继续按钮")

        # 等待登录完成
        log("等待登录完成...")
        await page.wait_for_timeout(8000)  # 等待更长时间以捕获所有请求

        # 检查是否登录成功
        current_url = page.url
        log(f"当前 URL: {current_url}")

        # 尝试获取用户信息
        try:
            user_str = await page.evaluate('() => localStorage.getItem("user")')
            if user_str:
                user_data = json.loads(user_str)
                user_id = user_data.get('id')
                username = user_data.get('username', email)
                log(f"[OK] 登录成功 (用户: {username}, ID: {user_id})")
        except Exception as e:
            log(f"获取用户信息异常: {e}")

        # 打印所有 API 请求
        log("\n" + "="*60)
        log("所有 API 请求列表：")
        log("="*60)
        for req in network_requests:
            if '/api/' in req['url']:
                log(f"\n[*] {req['method']} {req['url']}")
                if req['post_data']:
                    log(f"   请求体: {req['post_data'][:200]}")
        log("="*60)

        # 等待一段时间让用户观察
        log("\n等待 30 秒供观察，按 Ctrl+C 可提前结束...")
        await page.wait_for_timeout(30000)

    except Exception as e:
        log(f"错误: {str(e)}")
    finally:
        await browser.__aexit__(None, None, None)


if __name__ == '__main__':
    asyncio.run(test_login_with_network_monitor())
