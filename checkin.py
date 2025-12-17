import os
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


EMAIL = os.getenv("OIIOII_EMAIL")
PASSWORD = os.getenv("OIIOII_PASSWORD")
TG_BOT = os.getenv("TG_BOT_TOKEN")
TG_CHAT = os.getenv("TG_CHAT_ID")


def tg_send(msg):
    """发送 TG HTML 消息"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT}/sendMessage",
            data={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}
        )
    except:
        pass


def js_click(driver, element):
    """使用 JavaScript 强制点击（无视遮挡、动画、布局）"""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(1)


def run():
    safe_email = EMAIL[:3] + "***@" + EMAIL.split("@")[1]
    msg = ""

    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")

        driver = uc.Chrome(options=options)

        print("打开登录页…")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(3)

        print("输入账号密码…")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        # 点击登录
        driver.find_element(By.XPATH, "//form//button[@type='submit']").click()
        time.sleep(5)

        driver.get("https://www.oiioii.ai/home")
        time.sleep(3)

        # 登录成功检查
        print("检查是否登录成功…")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'_avatar')]"))
            )
            print("登录成功！")
        except:
            raise Exception("登录失败：未检测到头像元素")

        # 点击赚盒饭（JS click）
        print("点击赚盒饭…")
        earn_xpath = "//div[contains(text(),'赚盒饭')]/ancestor::button"
        earn_btn = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, earn_xpath))
        )
        js_click(driver, earn_btn)

        time.sleep(2)

        # 检查是否已签到
        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'明天见')]")
            msg = (
                "🏆 <b>OiiOii 自动签到</b>\n\n"
                f"账号：<code>{safe_email}</code>\n"
                f"✔ 今日已签到。\n"
            )
            driver.quit()
            tg_send(msg)
            print(msg)
            return
        except:
            pass

        # 点击 +300（JS click）
        print("点击 +300…")
        claim_xpath = "//span[contains(text(),'+ 300')]/ancestor::button"
        claim_btn = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, claim_xpath))
        )
        js_click(driver, claim_btn)

        time.sleep(3)

        msg = (
            "🏆 <b>OiiOii 自动签到成功</b>\n\n"
            f"账号：<code>{safe_email}</code>\n"
            "🎁 今日奖励：<b>+300</b>\n"
        )

        driver.quit()

    except Exception as e:
        msg = f"❌ <b>签到失败</b>\n原因：<code>{str(e)}</code>"

    print(msg)
    tg_send(msg)


if __name__ == "__main__":
    run()
