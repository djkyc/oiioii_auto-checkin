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
    """坐标点击"""
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()
    actions.move_by_offset(-x, -y).perform()

def get_balance_from_popup(driver):
    """从余额弹窗读取积分（最稳定）"""
    try:
        el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "(//span[contains(@class,'balance-amount')])[1]")
            )
        )
        text = el.text.strip().replace(",", "")
        if text.isdigit():
            return text
        return text
    except:
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

        # 打开赚盒饭
        click_at(driver, 1180, 95)
        time.sleep(2)

        # 点击 “余额和交易记录”
        click_at(driver, 650, 300)  # 你截图位置大概中左区域，必要时可调整

        time.sleep(2)

        # 从弹窗读取余额
        balance = get_balance_from_popup(driver)

        # 判断是否已签到（明天见）
        try:
            driver.find_element(By.XPATH, "//span[contains(text(),'明天见')]")
            msg = (
                "🏆 <b>OiiOii 自动签到通知</b>\n\n"
                f"👤 账号：<code>{safe_email}</code>\n"
                "✔ 今日已签到，无需重复领取。\n"

            )
            driver.quit()
            tg_send(msg)
            return
        except:
            pass

        # 点击 +300 签到按钮
        click_at(driver, 1110, 360)
        time.sleep(2)

        balance = get_balance_from_popup(driver)

        msg = (
            "🎉 <b>OiiOii 自动签到成功</b>\n\n"
            f"👤 账号：<code>{safe_email}</code>\n"
            f"🎁 今日奖励到账：<b>+300</b>\n"

            
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
