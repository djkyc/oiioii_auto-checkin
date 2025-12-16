import os
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TG = os.getenv("TG")
BOT, CHAT = TG.split(":", 1)


def tg_send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT}/sendMessage",
            data={"chat_id": CHAT, "text": msg}
        )
    except:
        pass


def js_click(driver, xpath):
    """强制点击（scroll + js click）"""
    el = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", el)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", el)


def run():
    msg = ""

    try:
        print("启动 UDC...")
        opts = uc.ChromeOptions()
        opts.add_argument("--window-size=1400,900")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=opts)

        print("打开登录页...")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(6)

        print("填写账号密码...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
        ).send_keys(EMAIL)

        driver.find_element(By.XPATH, "//input[@type='password']").send_keys(PASSWORD)

        driver.find_element(By.XPATH, "//input[@type='checkbox']").click()

        print("点击登录按钮...")
        js_click(driver, "//form//button[@type='submit']")
        time.sleep(8)

        print("进入首页...")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(6)

        print("点击赚盒饭按钮（最终稳定 XPath）...")
        # ← 这一条就是你 DOM 结构确认后的最精准定位
        js_click(driver, "(//button[contains(@class,'credit-btn')])[1]")

        print("等待奖励面板弹出...")
        time.sleep(2)

        print("点击『每日免费奖励 +300』按钮...")
        js_click(driver, "(//span[contains(text(),'+300')])[1]")

        msg = "🎉 签到成功 +300"

        driver.quit()

    except Exception as e:
        msg = f"❌ 失败：{e}"

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
