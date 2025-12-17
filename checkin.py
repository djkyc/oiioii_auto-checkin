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
    time.sleep(1)


def run():
    safe = EMAIL[:3] + "***@" + EMAIL.split("@")[1]

    try:
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

        # ⭐ 关键：不要用 headless=new，而是 headless=chrome（更兼容 React）
        opt.add_argument("--headless=chrome")

        # ⭐ 模拟真实浏览器（非常关键）
        opt.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        driver = uc.Chrome(options=opt)
        wait = WebDriverWait(driver, 25)

        # 🔥 隐藏 webdriver 指纹（极关键）
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                """
            }
        )

        print("打开登录页…")
        driver.get("https://www.oiioii.ai/login")
        time.sleep(3)

        print("输入账号密码…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))).send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()

        driver.find_element(By.XPATH, "//form//button[@type='submit']").click()
        time.sleep(5)

        print("进入首页…")
        driver.get("https://www.oiioii.ai/home")
        time.sleep(4)

        # ⭐ 等待 React/Vite 页面完全加载
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(3)

        # 打印页面文本，确认是否成功渲染
        body_text = driver.execute_script("return document.body.innerText")
        print("=== BODY CHECK START ===")
        print(body_text[:2000])  # 前2000字符
        print("=== BODY CHECK END ===")

        print("检查是否登录成功…")
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'_avatar')]")))
        print("登录成功！")

        print("等待赚盒饭入口渲染…")
        xp = "//button[contains(.,'Earn Bentos')] | //button[contains(.,'赚盒饭')] | //div[contains(text(),'Earn Bentos')] | //div[contains(text(),'赚盒饭')]"
        entry = wait.until(EC.presence_of_element_located((By.XPATH, xp)))

        print("点击赚盒饭入口…")
        js_click(driver, entry)
        time.sleep(2)

        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'明天见')]")
            msg = f"🏆 已签到\n账号：{safe}"
            print(msg)
            tg_send(msg)
            driver.quit()
            return
        except:
            pass

        print("点击 +300…")
        claim = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'+ 300')]/ancestor::button")
            )
        )
        js_click(driver, claim)

        msg = f"🏆 签到成功 +300\n账号：{safe}"
        print(msg)
        tg_send(msg)
        driver.quit()

    except Exception as e:
        msg = f"❌ 签到失败\n原因：{e}"
        print(msg)
        tg_send(msg)


if __name__ == "__main__":
    run()
