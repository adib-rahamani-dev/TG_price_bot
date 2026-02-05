#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import datetime
import os

API_KEY = "BXKcHwEDHznGNfYx4gLksS6wiLGqZwXe"
API_URL = f"https://BrsApi.ir/Api/Market/Gold_Currency.php?key={API_KEY}"
FILTER_SYMBOLS = ["IR_GOLD_18K", "IR_COIN_EMAMI", "USDT"]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*"
}

def fetch_prices():
    """دریافت قیمت‌ها از API"""
    try:
        print("🔄 درحال دریافت داده‌ها از API...")
        response = requests.get(API_URL, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
        now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        
        filtered = []
        for category, items in data.items():
            for item in items:
                if item.get("symbol") in FILTER_SYMBOLS:
                    price_item = {
                        "symbol": item.get("symbol"),
                        "name": item.get("name"),
                        "price": item.get("price"),
                        "change_value": item.get("change_value"),
                        "change_percent": item.get("change_percent"),
                        "time": now,
                        "unit": item.get("unit", "تومان")
                    }
                    filtered.append(price_item)
                    print(f"  ✓ {item.get('symbol')}: {item.get('name')}")
                    print(f"    قیمت: {item.get('price')} {item.get('unit', 'تومان')}")
        
        if filtered:
            print(f"\n✅ موفقیت! {len(filtered)} نماد دریافت شد:\n")
            for item in filtered:
                unit_symbol = "دلار" if item['unit'] != "تومان" else "تومان"
                print(f"  {item['symbol']}: {item['name']}")
                print(f"    قیمت: {item['price']} {unit_symbol}")
                print(f"    تغییر: {item['change_value']} ({item['change_percent']}%)\n")
            
            # ذخیره به market_cache.json
            with open('market_cache.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ داده‌ها در market_cache.json ذخیره شدند")
            
            return filtered
        else:
            print("⚠️ هیچ نمادی پیدا نشد!")
            return []
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        return []

if __name__ == "__main__":
    prices = fetch_prices()
