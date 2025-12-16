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
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT}/sendMessage",
            data={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}
        )
    except:
        pass


def click_at(driver, x, y):
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()
    actions.move_by_offset(-x, -y).perform()


def run():
    msg = ""
    safe_email = EMAIL[:3] + "***@" + EMAIL.split("@")[1]

    try:
        # 启动浏览器
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options)

        driver.get("https://www.oiioii.ai/login")
        time.sleep(6)

        # 填登录信息
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        # 登录
        login_btn = driver.find_element(By.XPATH, "//form//button[@type='submit']")
        login_btn.click()
        time.sleep(10)

        # 进入首页
        driver.get("https://www.oiioii.ai/home")
        time.sleep(6)

        # 点“赚盒饭”
        click_at(driver, 1180, 95)
        time.sleep(3)

        # 判断是否已经领取（检查 "明天见"）
        try:
            driver.find_element(By.XPATH, "//span[contains(text(),'明天见')]")
            # 如果找到了，说明今天已经领过
            msg = (
                "🏆 <b>OiiOii 自动签到通知</b>\n\n"
                f"👤 账号：<code>{safe_email}</code>\n"
                "✔ 今日已领取，无需重复签到。\n"
                "📌 <a href=\"https://www.oiioii.ai/\">官网链接</a>"
            )
            driver.quit()
            tg_send(msg)
            print(msg)
            return
        except:
            pass  # 没找到“明天见”，继续点击 +300

        # 点击 +300 领取奖励按钮
        click_at(driver, 1110, 360)
        time.sleep(2)

        msg = (
            "🏆 <b>OiiOii 自动签到成功</b>\n\n"
            f"👤 账号：<code>{safe_email}</code>\n"
            "🎁 今日奖励到账：<b>+300</b>\n\n"
            "🔗 https://www.oiioii.ai/---OiiOii 官网"
        )

        driver.quit()

    except Exception as e:
        msg = (
            "❌ <b>签到失败</b>\n\n"
            f"原因：<code>{e}</code>\n"
            f"👤 账号：{safe_email}"
        )

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
