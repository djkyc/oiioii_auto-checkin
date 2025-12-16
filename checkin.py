import time
import os
import random
import requests
from playwright.sync_api import sync_playwright

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

# 随机 UA 列表（真实 Chrome）
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def send_tg_message(text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)


def anti_detect(page):
    """注入反检测 JavaScript"""

    page.add_init_script("""
    // ----------------------------------
    // 1. 伪造 webdriver
    // ----------------------------------
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
    });

    // ----------------------------------
    // 2. 填充 plugins
    // ----------------------------------
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1,2,3,4],
    });

    // ----------------------------------
    // 3. languages
    // ----------------------------------
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh', 'en'],
    });

    // ----------------------------------
    // 4. 伪造权限
    // ----------------------------------
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters)
    );

    // ----------------------------------
    // 5. WebGL 指纹修补
    // ----------------------------------
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'NVIDIA';  // VENDOR
        if (parameter === 37446) return 'NVIDIA GeForce RTX'; // RENDERER
        return getParameter(parameter);
    };

    // ----------------------------------
    // 6. 鼠标移动事件补充（更像真人）
    // ----------------------------------
    document.addEventListener('mousemove', () => {});
    """)


def run():
    result_message = ""

    try:
        with sync_playwright() as p:
            # 真实浏览器模拟
            user_agent = random.choice(USER_AGENTS)

            browser = p.chromium.launch(
                headless=False,   # ❗ 反检测：必须关闭 headless（会自动模拟 GUI）
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--lang=zh-CN,zh,en",
                ]
            )

            context = browser.new_context(
                user_agent=user_agent,
                locale="zh-CN",
                screen={"width": 1366, "height": 768},
                viewport={"width": 1366, "height": 768},
            )

            page = context.new_page()
            anti_detect(page)

            page.goto("https://www.oiioii.ai/home", timeout=60000)

            time.sleep(random.uniform(2, 4))

            # 判断是否登录
            if "登录" in page.content():
                page.click("text=登录")
                time.sleep(2)
                page.fill("input[type=email]", EMAIL)
                time.sleep(1)
                page.fill("input[type=password]", PASSWORD)
                time.sleep(1)
                page.keyboard.press("Enter")
                time.sleep(random.uniform(5, 7))

            # 打开赚盒饭面板
            page.click("div.cursor-pointer")
            time.sleep(random.uniform(2, 3))

            # 查找按钮
            btn = page.locator("button:has-text('每日免费奖励')")
            if btn.count() > 0:
                btn.click()
                result_message = "🎉 已成功领取 +300 盒饭币"
            else:
                result_message = "✔ 今日已领取"

            browser.close()

    except Exception as e:
        result_message = f"❌ 签到失败：{e}"

    # Telegram 推送
    send_tg_message(result_message)


if __name__ == "__main__":
    run()
