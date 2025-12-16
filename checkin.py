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
        requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",
                      data={"chat_id": CHAT, "text": msg})
    except:
        pass


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
        time.sleep(5)

        print("输入邮箱密码...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)

        print("勾选协议...")
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        print("点击真正的提交按钮（submit）...")
        submit_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//form//button[@type='submit']"))
        )
        submit_btn.click()

        print("等待跳转...")
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
        reward_btn = driver.find_elements(By.XPATH, "//*[contains(text(),'每日免费奖励')]")

        if reward_btn:
            reward_btn[0].click()
            msg = "🎉 签到成功 +300"
        else:
            msg = "✔ 今日已领取"

        driver.quit()

    except Exception as e:
        msg = f"❌ 失败：{e}"

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
