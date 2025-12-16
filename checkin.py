import os
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


EMAIL = os.getenv("OIIOII_EMAIL")
PASSWORD = os.getenv("OIIOII_PASSWORD")
TG_BOT = os.getenv("TG_BOT_TOKEN")
TG_CHAT = os.getenv("TG_CHAT_ID")


def tg_send(msg):
    """向 Telegram 推送 HTML 格式消息"""
    try:
        url = f"https://api.telegram.org/bot{TG_BOT}/sendMessage"
        requests.post(url, data={
            "chat_id": TG_CHAT,
            "text": msg,
            "parse_mode": "HTML"
        })
        print("TG 推送成功")
    except Exception as e:
        print("TG 推送失败：", e)


def click_at(driver, x, y):
    """固定坐标点击"""
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()
    actions.move_by_offset(-x, -y).perform()  # 复位鼠标


def run():
    msg = ""

    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        print("启动 UDC...")
        driver = uc.Chrome(options=options)

        print("打开登录页...")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(6)

        print("输入账户信息...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        print("点击登录...")
        login_btn = driver.find_element(By.XPATH, "//form//button[@type='submit']")
        login_btn.click()
        time.sleep(10)

        print("进入首页...")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(6)

        print("点击赚盒饭（坐标点击）...")
        click_at(driver, 1180, 95)   # 你截图的固定位置
        time.sleep(3)

        print("点击 +300（坐标点击）...")
        click_at(driver, 1110, 360)
        time.sleep(2)

        # 美化推送（方案 A）
        safe_email = EMAIL[:3] + "***" + EMAIL.split("@")[1]

        msg = (
            "🎉 <b>OiiOii 自动签到成功</b>\n\n"
            f"👤 账号：<code>{safe_email}</code>\n"
            f"🎁 今日奖励：<b>+300</b>\n"
            f"💰 当前积分：<b>点击面板可查看</b>\n\n"
            "🔗 <a href=\"https://www.oiioii.ai/\">OiiOii 官网</a>"
        )

        driver.quit()

    except Exception as e:
        msg = f"❌ 签到失败：{e}"

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
