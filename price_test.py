import requests
import datetime
import json
import os
import time
import threading
import random
import logging
from io import StringIO
# Flask is imported lazily inside run_config_server to avoid import errors when not installed
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ------------------- تنظیمات Logging -------------------
LOG_FILE = "bot.log"
log_buffer = StringIO()

# تنظیم logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ------------------- تنظیمات -------------------
API_KEY = "BXKcHwEDHznGNfYx4gLksS6wiLGqZwXe"
API_URL = f"https://BrsApi.ir/Api/Market/Gold_Currency.php?key={API_KEY}"
FILTER_SYMBOLS = ["IR_GOLD_18K", "IR_COIN_EMAMI", "USD"]
MARKET_CACHE_FILE = "market_cache.json"

TELEGRAM_TOKEN = "8339623747:AAEiJZBwKwJW9HykBN_RerqKxzTMsdPuiG8"
DATA_FILE = "prices_history.json"
FEEDBACK_FILE = "feedback.json"
USERS_FILE = "users.json"
CONFIG_FILE = "configs.json"
PRICES_CACHE_FILE = "prices_cache.json"
ADMIN_USERNAMES = ["Rman_Rajae", "EP_ADR"]  # دو ادمین
REQUIRED_CHANNEL = "@rmanrajaei"  # کانال برای بررسی عضویت
ADMIN_VIEWED_FILE = "admin_viewed.json"  # فایل برای ذخیره آخرین فیدبک دیده‌شده
CONFIG_FILE = "configs.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*"
}

