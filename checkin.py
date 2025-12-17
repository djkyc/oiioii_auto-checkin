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
    time.sleep(0.8)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(0.8)


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
        opt.add_argument("--headless=chrome")  

        opt.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        driver = uc.Chrome(options=opt)
        wait = WebDriverWait(driver, 25)

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

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(3)

        print("=== BODY CHECK START ===")
        body_text = driver.execute_script("return document.body.innerText")
        print(body_text[:1000])_
