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
    safe_email = EMAIL[:3] + "***@" + EMAIL.split("@")[1]

    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")

        d = uc.Chrome(options=options)
        w = WebDriverWait(d, 20)

        print("打开登录页…")
        d.get("https://www.oiioii.ai/login")
        time.sleep(3)

        print("输入账号密码…")
        w.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))).send_keys(EMAIL)
        d.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(PASSWORD)
        d.find_element(By.CSS_SELECTOR, "input[type=checkbox]").click()
        d.find_element(By.XPATH, "//form//button[@type='submit']").click()
        time.sleep(5)

        d.get("https://www.oiioii.ai/home")
        time.sleep(3)

        print("检查是否登录成功…")
        w.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'_avatar')]")))
        print("登录成功！")

        # 强制滚回顶部
        d.execute_script("window.scrollTo(0,0);")
        time.sleep(1)

        # 打印 headless 页面结构
        print("=== HEADLESS DOM START ===")
        print(d.page_source[:15000])
        print("=== HEADLESS DOM END ===")

        print("寻找入口按钮…")
        xps = [
            "//div[contains(text(),'赚盒饭')]/ancestor::button",
            "//button[contains(.,'赚盒饭')]",
            "//button[contains(@class,'_credit-btn') and .//div[contains(text(),'赚盒饭')]]",
            "//div[contains(text(),'赚盒饭')]/parent::*"
        ]

        earn = None
        for xp in xps:
            try:
                earn = w.until(EC.presence_of_element_located((By.XPATH, xp)))
                break
            except:
                pass

        if not earn:
            raise Exception("入口按钮未找到")

        print("点击入口按钮…")
        js_click(d, earn)

        time.sleep(2)

        # 已签到检查
        try:
            d.find_element(By.XPATH, "//*[contains(text(),'明天见')]")
            msg = f"🏆 已签到\n账号：{safe_email}"
            print(msg)
            tg_send(msg)
            d.quit()
            return
        except:
            pass

        print("寻找 +300 按钮…")
        claim = w.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'+ 300')]/ancestor::button")
            )
        )

        print("点击 +300…")
        js_click(d, claim)

        msg = f"🏆 签到成功 +300\n账号：{safe_email}"
        print(msg)
        tg_send(msg)
        d.quit()

    except Exception as e:
        msg = f"❌ 签到失败\n原因：{e}"
        print(msg)
        tg_send(msg)

if __name__ == "__main__":
    run()
