#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سرور وب - پنل مدیریت
"""
import json
import os
from flask import Flask, jsonify, send_from_directory, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    """صفحه منوی اصلی"""
    try:
        return send_from_directory('.', 'index.html')
    except:
        return "<h1>❌ Index HTML not found</h1>", 404

@app.route('/dashboard')
def dashboard():
    """صفحه داشبورد"""
    try:
        return send_from_directory('.', 'dashboard.html')
    except:
        return "<h1>❌ Dashboard HTML not found</h1>", 404

@app.route('/config')
def config_page():
    """صفحه کانفیگ"""
    try:
        return send_from_directory('.', 'config_page.html')
    except:
        return "<h1>❌ Config Page HTML not found</h1>", 404

@app.route('/settings-panel')
def settings_panel():
    """صفحه تنظیمات"""
    try:
        return send_from_directory('.', 'settings_panel.html')
    except:
        return "<h1>❌ Settings Panel HTML not found</h1>", 404

@app.route('/save', methods=['POST'])
def save_config():
    """ذخیره کانفیگ جدید"""
    try:
        data = request.form.get('config')
        name = request.form.get('name') or None
        if not data:
            return jsonify({'ok': False, 'error': 'Empty config'}), 400

        entry = {
            'config': data,
            'name': name,
            'time': datetime.now().strftime('%Y/%m/%d %H:%M')
        }
        
        CONFIG_FILE = 'configs.json'
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfgs = json.load(f)
        
        cfgs.append(entry)
        if len(cfgs) > 200:
            cfgs = cfgs[-200:]
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfgs, f, ensure_ascii=False, indent=2)
        
        return jsonify({'ok': True, 'saved': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/list', methods=['GET'])
def list_configs():
    """دریافت لیست کانفیگ‌ها"""
    try:
        CONFIG_FILE = 'configs.json'
        if not os.path.exists(CONFIG_FILE):
            return jsonify([])
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfgs = json.load(f)
        return jsonify(cfgs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/random', methods=['GET'])
def random_configs():
    """دریافت کانفیگ‌های رندوم"""
    import random
    n = int(request.args.get('n', 10))
    try:
        CONFIG_FILE = 'configs.json'
        if not os.path.exists(CONFIG_FILE):
            return jsonify([])
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfgs = json.load(f)
        if not cfgs:
            return jsonify([])
        pool = cfgs[-100:]
        picks = random.sample(pool, min(n, len(pool)))
        return jsonify(picks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard-data', methods=['GET'])
def dashboard_data():
    """داده‌های داشبورد"""
    result = {
        'stats': {
            'total_users': 0,
            'total_configs': 0,
            'total_feedback': 0,
            'last_update': '-'
        },
        'prices': [],
        'users': [],
        'feedbacks': []
    }
    
    try:
        # قیمت‌ها
        PRICES_CACHE = 'prices_cache.json'
        if os.path.exists(PRICES_CACHE):
            try:
                with open(PRICES_CACHE, 'r', encoding='utf-8') as f:
                    prices = json.load(f)
                result['prices'] = prices
                if prices:
                    result['stats']['last_update'] = prices[0].get('time', '-')
            except:
                pass
        
        # کاربران
        USERS_FILE = 'users.json'
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    users = json.load(f)
                result['stats']['total_users'] = len(users) if isinstance(users, list) else 0
            except:
                pass
        
        # کانفیگ‌ها
        CONFIG_FILE = 'configs.json'
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    cfgs = json.load(f)
                result['stats']['total_configs'] = len(cfgs) if isinstance(cfgs, list) else 0
            except:
                pass
        
        # فیدبک‌ها
        FEEDBACK_FILE = 'feedback.json'
        if os.path.exists(FEEDBACK_FILE):
            try:
                with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                    feedbacks = json.load(f)
                result['stats']['total_feedback'] = len(feedbacks) if isinstance(feedbacks, list) else 0
            except:
                pass
        
        return jsonify(result)
    except Exception as e:
        return jsonify(result)

@app.route('/settings', methods=['GET', 'POST'])
def settings_api():
    """تنظیمات"""
    try:
        if request.method == 'GET':
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                return jsonify(settings)
            return jsonify({
                'config_enabled': True,
                'web_page_enabled': True,
                'prices_enabled': True,
                'feedback_enabled': True,
                'channel_check_enabled': True,
                'refresh_interval': 1800,
                'channel_name': '@rmanrajaei'
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return jsonify({'ok': True, 'message': 'تنظیمات ذخیره شدند'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 سرور وب شروع شد")
    print("=" * 70)
    print("📍 منو اصلی:      http://127.0.0.1:8080")
    print("📍 داشبورد:       http://127.0.0.1:8080/dashboard")
    print("📍 مدیریت کانفیگ:  http://127.0.0.1:8080/config")
    print("📍 تنظیمات:       http://127.0.0.1:8080/settings-panel")
    print("=" * 70)
    print("⏹️  برای توقف، Ctrl+C را فشار دهید\n")
    
    app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False)
