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


def js_click(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.4)
    driver.execute_script("arguments[0].click();", el)
    time.sleep(0.4)


def get_balance(driver):
    """v14：只提取 transform:none 的数字，得到真实余额"""
    try:
        container = driver.find_element(
            By.XPATH, "//*[contains(@class,'_counter-container')]"
        )
        digits = container.find_elements(By.CSS_SELECTOR, "div._counter-digit_cml2k_12")

        result = ""
        for d in digits:
            spans = d.find_elements(By.CSS_SELECTOR, "span._counter-number_cml2k_18")
            for s in spans:
                style = s.get_attribute("style") or ""
                if "none" in style:  # 当前真实数字
                    digit = s.text.strip()
                    if digit.isdigit():
                        result += digit
                    break
        return result if result else "未知"
    except:
        return "未知"


def send_success(safe, balance):
    log_msg = (
        f"🎉 OiiOii 自动签到成功\n"
        f"👤 账号：{safe}\n"
        f"🎁 今日奖励：+300\n"
        f"💰 当前积分：{balance}\n"
    )
    tg_msg = (
        f"🎉 <b>OiiOii 自动签到成功</b>\n"
        f"👤 账号：<code>{safe}</code>\n"
        f"🎁 今日奖励：<b>+300</b>\n"
        f"💰 当前积分：<b>{balance}</b>\n"
    )
    print(log_msg)
    tg_send(tg_msg)


def send_already(safe, balance):
    log_msg = (
        f"🎉 OiiOii 今日奖励已领取\n"
        f"👤 账号：{safe}\n"
        f"💰 当前积分：{balance}\n"
    )
    tg_msg = (
        f"🎉 <b>OiiOii 今日奖励已领取</b>\n"
        f"👤 账号：<code>{safe}</code>\n"
        f"💰 当前积分快：<b>{balance}</b>\n"
    )
    print(log_msg)
    tg_send(tg_msg)


def send_fail(safe, err):
    log_msg = (
        f"❌ OiiOii 签到失败\n"
        f"👤 账号：{safe}\n"
        f"⚠ 原因：{err}\n"
    )
    tg_msg = (
        f"❌ <b>OiiOii 签到失败</b>\n"
        f"👤 账号：<code>{safe}</code>\n"
        f"⚠ 原因：<code>{err}</code>\n"
    )
    print(log_msg)
    tg_send(tg_msg)


def run():
    safe = EMAIL[:3] + "***@" + EMAIL.split("@")[1]

    try:
        opt = uc.ChromeOptions()
        opt.add_argument("--window-size=1920,1080")
        opt.add_argument("--no-sandbox")
        opt.add_argument("--disable-dev-shm-usage")
        opt.add_argument("--disable-gpu")
        opt.add_argument("--disable-web-security")
        opt.add_argument("--ignore-certificate-errors")
        opt.add_argument("--remote-allow-origins=*")
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_argument("--headless=chrome")
        opt.add_argument("user-agent=Mozilla/5.0")

        driver = uc.Chrome(options=opt)
        wait = WebDriverWait(driver, 20)

        # 去除 webdriver 特征
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator,'webdriver',{get:()=>undefined});
                """
            }
        )

        print("打开登录页…")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(2)

        print("输入账号密码…")
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()
        driver.find_element(By.XPATH, "//form//button").click()
        time.sleep(4)

        print("进入首页…")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(2)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1)

        print("检查是否登录成功…")
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'_avatar')]")))
        print("登录成功！")

        print("进入赚盒饭入口…")
        xp_entry = (
            "//button[contains(.,'Earn Bentos')] | "
            "//button[contains(.,'赚盒饭')] | "
            "//div[contains(text(),'Earn Bentos')] | "
            "//div[contains(text(),'赚盒饭')]"
        )
        entry = wait.until(EC.presence_of_element_located((By.XPATH, xp_entry)))
        js_click(driver, entry)
        time.sleep(2)

        # =================== 核心签到判断 ===================
        print("检查签到状态…")

        # 试找 +300 按钮
        claim_btn = None
        for xp in [
            "//span[contains(text(),'+ 300')]/ancestor::button",
            "//button[contains(.,'+ 300')]"
        ]:
            try:
                claim_btn = driver.find_element(By.XPATH, xp)
                break
            except:
                pass

        # 情况 A：没有 +300 → 今日已领取
        if not claim_btn:
            balance = get_balance(driver)
            send_already(safe, balance)
            driver.quit()
            return

        # 情况 B：点击后出现“已领取”提示 → 今日已领取
        print("点击 +300…")
        js_click(driver, claim_btn)
        time.sleep(1)

        toast = driver.execute_script("return document.body.innerText;")

        if ("已领取" in toast) or ("Already" in toast):
            balance = get_balance(driver)
            send_already(safe, balance)
            driver.quit()
            return

        # 情况 C：成功领取
        balance = get_balance(driver)
        send_success(safe, balance)
        driver.quit()

    except Exception as e:
        send_fail(safe, e)


if __name__ == "__main__":
    run()
