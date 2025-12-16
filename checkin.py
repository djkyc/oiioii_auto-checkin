import os
import time
import re
import requests
from playwright.sync_api import sync_playwright


EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


def send_tg(msg: str):
    """发送 Telegram 推送"""
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


def login(page):
    """执行登录流程"""
    print("执行登录流程...")
    page.goto("https://www.oiioii.ai/login", timeout=60000)
    time.sleep(4)

    page.locator("input[type=email]").fill(EMAIL)
    page.locator("input[type=password]").fill(PASSWORD)

    page.get_by_role("button", name=re.compile("登录")).click()
    print("等待登录完成...")
    time.sleep(8)


def find_and_click_earn(page):
    """查找并点击 '赚盒饭' 按钮"""
    print("查找 ‘赚盒饭’ 按钮...")

    try:
        btn = page.get_by_text("赚盒饭", exact=False)
        btn.click()
        print("点击赚盒饭成功！")
        return True
    except:
        pass

    # Fallback: 扫描所有元素
    nodes = page.locator("*")
    for i in range(nodes.count()):
        try:
            txt = nodes.nth(i).inner_text()
        except:
            continue

        if "赚盒饭" in txt:
            print("Fallback 找到按钮：", txt)
            nodes.nth(i).click()
            return True

    raise Exception("无法找到赚盒饭按钮")


def find_and_click_daily_reward(page):
    """找到每日免费奖励按钮并点击"""
    print("查找每日免费奖励按钮...")

    btns = page.locator("button")
    for i in range(btns.count()):
        txt = btns.nth(i).inner_text().strip()
        print("按钮文本：", txt)
        if ("每日免费奖励" in txt) or ("300" in txt):
            print("找到每日奖励按钮！")
            btns.nth(i).click()
            return True

    return False


def run():
    print("=== OiiOii 签到脚本 V6 启动 ===")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 使用 XVFB，所以必须 headful
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            locale="zh-CN",
            viewport={"width": 1440, "height": 900}
        )

        page = context.new_page()

        print("打开首页...")
        page.goto("https://www.oiioii.ai/home", timeout=60000)
        time.sleep(5)

        # 检测是否已登录
        if "登录" in page.content():
            login(page)
        else:
            print("已登录状态")

        time.sleep(4)

        print("进入赚盒饭...")
        find_and_click_earn(page)
        time.sleep(4)

        print("尝试领取每日奖励...")
        ok = find_and_click_daily_reward(page)

        if ok:
            result = "🎉 签到成功！已领取 +300 盒饭币"
        else:
            result = "✔ 今日已领取或未检测到奖励按钮"

        print(result)

        send_tg(result)

        browser.close()

    print("=== 脚本执行完毕 ===")


if __name__ == "__main__":
    run()
