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
    """滚动 + 强制 JS 点击"""
    el = WebDriverWait(driver, 12).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", el)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", el)


def run():
    driver = None
    msg = ""

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

        print("填写账号密码...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
        ).send_keys(EMAIL)

        driver.find_element(By.XPATH, "//input[@type='password']").send_keys(PASSWORD)

        driver.find_element(By.XPATH, "//input[@type='checkbox']").click()

        print("点击登录按钮（type=submit）...")
        js_click(driver, "//form//button[@type='submit']")

        print("等待跳转到首页...")
        time.sleep(10)

        driver.get("https://www.oiioii.ai/home")
        time.sleep(6)

        print("点击『赚盒饭』按钮（第一层，下拉右上角按钮）...")
        # 根据你提供的截图精准锁定按钮
        credit_btn_xpath = "(//div[contains(@class,'credit-btn-text') and contains(text(),'赚盒饭')])[1]/parent::button"
        js_click(driver, credit_btn_xpath)

        print("等待奖励面板弹出...")
        time.sleep(2)

        print("点击『每日免费奖励 +300』按钮（第二层）...")
        reward_btn_xpath = "(//button[contains(@class,'credit-claim-btn')]//span[contains(text(),'+300')])[1]"
        js_click(driver, reward_btn_xpath)

        msg = "🎉 成功领取今日 +300 盒饭币"

        driver.quit()

    except Exception as e:
        msg = f"❌ 失败：{e}"

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
