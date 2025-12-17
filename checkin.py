import os
import time
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


EMAIL = os.getenv("OIIOII_EMAIL")
PASSWORD = os.getenv("OIIOII_PASSWORD")
TG_BOT = os.getenv("TG_BOT_TOKEN")
TG_CHAT = os.getenv("TG_CHAT_ID")


def tg_send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT}/sendMessage",
            data={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}
        )
    except:
        pass


def start_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1400,900")

    return webdriver.Chrome(
        ChromeDriverManager().install(),
        options=chrome_options
    )


def get_balance(driver):
    try:
        el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(@class,'balance-amount')]")
            )
        )
        return el.text.strip()
    except:
        return "未知"


def run():
    safe_email = EMAIL[:3] + "***@" + EMAIL.split("@")[1]

    try:
        driver = start_driver()

        # 1. 登录
        driver.get("https://www.oiioii.ai/login")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'登录')]"))
        ).click()

        WebDriverWait(driver, 20).until(EC.url_contains("/home"))
        time.sleep(2)

        # 2. 点击赚盒饭
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'赚盒饭')]"))
        ).click()

        time.sleep(1)

        # 3. 领取奖励
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'余额') or contains(text(),'交易')]")
            )
        )

        already = False
        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'明天见')]")
            already = True
        except:
            already = False

        if not already:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(@class,'credit-claim-btn') or .//span[contains(text(),'300')]]"
                    )
                )
            ).click()
            time.sleep(1)

        # 4. 查看积分
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(),'余额') or contains(text(),'交易')]")
            )
        ).click()

        balance = get_balance(driver)

        # 5. 推送
        if already:
            msg = (
                "🎉 <b>OiiOii 自动签到</b>\n"
                f"👤 <code>{safe_email}</code>\n"
                f"✔ 今日已签到（明天见）\n"
                f"💰 当前积分：<b>{balance}</b>"
            )
        else:
            msg = (
                "🎉 <b>OiiOii 自动签到成功</b>\n"
                f"👤 <code>{safe_email}</code>\n"
                f"🎁 领取：+300\n"
                f"💰 当前积分：<b>{balance}</b>"
            )

        driver.quit()

    except Exception as e:
        msg = (
            "❌ <b>签到失败</b>\n"
            f"<code>{traceback.format_exc()}</code>"
        )

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
