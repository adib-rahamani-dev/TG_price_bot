#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from flask import Flask, jsonify, send_from_directory
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    """صفحه اصلی"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/dashboard-data', methods=['GET'])
def dashboard_data():
    """تست endpoint"""
    result = {
        'stats': {
            'total_users': 2,
            'total_configs': 5,
            'total_feedback': 3,
            'last_update': '04:05:00'
        },
        'prices': [
            {'name': 'Apple', 'price': '$165.50', 'change_value': 2.50, 'change_percent': 1.5, 'time': '04:05:00'},
            {'name': 'Google', 'price': '$140.25', 'change_value': -3.75, 'change_percent': -2.6, 'time': '04:05:00'},
            {'name': 'Tesla', 'price': '$245.80', 'change_value': 5.20, 'change_percent': 2.1, 'time': '04:05:00'},
        ],
        'users': [
            {'user_id': 123456, 'username': 'user1', 'first_name': 'اسم'},
            {'user_id': 234567, 'username': 'user2', 'first_name': 'نام'},
        ],
        'feedbacks': [
            {'user_id': 123456, 'username': 'user1', 'text': 'ربات خوبی است', 'time': '2026-02-04 02:15:00'},
            {'user_id': 234567, 'username': 'user2', 'text': 'عالی و سریع', 'time': '2026-02-04 01:30:00'},
            {'user_id': 123456, 'username': 'user1', 'text': 'توصیه می‌کنم', 'time': '2026-02-04 00:45:00'},
        ]
    }
    return jsonify(result)

@app.route('/logs', methods=['GET'])
def get_logs():
    """دریافت لاگ‌های ربات"""
    logs = """2026-02-04 04:07:25 - INFO - 🔄 درحال دریافت داده‌ها از API...
2026-02-04 04:07:26 - INFO - ✅ داده‌ها ذخیره شد: 3 نماد
2026-02-04 04:07:30 - INFO - 👤 کاربر جدید ثبت شد: user1
2026-02-04 04:07:35 - INFO - ✅ کانفیگ ذخیره شد
2026-02-04 04:07:40 - INFO - 💬 فیدبک دریافت شد
2026-02-04 04:07:45 - INFO - 🔄 درحال دریافت داده‌ها از API...
2026-02-04 04:07:46 - INFO - ✅ داده‌ها ذخیره شد: 3 نماد"""
    return jsonify({'logs': logs})

@app.route('/channel-stats', methods=['GET'])
def channel_stats():
    """آمار کانال"""
    return jsonify({
        'status': 'warning',
        'channel_name': '@rmanrajaei',
        'message': '⚠️ برای دریافت اطلاعات کانال، ربات باید admin کانال باشد',
        'member_count': 0,
        'recent_joins': 0
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)
