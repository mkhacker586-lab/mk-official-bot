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
        self.wfile.write(b"M.K TRADER Official Master Bot is running 24/7!")

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
            print("Self-ping successful, master bot is active!")
        except Exception as e:
            print(f"Self-ping error: {e}")
        import time
        time.sleep(240)

# Main Start Command with Brand Menu
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"Master Bot /start command aayi hai: {user.first_name} ki taraf se.")
    
    # HD Banner Image (Aap yahan apni pasand ka direct image link bhi daal sakte hain)
    photo_url = "https://i.postimg.cc/Pvt9mWMg/image.jpg"
    
    welcome_caption = (
        f"👑 **WELCOME TO M.K TRADER OFFICIAL HUB** 👑\n\n"
        f"Hello **{user.first_name}**! Aapke trading safar, loss recovery aur high accuracy signals ke liye yeh official platform hai. 🚀🔥\n\n"
        "⚡ **Yahan aapko milay ga:**\n"
        "📊 • 100% Verified Trading Signals\n"
        "🖤 • Personal 1-on-1 Loss Recovery Sessions\n"
        "🆔 • Quick Trader ID Verification\n"
        "⭐ • Real Client Feedbacks & Proofs\n\n"
        "👇 *Neche diye gaye buttons se apna option select karein:*"
    )
    
    keyboard = [
        [InlineKeyboardButton("🖤 LOSS RECOVERY SESSION", callback_data="recovery")],
        [InlineKeyboardButton("📊 M.K TRADER VIP CHANNEL", url="https://t.me/+neTu5arl0spkNjFk")],
        [InlineKeyboardButton("🆔 TRADER ID VERIFICATION", callback_data="verification")],
        [InlineKeyboardButton("⭐ FEEDBACKS & REVIEWS", callback_data="feedbacks")],
        [InlineKeyboardButton("💎 PAID ANALYSIS (COMING SOON)", callback_data="paid_analysis")],
        [InlineKeyboardButton("💬 ADMIN SUPPORT", url="https://t.me/MK_TRADER586")]
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

# Button Click Handler (Menu Navigation)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "recovery":
        recovery_text = (
            "🚨 **PERSONAL 1-on-1 LOSS RECOVERY SESSION** 🚨\n\n"
            "📉 Bar bar loss ho raha hai?\n"
            "🖤 Balance kam ho gaya hai ya proper strategy nahi hai?\n"
            "⚡️ Abhi M.K Trader ke sath apne loss ko recover karein!\n\n"
            "✅ Special OTC & Live Trading Strategy\n"
            "✅ High Accuracy Entry Timing\n"
            "✅ Strict Risk Management\n"
            "✅ Professional Account Handling 💼\n\n"
            "🎯 **Step 1:** Yahan account banayein: https://broker-qx.pro/?lid=1614510\n"
            "🏦 **Step 2:** Deposit karke apni Trader ID admin ko bhejein!\n\n"
            "💬 *Direct Contact:* @MK_TRADER586"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ CREATE QX ACCOUNT NOW ⭐", url="https://broker-qx.pro/?lid=1614510")],
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(
                caption=recovery_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass
        
    elif query.data == "verification":
        verif_text = (
            "🆔 **TRADER ID VERIFICATION GUIDE** 🆔\n\n"
            "M.K Trader VIP signals aur personal session ke liye apni Trader ID verify karwayein:\n\n"
            "1️⃣ Hamare official link se account banayein: https://broker-qx.pro/?lid=1614510\n"
            "2️⃣ Account mein minimum deposit karein.\n"
            "3️⃣ Apni **Quotex Trader ID** copy karein.\n"
            "4️⃣ ID copy karke foran admin ko bhej dein verification ke liye ✅\n\n"
            "💬 *Send ID to:* @MK_TRADER586"
        )
        keyboard = [
            [InlineKeyboardButton("🎯 CREATE QX ACCOUNT", url="https://broker-qx.pro/?lid=1614510")],
            [InlineKeyboardButton("💬 SEND ID TO ADMIN", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(
                caption=verif_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass

    elif query.data == "feedbacks":
        feedback_text = (
            "⭐ **M.K TRADER CLIENT FEEDBACKS & REVIEWS** ⭐\n\n"
            "Hamaray VIP members aur students ke real profit proofs aur feedbacks check karein:\n\n"
            "🔥 100% Real Profit Screenshots\n"
            "🔥 Successful Loss Recovery Results\n"
            "🔥 Trusted by Hundreds of Traders\n\n"
            "🔗 *Channel par feedbacks dekhne ke liye ya proof ke liye admin se rabta karein.*"
        )
        keyboard = [
            [InlineKeyboardButton("💬 CONTACT ADMIN FOR PROOF", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(
                caption=feedback_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass

    elif query.data == "paid_analysis":
        paid_text = (
            "💎 **M.K TRADER PAID ANALYSIS (VIP ACCESS)** 💎\n\n"
            "Yeh section un serious traders ke liye hai jo advanced market analysis aur special tools ka access chahte hain.\n\n"
            "🔒 **Status:** Coming Soon / Launching Very Soon!\n"
            "💰 *Jald hi yahan fee payment aur automatic access ka system add kiya jayega.*"
        )
        keyboard = [
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ]
        try:
            await query.edit_message_caption(
                caption=paid_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass
        
    elif query.data == "back_home":
        user = query.from_user
        welcome_caption = (
            f"👑 **WELCOME TO M.K TRADER OFFICIAL HUB** 👑\n\n"
            f"Hello **{user.first_name}**! Aapke trading safar aur loss recovery ke liye yeh official platform hai. 🚀🔥\n\n"
            "👇 *Neche diye gaye buttons se apna option select karein:*"
        )
        keyboard = [
            [InlineKeyboardButton("🖤 LOSS RECOVERY SESSION", callback_data="recovery")],
            [InlineKeyboardButton("📊 M.K TRADER VIP CHANNEL", url="https://t.me/+neTu5arl0spkNjFk")],
            [InlineKeyboardButton("🆔 TRADER ID VERIFICATION", callback_data="verification")],
            [InlineKeyboardButton("⭐ FEEDBACKS & REVIEWS", callback_data="feedbacks")],
            [InlineKeyboardButton("💎 PAID ANALYSIS (COMING SOON)", callback_data="paid_analysis")],
            [InlineKeyboardButton("💬 ADMIN SUPPORT", url="https://t.me/MK_TRADER586")]
        ]
        try:
            await query.edit_message_caption(
                caption=welcome_caption,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass

async def main_bot():
    TOKEN = "8764957005:AAHegnKTuSR3GoGQ_6gUn7DeTzgw9W6t-AU"

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("M.K TRADER Ultimate Master Bot successfully start ho gaya hai...")
    
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
