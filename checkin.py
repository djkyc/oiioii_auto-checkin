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
    """读取积分（从余额弹窗）"""
    try:
        el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "(//span[contains(@class,'balance-amount')])[1]")
            )
        )
        text = el.text.strip().replace(",", "")
        return text if text.isdigit() else text
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
        time.sleep(4)

        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        driver.find_element(By.XPATH, "//form//button[@type='submit']").click()
        time.sleep(6)

        # 首页
        driver.get("https://www.oiioii.ai/home")
        time.sleep(3)

        # 打开赚盒饭
        click_at(driver, 1180, 95)
        time.sleep(2)

        # ⭐⭐ 新方法：点击余额和交易记录按钮（文本定位）
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'余额和交易记录')]"))
        ).click()

        time.sleep(2)

        # 获取积分
        balance = get_balance(driver)

        # 检查是否已签到
        try:
            driver.find_element(By.XPATH, "//span[contains(text(),'明天见')]")
            msg = (
                "🏆 <b>OiiOii 自动签到通知</b>\n\n"
                f"👤 账号：<code>{safe_email}</code>\n"
                "✔ 今日已签到，无需重复领取。\n"
                f"💰 当前积分：<b>{balance}</b>\n\n"
                
            )
            tg_send(msg)
            driver.quit()
            return
        except:
            pass

        # 点击 +300 奖励按钮
        click_at(driver, 1110, 360)
        time.sleep(2)

        balance = get_balance(driver)

        msg = (
            "🎉 <b>OiiOii 自动签到成功</b>\n\n"
            f"👤 账号：<code>{safe_email}</code>\n"
            "🎁 今日奖励到账：<b>+300</b>\n"
            f"💰 当前积分：<b>{balance}</b>\n\n"
           
        )

        tg_send(msg)
        driver.quit()

    except Exception as e:
        msg = (
            "❌ <b>签到失败</b>\n\n"
            f"原因：<code>{str(e)}</code>\n"
            f"账号：{safe_email}"
        )
        tg_send(msg)

if __name__ == "__main__":
    run()
