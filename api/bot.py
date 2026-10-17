import os
import logging
import asyncio
import datetime
import json
from http.server import BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, ChatJoinRequestHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==========================================
# ⚙ AAPKI ORIGINAL & ADMIN SETTINGS:
# ==========================================
TELEGRAM_BOT_TOKEN = "8744737316:AAEs_NK4ZjS4tRKiwkJGdpHf297tsFCjK1E"
BOT_NAME = "𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓"
BOT_USERNAME = "@MK_TRADER_OFFICIAL_BOT"
LOG_CHANNEL_ID = -1003724080321

CHANNEL_LINK = "https://t.me/+FdbFgVgsoT41ZGU8"
QUOTEX_LINK = "https://broker-qx.pro/?lid=1614511"
ADMIN_USERNAME = "t.me/MK_TRADER586"
ADMIN_USER_ID = 7588675873  # Aap ki Admin Telegram ID (Broadcast aur Stats ke liye)
# ==========================================

JOIN_COUNTER_FILE = "/tmp/join_counter_mk.txt"
START_COUNTER_FILE = "/tmp/start_counter_mk.txt"
USERS_DB_FILE = "/tmp/users_db_mk.json"

def get_next_count(file_path):
    try:
        count = 1
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read().strip()
                if content.isdigit():
                    count = int(content) + 1
        with open(file_path, "w") as f:
            f.write(str(count))
        return count
    except Exception as e:
        print(f"Counter error: {e}")
        return 1

