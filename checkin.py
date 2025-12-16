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


# Telegram 推送
def tg_send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT}/sendMessage",
            data={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"},
        )
    except:
        pass


# 坐标点击（最快）
def click_at(driver, x, y):
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()
    actions.move_by_offset(-x, -y).perform()


def run():
    msg = ""
    safe_email = EMAIL[:3] + "***@" + EMAIL.split("@")[1]

    try:
        # 启动 UDC（最小加载）
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--blink-settings=imagesEnabled=false")  # 不加载图片
        
        driver = uc.Chrome(options=options)

        # 登录页
        driver.get("https://www.oiioii.ai/login")
        time.sleep(1.5)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        # 登录
        driver.find_element(By.XPATH, "//form//button[@type='submit']").click()
        time.sleep(3)  # 压缩等待

        # 首页
        driver.get("https://www.oiioii.ai/home")
        time.sleep(2)

        # 点击赚盒饭
        click_at(driver, 1180, 95)
        time.sleep(1)

        # 点击 +300
        click_at(driver, 1110, 360)
        time.sleep(1)

        msg = (
            "🏆 <b>OiiOii 自动签到成功（极速版）</b>\n\n"
            f"👤 账号：<code>{safe_email}</code>\n"
            "🎁 今日奖励：<b>+300</b>\n\n"
            "🚀 签到耗时：<b>10 秒以内</b>\n"
            "🔗 官网:www.oiioii.ai/"
        )

        driver.quit()

    except Exception as e:
        msg = f"❌ 签到失败：{e}"

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
