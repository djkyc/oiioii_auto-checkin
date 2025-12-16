import time
import os
import random
import requests
from playwright.sync_api import sync_playwright

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]


def send_tg_message(text):
    """发送 TG 推送"""
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": TG_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        })
        print("TG 推送成功")
    except Exception as e:
        print("TG 推送失败：", e)


def run():
    print("=== 启动签到脚本 ===")

    try:
        with sync_playwright() as p:

            ua = random.choice(USER_AGENTS)
            print(f"使用 User-Agent: {ua}")

            browser = p.chromium.launch(
                headless=True,   # ← 在 GitHub Actions 必须使用 headless
                args=["--disable-blink-features=AutomationControlled"]
            )

            context = browser.new_context(
                user_agent=ua,
                locale="zh-CN",
                viewport={"width": 1280, "height": 800}
            )

            page = context.new_page()
            print("访问首页...")
            page.goto("https://www.oiioii.ai/home", timeout=60000)
            time.sleep(5)

            if "登录" in page.content():
                print("执行登录...")
                page.click("text=登录")
                time.sleep(2)
                page.fill("input[type=email]", EMAIL)
                page.fill("input[type=password]", PASSWORD)
                page.keyboard.press("Enter")
                print("等待登录完成...")
                time.sleep(8)

            print("展开赚盒饭面板")
            page.wait_for_selector("div.cursor-pointer", timeout=15000)
            page.click("div.cursor-pointer")
            time.sleep(3)

            print("查找签到按钮...")
            page.wait_for_selector("button", timeout=20000)
            buttons = page.locator("button")

            daily_button = None

            for i in range(buttons.count()):
                text = buttons.nth(i).inner_text()
                print("检测按钮：", text)
                if "每日免费奖励" in text or "+300" in text:
                    daily_button = buttons.nth(i)
                    break

            if daily_button:
                print("点击签到按钮...")
                daily_button.click()
                result = "🎉 签到成功！已领取 +300 盒饭币"
            else:
                print("没有找到可领取按钮")
                result = "✔ 今日已领取，无需重复签到"

            browser.close()

    except Exception as e:
        result = f"❌ 签到失败：{e}"
        print(result)

    send_tg_message(result)
    print("=== 脚本结束 ===")


if __name__ == "__main__":
    run()
