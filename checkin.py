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
    """精准提取饭币余额"""
    try:
        el = driver.find_element(By.XPATH, "//*[contains(@class,'_counter-container')]")
        nums = "".join([c for c in el.text if c.isdigit()])
        return nums if nums else "未知"
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
            {"source":"Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"}
        )

        print("打开登录页…")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(2)

        print("输入账号密码…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input[type=email]"))).send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR,"input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR,"input[type=checkbox]").click()
        driver.find_element(By.XPATH,"//form//button").click()
        time.sleep(4)

        print("进入首页…")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(2)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1)

        print("检查是否登录成功…")
        wait.until(EC.presence_of_element_located((By.XPATH,"//*[contains(@class,'_avatar')]")))
        print("登录成功！")

        # 打开入口
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

        # =============== 关键判断区 ===============
        print("检查签到状态…")

        # 查找 +300 按钮
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

        # 情况 A：+300 不存在 → 今日已领取
        if not claim_btn:
            balance = get_balance(driver)
            msg = (
                f"🎉 <b>OiiOii 今日奖励已领取</b>\n"
                f"👤 账号：<code>{safe}</code>\n"
                f"💰 当前积分：<b>{balance}</b>\n"
            )
            print(msg); tg_send(msg); driver.quit(); return

        # 情况 B：存在 +300 → 点击看看是不是提示“已领取”
        print("点击 +300…")
        js_click(driver, claim_btn)
        time.sleep(1)

        toast = driver.execute_script("return document.body.innerText;")

        # 若提示已领取过
        if ("已领取" in toast) or ("Already" in toast):
            balance = get_balance(driver)
            msg = (
                f"🎉 <b>OiiOii 今日奖励已领取</b>\n"
                f"👤 账号：<code>{safe}</code>\n"
                f"💰 当前积分：<b>{balance}</b>\n"
            )
            print(msg); tg_send(msg); driver.quit(); return

        # 情况 C：真正成功签到
        balance = get_balance(driver)
        msg = (
            f"🎉 <b>OiiOii 自动签到成功</b>\n"
            f"👤 账号：<code>{safe}</code>\n"
            f"🎁 今日奖励：<b>+300</b>\n"
            f"💰 当前积分：<b>{balance}</b>\n"
        )
        print(msg); tg_send(msg); driver.quit()

    except Exception as e:
        msg = (
            f"❌ <b>OiiOii 签到失败</b>\n"
            f"👤 账号：<code>{safe}</code>\n"
            f"⚠ 原因：<code>{e}</code>\n"
        )
        print(msg); tg_send(msg)


if __name__ == "__main__":
    run()
