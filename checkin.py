import os
import requests
import json

TOKEN = os.getenv("OIIOII_TOKEN")  # Secret 中存 access_token
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


def send_tg(msg):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": TG_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
        })
        print("TG 推送成功")
    except Exception as e:
        print("TG 推送失败:", e)


def run():
    result = "❌ 未知错误"

    try:
        url = "https://api.hogi.ai/points/free/daily"
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        }

        print("发送签到请求...")
        r = requests.post(url, headers=headers)

        print("状态码:", r.status_code)
        print("响应:", r.text)

        if r.status_code == 200:
            data = r.json()
            if data.get("success", False):
                result = "🎉 今日签到成功！+300 盒饭币"
            else:
                result = f"⚠️ 无法重复签到：{data}"
        else:
            result = f"❌ 请求失败：{r.status_code} - {r.text}"

    except Exception as e:
        result = f"❌ 运行报错：{e}"

    print(result)
    send_tg(result)


if __name__ == "__main__":
    run()
