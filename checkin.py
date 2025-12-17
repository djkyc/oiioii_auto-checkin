import os
import time
import requests
import base64
import undetected_chromedriver as uc
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


def js_click(driver, el):
    """JavaScript 强制点击（无视遮挡+动画+位置偏移）"""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.6)
    driver.execute_script("arguments[0].click();", el)
    time.sleep(1)


def run():
    safe_email = EMAIL[:3] + "***@" + EMAIL.split("@")[1]

    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")

        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 20)

        print("打开登录页…")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(3)

        print("输入账号密码…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))).send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        # 登录
        driver.find_element(By.XPATH, "//form//button[@type='submit']").click()
        time.sleep(6)

        driver.get("https://www.oiioii.ai/home")
        time.sle