# ------------------- توابع JSON -------------------
def load_json(file_path):
    """خواندن فایل JSON با پشتیبانی از BOM"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"خطا در خواندن {file_path}: {e}")
        return []

# ------------------- دریافت داده -------------------
def fetch_data():
    """Fetch data from API. Returns a tuple (prices_list, from_cache_flag).
    If API succeeds, saves to DATA_FILE, market_cache.json and prices_cache.json, returns (filtered, False).
    If API fails, tries to return last entry from DATA_FILE or market_cache.json with from_cache=True.
    """
    try:
        logger.info("🔄 درحال دریافت داده‌ها از API...")
        response = requests.get(API_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")

        filtered = []
        for category, items in data.items():
            for item in items:
                if item.get("symbol") in FILTER_SYMBOLS:
                    filtered.append({
                        "symbol": item.get("symbol"),
                        "name": item.get("name"),
                        "price": item.get("price"),
                        "change_value": item.get("change_value"),
                        "change_percent": item.get("change_percent"),
                        "time": now,
                        "unit": item.get("unit", "تومان")
                    })

        if filtered:
            # ensure DATA_FILE exists
            if not os.path.exists(DATA_FILE):
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False)

            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except Exception:
                    history = []

            history.append(filtered)
            if len(history) > 48:
                history = history[-48:]

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            # Save full API response to market_cache.json
            try:
                with open(MARKET_CACHE_FILE, 'w', encoding='utf-8') as mf:
                    json.dump(data, mf, ensure_ascii=False, indent=2)
                logger.info(f"✅ بازگشت به {MARKET_CACHE_FILE}")
            except Exception as e:
                logger.warning(f"⚠️ خطا در نوشتن {MARKET_CACHE_FILE}: {e}")

            # also save filtered prices to prices cache for backward compatibility
            try:
                with open(PRICES_CACHE_FILE, 'w', encoding='utf-8') as cf:
                    json.dump(filtered, cf, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"⚠️ خطا در نوشتن {PRICES_CACHE_FILE}: {e}")

            logger.info(f"✅ داده‌ها با موفقیت ذخیره شد: {len(filtered)} نماد")
            return filtered, False

        logger.warning("⚠️ هیچ داده‌ای مطابق فیلتر پیدا نشد")
        return [], False

    except Exception as e:
        logger.error(f"⚠️ خطا در دریافت داده‌ها: {e}")
        logger.info("🔄 درحال استفاده از داده قبلی...")

        # first try DATA_FILE (prices_history.json)
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
                if history:
                    logger.info("✅ استفاده از آخرین داده ذخیره شده (prices_history.json)")
                    return history[-1], True
        except Exception as history_error:
            logger.warning(f"⚠️ خطا در خواندن prices_history.json: {history_error}")

        # fallback to market_cache.json
        try:
            if os.path.exists(MARKET_CACHE_FILE):
                with open(MARKET_CACHE_FILE, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                filtered = []
                for category, items in cache_data.items():
                    for item in items:
                        if item.get("symbol") in FILTER_SYMBOLS:
                            filtered.append({
                                "symbol": item.get("symbol"),
                                "name": item.get("name"),
                                "price": item.get("price"),
                                "change_value": item.get("change_value"),
                                "change_percent": item.get("change_percent"),
                                "time": item.get("time", f"{item.get('date')} {item.get('time')}"),
                                "unit": item.get("unit", "تومان")
                            })
                if filtered:
                    logger.info("✅ استفاده از داده کش (market_cache.json)")
                    return filtered, True
        except Exception as cache_error:
            logger.warning(f"⚠️ خطا در خواندن market_cache.json: {cache_error}")

        # fallback to prices_cache.json for backward compatibility
        try:
            if os.path.exists(PRICES_CACHE_FILE):
                with open(PRICES_CACHE_FILE, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                if isinstance(cache_data, list):
                    filtered = [item for item in cache_data if item.get("symbol") in FILTER_SYMBOLS]
                    if filtered:
                        logger.info("✅ استفاده از داده کش (prices_cache.json)")
                        return filtered, True
        except Exception as prices_error:
            logger.warning(f"⚠️ خطا در خواندن prices_cache.json: {prices_error}")

        logger.error("❌ هیچ داده‌ای موجود نیست!")
        return [], True

# ------------------- ذخیره کاربران -------------------
def save_user(user_id, username):
    try:
        # ایجاد فایل اگر وجود نداشت
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
        
        # خواندن کاربران موجود
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        
        # چک کردن که کاربر قبلاً ثبت شده یا خیر
        user_exists = any(user["user_id"] == user_id for user in users)
        
        if not user_exists:
            user_entry = {
                "user_id": user_id,
                "username": username if username else f"User_{user_id}",
                "join_date": datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
            }
            users.append(user_entry)
            
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ کاربر جدید ثبت شد: {username} ({user_id})")
    except Exception as e:
        logger.warning(f"⚠️ خطا در ذخیره کاربر: {e}")


# ------------------- Config web server -------------------
def run_config_server(host="0.0.0.0", port=8080):
    try:
        from flask import Flask, request, jsonify, send_from_directory
    except Exception:
        print("⚠️ Flask is not installed. Run 'pip install Flask' to enable the config web UI.")
        return

    app = Flask(__name__)

    @app.route('/')
    def index():
        return send_from_directory('.', 'dashboard.html')

    @app.route('/save', methods=['POST'])
    def save_config():
        data = request.form.get('config')
        name = request.form.get('name') or None
        if not data:
            return jsonify({'ok': False, 'error': 'Empty config'}), 400

        entry = {
            'config': data,
            'name': name,
            'time': datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
        }
        try:
            if not os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False)
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfgs = json.load(f)
        except Exception:
            cfgs = []

        cfgs.append(entry)
        # keep only last 200 configs to avoid huge file
        if len(cfgs) > 200:
            cfgs = cfgs[-200:]
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfgs, f, ensure_ascii=False, indent=2)

        return jsonify({'ok': True, 'saved': True})

    @app.route('/list', methods=['GET'])
    def list_configs():
        try:
            if not os.path.exists(CONFIG_FILE):
                return jsonify([])
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfgs = json.load(f)
            return jsonify(cfgs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/random', methods=['GET'])
    def random_configs():
        n = int(request.args.get('n', 10))
        try:
            if not os.path.exists(CONFIG_FILE):
                return jsonify([])
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfgs = json.load(f)
            if not cfgs:
                return jsonify([])
            # choose from last 100 entries to bias recent
            pool = cfgs[-100:]
            picks = random.sample(pool, min(n, len(pool)))
            return jsonify(picks)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/dashboard-data', methods=['GET'])
    def dashboard_data():
        """بازگرداندن اطلاعات داشبورد"""
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
            # خواندن اعضا
            if os.path.exists(USERS_FILE):
                try:
                    users = load_json(USERS_FILE)
                    if isinstance(users, list):
                        result['users'] = users[-5:][::-1]
                        result['stats']['total_users'] = len(users)
                except Exception as e:
                    logger.warning(f"خطا در خواندن کاربران: {e}")

            # خواندن کانفیگ‌ها
            if os.path.exists(CONFIG_FILE):
                try:
                    cfgs = load_json(CONFIG_FILE)
                    if isinstance(cfgs, list):
                        result['stats']['total_configs'] = len(cfgs)
                except Exception as e:
                    logger.warning(f"خطا در خواندن کانفیگ‌ها: {e}")

            # خواندن فیدبک‌ها
            if os.path.exists(FEEDBACK_FILE):
                try:
                    feedbacks_data = load_json(FEEDBACK_FILE)
                    if isinstance(feedbacks_data, list):
                        result['stats']['total_feedback'] = len(feedbacks_data)
                        result['feedbacks'] = feedbacks_data[-5:][::-1]
                except Exception as e:
                    logger.warning(f"خطا در خواندن فیدبک‌ها: {e}")

            # خواندن آخرین قیمت‌ها
            if os.path.exists(DATA_FILE):
                try:
                    history = load_json(DATA_FILE)
                    if isinstance(history, list) and len(history) > 0:
                        latest = history[-1]
                        if isinstance(latest, list):
                            for item in latest:
                                if isinstance(item, dict) and item.get('symbol') in FILTER_SYMBOLS:
                                    result['prices'].append({
                                        'name': item.get('name', ''),
                                        'price': item.get('price', ''),
                                        'change_value': item.get('change_value', 0),
                                        'change_percent': item.get('change_percent', 0),
                                        'time': item.get('time', '-'),
                                        'unit': item.get('unit', 'تومان')
                                    })
                        if result['prices']:
                            result['stats']['last_update'] = result['prices'][0].get('time', '-')
                except Exception as e:
                    logger.warning(f"خطا در خواندن قیمت‌ها: {e}")

            logger.info(f"Dashboard: {result['stats']['total_users']} users, {result['stats']['total_configs']} configs, {result['stats']['total_feedback']} feedbacks")
            return jsonify(result)

        except Exception as e:
            logger.error(f"خطا در endpoint dashboard-data: {e}", exc_info=True)
            return jsonify(result)

    @app.route('/settings', methods=['GET', 'POST'])
    def settings_api():
        """دریافت و به‌روزرسانی تنظیمات"""
        try:
            if request.method == 'GET':
                if os.path.exists('settings.json'):
                    with open('settings.json', 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    return jsonify(settings)
                return jsonify({'features': {}, 'channel_check_enabled': True})
            
            elif request.method == 'POST':
                data = request.get_json()
                with open('settings.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return jsonify({'ok': True, 'message': 'تنظیمات ذخیره شد'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/logs', methods=['GET'])
    def get_logs():
        """دریافت لاگ‌های ربات"""
        try:
            lines = request.args.get('lines', 50, type=int)
            if os.path.exists('bot.log'):
                with open('bot.log', 'r', encoding='utf-8') as f:
                    all_logs = f.readlines()
                    recent_logs = all_logs[-lines:]
                    return jsonify({'logs': ''.join(recent_logs)})
            return jsonify({'logs': 'هنوز لاگی ثبت نشده'})
        except Exception as e:
            logger.error(f"خطا در endpoint logs: {e}")
            return jsonify({'logs': f'خطا: {e}'})

    @app.route('/channel-stats', methods=['GET'])
    def channel_stats():
        """دریافت آمار کانال"""
        try:
            stats = {
                'channel_name': REQUIRED_CHANNEL,
                'message': 'برای دریافت تعداد دقیق اعضا، لطفاً ربات را admin کنید',
                'status': 'warning'
            }
            return jsonify(stats)
        except Exception as e:
            logger.error(f"خطا در دریافت آمار کانال: {e}")
            return jsonify({'error': str(e), 'status': 'error'}), 500

    app.run(host=host, port=port)

# ------------------- ساخت پیام -------------------
def build_message(prices, from_cache=False):
    if not prices:
        return "❌ داده‌ای موجود نیست"
    now = prices[0]["time"]
    cache_indicator = "📊 (کش‌شده)" if from_cache else "💰"
    msg = f"{cache_indicator} <b>آخرین قیمت‌ها</b>\n⏰ {now}\n\n"
    for item in prices:
        change_val = item.get("change_value")
        arrow = "🔺" if (change_val is not None and change_val >= 0) else "🔻"
        unit = item.get("unit", "تومان")
        change_pct = item.get("change_percent", 0)
        msg += f"<b>{item['name']}:</b> {item['price']} {unit} ({arrow} {change_pct}%)\n"
    return msg


# ------------------- بررسی عضویت در کانال -------------------
async def check_channel_membership(user_id, context: ContextTypes.DEFAULT_TYPE):
    """بررسی کنید که آیا کاربر در کانال مورد نیاز عضو است یا نه."""
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        # statuses that mean the user is a member
        allowed_statuses = ['member', 'administrator', 'creator']
        if member.status in allowed_statuses:
            return True
        return False
    except Exception as e:
        print(f"⚠️ خطا در بررسی عضویت: {e}")
        # اگر خطا داشت (مثلاً کانال نامعتبر)، False برگردان
        return False



# ------------------- منوی اصلی (ارسال مجدد صفحه اول) -------------------
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    first = user.first_name if user and user.first_name else ''
    # Build keyboard; show admin panel button only to admin username
    keyboard = []
    keyboard.append([InlineKeyboardButton("💰 قیمت لحظه‌ای", callback_data="get_price")])
    keyboard.append([InlineKeyboardButton("📝 ارسال فیدبک", callback_data="feedback")])
    try:
        uname = user.username if user and user.username else ''
        if uname and uname.lower() in [admin.lower() for admin in ADMIN_USERNAMES]:
            keyboard.append([InlineKeyboardButton("🛠️ پنل ادمین", callback_data="admin_panel")])
    except Exception:
        pass
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"سلام {first}! برای دریافت آخرین قیمت‌ها یا ارسال فیدبک، روی دکمه‌ها کلیک کنید:"
    await context.bot.send_message(chat.id, text=text, reply_markup=reply_markup)

# ------------------- ذخیره خودکار قیمت‌ها -------------------
def auto_update_prices():
    while True:
        try:
            prices, from_cache = fetch_data()
            if prices:
                src = "کش" if from_cache else "API"
                logger.info(f"✅ داده‌ها ذخیره شد: {len(prices)} نماد (منبع: {src})")
            else:
                logger.warning("⚠️ داده جدیدی دریافت نشد، از کش استفاده می‌شود")
        except Exception as e:
            logger.error(f"⚠️ خطا در تازه‌سازی خودکار: {e}")
        time.sleep(1800)

# ------------------- هندلر دکمه‌ها -------------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "get_price":
        prices, from_cache = fetch_data()  # سعی کردن برای دریافت داده جدید
        is_from_cache = bool(from_cache)

        # if fetch_data returned nothing, try to read history/cache directly as a last resort
        if not prices:
            try:
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, "r", encoding="utf-8") as f:
                        history = json.load(f)
                    if history:
                        prices = history[-1]
                        is_from_cache = True
                        print("✅ استفاده از داده کش‌شده (prices_history.json)")
                elif os.path.exists(MARKET_CACHE_FILE):
                    with open(MARKET_CACHE_FILE, "r", encoding="utf-8") as f:
                        cache_data = json.load(f)
                    prices = []
                    for category, items in cache_data.items():
                        for item in items:
                            if item.get("symbol") in FILTER_SYMBOLS:
                                prices.append({
                                    "symbol": item.get("symbol"),
                                    "name": item.get("name"),
                                    "price": item.get("price"),
                                    "change_value": item.get("change_value"),
                                    "change_percent": item.get("change_percent"),
                                    "time": item.get("time", f"{item.get('date')} {item.get('time')}"),
                                    "unit": item.get("unit", "تومان")
                                })
                    if prices:
                        is_from_cache = True
                        print("✅ استفاده از داده کش‌شده (market_cache.json)")
                elif os.path.exists(PRICES_CACHE_FILE):
                    with open(PRICES_CACHE_FILE, "r", encoding="utf-8") as f:
                        cache_data = json.load(f)
                    if isinstance(cache_data, list):
                        prices = [item for item in cache_data if item.get("symbol") in FILTER_SYMBOLS]
                        if prices:
                            is_from_cache = True
                            print("✅ استفاده از داده کش‌شده (prices_cache.json)")
            except Exception as e:
                print(f"❌ خطا در خواندن کش: {e}")

        if prices:
            msg = build_message(prices, from_cache=is_from_cache)
        else:
            msg = "❌ هنوز هیچ قیمتی ذخیره نشده"

        await query.edit_message_text(text=msg, parse_mode=ParseMode.HTML)
        # بازگرداندن کاربر به منوی اصلی
        await send_main_menu(update, context)

    elif query.data == "feedback":
        await query.edit_message_text(text="لطفاً فیدبک خود را تایپ کنید. بعد از ارسال، ذخیره خواهد شد.")

        # یک flag برای ذخیره فیدبک در context
        context.user_data["waiting_feedback"] = True
        return
    elif query.data == "admin_panel":
        # show admin options only if username matches
        user = update.effective_user
        uname = user.username if user and user.username else ''
        if not uname or uname.lower() not in [admin.lower() for admin in ADMIN_USERNAMES]:
            await query.answer("دسترسی ندارید", show_alert=True)
            return
        kb = [
            [InlineKeyboardButton("📥 دیدن فیدبک‌ها", callback_data="admin_view_feedback")],
            [InlineKeyboardButton("👥 اعضای کانال", callback_data="admin_channel_members")],
            [InlineKeyboardButton("📊 آمار سیستم", callback_data="admin_stats")],
            [InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings")],
            [InlineKeyboardButton("🔙 برگشت", callback_data="main_menu")]
        ]
        await query.edit_message_text(text="🛠️ پنل ادمین:", reply_markup=InlineKeyboardMarkup(kb))
        return
    elif query.data == "admin_view_feedback":
        # only admin
        user = update.effective_user
        uname = user.username if user and user.username else ''
        if not uname or uname.lower() not in [admin.lower() for admin in ADMIN_USERNAMES]:
            await query.answer("دسترسی ندارید", show_alert=True)
            return
        # show only NEW feedbacks (not previously viewed)
        try:
            if not os.path.exists(FEEDBACK_FILE):
                await query.answer("فیدبکی وجود ندارد", show_alert=True)
                return
            with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
            
            # خواندن آخرین فیدبک دیده‌شده
            last_viewed_idx = -1
            if os.path.exists(ADMIN_VIEWED_FILE):
                try:
                    with open(ADMIN_VIEWED_FILE, 'r', encoding='utf-8') as f:
                        viewed_data = json.load(f)
                        last_viewed_idx = viewed_data.get('last_viewed_idx', -1)
                except:
                    last_viewed_idx = -1
            
            # فیلتر کردن فیدبک‌های جدید
            new_feedbacks = feedbacks[last_viewed_idx + 1:]
            if not new_feedbacks:
                await query.answer("فیدبک جدیدی نیست", show_alert=True)
                return
            
            # ارسال فیدبک‌های جدید
            text = "<b>فیدبک‌های جدید:</b>\n\n"
            for fb in new_feedbacks:
                uname2 = fb.get('username') or str(fb.get('user_id'))
                text += f"👤 <b>{uname2}</b> — {fb.get('time')}\n{fb.get('text')}\n\n" + ("-"*30) + "\n\n"
            
            await query.delete_message()
            await context.bot.send_message(update.effective_chat.id, text, parse_mode=ParseMode.HTML)
            
            # ذخیره آخرین فیدبک دیده‌شده
            with open(ADMIN_VIEWED_FILE, 'w', encoding='utf-8') as f:
                json.dump({'last_viewed_idx': len(feedbacks) - 1}, f)
            
            # بازگشت به منوی اصلی
            await send_main_menu(update, context)
        except Exception as e:
            await query.answer(f"خطا: {e}", show_alert=True)
        return
    elif query.data == "main_menu":
        await query.delete_message()
        await send_main_menu(update, context)
    elif query.data == "get_configs_btn":
        # کاربر می‌خواهد کانفیگ‌ها را دریافت کند
        try:
            # ✅ بررسی عضویت در کانال
            user_id = update.effective_user.id
            is_member = await check_channel_membership(user_id, context)
            
            if not is_member:
                await query.answer(f"❌ شما باید عضو کانال {REQUIRED_CHANNEL} باشید", show_alert=True)
                await send_main_menu(update, context)
                return
            
            if not os.path.exists(CONFIG_FILE):
                await query.answer("هیچ کانفیگی ثبت نشده", show_alert=True)
                return
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfgs = json.load(f)
            if not cfgs:
                await query.answer("هیچ کانفیگی ثبت نشده", show_alert=True)
                return
            
            # ارسال کانفیگ‌ها به صورت پیام‌های جداگانه
            pool = cfgs[-100:]
            picks = random.sample(pool, min(10, len(pool)))
            
            msg_text = "<b>کانفیگ</b>\n\n"
            for i, cfg in enumerate(picks, 1):
                name = cfg.get('name') or 'بدون نام'
                config_text = cfg.get('config', '')
                time_str = cfg.get('time', '')
                msg_text += f"<b>#{i} — {name} ({time_str})</b>\n"
                msg_text += f"<code>{config_text[:100]}...</code>\n\n"
            
            await query.delete_message()
            # ارسال پیام اصلی
            await context.bot.send_message(
                update.effective_chat.id,
                msg_text,
                parse_mode=ParseMode.HTML
            )
            # ارسال تمام کانفیگ‌ها در یک یا چند پیام
            CHUNK = 3
            items = picks
            for i in range(0, len(items), CHUNK):
                chunk = items[i:i+CHUNK]
                text = ""
                for cfg in chunk:
                    name = cfg.get('name') or 'بدون نام'
                    config_text = cfg.get('config', '')
                    time_str = cfg.get('time', '')
                    text += f"<b>{name}</b> ({time_str})\n<code>{config_text}</code>\n\n" + ("-"*30) + "\n\n"
                await context.bot.send_message(
                    update.effective_chat.id,
                    text,
                    parse_mode=ParseMode.HTML
                )
            # بازگشت به منوی اصلی
            await send_main_menu(update, context)
        except Exception as e:
            await query.answer(f"خطا: {e}", show_alert=True)
    
    elif query.data == "admin_channel_members":
        """اعضای کانال"""
        user = update.effective_user
        uname = user.username if user and user.username else ''
        if not uname or uname.lower() not in [admin.lower() for admin in ADMIN_USERNAMES]:
            await query.answer("دسترسی ندارید", show_alert=True)
            return
        
        text = f"""👥 <b>اطلاعات کانال</b>

