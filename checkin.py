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
    requests.post(url, data={
        "chat_id": TG_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    })


def run():
    print("=== OiiOii 签到脚本 V8（Shadow DOM 支持） ===")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            locale="zh-CN",
            viewport={"width": 1440, "height": 900}
        )
        page = context.new_page()

        print("访问登录页...")
        page.goto("https://www.oiioii.ai/login", timeout=60000)
        page.wait_for_load_state("networkidle")
        time.sleep(4)

        print("输入邮箱和密码...")
        page.locator(":text-matches('example@email.com', 'i')").fill(EMAIL)
        page.locator(":text-matches('至少6个字符', 'i')").locator("xpath=..").locator("input").fill(PASSWORD)

        print("点击粉色登录按钮...")
        page.locator("button:has-text('登录')").nth(0).click()
        time.sleep(8)

        print("访问首页，等待全部渲染...")
        page.goto("https://www.oiioii.ai/home")
        page.wait_for_load_state("networkidle")
        time.sleep(5)

        print("查找『赚盒饭』按钮（Shadow DOM）...")
        earn_btn = page.locator(":deep(button:has-text('赚盒饭'))")

        if earn_btn.count() == 0:
            raise Exception("未找到『赚盒饭』按钮")

        earn_btn.first.click()
        time.sleep(4)

        print("查找『每日免费奖励』按钮...")
        reward = page.locator(":deep(button:has-text('每日免费奖励'))")

        if reward.count() == 0:
            reward = page.locator(":deep(button:has-text('+300'))")

        if reward.count() == 0:
            msg = "✔ 今日已领取"
        else:
            reward.first.click()
            msg = "🎉 领取成功！+300 盒饭币"

        print(msg)
        send_tg(msg)
        browser.close()


if __name__ == "__main__":
    run()
