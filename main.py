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

# Main Start Menu (Screenshot Style Layout)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"Start command from: {user.first_name}")
    
    welcome_text = (
        "👀 **Hello M.K TRADER!**\n\n"
        "🌐 **Welcome to M.K TRADER OFFICIAL HUB, Can I help you?**\n\n"
        "👑 **M.K TRADER thanks for contacting!**\n\n"
        "📊 **Free signals & official tools available here.**\n\n"
        "🌈 **Join now for free signals everyday**\n\n"
        "🚦 **If any problem sms me: T.me/MK_TRADER586**\n\n"
        "👇 **Select your option below:**"
    )
    
    # Screenshot jaise ek ke niche ek lambe buttons
    keyboard = [
        [InlineKeyboardButton("🟢 VIP JOINING PROCESS", callback_data="vip_process")],
        [InlineKeyboardButton("🏛 HOW TO CREATE QUOTEX NEW ACCOUNT", url="https://broker-qx.pro/?lid=1614511")],
        [InlineKeyboardButton("💠 HOW TO DELETE QUOTEX OLD ACCOUNT", callback_data="delete_old")],
        [InlineKeyboardButton("👇 OUR VIP GROUPS PIC'S", callback_data="vip_pics")],
        [InlineKeyboardButton("⭐ SEND TRADER ID HERE", url="https://T.me/MK_TRADER586")],
        [InlineKeyboardButton("📩 ANY QUESTION DM US", url="https://T.me/MK_TRADER586")]
    ]
    
    try:
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print(f"Start error: {e}")

# Button Click Handlers (Separate Pages)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "vip_process":
        text = (
            "🟢 **VIP JOINING PROCESS** 🟢\n\n"
            "🔥 Step-by-step guide to join M.K Trader VIP team:\n\n"
            "1️⃣ Create a fresh account using our official link:\n"
            "🔗 https://broker-qx.pro/?lid=1614511\n\n"
            "2️⃣ Deposit minimum funds into your account.\n\n"
            "3️⃣ Send your Trader ID to admin:\n"
            "👉 T.me/MK_TRADER586"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE QX ACCOUNT", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💬 SEND ID TO ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "delete_old":
        text = (
            "💠 **HOW TO DELETE QUOTEX OLD ACCOUNT** 💠\n\n"
            "📉 Purane account mein loss ho raha hai ya affiliate change karna hai?\n\n"
            "✅ Naya account banane ka tarika:\n"
            "1️⃣ Purane account ki profile se logout karein ya support se deactivate karwayein.\n"
            "2️⃣ Naye email par hamare link se naya account banayein:\n"
            "🔗 https://broker-qx.pro/?lid=1614511"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE NEW ACCOUNT", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "vip_pics":
        text = (
            "👇 **OUR VIP GROUPS PROOFS & PICS** 👇\n\n"
            "🔥 100% Real Profit Screenshots & VIP Trading Session Results!\n"
            "⭐ Proofs dekhne ke liye seedha admin se rabta karein:\n"
            "👉 T.me/MK_TRADER586"
        )
        keyboard = [
            [InlineKeyboardButton("💬 CONTACT ADMIN FOR PROOFS", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "back_home":
        welcome_text = (
            "👀 **Hello M.K TRADER!**\n\n"
            "🌐 **Welcome to M.K TRADER OFFICIAL HUB, Can I help you?**\n\n"
            "👑 **M.K TRADER thanks for contacting!**\n\n"
            "📊 **Free signals & official tools available here.**\n\n"
            "🌈 **Join now for free signals everyday**\n\n"
            "🚦 **If any problem sms me: T.me/MK_TRADER586**\n\n"
            "👇 **Select your option below:**"
        )
        keyboard = [
            [InlineKeyboardButton("🟢 VIP JOINING PROCESS", callback_data="vip_process")],
            [InlineKeyboardButton("🏛 HOW TO CREATE QUOTEX NEW ACCOUNT", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💠 HOW TO DELETE QUOTEX OLD ACCOUNT", callback_data="delete_old")],
            [InlineKeyboardButton("👇 OUR VIP GROUPS PIC'S", callback_data="vip_pics")],
            [InlineKeyboardButton("⭐ SEND TRADER ID HERE", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("📩 ANY QUESTION DM US", url="https://T.me/MK_TRADER586")]
        ]
        try:
            await query.edit_message_text(text=welcome_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

async def main_bot():
    TOKEN = "8764957005:AAHegnKTuSR3GoGQ_6gUn7DeTzgw9W6t-AU"

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("M.K TRADER Master Bot started successfully...")
    
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
