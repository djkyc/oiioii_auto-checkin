import os
import time
import random
import requests
from playwright.sync_api import sync_playwright

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


def send_tg(text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": TG_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        })
        print("TG 推送成功")
    except:
        print("TG 推送失败")


def run():
    print("=== 启动 OiiOii 签到 V4 ===")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(locale="zh-CN")
            page = context.new_page()

            print("访问首页...")
            page.goto("https://www.oiioii.ai/home", timeout=60000)
            time.sleep(6)
            print("打印页面 HTML 前 5000 字符：")
            html = page.content()
            print(html[:5000])


            # 登录检测
            content = page.content()
            if "登录" in content or "登入" in content:
                print("检测到未登录，执行登录...")
                page.get_by_text("登录").click()
                time.sleep(2)

                page.fill("input[type=email]", EMAIL)
                page.fill("input[type=password]", PASSWORD)
                page.keyboard.press("Enter")
                print("等待登录完成...")
                time.sleep(10)

            print("寻找“赚盒饭”按钮...")

            # ---------- 最强定位 1：可见文本 ----------
            try:
                earn_btn = page.get_by_text("赚盒饭")
                earn_btn.wait_for(timeout=8000)
                print("找到按钮：赚盒饭 (文本定位)")
                earn_btn.click()
            except:
                print("文本定位失败，进入 Fallback 扫描...")

                # ---------- Fallback：扫描所有文本 ----------
                all_nodes = page.locator("*")
                count = all_nodes.count()

                earn_btn = None
                for i in range(count):
                    node = all_nodes.nth(i)
                    try:
                        txt = node.inner_text().strip()
                    except:
                        continue

                    if "赚盒饭" in txt:
                        print(f"找到疑似按钮：{txt}")
                        earn_btn = node
                        break

                if not earn_btn:
                    raise Exception("无法找到赚盒饭按钮")

                earn_btn.click()

            time.sleep(4)

            print("寻找每日奖励按钮...")

            daily_btn = None
            buttons = page.locator("button")
            for i in range(buttons.count()):
                txt = buttons.nth(i).inner_text().strip()
                print("检测按钮：", txt)

                if ("每日免费奖励" in txt) or ("300" in txt):
                    daily_btn = buttons.nth(i)
                    break

            if daily_btn:
                print("点击每日奖励按钮...")
                daily_btn.click()
                result = "🎉 签到成功！获得 +300 盒饭币"
            else:
                result = "✔ 今日已签到或未检测到可领取奖励"

            browser.close()

    except Exception as e:
        result = f"❌ 签到失败：{e}"
        print(result)

    send_tg(result)
    print("=== 脚本结束 ===")


if __name__ == "__main__":
    run()
