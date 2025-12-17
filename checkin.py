import os, time, requests, undetected_chromedriver as uc
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


def js_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    time.sleep(0.6)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(0.6)


def get_balance(driver):
    """自动抓取余额数字（饭币）"""
    try:
        balance_el = driver.find_element(By.XPATH, "//*[@class='_credit-container_1nruh_1']")
        return balance_el.text.strip()
    except:
        return "未知"


def run():
    safe = EMAIL[:3] + "***@" + EMAIL.split("@")[1]

    try:
        # 浏览器配置
        opt = uc.ChromeOptions()
        opt.add_argument("--window-size=1920,1080")
        opt.add_argument("--no-sandbox")
        opt.add_argument("--disable-dev-shm-usage")
        opt.add_argument("--disable-gpu")
        opt.add_argument("--disable-web-security")
        opt.add_argument("--allow-running-insecure-content")
        opt.add_argument("--ignore-certificate-errors")
        opt.add_argument("--remote-allow-origins=*")
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_argument("--headless=chrome")  # 关键

        # 真实浏览器 UA
        opt.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        driver = uc.Chrome(options=opt)
        wait = WebDriverWait(driver, 25)

        # 去掉 webdriver 标识
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"}
        )

        print("打开登录页…")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(2)

        print("输入账号密码…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))).send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()
        driver.find_element(By.XPATH, "//form//button").click()
        time.sleep(4)

        print("进入首页…")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(3)

        # 等待页面渲染完成
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(2)

        print("检查是否登录成功…")
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'_avatar')]")))
        print("登录成功！")

        print("等待赚盒饭入口渲染…")
        xp = ("//button[contains(.,'Earn Bentos')] | "
              "//button[contains(.,'赚盒饭')] | "
              "//div[contains(text(),'Earn Bentos')] | "
              "//div[contains(text(),'赚盒饭')]")
        entry = wait.until(EC.presence_of_element_located((By.XPATH, xp)))

        print("点击赚盒饭入口…")
        js_click(driver, entry)
        time.sleep(2)

        # 判断今日是否已签到
        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'明天见')]")
            balance = get_balance(driver)
            msg = (
                f"🎉 <b>OiiOii 今日已签到</b>\n"
                f"👤 账号：<code>{safe}</code>\n"
                f"✔ 今日奖励已领取\n"
                f"💰 当前积分：<b>{balance}</b>\n"
            )
            print(msg)
            tg_send(msg)
            driver.quit()
            return
        except:
            pass

        print("寻找 +300 按钮…")
        claim_xps = [
            "//span[contains(text(),'+ 300')]/ancestor::button",
            "//button[contains(.,'+ 300')]",
            "//div[contains(text(),'+ 300')]/ancestor::button"
        ]

        claim = None
        for xp in claim_xps:
            try:
                claim = wait.until(EC.presence_of_element_located((By.XPATH, xp)))
                break
            except:
                pass

        print("点击 +300 强化模式…")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", claim)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", claim)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", claim)
        time.sleep(1.5)

        balance = get_balance(driver)
        msg = (
            f"🎉 <b>OiiOii 自动签到成功</b>\n"
            f"👤 账号：<code>{safe}</code>\n"
            f"🎁 今日奖励：<b>+300</b>\n"
            f"💰 当前积分：<b>{balance}</b>\n"
        )
        print(msg)
        tg_send(msg)
        driver.quit()

    except Exception as e:
        msg = (
            f"❌ <b>OiiOii 签到失败</b>\n"
            f"👤 账号：<code>{safe}</code>\n"
            f"⚠ 原因：<code>{e}</code>\n"
        )
        print(msg)
        tg_send(msg)


if __name__ == "__main__":
    run()
