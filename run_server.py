#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import time
import webbrowser

print("🚀 درحال شروع Flask server...")
print("📍 http://127.0.0.1:8080")
print("⏹️  برای توقف، Ctrl+C را فشار دهید\n")

# شروع Flask server
proc = subprocess.Popen([sys.executable, 'test_server.py'])

# منتظر شروع server
time.sleep(2)

# باز کردن مرورگر
try:
    webbrowser.open('http://127.0.0.1:8080')
except:
    print("⚠️ نتوانست مرورگر را باز کند")

# انتظار تا server متوقف شود
proc.wait()
