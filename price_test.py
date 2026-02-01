import requests
import json
import datetime
import os

API_KEY = "BXKcHwEDHznGNfYx4gLksS6wiLGqZwXe"
API_URL = f"https://BrsApi.ir/Api/Market/Gold_Currency.php?key={API_KEY}"
CACHE_FILE = "prices_cache.json"
HTML_FILE = "prices.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

# فقط این نمادها نمایش داده شوند
FILTER_SYMBOLS = ["USD", "IR_GOLD_18K", "IR_COIN_EMAMI"]

def fetch_data():
    """دریافت داده‌ها از API"""
    try:
        print("⏳ دریافت داده‌ها از API...")
        response = requests.get(API_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ داده‌ها از API دریافت و در کش ذخیره شدند")
        return data
    except Exception as e:
        print("⚠️ خطا در دریافت داده‌ها از API:", e)
        if os.path.exists(CACHE_FILE):
            print("⏳ استفاده از داده‌های کش...")
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

def generate_html(data):
    """ایجاد جدول HTML برای نمایش قیمت‌ها"""
    now = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M")
    
    rows = ""
    for category, items in data.items():
        for item in items:
            symbol = item.get("symbol")
            if symbol not in FILTER_SYMBOLS:
                continue

            name = item.get("name", "نامشخص")
            price = item.get("price", "پیدا نشد")
            change_value = item.get("change_value", 0)
            change_percent = item.get("change_percent", 0)
            unit = item.get("unit", "")

            # رنگ سبز برای مثبت و قرمز برای منفی
            color = "green" if change_value >= 0 else "red"
            change_str = f"<span style='color:{color}'>{change_value} ({change_percent}%)</span>"

            rows += f"<tr><td>{name}</td><td>{price} {unit}</td><td>{change_str}</td></tr>\n"

    if not rows:
        rows = "<tr><td colspan='3'>داده‌ای موجود نیست</td></tr>"

    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>قیمت لحظه‌ای طلا و ارز</title>
        <style>
            body {{ font-family: Tahoma, sans-serif; background: #f4f4f4; }}
            h1 {{ text-align:center; color:#333; }}
            table {{ margin: 20px auto; border-collapse: collapse; width: 60%; background: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            th, td {{ border: 1px solid #ccc; padding: 10px; text-align: center; }}
            th {{ background: #333; color: #fff; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>💰 قیمت لحظه‌ای طلا و ارز</h1>
        <table>
            <tr>
                <th>نماد</th>
                <th>قیمت</th>
                <th>تغییر</th>
            </tr>
            {rows}
        </table>
        <p style="text-align:center;">⏰ زمان دریافت: {now}</p>
    </body>
    </html>
    """

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ فایل HTML ساخته شد: {HTML_FILE}")

def main():
    data = fetch_data()
    generate_html(data)

if __name__ == "__main__":
    main()