📍 کانال: {REQUIRED_CHANNEL}
⚠️ نوت: برای دریافت تعداد دقیق اعضا، ربات باید admin کانال باشد.

اگر ربات admin نیست:
1. ربات را به کانال اضافه کنید
2. مجوزهای لازم را بدهید (Read member list)
3. سپس این بخش داده‌ی دقیق خواهد داشت"""
        
        await query.edit_message_text(text=text, parse_mode=ParseMode.HTML)
        await send_main_menu(update, context)
    
    elif query.data == "admin_stats":
        """آمار سیستم"""
        user = update.effective_user
        uname = user.username if user and user.username else ''
        if not uname or uname.lower() not in [admin.lower() for admin in ADMIN_USERNAMES]:
            await query.answer("دسترسی ندارید", show_alert=True)
            return
        
        # دریافت آمار
        total_users = 0
        total_feedback = 0
        total_configs = 0
        
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                total_users = len(json.load(f))
        
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                total_feedback = len(json.load(f))
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                total_configs = len(json.load(f))
        
        text = f"""📊 <b>آمار سیستم</b>

👥 کل اعضا: <b>{total_users}</b>
💬 فیدبک‌های دریافت شده: <b>{total_feedback}</b>
📦 کانفیگ‌های ذخیره شده: <b>{total_configs}</b>

