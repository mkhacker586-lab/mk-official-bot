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
        self.wfile.write(b"M.K TRADER Professional Master Bot is active 24/7!")

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
    
    welcome_text = (
        "👑 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐇𝐔𝐁 👑\n\n"
        f"✨ Hello {user.first_name}! Aapke trading safar ko behtareen aur profitable banane ke liye yeh official platform hai. 🚀🔥\n\n"
        "💎 Please select your desired option below:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🚀 𝐕𝐈𝐏 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐒𝐈𝐆𝐍𝐀𝐋𝐒", callback_data="vip_signals"),
            InlineKeyboardButton("🖤 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘", callback_data="loss_recovery")
        ],
        [
            InlineKeyboardButton("🆔 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍", callback_data="id_verification"),
            InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊", callback_data="send_feedback")
        ],
        [
            InlineKeyboardButton("🤖 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐀𝐈 𝐁𝐎𝐓", callback_data="ai_bot_access")
        ],
        [
            InlineKeyboardButton("👑 𝐑𝐎𝐘𝐀𝐋 𝐕𝐈𝐏 𝐏𝐋𝐀𝐍", callback_data="royal_plan"),
            InlineKeyboardButton("📊 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐓𝐎𝐎𝐋𝐒", callback_data="advanced_tools")
        ],
        [
            InlineKeyboardButton("💬 𝐀𝐃𝐌𝐈𝐍 𝐒𝐔𝐏𝐏𝐎𝐑𝐓", url="https://T.me/MK_TRADER586")
        ]
    ]
    
    try:
        await update.message.reply_text(
            welcome_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print(f"Start error: {e}")

# Button Click Handlers with separate clean pages
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "vip_signals":
        text = (
            "🚀 𝐕𝐈𝐏 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐀𝐍𝐄𝐋 🚀\n\n"
            "🔥 Get high-accuracy daily signals with proper risk management.\n"
            "⚡ Real-time market execution alerts for maximum profit.\n\n"
            "🎯 Step 1: Create your official account here:\n"
            "🔗 https://broker-qx.pro/?lid=1614511[span_0](start_span)[span_0](end_span)\n\n"
            "💬 Step 2: Send your ID to admin for VIP access:\n"
            "👉 T.me/MK_TRADER586[span_1](start_span)[span_1](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐀𝐃𝐌𝐈𝐍", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ]
        try:
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "loss_recovery":
        text = (
            "🚨 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 🚨\n\n"
            "📉 Facing continuous losses? Recover your account balance step-by-step with M.K Trader's expert strategies.\n\n"
            "✅ Step 1: Create a fresh account using our official link:\n"
            "🔗 https://broker-qx.pro/?lid=1614511[span_2](start_span)[span_2](end_span)\n\n"
            "✅ Step 2: Deposit funds and share your Trader ID directly with admin to join the recovery session:\n"
            "👉 T.me/MK_TRADER586[span_3](start_span)[span_3](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐀𝐃𝐌𝐈𝐍", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ]
        try:
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "id_verification":
        text = (
            "🆔 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍 🆔\n\n"
            "Want to verify your account for VIP signals and sessions? Follow these simple steps:\n\n"
            "1️⃣ Create your account through our official link:\n"
            "🔗 https://broker-qx.pro/?lid=1614511[span_4](start_span)[span_4](end_span)\n\n"
            "2️⃣ Complete minimum deposit in your account.\n\n"
            "3️⃣ Copy your Trader ID and send it directly to admin for verification:\n"
            "👉 T.me/MK_TRADER586[span_5](start_span)[span_5](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐈𝐃 𝐓𝐎 𝐀𝐃𝐌𝐈𝐍", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ]
        try:
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "send_feedback":
        text = (
            "💬 𝐒𝐄𝐍𝐃 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 & 𝐑𝐄𝐕𝐈𝐄𝐖𝐒 💬\n\n"
            "🔥 Share your profit screenshots, success stories, and recovery feedback with us!\n"
            "⭐ Your reviews help our community grow stronger.\n\n"
            "🔗 Send your feedback directly to admin:\n"
            "👉 T.me/MK_TRADER586[span_6](start_span)[span_6](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ 𝐒𝐄𝐍𝐃 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ]
        try:
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "ai_bot_access":
        text = (
            "🤖 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐀𝐈 𝐁𝐎𝐓 (𝐕𝐈𝐏 𝐀𝐂𝐂𝐄𝐒𝐒) 🤖\n\n"
            "🔒 Status: Paid Access & Key Verification System Setup.\n"
            "💎 Yeh section aage ke liye reserved hai jahan payment ke baad aapko automated AI Bot ki key aur access milega.\n\n"
            "💬 Abhi access lene ke liye admin se rabta karein:\n"
            "👉 T.me/MK_TRADER586[span_7](start_span)[span_7](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐀𝐃𝐌𝐈𝐍 𝐅𝐎𝐑 𝐀𝐂𝐂𝐄𝐒𝐒", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ]
        try:
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "royal_plan":
        text = (
            "👑 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐑𝐎𝐘𝐀𝐋 𝐕𝐈𝐏 𝐏𝐋𝐀𝐍 👑\n\n"
            "✅ Unlimited Signals • Direct VIP Access • 24/7 Personal Support\n"
            "🔥 Go Royal and maximize your daily trading profits.\n\n"
            "🎯 Step 1: Create account: https://broker-qx.pro/?lid=1614511[span_8](start_span)[span_8](end_span)\n"
            "🎯 Step 2: Send ID to admin: T.me/MK_TRADER586[span_9](start_span)[span_9](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("⭐ 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url="https://broker-qx.pro/?lid=1614511")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐀𝐃𝐌𝐈𝐍", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ]
        try:
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "advanced_tools":
        text = (
            "📊 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐓𝐎𝐎𝐋𝐒 📊\n\n"
            "⚡ Professional market analyzers & risk calculation guides.\n"
            "🔥 Coming soon with automated tools integration!\n\n"
            "💬 Contact admin for details: T.me/MK_TRADER586[span_10](start_span)[span_10](end_span)"
        )
        keyboard = [
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐀𝐃𝐌𝐈𝐍", url="https://T.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ]
        try:
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass

    elif query.data == "back_home":
        welcome_text = (
            "👑 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐇𝐔𝐁 👑\n\n"
            "✨ Hello! Aapke trading safar ko behtareen aur profitable banane ke liye yeh official platform hai. 🚀🔥\n\n"
            "💎 Please select your desired option below:"
        )
        keyboard = [
            [
                InlineKeyboardButton("🚀 𝐕𝐈𝐏 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐒𝐈𝐆𝐍𝐀𝐋𝐒", callback_data="vip_signals"),
                InlineKeyboardButton("🖤 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘", callback_data="loss_recovery")
            ],
            [
                InlineKeyboardButton("🆔 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍", callback_data="id_verification"),
                InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊", callback_data="send_feedback")
            ],
            [
                InlineKeyboardButton("🤖 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐀𝐈 𝐁𝐎𝐓", callback_data="ai_bot_access")
            ],
            [
                InlineKeyboardButton("👑 𝐑𝐎𝐘𝐀𝐋 𝐕𝐈𝐏 𝐏𝐋𝐀𝐍", callback_data="royal_plan"),
                InlineKeyboardButton("📊 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐓𝐎𝐎𝐋𝐒", callback_data="advanced_tools")
            ],
            [
                InlineKeyboardButton("💬 𝐀𝐃𝐌𝐈𝐍 𝐒𝐔𝐏𝐏𝐎𝐑𝐓", url="https://T.me/MK_TRADER586")
            ]
        ]
        try:
            await query.edit_message_text(text=welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))
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
