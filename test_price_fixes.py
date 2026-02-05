#!/usr/bin/env python3
"""
تست کد برای بررسی قیمت‌های اصلاح‌شده
"""
import json
import os

# فایل‌های مورد استفاده
DATA_FILE = "prices_history.json"
MARKET_CACHE_FILE = "market_cache.json"
PRICES_CACHE_FILE = "prices_cache.json"
FILTER_SYMBOLS = ["USDT", "IR_GOLD_18K", "IR_COIN_EMAMI"]

def test_filter_symbols():
    """تست نمادهای فیلتر شده"""
    print("✅ نمادهای فیلتر شده:")
    for symbol in FILTER_SYMBOLS:
        print(f"  - {symbol}")
    print()

def test_cache_files():
    """بررسی فایل‌های کش"""
    print("📋 بررسی فایل‌های کش:")
    
    # بررسی prices_history.json
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
            if history and isinstance(history, list):
                latest = history[-1]
                print(f"✅ {DATA_FILE}: {len(latest)} نماد")
                for item in latest:
                    symbol = item.get('symbol', 'N/A')
                    name = item.get('name', 'N/A')
                    price = item.get('price', 'N/A')
                    unit = item.get('unit', 'N/A')
                    print(f"   - {symbol}: {name} = {price} {unit}")
    else:
        print(f"❌ {DATA_FILE} موجود نیست")
    
    print()
    
    # بررسی market_cache.json
    if os.path.exists(MARKET_CACHE_FILE):
        with open(MARKET_CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            total = 0
            matching = []
            if isinstance(cache, dict):
                for category, items in cache.items():
                    if isinstance(items, list):
                        total += len(items)
                        for item in items:
                            if item.get('symbol') in FILTER_SYMBOLS:
                                matching.append(item)
            print(f"✅ {MARKET_CACHE_FILE}: {total} کل، {len(matching)} مطابق")
            for item in matching:
                symbol = item.get('symbol', 'N/A')
                name = item.get('name', 'N/A')
                price = item.get('price', 'N/A')
                unit = item.get('unit', 'N/A')
                print(f"   - {symbol}: {name} = {price} {unit}")
    else:
        print(f"❌ {MARKET_CACHE_FILE} موجود نیست")
    
    print()

def test_message_format():
    """تست فرمت پیام"""
    print("💬 نمونه پیام:")
    
    sample_price = {
        'name': 'طلای 18 عیار',
        'price': 19483900,
        'change_value': -92300,
        'change_percent': -0.47,
        'time': '2026/02/04 14:14',
        'unit': 'تومان'
    }
    
    arrow = "🔺" if sample_price['change_value'] >= 0 else "🔻"
    unit = sample_price.get('unit', 'تومان')
    msg = f"<b>{sample_price['name']}:</b> {sample_price['price']} {unit} ({arrow} {sample_price['change_percent']}%)"
    print(msg)
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 تست اصلاحات قیمت‌ها")
    print("=" * 50)
    print()
    
    test_filter_symbols()
    test_cache_files()
    test_message_format()
    
    print("=" * 50)
    print("✅ تست تمام شد")
    print("=" * 50)