🔧 ادمین‌ها: <b>{', '.join(ADMIN_USERNAMES)}</b>
🎯 کانال نیاز: <b>{REQUIRED_CHANNEL}</b>"""
        
        await query.edit_message_text(text=text, parse_mode=ParseMode.HTML)
        await send_main_menu(update, context)
    
    elif query.data == "admin_settings":
        """تنظیمات ادمین"""
        user = update.effective_user
        uname = user.username if user and user.username else ''
        if not uname or uname.lower() not in [admin.lower() for admin in ADMIN_USERNAMES]:
            await query.answer("دسترسی ندارید", show_alert=True)
            return
        
        text = """⚙️ <b>تنظیمات سیستم</b>

تنظیمات را می‌توانید در داشبورد وب تغییر دهید:
🌐 http://localhost:8080/dashboard

انواع تنظیمات:
✅ فعال/غیرفعال کردن ویژگی کانفیگ
✅ فعال/غیرفعال کردن فیدبک
✅ فعال/غیرفعال کردن بررسی عضویت در کانال
✅ تغییر فاصله زمانی آپدیت قیمت‌ها"""
        
        await query.edit_message_text(text=text, parse_mode=ParseMode.HTML)
        await send_main_menu(update, context)


# ------------------- هندلر شروع ربات -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    save_user(user.id, user.username)
    await send_main_menu(update, context)


async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force fetch from API and report status to the user."""
    await update.message.reply_text("⏳ درحال دریافت جدیدترین قیمت‌ها...")
    prices, from_cache = fetch_data()
    if prices:
        src = "کش" if from_cache else "API"
        msg = build_message(prices, from_cache=from_cache)
        await update.message.reply_text(f"✅ به‌روزرسانی انجام شد (منبع: {src})\n\n" + msg, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("❌ نتوانستیم قیمت‌ها را به‌روزرسانی کنیم.")
    await send_main_menu(update, context)


async def get_configs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send 10 random configs (from recent ones) to the user."""
    try:
        if not os.path.exists(CONFIG_FILE):
            await update.message.reply_text("هیچ کانفیگی وجود ندارد.")
            return
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfgs = json.load(f)
        if not cfgs:
            await update.message.reply_text("هیچ کانفیگی وجود ندارد.")
            return
        pool = cfgs[-100:]
        picks = random.sample(pool, min(10, len(pool)))
        text = ''
        for i, p in enumerate(picks, 1):
            header = f"کانفیگ #{i} — {p.get('name','بدون نام')} — {p.get('time')}\n"
            text += header + p.get('config') + "\n\n" + ('-'*20) + "\n\n"
        await update.message.reply_text(text)
        await send_main_menu(update, context)
    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")
        await send_main_menu(update, context)


async def view_feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only: view stored feedback entries."""
    user = update.message.from_user
    uname = user.username if user else None
    if not uname or uname.lower() not in [admin.lower() for admin in ADMIN_USERNAMES]:
        await update.message.reply_text("❌ دسترسی ندارید.")
        return
    try:
        if not os.path.exists(FEEDBACK_FILE):
            await update.message.reply_text("هیچ فیدبکی ثبت نشده است.")
            await send_main_menu(update, context)
            return
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)
        if not feedbacks:
            await update.message.reply_text("هیچ فیدبکی ثبت نشده است.")
            await send_main_menu(update, context)
            return

        # send in chunks to avoid message size limits
        CHUNK = 5
        items = feedbacks[-50:][::-1]  # latest up to 50
        for i in range(0, len(items), CHUNK):
            chunk = items[i:i+CHUNK]
            text = ''
            for fb in chunk:
                uname = fb.get('username') or str(fb.get('user_id'))
                text += f"{uname} — {fb.get('time')}\n{fb.get('text')}\n\n"
            await update.message.reply_text(text)
        await send_main_menu(update, context)
    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")
        await send_main_menu(update, context)

