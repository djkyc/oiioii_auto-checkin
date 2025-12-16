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
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT}/sendMessage",
            data={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}
        )
    except:
        pass


def click_at(driver, x, y):
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()
    actions.move_by_offset(-x, -y).perform()


def get_balance(driver):
    """三层兜底机制：稳定读取积分"""
    # 方案 1：标准 DOM
    xpaths = [
        "(//div[contains(@class,'credit-balance')])[1]",
        "(//div[contains(@class,'credit-panel')]//div)[1]",
        "//div[normalize-space(text()) and string-length(text()) < 6]"
    ]
    for xp in xpaths:
        try:
            el = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.XPATH, xp))
            )
            text = el.text.strip().replace(",", "")
            if text.isdigit():
                return text
        except:
            pass
    return "未知"


def run():
    safe_email = EMAIL[:3] + "***@" + EMAIL.split("@")[1]

    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options)

        driver.get("https://www.oiioii.ai/login")
        time.sleep(5)

        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        driver.find_element(By.XPATH, "//form//button[@type='submit']").click()
        time.sleep(8)

        driver.get("https://www.oiioii.ai/home")
        time.sleep(4)

        click_at(driver, 1180, 95)
        time.sleep(2)

        balance = get_balance(driver)

        # 判断是否已签到
        try:
            driver.find_element(By.XPATH, "//span[contains(text(),'明天见')]")
            msg = (
                "🏆 <b>OiiOii 自动签到通知</b>\n\n"
                f"👤 账号：<code>{safe_email}</code>\n"
                "✔ 今日已签到，无需重复领取。\n"
                f"💰 当前积分：<b>{balance}</b>\n\n"
                "🔗 <a href=\"https://www.oiioii.ai/\">OiiOii 官网</a>"
            )
            driver.quit()
            tg_send(msg)
            print(msg)
            return
        except:
            pass

        click_at(driver, 1110, 360)
        time.sleep(2)

        balance = get_balance(driver)

        msg = (
            "🏆 <b>OiiOii官网 自动签到成功</b>\n\n"
            f"👤 账号：<code>{safe_email}</code>\n"
            "🎁 今日奖励到账：<b>+300</b>\n"
            f"💰 当前积分：<b>{balance}</b>\n\n"
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
