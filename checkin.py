import os
import time
import re
import requests
from playwright.sync_api import sync_playwright


EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


def send_tg(msg):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": TG_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        })
        print("TG 推送成功")
    except Exception as e:
        print("TG 推送失败:", e)


def run():
    result = "❌ 未知错误"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-gpu",
                    "--use-gl=swiftshader",
                    "--ignore-gpu-blacklist",
                    "--enable-webgl",
                ]
            )

            context = browser.new_context(
                locale="zh-CN",
                viewport={"width": 1440, "height": 900}
            )
            page = context.new_page()

            print("访问登录页面...")
            page.goto("https://www.oiioii.ai/login", timeout=60000)
            time.sleep(5)

            print("填写邮箱密码...")
            page.locator("input[type=email]").fill(EMAIL)
            page.locator("input[type=password]").fill(PASSWORD)

            print("勾选同意协议...")
            checkbox = page.locator("input[type=checkbox]")
            checkbox.check()

            print("点击登录按钮...")
            login_btn = page.get_by_role("button", name="登录", exact=True)
            login_btn.click()

            print("等待登录...")
            time.sleep(8)
            page.wait_for_load_state("networkidle")

            # 判断是否真正登录成功（检查 localStorage 里 token）
            token = page.evaluate("localStorage.getItem('token') || ''")
            if not token:
                raise Exception("登录失败：token 未生成")

            print("登录成功，访问首页...")
            page.goto("https://www.oiioii.ai/home", timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(5)

            print("查找并点击赚盒饭按钮...")
            page.get_by_text("赚盒饭").click()
            time.sleep(4)

            print("查找每日奖励按钮...")
            reward1 = page.get_by_text("每日免费奖励")
            reward2 = page.locator("button:has-text('+300')")

            if reward1.count() > 0:
                reward1.click()
                result = "🎉 成功领取 +300 盒饭币"
            elif reward2.count() > 0:
                reward2.click()
                result = "🎉 成功领取 +300 盒饭币"
            else:
                result = "✔ 今日已领取"

            browser.close()

    except Exception as e:
        result = f"❌ 签到失败: {e}"
        print(result)

    send_tg(result)
    print(result)


if __name__ == "__main__":
    run()