# ------------------- پاسخ به پیام‌ها -------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if context.user_data.get("waiting_feedback"):
        # ذخیره فیدبک
        feedback_entry = {
            "user_id": update.message.from_user.id,
            "username": update.message.from_user.username,
            "text": user_text,
            "time": datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        }
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                feedbacks = json.load(f)
        else:
            feedbacks = []

        feedbacks.append(feedback_entry)
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)

        await update.message.reply_text("✅ فیدبک شما ثبت شد. متشکریم!")
        context.user_data["waiting_feedback"] = False
        await send_main_menu(update, context)
    else:
        # پیام خوش آمدگویی و دکمه‌ها
        keyboard = [
            [InlineKeyboardButton("💰 قیمت لحظه‌ای", callback_data="get_price")],
            [InlineKeyboardButton("📝 ارسال فیدبک", callback_data="feedback")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "سلام! برای دریافت آخرین قیمت‌ها یا ارسال فیدبک، روی دکمه‌ها کلیک کنید:",
            reply_markup=reply_markup
        )

# ------------------- اجرای ربات -------------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # ensure data files exist to avoid "no price saved" errors before first fetch
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

    # هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("update", update_command))
    app.add_handler(CommandHandler("getconfigs", get_configs_command))
    app.add_handler(CommandHandler("viewfeedback", view_feedback_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button))

    # ذخیره خودکار قیمت‌ها در پس‌زمینه
    threading.Thread(target=auto_update_prices, daemon=True).start()
    # راه‌اندازی سرور کانفیگ در پس‌زمینه (قابل دسترسی روی پورت 8080)
    try:
        def run_config_thread():
            try:
                run_config_server()
            except Exception as te:
                print(f"❌ خطا در سرور کانفیگ: {te}")
        threading.Thread(target=run_config_thread, daemon=True).start()
        print("🔧 سرور کانفیگ در حال راه‌اندازی روی پورت 8080...")
        time.sleep(1)  # اجازه دادن به سرور که شروع شود
        print("✅ سرور کانفیگ فعال است: http://localhost:8080/ یا http://127.0.0.1:8080/")
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی سرور کانفیگ: {e}")

    print("✅ ربات آماده است")
    app.run_polling()

if __name__ == "__main__":
    main()
