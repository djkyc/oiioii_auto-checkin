import os
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EMAIL = os.getenv("OIIOII_EMAIL")
PASSWORD = os.getenv("OIIOII_PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


def send_tg(msg):
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": TG_CHAT_ID,
            "text": msg
        })
    except Exception:
        pass



def run():
    result = ""

    try:
        print("启动 undetected-chromedriver 浏览器...")
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1400,900")

        driver = uc.Chrome(options=options)

        print("打开登录页...")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(5)

        print("输入邮箱...")
        email_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        )
        email_box.send_keys(EMAIL)

        print("输入密码...")
        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)

        print("勾选协议...")
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        print("点击登录按钮...")
        login_btn = driver.find_element(By.XPATH, "//button/div[contains(text(),'登录')]")
        login_btn.click()

        print("等待登录完成...")
        time.sleep(10)

        print("进入首页...")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(6)

        print("打开赚盒饭...")
        earn_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'赚盒饭')]"))
        )
        earn_btn.click()
        time.sleep(3)

        print("寻找每日免费奖励按钮...")
        reward_btn = driver.find_elements(By.XPATH, "//*[contains(text(),'每日免费奖励')]")

        if reward_btn:
            reward_btn[0].click()
            result = "🎉 今日成功领取 +300 盒饭币"
        else:
            result = "✔ 今日已经领取或没有奖励按钮"

        driver.quit()

    except Exception as e:
        result = f"❌ 签到失败：{e}"
        print(result)

    send_tg(result)
    print(result)


if __name__ == "__main__":
    run()
