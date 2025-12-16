import os
import time
import requests
from playwright.sync_api import sync_playwright

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


def send_tg(msg):
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"})
        print("TG 推送成功")
    except:
        print("TG 推送失败")


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

            print("访问登录页...")
            page.goto("https://www.oiioii.ai/login", timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(5)

            print("填写账号密码...")
            page.locator("input[type=email]").fill(EMAIL)
            page.locator("input[type=password]").fill(PASSWORD)
            time.sleep(1)

            print("勾选协议...")
            page.locator("input[type=checkbox]").check()

            print("点击真正的粉色登录按钮...")
            login_btn = page.locator("button:has(div:has-text('登录'))").first
            login_btn.click()

            print("等待登录完成...")
            time.sleep(8)
            page.wait_for_load_state("networkidle")

            # 检查 token 是否写入 localStorage
            token = page.evaluate("localStorage.getItem('token') || ''")
            if not token:
                raise Exception("登录失败（token 未生成）")

            print("登录成功！访问首页...")
            page.goto("https://www.oiioii.ai/home")
            page.wait_for_load_state("networkidle")
            time.sleep(5)

            print("点击赚盒饭按钮...")
            page.get_by_text("赚盒饭").click()
            time.sleep(4)

            print("查找每日奖励按钮...")
            reward = page.get_by_text("每日免费奖励")
            reward2 = page.locator("button:has-text('+300')")

            if reward.count() > 0:
                reward.first.click()
                result = "🎉 成功领取 +300 盒饭币"
            elif reward2.count() > 0:
                reward2.first.click()
                result = "🎉 成功领取 +300 盒饭币"
            else:
                result = "✔ 今日已领取"

            browser.close()

    except Exception as e:
        result = f"❌ 签到失败：{e}"
        print(result)

    send_tg(result)
    print(result)


if __name__ == "__main__":
    run()
