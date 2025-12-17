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
    """发送 TG HTML 消息"""
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
    actions.move_by_offset(-x, -y).perform()  # 归位


def run():
    safe_email = EMAIL[:3] + "***@" + EMAIL.split("@")[1]
    msg = ""

    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options)

        print("打开登录页…")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(6)

        print("输入账号密码…")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        # 登录按钮
        driver.find_element(By.XPATH, "//form//button[@type='submit']").click()
        time.sleep(8)

        # 首页
        driver.get("https://www.oiioii.ai/home")
        time.sleep(4)

        # 点击赚盒饭
        click_at(driver, 1180, 95)
        time.sleep(2)

        # 获取最新积分
        try:
            balance_el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "(//div[contains(@class,'credit-balance')])[1]"))
            )
            balance = balance_el.text.strip()
        except:
            balance = "未知"

        # 检查是否已签到
        try:
            driver.find_element(By.XPATH, "//span[contains(text(),'明天见')]")
            msg = (
                "🏆 <b>OiiOii 自动签到通知</b>\n\n"
                f"👤 账号：<code>{safe_email}</code>\n"
                f"✔ 今日已签到，无需重复领取。\n"
                f"💰 当前积分：<b>{balance}</b>\n\n"
                "🔗 <a href=\"https://www.oiioii.ai/\">OiiOii 官网</a>"
            )
            driver.quit()
            tg_send(msg)
            print(msg)
            return
        except:
            pass

        # 点击 +300 按钮
        click_at(driver, 1110, 360)
        time.sleep(2)

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
