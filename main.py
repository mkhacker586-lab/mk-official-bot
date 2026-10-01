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
        self.wfile.write(b"M.K TRADER AI Signal Bot is running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Self-Ping function jo bot ko 24/7 active rakhega
def self_ping():
    app_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not app_url:
        return
    while True:
        try:
            urllib.request.urlopen(app_url)
            print("Self-ping successful, bot is active!")
        except Exception as e:
            print(f"Self-ping error: {e}")
        import time
        time.sleep(240)

# Main Start Command - Jaise reference bot ka layout hai
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"Bot /start command aayi hai: {user.first_name}")
    
    # HD Banner image jo reference bot jesi high quality look degi
    photo_url = "https://i.postimg.cc/Pvt9mWMg/image.jpg"
    
    welcome_caption = (
        f"👋 **HELLO M.K TRADER!**[span_13](start_span)[span_13](end_span)\n\n"
        f"🚀 **WELCOME TO M.K TRADER AI ANALYZER**[span_14](start_span)[span_14](end_span)\n"
        f"🤖 **Your AI-Powered Trading Assistant**[span_15](start_span)[span_15](end_span)\n\n"
        f"📊 Analyze the market with advanced AI technology[span_16](start_span)[span_16](end_span)\n"
        f"🔥 Get smarter insights and powerful signal analysis[span_17](start_span)[span_17](end_span)\n"
        f"🎯 Designed to help you make better trading decisions[span_18](start_span)[span_18](end_span)\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💎 **CHOOSE YOUR PLAN / OPTION**[span_19](start_span)[span_19](end_span)\n\n"
        f"✨ Select a button below to unlock your desired features[span_20](start_span)[span_20](end_span):"
    )
    
    # Reference bot jaise do main plans aur niche extra options
    keyboard = [
        [
            InlineKeyboardButton("🚀 Starter Plan", callback_data="starter_plan"),
            InlineKeyboardButton("👑 Royal Plan", callback_data="royal_plan")
        ],
        [
            InlineKeyboardButton("🖤 LOSS RECOVERY SESSION", callback_data="recovery")
        ],
        [
            InlineKeyboardButton("📊 M.K TRADER VIP CHANNEL", url="https://t.me/+neTu5arl0spkNjFk")
        ],
        [
            InlineKeyboardButton("🆔 TRADER ID VERIFICATION", callback_data="verification"),
            InlineKeyboardButton("⭐ FEEDBACKS", callback_data="feedbacks")
        ],
        [
            InlineKeyboardButton("💬 ADMIN SUPPORT", url="https://t.me/MK_TRADER586")
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
    
    if query.data == "starter_plan":
        text = (
            "🚀 **STARTER FREE SIGNALS ACTIVE** 🚀[span_21](start_span)[span_21](end_span)\n\n"
            "🔥 **5 LIVE SIGNALS / 24H**[span_22](start_span)[span_22](end_span)\n"
            "⚡ 2 TIME FUTURE SIGNALS GENERATE[span_23](start_span)[span_23](end_span)\n"
            "📊 5 CHART ANALYZER SIGNALS DAILY[span_24](start_span)[span_24](end_span)\n"
            "🤖 AI CHAT SUPPORT[span_25](start_span)[span_25](end_span)\n"
            "✅ FS RESULTS CHECKER[span_26](start_span)[span_26](end_span)\n\n"
            "✨ Get started with our Free Plan and experience the high accuracy signals[span_27](start_span)[span_27](end_span).\n\n"
            "👑 Want UNLIMITED Signals? Upgrade to the ROYAL PLAN 👑[span_28](start_span)[span_28](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("👑 Switch to Royal Plan", callback_data="royal_plan")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "royal_plan":
        text = (
            "👑 **M.K TRADER ROYAL VIP PLAN** 👑\n\n"
            "✅ **UNLIMITED SIGNALS • PREMIUM ACCESS • MORE OPPORTUNITIES**[span_29](start_span)[span_29](end_span)\n"
            "🔥 Go Royal. Unlock Unlimited[span_30](start_span)[span_30](end_span).\n\n"
            "🎯 Account banane ke liye niche diye gaye link par click karein aur ID admin ko bhejein:\n"
            "🔗 https://broker-qx.pro/?lid=1614510"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE QX ACCOUNT NOW ⭐", url="https://broker-qx.pro/?lid=1614510")],
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "recovery":
        text = (
            "🚨 **PERSONAL 1-on-1 LOSS RECOVERY SESSION** 🚨\n\n"
            "📉 Bar bar loss ho raha hai? Apne loss ko recover karne ke liye M.K Trader ke sath join karein.\n\n"
            "✅ Special OTC & Live Trading Strategy\n"
            "✅ High Accuracy Entry Timing\n\n"
            "🎯 **Step 1:** Account banayein: https://broker-qx.pro/?lid=1614510\n"
            "🏦 **Step 2:** Deposit karke Trader ID admin ko bhejein: @MK_TRADER586"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE QX ACCOUNT", url="https://broker-qx.pro/?lid=1614510")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass
        
    elif query.data == "verification":
        text = (
            "🆔 **TRADER ID VERIFICATION GUIDE** 🆔\n\n"
            "1️⃣ Hamare official link se account banayein: https://broker-qx.pro/?lid=1614510\n"
            "2️⃣ Account mein minimum deposit karein.\n"
            "3️⃣ Apni **Quotex Trader ID** copy karke admin ko bhej dein ✅\n\n"
            "💬 *Admin Username:* @MK_TRADER586"
        )
        keyboard = [
            [InlineKeyboardButton("💬 SEND ID TO ADMIN", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "feedbacks":
        text = (
            "⭐ **M.K TRADER CLIENT FEEDBACKS & REVIEWS** ⭐\n\n"
            "🔥 100% Real Profit Screenshots\n"
            "🔥 Successful Loss Recovery Results\n"
            "🔥 Trusted by Hundreds of Traders\n\n"
            "🔗 Proofs dekhne ke liye channel join karein ya admin se rabta karein."
        )
        keyboard = [
            [InlineKeyboardButton("📊 M.K TRADER VIP CHANNEL", url="https://t.me/+neTu5arl0spkNjFk")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "back_home":
        welcome_caption = (
            f"👋 **HELLO M.K TRADER!**[span_31](start_span)[span_31](end_span)\n\n"
            f"🚀 **WELCOME TO M.K TRADER AI ANALYZER**[span_32](start_span)[span_32](end_span)\n"
            f"🤖 **Your AI-Powered Trading Assistant**[span_33](start_span)[span_33](end_span)\n\n"
            f"📊 Analyze the market with advanced AI technology[span_34](start_span)[span_34](end_span)\n"
            f"🔥 Get smarter insights and powerful signal analysis[span_35](start_span)[span_35](end_span)\n\n"
            f"👇 *Select your preferred plan to continue:*[span_36](start_span)[span_36](end_span)"
        )
        keyboard = [
            [
                InlineKeyboardButton("🚀 Starter Plan", callback_data="starter_plan"),
                InlineKeyboardButton("👑 Royal Plan", callback_data="royal_plan")
            ],
            [
                InlineKeyboardButton("🖤 LOSS RECOVERY SESSION", callback_data="recovery")
            ],
            [
                InlineKeyboardButton("📊 M.K TRADER VIP CHANNEL", url="https://t.me/+neTu5arl0spkNjFk")
            ],
            [
                InlineKeyboardButton("🆔 TRADER ID VERIFICATION", callback_data="verification"),
                InlineKeyboardButton("⭐ FEEDBACKS", callback_data="feedbacks")
            ],
            [
                InlineKeyboardButton("💬 ADMIN SUPPORT", url="https://t.me/MK_TRADER586")
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

    print("M.K TRADER Bot successfully start ho gaya hai...")
    
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
