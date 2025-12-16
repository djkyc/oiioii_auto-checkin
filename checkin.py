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


def tg_send(msg):
    """向 Telegram 推送文本消息"""
    try:
        url = f"https://api.telegram.org/bot{TG_BOT}/sendMessage"
        requests.post(url, data={"chat_id": TG_CHAT, "text": msg})
        print("TG 推送成功")
    except Exception as e:
        print("TG 推送失败：", e)


def click_at(driver, x, y):
    """在固定坐标点击（绝对稳定）"""
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()
    actions.move_by_offset(-x, -y).perform()  # 复位鼠标


def run():
    msg = ""

    try:
        print("启动 UDC…")
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options)

        print("打开登录页…")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(6)

        print("输入邮箱密码…")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)

        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        print("点击登录按钮…")
        login_btn = driver.find_element(By.XPATH, "//form//button[@type='submit']")
        login_btn.click()
        time.sleep(10)

        print("进入首页…")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(6)

        print("点击『赚盒饭』按钮（坐标点击）…")
        click_at(driver, 1180, 95)    # 根据你的截图固定坐标
        time.sleep(3)

        print("点击『+300』按钮（坐标点击）…")
        click_at(driver, 1110, 360)   # 弹窗内的 +300 按钮坐标

        msg = "🎉 自动签到成功 +300（坐标点击版）"

        driver.quit()

    except Exception as e:
        msg = f"❌ 自动签到失败：{e}"

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
