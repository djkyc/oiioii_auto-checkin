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
    """Telegram 推送消息"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT}/sendMessage",
            data={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}
        )
    except:
        pass


def get_balance(driver):
    """读取积分余额"""
    try:
        el = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'credit-balance')]//div[contains(@class,'credit-amount')]")
            )
        )
        return el.text.strip()
    except:
        return "未知"


def run():
    safe_email = EMAIL[:3] + "***@" + EMAIL.split("@")[1]

    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # GitHub Actions / Linux Chrome 路径支持
        chrome_path = "/usr/bin/google-chrome"
        if os.path.exists(chrome_path):
            driver = uc.Chrome(
                options=options,
                browser_executable_path=chrome_path,
                headless=True
            )
        else:
            driver = uc.Chrome(options=options)

        # 打开登录页
        driver.get("https://www.oiioii.ai/login")

        # 输入账号密码
        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        # 点击登录按钮
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//div[contains(text(),'登录')]]")
            )
        ).click()

        # 等待跳转主页
        WebDriverWait(driver, 20).until(EC.url_contains("/home"))
        time.sleep(2)

        # 点击赚盒饭
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(),'赚盒饭')]")
            )
        ).click()

        time.sleep(1)

        # 打开余额/交易记录弹窗
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(),'余额') or contains(text(),'交易')]")
            )
        ).click()

        time.sleep(1)

        # 检查是否已签到（弹出“明天见”）
        already = False
        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'明天见')]")
            already = True
        except:
            already = False

        balance = get_balance(driver)

        if already:
            msg = (
                "🎉 <b>OiiOii 自动签到通知</b>\n\n"
                f"👤 账号：<code>{safe_email}</code>\n"
                f"✔ 今日已签到\n"
                f"💰 当前积分：<b>{balance}</b>"
            )
            driver.quit()
            tg_send(msg)
            return

        # 点击 +300 按钮（每日奖励）
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(@class,'credit-claim-btn') or .//span[contains(text(),'300')]]"
                )
            )
        ).click()

        time.sleep(1)
        balance = get_balance(driver)

        msg = (
            "🎉 <b>OiiOii 自动签到成功</b>\n\n"
            f"👤 账号：<code>{safe_email}</code>\n"
            f"🎁 今日奖励：<b>+300</b>\n"
            f"💰 当前积分：<b>{balance}</b>"
        )

        driver.quit()

    except Exception as e:
        msg = (
            "❌ <b>签到失败</b>\n\n"
            f"原因：<code>{str(e)}</code>\n"
            f"账号：{safe_email}"
        )

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