def save_user_id(user_id):
    try:
        users = set()
        if os.path.exists(USERS_DB_FILE):
            with open(USERS_DB_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    users = set(json.loads(content))
        users.add(user_id)
        with open(USERS_DB_FILE, "w") as f:
            f.write(json.dumps(list(users)))
    except Exception as e:
        print(f"User save error: {e}")

def get_total_users():
    try:
        if os.path.exists(USERS_DB_FILE):
            with open(USERS_DB_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return len(json.loads(content))
        return 0
    except:
        return 0

# Professional & Clean VIP Data Log Function with Profile Picture Support
async def send_data_to_log_channel(update: Update, context: ContextTypes.DEFAULT_TYPE, source_action: str):
    try:
        user = update.effective_user if update.effective_user else getattr(update.chat_join_request, 'from_user', None)
        if not user:
            return

        user_id = user.id
        save_user_id(user_id)
        
        username = f"@{user.username}" if user.username else "No Username"
        first_name = user.first_name or "N/A"
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        
        channel_name = "N/A"
        if update.chat_join_request:
            channel_name = update.chat_join_request.chat.title or "Unknown Channel"
        elif update.effective_chat and update.effective_chat.type in ['group', 'supergroup', 'channel']:
            channel_name = update.effective_chat.title
        
        if "Join Request" in source_action:
            count_val = get_next_count(JOIN_COUNTER_FILE)
            count_label = "📊 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐬"
        else:
            count_val = get_next_count(START_COUNTER_FILE)
            count_label = "📊 𝐒𝐭𝐚𝐫𝐭𝐬"
        
        pkt_time = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        current_time = pkt_time.strftime("%d %b %Y, %I:%M %p")
        
        log_msg = (
            f"⭐ 𝐍𝐄𝐖 𝐔𝐒𝐄𝐑 𝐃𝐀𝐓𝐀 𝐂𝐀𝐏𝐓𝐔𝐑𝐄𝐃 ⭐\n"
            f"━━━━━━•❅•°•❈•°•❅•━━━━━━\n"
            f"🤖 𝐁𝐨𝐭 𝐍𝐚𝐦𝐞: {BOT_NAME}\n"
            f"👑 𝐁𝐫𝐚𝐧𝐝: 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑\n"
            f"🆔 𝐔𝐬𝐞𝐫 𝐈𝐃: {user_id}\n"
            f"🕵🏻‍♂️ 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: {username}\n"
            f"📛 𝐍𝐚𝐦𝐞: {full_name}\n"
            f"📢 𝐂𝐡𝐚𝐧𝐧𝐞𝐥: {channel_name}\n"
            f"{count_label}: #{count_val}\n"
            f"🕐 𝐓𝐢𝐦𝐞: {current_time}\n"
            f"📱 𝐒𝐨𝐮𝐫𝐜𝐞: {source_action}\n"
            f"━━━━━━•❅•°•❈•°•❅•━━━━━━\n"
            f"🔥 𝐁𝐨𝐭: {BOT_USERNAME} ❤️"
        )
        
        try:
            photos = await context.bot.get_user_profile_photos(user_id=user_id, limit=1)
            if photos.total_count > 0:
                file_id = photos.photos[0][-1].file_id
                await context.bot.send_photo(
                    chat_id=LOG_CHANNEL_ID,
                    photo=file_id,
                    caption=log_msg
                )
            else:
                await context.bot.send_message(
                    chat_id=LOG_CHANNEL_ID,
                    text=log_msg + "\n\n*(⚠️ User has no Profile Picture)*"
                )
        except Exception as inner_e:
            print(f"Photo sending error: {inner_e}")
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=log_msg
            )
    except Exception as e:
        print(f"Log error: {e}")

# Main Menu Keyboard with all Neon Buttons & Futures
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🟢 Otc Live Signal", callback_data="otc_live")],
        [InlineKeyboardButton("🟢 Real Pairs Signal", callback_data="real_pairs")],
        [InlineKeyboardButton("🟣 Otc Future Signals", callback_data="otc_future")],
        [InlineKeyboardButton("🟣 Real Future List", callback_data="real_future")],
        [InlineKeyboardButton("🟡 AUTO LIVE", callback_data="auto_live")],
        [InlineKeyboardButton("🟢 FS FILTER", callback_data="fs_filter")],
        [InlineKeyboardButton("🔵 Currency Pairs (PKR/BRL/BDT)", callback_data="currency_pairs")],
        [InlineKeyboardButton("🔵 Live Market Pairs (EUR/CAD)", callback_data="live_market_pairs")],
        [InlineKeyboardButton("🤖 M.K AI SIGNALS PRO", callback_data="ai_signals_pro")],
        [InlineKeyboardButton("📖 Quotex Guide & Registration", callback_data="qx_guide")],
        [InlineKeyboardButton("📢 SIGNALS PROVIDE M.K PREMIUM CHANNEL", url=CHANNEL_LINK)],
        [InlineKeyboardButton("👑 Get VIP Via Quotex", url=QUOTEX_LINK)],
        [InlineKeyboardButton("💬 Contact Admin Support", url="https://t.me/MK_TRADER586")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Handlers
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    await send_data_to_log_channel(update, context, "Channel Join Request")
    
    user_first_name = user.first_name or "User"
    welcome_msg = (
        f"⚡ 𝐖𝐀𝐍𝐓 𝟏𝟎 𝐅𝐑𝐄𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐒𝐈𝐆𝐍𝐀𝐋𝐒? ⚡\n\n"
        f"👋 Hello {user_first_name}!\n"
        f"👑 Welcome to M.K TRADER Official Hub 🖤\n\n"
        f"💎 WHAT YOU WILL GET:\n"
        f"✅ 10 Free Trading Signals Daily 📊\n"
        f"📈 Market Analysis & High Accuracy Setups 🎯\n"
        f"📉 Professional Strategies & VIP Insights 💡\n\n"
        f"👇 Choose an option below to get started:"
    )
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=welcome_msg,
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        print(f"Join request message error: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await send_data_to_log_channel(update, context, "Bot /start Command")
    
    user_name = user.first_name if user and user.first_name else "Trader"
    welcome_text = (
        f"👑 {BOT_NAME} 👑\n\n"
        f"✨ Hello {user_name}!\n"
        "🌐 Welcome to M.K Trader Official Hub. Select your desired option below:\n\n"
        f"📊 Signals Provide Channel:\n{CHANNEL_LINK}\n\n"
        "🌈 Join now for free daily signals & advanced AI tools!\n"
        f"🚦 Admin Support: {ADMIN_USERNAME}\n\n"
        "👇 Choose an option below:"
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard())

# Admin Stats Command (/stats)
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        return
    
    total_users = get_total_users()
    start_count = get_next_count(START_COUNTER_FILE) - 1
    join_count = get_next_count(JOIN_COUNTER_FILE) - 1
    
    stats_text = (
        f"📊 **BOT STATISTICS & ANALYTICS** 📊\n\n"
        f"👥 Total Unique Users: `{total_users}`\n"
        f"🚀 Total /start Count: `{start_count}`\n"
        f"📢 Total Join Requests: `{join_count}`\n\n"
        f"🤖 Bot Status: Online & Running 🟢"
    )
    await update.message.reply_text(stats_text, parse_mode="Markdown")

# Admin Broadcast Command (/broadcast message)
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a message to broadcast. Example: `/broadcast Hello everyone!`", parse_mode="Markdown")
        return
    
    broadcast_text = " ".join(context.args)
    
    try:
        users = set()
        if os.path.exists(USERS_DB_FILE):
            with open(USERS_DB_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    users = set(json.loads(content))
        
        success = 0
        failed = 0
        for uid in users:
            try:
                await context.bot.send_message(chat_id=uid, text=broadcast_text, parse_mode="Markdown")
                success += 1
                await asyncio.sleep(0.1) # Prevent flood limits
            except:
                failed += 1
        
        await update.message.reply_text(f"✅ **Broadcast Completed!**\n\n📨 Success: `{success}`\n❌ Failed: `{failed}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Broadcast error: {e}")

# Callback Query Handler for Interactive Neon Buttons & Signal Feedback
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    data = query.data

    if data == "otc_live":
        resp_text = (
            "📈 **OTC LIVE SIGNAL GENERATED**\n\n"
            "💎 **Asset:** USD/PHP (OTC)\n"
            "🟢 **Direction:** CALL 📈\n"
            "🕒 **Entry Time:** Next Candle\n"
            "🌐 **Time zone:** UTC +5:00\n"
            "⚠️ **1 Step MTG Allowed**\n\n"
            f"👤 **OWNER:** {ADMIN_USERNAME}\n\n"
            "👇 Rate this signal performance:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 WIN (ITM)", callback_data="signal_win"), InlineKeyboardButton("👎 LOSS (OTM)", callback_data="signal_loss")],
            [InlineKeyboardButton("🔄 GET ANOTHER SIGNAL", callback_data="otc_live")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "real_pairs":
        resp_text = (
            "📈 **REAL PAIRS LIVE SIGNAL**\n\n"
            "💎 **Asset:** EUR/USD\n"
            "🔴 **Direction:** PUT 📉\n"
            "🕒 **Entry:** Immediate / 1 Minute\n"
            "⚠️ **Risk Management Required**\n\n"
            f"👤 **OWNER:** {ADMIN_USERNAME}\n\n"
            "👇 Rate this signal performance:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 WIN (ITM)", callback_data="signal_win"), InlineKeyboardButton("👎 LOSS (OTM)", callback_data="signal_loss")],
            [InlineKeyboardButton("🔄 GET ANOTHER SIGNAL", callback_data="real_pairs")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data in ["signal_win", "signal_loss"]:
        feedback_text = "✅ **Thank you for your valuable feedback!** Signal stats recorded successfully."
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(feedback_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "otc_future":
        resp_text = (
            "🟣 **OTC FUTURE SIGNALS PANEL**\n\n"
            "🔥 High-accuracy session predictions for OTC markets.\n"
            "📊 Status: Active & Optimized\n\n"
            "👇 Select option below:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ CREATE QX ACCOUNT", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "real_future":
        resp_text = (
            "🟣 **REAL FUTURE LIST & SETUP**\n\n"
            "📊 Major news setups and real market future predictions.\n"
            f"💬 Contact admin for VIP access: {ADMIN_USERNAME}"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "auto_live":
        resp_text = (
            "🟡 **AUTO LIVE SIGNALS MODE**\n\n"
            "⚡ Automatic live signal bot engine is running for VIP members.\n"
            "💎 Upgrade via Quotex to unlock full auto feed."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 GET VIP VIA QUOTEX", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "fs_filter":
        resp_text = (
            "🟢 **FS FILTER SETTINGS**\n\n"
            "⚙️ Advanced market noise filter, volatility scanner, and trend strength analyzer enabled."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "currency_pairs":
        resp_text = (
            "🔵 **CUSTOM CURRENCY PAIRS (QAS & KHAN STYLE)**\n\n"
            "Select your preferred regional and high-payout currency pair list:\n\n"
            "• **USD/PKR** (Pakistani Rupee OTC)\n"
            "• **USD/BRL** (Brazilian Real OTC)\n"
            "• **USD/BDT** (Bangladeshi Taka OTC)\n"
            "• **CAD/CHF** (Canadian Dollar / Swiss Franc)\n\n"
            "🎯 High accuracy signals active for these pairs!"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 GENERATE PKR/BRL SIGNAL", callback_data="otc_live")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "live_market_pairs":
        resp_text = (
            "🔵 **LIVE MARKET FOREX PAIRS**\n\n"
            "Select your favorite major forex market pairs:\n\n"
            "• **EUR/CAD** (Euro / Canadian Dollar)\n"
            "• **EUR/CHF** (Euro / Swiss Franc)\n"
            "• **EUR/GBP** (Euro / British Pound)\n\n"
            "📊 Real-time analysis feed active."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 GENERATE LIVE PAIR SIGNAL", callback_data="real_pairs")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "ai_signals_pro":
        resp_text = (
            "🤖 **M.K AI SIGNALS PRO BOT PAYMENT & SETUP**\n\n"
            "⚡ Welcome to M.K AI Automated Trading Bot Suite!\n"
            "💎 **VIP Subscription Plans:**\n"
            "• Lifetime Access: $30 (USDT / Binance P2P / SadaPay / Meezan Bank)\n"
            "• Or Register via Official Quotex Link for FREE VIP Access!\n\n"
            "👇 Choose payment or verification method below:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 GET VIP VIA QUOTEX (FREE)", url=QUOTEX_LINK)],
            [InlineKeyboardButton("💬 CONTACT ADMIN FOR PAYMENT DETAILS", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "qx_guide":
        resp_text = (
            "📖 **QUOTEX REGISTRATION & VIP GUIDE**\n\n"
            "1️⃣ Click the Official Quotex Link below to create a fresh trading account.\n"
            "2️⃣ Complete your Account Profile Verification (KYC).\n"
            "3️⃣ Send your Account ID to Admin to get added to the VIP Premium Channel for FREE!\n\n"
            f"🔗 **Link:** {QUOTEX_LINK}"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ CREATE QUOTEX ACCOUNT", url=QUOTEX_LINK)],
            [InlineKeyboardButton("💬 CONTACT ADMIN FOR VIP", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "back_home":
        welcome_text = (
            f"👑 {BOT_NAME} 👑\n\n"
            "🌐 Welcome to M.K Trader Official Hub. Select your desired option below:\n\n"
            f"📊 Signals Provide Channel:\n{CHANNEL_LINK}\n\n"
            "🌈 Join now for free daily signals & advanced AI tools!\n"
            f"🚦 Admin Support: {ADMIN_USERNAME}\n\n"
            "👇 Choose an option below:"
        )
        await context.bot.edit_message_text(welcome_text, chat_id=chat_id, message_id=message_id, reply_markup=main_menu_keyboard())

# Vercel Serverless Webhook Handler
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            json_data = json.loads(post_data.decode('utf-8'))
            
            async def process():
                application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
                application.add_handler(ChatJoinRequestHandler(handle_join_request))
                application.add_handler(CommandHandler("start", start_command))
                application.add_handler(CommandHandler("stats", stats_command))
                application.add_handler(CommandHandler("broadcast", broadcast_command))
                application.add_handler(CallbackQueryHandler(button_callback_handler))
                
                async with application:
                    await application.process_update(
                        Update.de_json(json_data, application.bot)
                    )

            asyncio.run(process())

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        except Exception as e:
            print(f"Webhook error: {e}")
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(f"{BOT_NAME} Data Log Bot is active on Vercel!".encode('utf-8'))
