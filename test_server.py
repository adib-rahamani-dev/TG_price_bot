#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from flask import Flask, jsonify, send_from_directory, request

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# فایل‌های داده
DATA_FILES = {
    'users': os.path.join(BASE_DIR, 'users.json'),
    'configs': os.path.join(BASE_DIR, 'configs.json'),
    'feedbacks': os.path.join(BASE_DIR, 'feedback.json'),
    'prices': os.path.join(BASE_DIR, 'prices.json')
}

# ===== صفحات HTML =====
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'dashboard.html')

# ===== ابزار کمک برای خواندن فایل =====
def read_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def write_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===== API ها =====
@app.route('/dashboard-data', methods=['GET'])
def dashboard_data():
    users = read_json(DATA_FILES['users'])
    configs = read_json(DATA_FILES['configs'])
    feedbacks = read_json(DATA_FILES['feedbacks'])
    prices = read_json(DATA_FILES['prices'])

    result = {
        'stats': {
            'total_users': len(users),
            'total_configs': len(configs),
            'total_feedback': len(feedbacks),
            'last_update': 'درحال حاضر'
        },
        'prices': prices,
        'users': users,
        'feedbacks': feedbacks
    }
    return jsonify(result)

@app.route('/logs', methods=['GET'])
def get_logs():
    logs_file = os.path.join(BASE_DIR, 'logs.txt')
    if os.path.exists(logs_file):
        with open(logs_file, 'r', encoding='utf-8') as f:
            logs = f.read()
    else:
        logs = "هیچ لاگی ثبت نشده"
    return jsonify({'logs': logs})

@app.route('/channel-stats', methods=['GET'])
def channel_stats():
    return jsonify({
        'status': 'warning',
        'channel_name': '@rmanrajaei',
        'message': '⚠️ برای دریافت اطلاعات کانال، ربات باید admin کانال باشد',
        'member_count': 0,
        'recent_joins': 0
    })

# ===== تنظیمات =====
settings_file = os.path.join(BASE_DIR, 'settings.json')
if not os.path.exists(settings_file):
    default_settings = {
        'features': {
            'feedback_enabled': True,
            'config_enabled': True
        }
    }
    write_json(settings_file, default_settings)

@app.route('/settings', methods=['GET', 'POST'])
def settings_route():
    if request.method == 'POST':
        new_settings = request.get_json()
        write_json(settings_file, new_settings)
    return jsonify(read_json(settings_file))

# ===== اجرای سرور =====
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
