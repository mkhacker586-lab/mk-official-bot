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

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"M.K TRADER Professional Bot is active 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

def self_ping():
    app_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not app_url:
        return
    while True:
        try:
            urllib.request.urlopen(app_url)
        except Exception:
            pass
        import time
        time.sleep(240)

# Main Start Menu Hub
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"Start command from: {user.first_name}")
    
    # Clean professional banner image link (No King branding)
    photo_url = "https://i.postimg.cc/9Q33x825/mk-trader-banner.jpg"
    
    welcome_caption = (
        f"🔥 **M.K TRADER OFFICIAL HUB** 🔥\n\n"
        f"👋 Welcome! Choose your desired option below to get accurate trading signals, loss recovery, and VIP access.\n\n"
        f"👇 **Select an option from the menu:**"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🚀 VIP Trading Signals", callback_data="vip_signals"),
            InlineKeyboardButton("🖤 Loss Recovery", callback_data="loss_recovery")
        ],
        [
            InlineKeyboardButton("🆔 Trader ID Verification", callback_data="id_verification"),
            InlineKeyboardButton("💬 Send Feedback", callback_data="send_feedback")
        ],
        [
            InlineKeyboardButton("👑 Switch to Royal VIP Plan", callback_data="royal_plan")
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
        # Fallback agar photo load na ho toh text bhej dega taaki error na aaye
        await update.message.reply_text(
            welcome_caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Button Click Handlers with separate pages
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "vip_signals":
        text = (
            "🚀 **VIP TRADING SIGNALS PANEL** 🚀\n\n"
            "🔥 Get high accuracy daily signals with proper risk management.\n"
            "⚡ Real-time market execution alerts for maximum profit.\n\n"
            "🎯 **Step 1:** Create your official account here:\n"
            "🔗 https://broker-qx.pro/?lid=1614511[span_1](start_span)[span_1](end_span)\n\n"
            "💬 **Step 2:** Send your ID to admin for VIP access:\n"
            "👉 T.me/MK_TRADER586[span_2](start_span)[span_2](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE QX ACCOUNT", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "loss_recovery":
        text = (
            "🚨 **LOSS RECOVERY SESSION** 🚨\n\n"
            "📉 Facing continuous losses? Recover your account balance step-by-step with M.K Trader's expert strategies.\n\n"
            "✅ **Step 1:** Create a fresh account using our official link:\n"
            "🔗 https://broker-qx.pro/?lid=1614511[span_3](start_span)[span_3](end_span)\n\n"
            "✅ **Step 2:** Deposit funds and share your Trader ID directly with admin to join the recovery session:\n"
            "👉 T.me/MK_TRADER586[span_4](start_span)[span_4](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE QX ACCOUNT", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "id_verification":
        text = (
            "🆔 **TRADER ID VERIFICATION** 🆔\n\n"
            "Want to verify your account for VIP signals and sessions? Follow these simple steps:\n\n"
            "1️⃣ Create your account through our official link:\n"
            "🔗 https://broker-qx.pro/?lid=1614511[span_5](start_span)[span_5](end_span)\n\n"
            "2️⃣ Complete minimum deposit in your account.\n\n"
            "3️⃣ Copy your **Trader ID** and send it directly to admin for verification:\n"
            "👉 T.me/MK_TRADER586[span_6](start_span)[span_6](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("💬 SEND ID TO ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "send_feedback":
        text = (
            "💬 **SEND FEEDBACK & REVIEWS** 💬\n\n"
            "🔥 Share your profit screenshots, success stories, and recovery feedback with us!\n"
            "⭐ Your reviews help our community grow stronger.\n\n"
            "🔗 Send your feedback directly to admin:\n"
            "👉 T.me/MK_TRADER586[span_7](start_span)[span_7](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ SEND FEEDBACK", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "royal_plan":
        text = (
            "👑 **M.K TRADER ROYAL VIP PLAN** 👑\n\n"
            "✅ Unlimited Signals • Direct VIP Access • 24/7 Personal Support\n"
            "🔥 Go Royal and maximize your daily trading profits.\n\n"
            "🎯 **Step 1:** Create account: https://broker-qx.pro/?lid=1614511[span_8](start_span)[span_8](end_span)\n"
            "🎯 **Step 2:** Send ID to admin: T.me/MK_TRADER586[span_9](start_span)[span_9](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE QX ACCOUNT", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "back_home":
        welcome_caption = (
            f"🔥 **M.K TRADER OFFICIAL HUB** 🔥\n\n"
            f"👋 Welcome! Choose your desired option below to get accurate trading signals, loss recovery, and VIP access.\n\n"
            f"👇 **Select an option from the menu:**"
        )
        keyboard = [
            [
                InlineKeyboardButton("🚀 VIP Trading Signals", callback_data="vip_signals"),
                InlineKeyboardButton("🖤 Loss Recovery", callback_data="loss_recovery")
            ],
            [
                InlineKeyboardButton("🆔 Trader ID Verification", callback_data="id_verification"),
                InlineKeyboardButton("💬 Send Feedback", callback_data="send_feedback")
            ],
            [
                InlineKeyboardButton("👑 Switch to Royal VIP Plan", callback_data="royal_plan")
            ],
            [
                InlineKeyboardButton("💬 ADMIN SUPPORT", url="https://T.me/MK_TRADER586")
            ]
        ]
        try:
            await query.edit_message_caption(caption=welcome_caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await query.edit_message_text(text=welcome_caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

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
