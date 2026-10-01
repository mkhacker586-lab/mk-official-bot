import logging
import os
import asyncio
import threading
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Render port requirement ke liye dummy web server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"M.K TRADER Professional Bot is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Self-Ping function jo bot ko active rakhega
def self_ping():
    app_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not app_url:
        return
    while True:
        try:
            urllib.request.urlopen(app_url)
            print("Self-ping successful!")
        except Exception as e:
            print(f"Self-ping error: {e}")
        import time
        time.sleep(240)

# Main Start Command / Menu Hub
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"Start command received from: {user.first_name}")
    
    # Professional banner image (No King branding)
    photo_url = "https://i.postimg.cc/Pvt9mWMg/image.jpg"
    
    welcome_caption = (
        f"👋 **HELLO M.K TRADER!**\n\n"
        f"🚀 **WELCOME TO M.K TRADER OFFICIAL HUB**\n"
        f"🤖 **Your Advanced AI Trading Assistant**\n\n"
        f"📊 Analyze the market with high precision tools\n"
        f"🔥 Get smart insights and powerful signals\n\n"
        f"👇 **Select an option from the menu below:**"
    )
    
    # Menu layout exactly matching your requirements
    keyboard = [
        [
            InlineKeyboardButton("📊 Future Signals", callback_data="future_signals"),
            InlineKeyboardButton("⭐ Live Signals", callback_data="live_signals")
        ],
        [
            InlineKeyboardButton("✅ Signal Verifiers", callback_data="verification"),
            InlineKeyboardButton("🖤 Loss Recovery", callback_data="recovery")
        ],
        [
            InlineKeyboardButton("📈 Chart Analyzer", callback_data="chart_analyzer"),
            InlineKeyboardButton("💬 Send Feedback", callback_data="send_feedback")
        ],
        [
            InlineKeyboardButton("👑 Switch to Royal Plan", callback_data="royal_plan")
        ],
        [
            InlineKeyboardButton("💬 ADMIN SUPPORT", url="https://T.me/MK_TRADER586")
        ]
    ]
    
    try:
        await update.message.reply_photo(
            photo=photo_url,
            caption=welcome_caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print(f"Start message error: {e}")

# Button Click Handlers
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "future_signals":
        text = (
            "📊 **FUTURE SIGNALS PANEL** 📊\n\n"
            "⚡ 2 Time Future Signals Generate Daily\n"
            "🔥 High accuracy trend forecasting for crypto & forex markets.\n\n"
            "🔗 **Quotex Official Platform:** https://broker-qx.pro/?lid=1614511"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE ACCOUNT", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "live_signals":
        text = (
            "⭐ **LIVE SIGNALS ACTIVE** ⭐\n\n"
            "🔥 5 Live Signals / 24H Provided\n"
            "⚡ Real-time market execution alerts with high win-rate.\n\n"
            "💬 Contact admin to join VIP Live sessions: T.me/MK_TRADER586"
        )
        keyboard = [
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "verification":
        text = (
            "🆔 **TRADER ID VERIFICATION GUIDE** 🆔\n\n"
            "1️⃣ Sign up using our official link: https://broker-qx.pro/?lid=1614511[span_20](start_span)[span_20](end_span)\n"
            "2️⃣ Deposit funds into your trading account.\n"
            "3️⃣ Send your **Trader ID** directly to admin for verification ✅\n\n"
            "💬 *Admin Contact Link:* T.me/MK_TRADER586[span_21](start_span)[span_21](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("💬 SEND ID TO ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "recovery":
        text = (
            "🚨 **LOSS RECOVERY SESSION** 🚨\n\n"
            "📉 Facing losses? Recover your account balance with M.K Trader's expert recovery team.\n\n"
            "✅ **Step 1:** Create a fresh account: https://broker-qx.pro/?lid=1614511[span_22](start_span)[span_22](end_span)\n"
            "✅ **Step 2:** Deposit and share your ID with admin: T.me/MK_TRADER586[span_23](start_span)[span_23](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE ACCOUNT", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "chart_analyzer":
        text = (
            "📈 **AI CHART ANALYZER** 📈\n\n"
            "⚡ Automatic support & resistance detection\n"
            "🔥 Candlestick pattern scanner for accurate entry points.\n\n"
            "💬 Need help reading charts? Contact admin: T.me/MK_TRADER586"
        )
        keyboard = [
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "send_feedback":
        text = (
            "💬 **SEND FEEDBACK & REVIEWS** 💬\n\n"
            "🔥 Share your profit screenshots, feedback, or recovery results with us!\n"
            "⭐ Your success stories motivate our community.\n\n"
            "🔗 Send your reviews directly to admin: T.me/MK_TRADER586"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ SEND FEEDBACK TO ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "royal_plan":
        text = (
            "👑 **M.K TRADER ROYAL VIP PLAN** 👑\n\n"
            "✅ UNLIMITED SIGNALS • PREMIUM ACCESS • 24/7 SUPPORT\n"
            "🔥 Go Royal. Unlock Maximum Profits.\n\n"
            "🎯 **Step 1:** Create account: https://broker-qx.pro/?lid=1614511[span_24](start_span)[span_24](end_span)\n"
            "🎯 **Step 2:** Send ID to admin: T.me/MK_TRADER586[span_25](start_span)[span_25](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE QX ACCOUNT", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "back_home":
        welcome_caption = (
            f"👋 **HELLO M.K TRADER!**\n\n"
            f"🚀 **WELCOME TO M.K TRADER OFFICIAL HUB**\n"
            f"🤖 **Your Advanced AI Trading Assistant**\n\n"
            f"📊 Analyze the market with high precision tools\n"
            f"🔥 Get smart insights and powerful signals\n\n"
            f"👇 **Select an option from the menu below:**"
        )
        keyboard = [
            [
                InlineKeyboardButton("📊 Future Signals", callback_data="future_signals"),
                InlineKeyboardButton("⭐ Live Signals", callback_data="live_signals")
            ],
            [
                InlineKeyboardButton("✅ Signal Verifiers", callback_data="verification"),
                InlineKeyboardButton("🖤 Loss Recovery", callback_data="recovery")
            ],
            [
                InlineKeyboardButton("📈 Chart Analyzer", callback_data="chart_analyzer"),
                InlineKeyboardButton("💬 Send Feedback", callback_data="send_feedback")
            ],
            [
                InlineKeyboardButton("👑 Switch to Royal Plan", callback_data="royal_plan")
            ],
            [
                InlineKeyboardButton("💬 ADMIN SUPPORT", url="https://T.me/MK_TRADER586")
            ]
        ]
        try:
            await query.edit_message_caption(caption=welcome_caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

async def main_bot():
    TOKEN = "8764957005:AAHegnKTuSR3GoGQ_6gUn7DeTzgw9W6t-AU"

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("M.K TRADER Bot started successfully...")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    while True:
        await asyncio.sleep(3600)

def run_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_bot())

def main():
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    
    ping_thread = threading.Thread(target=self_ping, daemon=True)
    ping_thread.start()
    
    run_async_loop()

if __name__ == '__main__':
    main()
