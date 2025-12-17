import os
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


EMAIL = os.getenv("OIIOII_EMAIL")
PASSWORD = os.getenv("OIIOII_PASSWORD")
TG_BOT = os.getenv("TG_BOT_TOKEN")
TG_CHAT = os.getenv("TG_CHAT_ID")


def tg_send(msg):
    """发送 TG HTML 消息"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT}/sendMessage",
            data={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}
        )
    except:
        pass


def run():
    safe_email = EMAIL[:3] + "***@" + EMAIL.split("@")[1]
    msg = ""

    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")

        driver = uc.Chrome(options=options)

        print("打开登录页…")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(3)

        print("输入账号密码…")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        # 点击登录
        driver.find_element(By.XPATH, "//form//button[@type='submit']").click()
        time.sleep(6)

        # 跳转首页
        driver.get("https://www.oiioii.ai/home")
        time.sleep(3)

        # -------------------------------------------------------
        # 点击“赚盒饭”按钮（使用真实 DOM）
        # -------------------------------------------------------
        print("点击赚盒饭…")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH,
                "//*[contains(@class,'_credit-btn-text') and contains(text(),'赚盒饭')]"))
        ).click()

        time.sleep(2)

        # -------------------------------------------------------
        # 检查是否已经签到
        # -------------------------------------------------------
        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'明天见')]")
            msg = (
                "🏆 <b>OiiOii 自动签到</b>\n\n"
                f"👤 账号：<code>{safe_email}</code>\n"
                f"✔ 今日已签到。\n"
            )
            driver.quit()
            tg_send(msg)
            print(msg)
            return
        except:
            pass

        # -------------------------------------------------------
        # 点击 +300 按钮（真实 DOM）
        # -------------------------------------------------------
        print("点击 +300…")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'+ 300')]"))
        ).click()

        time.sleep(3)

        msg = (
            "🏆 <b>OiiOii 自动签到成功</b>\n\n"
            f"👤 账号：<code>{safe_email}</code>\n"
            "🎁 今日奖励到账：<b>+300</b>\n"
        )

        driver.quit()

    except Exception as e:
        msg = (
            "❌ <b>签到失败</b>\n\n"
            f"原因：<code>{str(e)}</code>"
        )

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
