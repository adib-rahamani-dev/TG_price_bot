@echo off
chcp 65001 > nul
cd /d "c:\Users\EXO\Desktop\TG_bot"
title Telegram Bot
.venv\Scripts\python.exe price_test.py
pause
