import os
import datetime
import requests
from flask import Flask, request

# ==========================================
# ⚙ AAPKI ORIGINAL SETTINGS:
# ==========================================
TOKEN = "8698303434:AAHN9ccgl5u3ZoIh0RKNRTIh55DiSbCJO-g"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
BOT_NAME = "𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓"
BOT_USERNAME = "@MK_TRADER_OFFICIAL_BOT"
LOG_CHANNEL_ID = -1003724080321

CHANNEL_LINK = "https://t.me/+FdbFgVgsoT41ZGU8"
QUOTEX_LINK = "https://broker-qx.pro/?lid=1614511"
ADMIN_USERNAME = "t.me/MK_TRADER586"
# ==========================================

app = Flask(__name__)

COUNTER_FILE = "/tmp/request_counter_bot1.txt"

def get_next_request_count():
    try:
        count = 1
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "r") as f:
                content = f.read().strip()
                if content.isdigit():
                    count = int(content) + 1
        with open(COUNTER_FILE, "w") as f:
            f.write(str(count))
        return count
    except Exception as e:
        print(f"Counter error: {e}")
        return 1

def send_telegram_request(method, payload):
    url = f"{TELEGRAM_API}/{method}"
    try:
        return requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram API error ({method}): {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    send_telegram_request("sendMessage", payload)

def edit_message(chat_id, message_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    send_telegram_request("editMessageText", payload)

def send_data_to_log_channel(user, source_action):
    try:
        user_id = user.get("id")
        username = f"@{user.get('username')}" if user.get("username") else "𝐍𝐨 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞"
        first_name = user.get("first_name", "N/A")
        last_name = user.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        
        req_number = get_next_request_count() if "Join Request" in source_action else "𝐍/𝐀"
        pkt_time = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        current_time = pkt_time.strftime("%d %b %Y, %I:%M %p")
        
        log_msg = (
            f"⭐ 𝐍𝐄𝐖 𝐔𝐒𝐄𝐑 𝐃𝐀𝐓𝐀 𝐂𝐀𝐏𝐓𝐔𝐑𝐄𝐃 ⭐\n"
            f"━━━━━━•❅•°•❈•°•❅•━━━━━━\n"
            f"🤖 𝐁𝐨𝐭 𝐍𝐚𝐦𝐞  : {BOT_NAME}\n"
            f"👑 𝐁𝐫𝐚𝐧𝐝      : 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑\n"
            f"🆔 𝐔𝐬𝐞𝐫 𝐈𝐃    : {user_id}\n"
            f"🕵🏻‍♂️ 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞 : {username}\n"
            f"📛 𝐍𝐚𝐦𝐞     : {full_name}\n"
            f"📢 𝐂𝐡𝐚𝐧𝐧𝐞𝐥   : 𝐍/𝐀\n"
            f"📊 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐬  : #{req_number}\n"
            f"🕐 𝐓𝐢𝐦𝐞      : {current_time}\n"
            f"📱 𝐒𝐨𝐮𝐫𝐜𝐞   : {source_action}\n"
            f"━━━━━━•❅•°•❈•°•❅•━━━━━━\n"
            f"🔥 𝐁𝐨𝐭: {BOT_USERNAME} ❤️"
        )
        send_message(LOG_CHANNEL_ID, log_msg)
    except Exception as e:
        print(f"Log error: {e}")

def get_main_menu():
    return {
        "inline_keyboard": [
            [{"text": "🟢 Otc Live Signal", "callback_data": "otc_live"}],
            [{"text": "🟢 Real Pairs Signal", "callback_data": "real_pairs"}],
            [{"text": "🟣 Otc Future Signals", "callback_data": "otc_future"}],
            [{"text": "🟣 Real Future List", "callback_data": "real_future"}],
            [{"text": "🟡 AUTO LIVE", "callback_data": "auto_live"}],
            [{"text": "🟢 FS FILTER", "callback_data": "fs_filter"}],
            [{"text": "🔵 Currency Pairs (PKR/BRL/BDT)", "callback_data": "currency_pairs"}],
            [{"text": "🔵 Live Market Pairs (EUR/CAD)", "callback_data": "live_market_pairs"}],
            [{"text": "🤖 M.K AI SIGNALS PRO", "callback_data": "ai_signals_pro"}],
            [{"text": "📢 SIGNALS PROVIDE M.K PREMIUM CHANNEL", "url": CHANNEL_LINK}],
            [{"text": "👑 Get VIP Via Quotex", "url": QUOTEX_LINK}],
            [{"text": "💬 Contact Admin Support", "url": f"https://{ADMIN_USERNAME}"}]
        ]
    }

@app.route('/api/bot', methods=['POST'])
@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return "OK", 200

    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        user = msg.get("from", {})
        user_name = user.get("first_name", "Trader")

        if text == "/start":
            send_data_to_log_channel(user, "Bot /start Command")
            welcome_text = (
                f"👑 **{BOT_NAME}** 👑\n\n"
                f"✨ Hello {user_name}!\n"
                "🌐 Welcome to M.K Trader Official Hub. Select your desired option below:\n\n"
                "📊 **Signals Provide Channel:**\n"
                f"🔗 {CHANNEL_LINK}\n\n"
                "🌈 Join now for free daily signals & advanced AI tools!\n"
                f"🚦 Admin Support: {ADMIN_USERNAME}\n\n"
                "👇 **Choose an option below:**"
            )
            send_message(chat_id, welcome_text, get_main_menu())

    elif "callback_query" in data:
        cq = data["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        message_id = cq["message"]["message_id"]
        cb_data = cq["data"]

        if cb_data == "otc_live":
            resp_text = (
                "📈 **OTC LIVE SIGNAL GENERATED**\n\n"
                "💎 **Asset:** USD/PHP (OTC)\n"
                "🟢 **Direction:** CALL 📈\n"
                "🕒 **Entry Time:** Next Candle\n"
                "🌐 **Time zone:** UTC +5:00\n"
                "⚠️ **1 Step MTG Allowed**\n\n"
                f"👤 **OWNER:** {ADMIN_USERNAME}"
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "🔄 GET ANOTHER SIGNAL", "callback_data": "otc_live"}],
                    [{"text": "🔙 MAIN MENU", "callback_data": "back_home"}]
                ]
            }
            edit_message(chat_id, message_id, resp_text, kb)

        elif cb_data == "real_pairs":
            resp_text = (
                "📈 **REAL PAIRS LIVE SIGNAL**\n\n"
                "💎 **Asset:** EUR/USD\n"
                "🔴 **Direction:** PUT 📉\n"
                "🕒 **Entry:** Immediate / 1 Minute\n"
                "⚠️ **Risk Management Required**\n\n"
                f"👤 **OWNER:** {ADMIN_USERNAME}"
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "🔄 GET ANOTHER SIGNAL", "callback_data": "real_pairs"}],
                    [{"text": "🔙 MAIN MENU", "callback_data": "back_home"}]
                ]
            }
            edit_message(chat_id, message_id, resp_text, kb)

        elif cb_data == "otc_future":
            resp_text = (
                "🟣 **OTC FUTURE SIGNALS PANEL**\n\n"
                "🔥 High-accuracy session predictions for OTC markets.\n"
                "📊 Status: Active & Optimized\n\n"
                "👇 Select option below:"
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "⭐ CREATE QX ACCOUNT", "url": QUOTEX_LINK}],
                    [{"text": "🔙 MAIN MENU", "callback_data": "back_home"}]
                ]
            }
            edit_message(chat_id, message_id, resp_text, kb)

        elif cb_data == "real_future":
            resp_text = (
                "🟣 **REAL FUTURE LIST & SETUP**\n\n"
                "📊 Major news setups and real market future predictions.\n"
                f"💬 Contact admin for VIP access: {ADMIN_USERNAME}"
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "💬 CONTACT ADMIN", "url": f"https://{ADMIN_USERNAME}"}],
                    [{"text": "🔙 MAIN MENU", "callback_data": "back_home"}]
                ]
            }
            edit_message(chat_id, message_id, resp_text, kb)

        elif cb_data == "auto_live":
            resp_text = (
                "🟡 **AUTO LIVE SIGNALS MODE**\n\n"
                "⚡ Automatic live signal bot engine is running for VIP members.\n"
                "💎 Upgrade via Quotex to unlock full auto feed."
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "👑 GET VIP VIA QUOTEX", "url": QUOTEX_LINK}],
                    [{"text": "🔙 MAIN MENU", "callback_data": "back_home"}]
                ]
            }
            edit_message(chat_id, message_id, resp_text, kb)

        elif cb_data == "fs_filter":
            resp_text = (
                "🟢 **FS FILTER SETTINGS**\n\n"
                "⚙️ Advanced market noise filter, volatility scanner, and trend strength analyzer enabled."
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "🔙 MAIN MENU", "callback_data": "back_home"}]
                ]
            }
            edit_message(chat_id, message_id, resp_text, kb)

        elif cb_data == "currency_pairs":
            resp_text = (
                "🔵 **CUSTOM CURRENCY PAIRS (QAS & KHAN STYLE)**\n\n"
                "Select your preferred regional and high-payout currency pair list:\n\n"
                "• **USD/PKR** (Pakistani Rupee OTC)\n"
                "• **USD/BRL** (Brazilian Real OTC)\n"
                "• **USD/BDT** (Bangladeshi Taka OTC)\n"
                "• **CAD/CHF** (Canadian Dollar / Swiss Franc)\n\n"
                "🎯 High accuracy signals active for these pairs!"
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "🟢 GENERATE PKR/BRL SIGNAL", "callback_data": "otc_live"}],
                    [{"text": "🔙 MAIN MENU", "callback_data": "back_home"}]
                ]
            }
            edit_message(chat_id, message_id, resp_text, kb)

        elif cb_data == "live_market_pairs":
            resp_text = (
                "🔵 **LIVE MARKET FOREX PAIRS**\n\n"
                "Select your favorite major forex market pairs:\n\n"
                "• **EUR/CAD** (Euro / Canadian Dollar)\n"
                "• **EUR/CHF** (Euro / Swiss Franc)\n"
                "• **EUR/GBP** (Euro / British Pound)\n\n"
                "📊 Real-time analysis feed active."
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "🟢 GENERATE LIVE PAIR SIGNAL", "callback_data": "real_pairs"}],
                    [{"text": "🔙 MAIN MENU", "callback_data": "back_home"}]
                ]
            }
            edit_message(chat_id, message_id, resp_text, kb)

        elif cb_data == "ai_signals_pro":
            resp_text = (
                "🤖 **M.K AI SIGNALS PRO BOT PAYMENT & SETUP**\n\n"
                "⚡ Welcome to M.K AI Automated Trading Bot Suite!\n"
                "💎 **VIP Subscription Plans:**\n"
                "• Lifetime Access: $30 (USDT / Binance P2P / SadaPay / Meezan Bank)\n"
                "• Or Register via Official Quotex Link for FREE VIP Access!\n\n"
                "👇 Choose payment or verification method below:"
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "👑 GET VIP VIA QUOTEX (FREE)", "url": QUOTEX_LINK}],
                    [{"text": "💬 CONTACT ADMIN FOR PAYMENT DETAILS", "url": f"https://{ADMIN_USERNAME}"}],
                    [{"text": "🔙 MAIN MENU", "callback_data": "back_home"}]
                ]
            }
            edit_message(chat_id, message_id, resp_text, kb)

        elif cb_data == "back_home":
            welcome_text = (
                f"👑 **{BOT_NAME}** 👑\n\n"
                "🌐 Welcome to M.K Trader Official Hub. Select your desired option below:\n\n"
                "📊 **Signals Provide Channel:**\n"
                f"🔗 {CHANNEL_LINK}\n\n"
                "🌈 Join now for free daily signals & advanced AI tools!\n"
                f"🚦 Admin Support: {ADMIN_USERNAME}\n\n"
                "👇 **Choose an option below:**"
            )
            edit_message(chat_id, message_id, welcome_text, get_main_menu())

    return "OK", 200

@app.route('/', methods=['GET'])
@app.route('/api/bot', methods=['GET'])
def index():
    return f"{BOT_NAME} is active on Vercel!", 200
