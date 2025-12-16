import os
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
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


def click_at(driver, x, y):
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()
    actions.move_by_offset(-x, -y).perform()  # 复位坐标


def run():
    msg = ""

    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        print("启动 UDC...")
        driver = uc.Chrome(options=options)

        print("打开登录页...")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(6)

        print("输入账号密码...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        print("点击登录按钮...")
        submit_btn = driver.find_element(By.XPATH, "//form//button[@type='submit']")
        submit_btn.click()
        time.sleep(8)

        print("进入首页...")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(6)

        print("点击『赚盒饭』按钮（坐标点击）...")
        click_at(driver, 1180, 95)   # ← 第一层按钮位置
        time.sleep(3)

        print("点击『+300 奖励』按钮（坐标点击）...")
        click_at(driver, 1110, 360)  # ← 第二层奖励按钮位置

        msg = "🎉 自动签到成功！（坐标点击版）"

        driver.quit()

    except Exception as e:
        msg = f"❌ 自动签到失败：{e}"

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
