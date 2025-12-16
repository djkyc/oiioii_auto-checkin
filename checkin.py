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


def tg(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT}/sendMessage",
            data={"chat_id": CHAT, "text": msg}
        )
    except:
        pass


def wait_and_click(driver, xpath):
    el = WebDriverWait(driver, 15).until(
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
        time.sleep(5)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        print("点击提交登录按钮...")
        wait_and_click(driver, "//form//button[@type='submit']")
        time.sleep(8)

        print("进入首页...")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(6)

        print("点击『赚盒饭』按钮（使用新的精准 XPath）...")
        credit_xpath = "(//div[contains(@class,'credit-btn-text') and contains(text(),'赚盒饭')])[1]/parent::button"
        wait_and_click(driver, credit_xpath)

        print("等待浮层加载...")
        time.sleep(3)

        print("点击『每日免费奖励 +300』按钮...")
        reward_xpath = "(//span[contains(text(),'+300')])[1]"
        wait_and_click(driver, reward_xpath)

        msg = "🎉 签到成功 +300"

        driver.quit()

    except Exception as e:
        msg = f"❌ 失败：{e}"

    print(msg)
    tg(msg)


if __name__ == "__main__":
    run()
