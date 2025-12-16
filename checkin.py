import os
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TG = os.getenv("TG")   # 格式： BOT:CHAT
BOT, CHAT = TG.split(":", 1)


def tg_send(msg):
    url = f"https://api.telegram.org/bot{BOT}/sendMessage"
    requests.post(url, data={"chat_id": CHAT, "text": msg})


def run():
    result = ""

    try:
        print("启动 UDC...")
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options)

        print("打开登录页...")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(5)

        print("输入账号密码...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)

        print("勾选协议...")
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        print("点击真正的登录按钮...")
        # ⭐ 匹配你截图里的真实按钮结构
        login_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'登录') and @role='button']"))
        )
        login_btn.click()

        print("等待登录完成...")
        time.sleep(10)

        print("进入首页...")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(6)

        print("点击赚盒饭...")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'赚盒饭')]"))
        ).click()

        time.sleep(3)

        print("查找每日奖励按钮...")
        daily = driver.find_elements(By.XPATH, "//*[contains(text(),'每日免费奖励')]")

        if daily:
            daily[0].click()
            result = "🎉 签到成功 +300"
        else:
            result = "✔ 今天已经领过或按钮未出现"

        driver.quit()

    except Exception as e:
        result = "❌ 失败：" + str(e)

    print(result)
    tg_send(result)


if __name__ == "__main__":
    run()
