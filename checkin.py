import os
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TG = os.getenv("TG")   # 你的 tg_bot_token:chat_id

BOT_TOKEN, CHAT_ID = TG.split(":", 1)


def tg(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": msg})


def run():
    try:
        opts = uc.ChromeOptions()
        opts.add_argument("--window-size=1400,900")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=opts)

        driver.get("https://www.oiioii.ai/login")
        time.sleep(5)

        driver.find_element(By.CSS_SELECTOR, "input[type=email]").send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()
        driver.find_element(By.XPATH, "//button/div[contains(text(),'登录')]").click()

        time.sleep(10)
        driver.get("https://www.oiioii.ai/home")
        time.sleep(6)

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'赚盒饭')]"))
        ).click()

        time.sleep(3)

        reward = driver.find_elements(By.XPATH, "//*[contains(text(),'每日免费奖励')]")
        if reward:
            reward[0].click()
            msg = "🎉 签到成功 +300"
        else:
            msg = "✔ 今天已经领过了"

        driver.quit()

    except Exception as e:
        msg = f"❌ 失败：{e}"

    tg(msg)
    print(msg)


if __name__ == "__main__":
    run()
