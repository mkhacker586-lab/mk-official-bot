import os
import logging
import asyncio
import datetime
import json
import html
from http.server import BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, ContextTypes, ChatJoinRequestHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==========================================
# ⚙ ADMIN & BOT SETTINGS:
# ==========================================
TELEGRAM_BOT_TOKEN = "8744737316:AAEs_NK4ZjS4tRKiwkJGdpHf297tsFCjK1E"
BOT_NAME = "𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓"
BOT_USERNAME = "@MK_TRADER_OFFICIAL_BOT"
LOG_CHANNEL_ID = -1003724080321
BROADCAST_CHANNEL_ID = -1004470268041  # M.K UPCOMING POSTINGS Channel ID

CHANNEL_LINK = "https://t.me/+FdbFgVgsoT41ZGU8"
QUOTEX_LINK = "https://broker-qx.pro/?lid=1614511"
ADMIN_USERNAME = "https://t.me/MK_TRADER586"
ADMIN_USER_ID = 7588675873
# ==========================================

WAITING_FOR_TRADER_ID = 1

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

# ==========================================
# 🌟 ORIGINAL DATA LOG FUNCTION (UNTOUCHED)
# ==========================================
async def send_data_to_log_channel(update: Update, context: ContextTypes.DEFAULT_TYPE, source_action: str):
    try:
        user = update.effective_user if update.effective_user else getattr(update.chat_join_request, 'from_user', None)
        if not user:
            return

        user_id = user.id
        save_user_id(user_id)
        
        username = f"@{user.username}" if user.username else "No Username"
        first_name = user.first_name or "Trader"
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
            f"⭐ <b>𝐍𝐄𝐖 𝐔𝐒𝐄𝐑 𝐃𝐀𝐓𝐀 𝐂𝐀𝐏𝐓𝐔𝐑𝐄𝐃</b> ⭐\n"
            f"━━━━━━•❅•°•❈•°•❅•━━━━━━\n"
            f"🤖 <b>𝐁𝐨𝐭 𝐍𝐚𝐦𝐞:</b> {html.escape(str(BOT_NAME))}\n"
            f"👑 <b>𝐁𝐫𝐚𝐧𝐝:</b> 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑\n"
            f"🆔 <b>𝐔𝐬𝐞𝐫 𝐈𝐃:</b> {user_id}\n"
            f"🕵🏻‍♂️ <b>𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞:</b> {html.escape(str(username))}\n"
            f"📛 <b>𝐍𝐚𝐦𝐞:</b> {html.escape(str(full_name))}\n"
            f"📢 <b>𝐂𝐡𝐚𝐧𝐧𝐞𝐥:</b> {html.escape(str(channel_name))}\n"
            f"{count_label}: #{count_val}\n"
            f"🕐 <b>𝐓𝐢𝐦𝐞:</b> {current_time}\n"
            f"📱 <b>𝐒𝐨𝐮𝐫𝐜𝐞:</b> {html.escape(str(source_action))}\n"
            f"━━━━━━•❅•°•❈•°•❅•━━━━━━\n"
            f"🔥 <b>𝐁𝐨𝐭:</b> {html.escape(str(BOT_USERNAME))} ❤️"
        )
        
        try:
            photos = await context.bot.get_user_profile_photos(user_id=user_id, limit=1)
            if photos.total_count > 0:
                file_id = photos.photos[0][-1].file_id
                await context.bot.send_photo(
                    chat_id=LOG_CHANNEL_ID,
                    photo=file_id,
                    caption=log_msg,
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(
                    chat_id=LOG_CHANNEL_ID,
                    text=log_msg + "\n\n<i>(⚠️ User has no Profile Picture)</i>",
                    parse_mode="HTML"
                )
        except Exception as inner_e:
            print(f"Photo sending error: {inner_e}")
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=log_msg,
                parse_mode="HTML"
            )
    except Exception as e:
        print(f"Log error: {e}")

# ==========================================
# 📌 MAIN MENU BUTTONS
# ==========================================
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 𝐎𝐓𝐂 𝐋𝐢𝐯𝐞 𝐒𝐢𝐠𝐧𝐚𝐥𝐬", callback_data="otc_live"), InlineKeyboardButton("📈 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬 𝐒𝐢𝐠𝐧𝐚𝐥𝐬", callback_data="analysis_signals")],
        [InlineKeyboardButton("🔮 𝐅𝐮𝐭𝐮𝐫𝐞 𝐒𝐢𝐠𝐧𝐚𝐥𝐬", callback_data="future_signals"), InlineKeyboardButton("📋 𝐅𝐮𝐭𝐮𝐫𝐞 𝐋𝐢𝐬𝐭", callback_data="future_list")],
        [InlineKeyboardButton("👤 𝐏𝐞𝐫𝐬𝐨𝐧𝐚𝐥 𝐒𝐞𝐬𝐬𝐢𝐨𝐧𝐬", callback_data="personal_sessions"), InlineKeyboardButton("💸 𝐋𝐨𝐬𝐬 𝐑𝐞𝐜𝐨𝐯𝐞𝐫𝐲 𝐒𝐞𝐬𝐬𝐢𝐨𝐧𝐬", callback_data="loss_recovery")],
        [InlineKeyboardButton("🎩 𝐇𝐨𝐰 𝐓𝐨 𝐂𝐑𝐄𝐀𝐓𝐄 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", callback_data="how_to_create"), InlineKeyboardButton("💎 𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆", callback_data="vip_joining")],
        [InlineKeyboardButton("📜 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐑𝐔𝐋𝐄𝐒", callback_data="trading_rules"), InlineKeyboardButton("💎 𝐌.𝐊 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐕𝐈𝐏", callback_data="mk_premium_vip")],
        [InlineKeyboardButton("⚡️ 𝐃𝐀𝐈𝐋𝐘 𝟑-𝐒𝐓𝐄𝐏 𝐂𝐎𝐌𝐏𝐎𝐔𝐍𝐃𝐈𝐍𝐆⚡️", callback_data="daily_compounding"), InlineKeyboardButton("$𝟑𝟎 𝐓𝐎 $𝟓𝟎𝟎 𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓", callback_data="tour_challenge")],
        [InlineKeyboardButton("🗑️ 𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐃𝐄𝐋𝐄𝐓𝐈𝐎𝐍", callback_data="acc_deleting"), InlineKeyboardButton("📖 𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍", callback_data="acc_creation_guidance")],
        [InlineKeyboardButton("📚 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐄𝐃𝐔𝐂𝐀𝐓𝐈𝐎𝐍", callback_data="trading_guidance"), InlineKeyboardButton("🏆 𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓 𝐉𝐎𝐈𝐍𝐈𝐍𝐆", callback_data="tournament_joining")],
        [InlineKeyboardButton("⏱️ 𝐌.𝐊 𝐃𝐀𝐈𝐋𝐘 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 𝐓𝐈𝐌𝐈𝐍𝐆𝐒", callback_data="session_timings")],
        [InlineKeyboardButton("🤖 𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎", callback_data="ai_signals_pro")],
        [InlineKeyboardButton("👑 𝐌.𝐊 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓 👑", url="https://t.me/MK_TRADER_OFFICIAL_BOT?start=start")],
        [InlineKeyboardButton("📢 𝐉𝐎𝐈𝐍 𝐌.𝐊 𝐏𝐑𝐄𝐌𝐈Ւ𝐌 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 🚀", url=CHANNEL_LINK)],
        [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==========================================
# 🎯 JOIN REQUEST PENDING HANDLER
# ==========================================
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    if not req:
        return

    user = req.from_user
    await send_data_to_log_channel(update, context, "Channel Join Request")
    
    pending_msg = (
        f"👑✨ <b>𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓</b> ✨👑\n\n"
        f"💎 <b>𝐇𝐄𝐋𝐋𝐎,</b> 😈☠️ 𝗠.𝐊 𝗛𝗔𝗖𝗞𝗘𝗥 ☠️😈!\n\n"
        f"⏳ <b>𝐉𝐎𝐈𝐍 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐏𝐄𝐍𝐃𝐈𝐍𝐆</b> ⏳\n\n"
        f"💌 Your join request has been received and is currently pending admin approval. You'll get access once your request is accepted. ❤️‍🔥\n\n"
        f"📜 <b>𝐂𝐎𝐌𝐌𝐔𝐍𝐈𝐓𝐘 𝐆𝐔𝐈𝐃𝐄𝐋𝐈𝐍𝐄𝐒</b>\n\n"
        f"🎯 <b>𝐅𝐎𝐋𝐋𝐎𝐖 𝐀𝐋𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒</b>\n"
        f"⏰ Join on time and stay active during scheduled sessions.\n\n"
        f"📝 <b>𝐒𝐄𝐍𝐃 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊</b>\n"
        f"✅ Submit your session feedback after every session.\n\n"
        f"📊 <b>𝐒𝐓𝐀𝐘 𝐔𝐏𝐃𝐀𝐓𝐄𝐃</b>\n"
        f"⚡ Follow official announcements and market updates.\n\n"
        f"🤝 <b>𝐌𝐀𝐈𝐍𝐓𝐀𝐈𝐍 𝐃𝐈𝐒𝐂𝐈𝐏𝐋𝐈𝐍𝐄</b>\n"
        f"💎 Respect community rules and follow the instructions.\n\n"
        f"🛡️ <b>𝐌𝐀𝐍𝐀𝐆𝐄 𝐑𝐈𝐒𝐊 𝐖𝐈𝐒𝐄𝐋𝐘</b>\n"
        f"Never make decisions without understanding the risks.\n\n"
        f"🚀 <b>𝐀𝐂𝐂𝐄𝐒𝐒 𝐀𝐋𝐋 𝐁𝐎𝐓 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒</b>\n\n"
        f"👇 <b>𝐂𝐋𝐈𝐂𝐊 𝐓𝐎 𝐎𝐏𝐄𝐍 𝐁𝐎𝐓 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃</b>"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
        [
            InlineKeyboardButton("👤 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍", url="https://t.me/m/jY55Z4p_Yzhk"),
            InlineKeyboardButton("💸 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘", url="https://t.me/m/i7Y4TWPaMWZk")
        ],
        [
            InlineKeyboardButton("💎 𝐕𝐈𝐏 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐀𝐂𝐂𝐄𝐒𝐒", url="https://t.me/m/7LE78wShYTc0"),
            InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)
        ],
        [InlineKeyboardButton("👀 𝐕𝐈𝐄𝐖 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🚀 𝐎𝐏𝐄𝐍 𝐁𝐎𝐓 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃", callback_data="back_home")]
    ])
    
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=pending_msg,
            reply_markup=kb,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Join request message error: {e}")

# Start Command Handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await send_data_to_log_channel(update, context, "Bot /start Command")
    
    user_name = html.escape(user.first_name if user and user.first_name else "Trader")
    welcome_text = (
        f"👑 <b>{BOT_NAME}</b> 👑\n\n"
        f"✨ <b>𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐁𝐀𝐂𝐊, {user_name.upper()}!</b>\n\n"
        f"🌐 <b>𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐇𝐔𝐁</b> 💎\n\n"
        f"📊 <b>𝐀𝐜𝐜𝐞𝐬𝐬 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐒𝐢𝐠𝐧𝐚𝐥𝐬, 𝐌𝐚𝐫𝐤𝐞𝐭 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐆𝐮𝐢𝐝𝐞𝐬, 𝐕𝐈𝐏 𝐀𝐜𝐜𝐞𝐬𝐬, 𝐚𝐧𝐝 𝐁𝐨𝐭 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 — 𝐀𝐥𝐥 𝐈𝐧 𝐎𝐧𝐞 𝐏𝐥𝐚𝐜𝐞.</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🔗 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐂𝐇𝐀𝐍𝐍𝐄𝐋:</b>\n"
        f"{CHANNEL_LINK}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ <b>𝐒𝐭𝐚𝐲 𝐂𝐨𝐧𝐧𝐞𝐜𝐭𝐞𝐝 • 𝐒𝐭𝐚𝐲 𝐈𝐧𝐟𝐨𝐫𝐦𝐞𝐝</b>\n\n"
        f"👇 <b>𝐒𝐄𝐋𝐄𝐂𝐓 𝐘𝐎𝐔𝐑 𝐃𝐄𝐒𝐈𝐑𝐄𝐃 𝐎𝐏𝐓𝐈𝐎𝐍</b>\n\n"
        f"🛡️ <i>Trading involves financial risk. Signals are not guaranteed profits.</i>"
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="HTML", disable_web_page_preview=True)

# Channel Command Handler (/channel)
async def channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_text = (
        f"👑 <b>{BOT_NAME}</b> 👑\n\n"
        f"📢 <b>𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋</b>\n\n"
        f"✨ <b>𝐒𝐭𝐚𝐲 𝐂𝐨𝐧𝐧𝐞𝐜𝐭𝐞𝐝 • 𝐒𝐭𝐚𝐲 𝐈𝐧𝐟𝐨𝐫𝐦𝐞𝐝</b>\n\n"
        f"🔥 <b>𝐆𝐞𝐭 𝐭𝐡𝐞 𝐋𝐚𝐭𝐞𝐬𝐭 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐔𝐩𝐝𝐚𝐭𝐞𝐬, 𝐌𝐚𝐫𝐤𝐞𝐭 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐒𝐢𝐠𝐧𝐚𝐥 𝐔𝐩𝐝𝐚𝐭𝐞𝐬, 𝐚𝐧𝐝 𝐎𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐀𝐧𝐧𝐨𝐮𝐧𝐜𝐞𝐦𝐞𝐧𝐭𝐬.</b>\n\n"
        f"👇 <b>𝐓𝐚𝐩 𝐭𝐡𝐞 𝐁𝐮𝐭𝐭𝐨𝐧 𝐁𝐞𝐥𝐨𝐰 𝐭𝐨 𝐉𝐨𝐢𝐧 𝐎𝐮𝐫 𝐎𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐂𝐡𝐚𝐧𝐧𝐞𝐥!</b> 📢"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 𝐉𝐎𝐈𝐍 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
    ])
    await update.message.reply_text(resp_text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

# Signals Command Handler (/signals)
async def signals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_text = (
        f"👑 <b>{BOT_NAME}</b> 👑\n\n"
        f"📊 <b>𝐋𝐈𝐕𝐄 𝐎𝐓𝐂 & 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐇𝐔𝐁</b> 📊\n\n"
        f"✨ <b>Access high-accuracy market predictions and professional technical setups:</b>\n\n"
        f"⚡ <b>𝐋𝐈𝐕𝐄 𝐌𝐀𝐑𝐊𝐄𝐓 𝐓𝐑𝐄𝐍𝐃𝐒:</b>\nGet instant updates on running market sessions and active asset movements.\n\n"
        f"📈 <b>𝐏𝐑𝐈𝐂𝐄 𝐀𝐂𝐓𝐈𝐎𝐍 & 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒:</b>\nExplore detailed support/resistance levels and professional chart breakdowns.\n\n"
        f"🎯 <b>𝐒𝐈𝐆𝐍𝐀𝐋 𝐎𝐏𝐓𝐈𝐎𝐍𝐒:</b>\nChoose between OTC live signals, trend analysis, and future predictions.\n\n"
        f"👇 <b>𝐒𝐄𝐋𝐄𝐂𝐓 𝐘𝐎𝐔𝐑 𝐏𝐑𝐄𝐅𝐄𝐑𝐑𝐄𝐃 𝐎𝐏𝐓𝐈𝐎𝐍 𝐅𝐑𝐎𝐌 𝐓𝐇𝐄 𝐌𝐄𝐍𝐔 𝐁𝐄𝐋𝐎𝐖:</b>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 𝐎𝐓𝐂 𝐋𝐢𝐯𝐞 𝐒𝐢𝐠𝐧𝐚𝐥𝐬", callback_data="otc_live"), InlineKeyboardButton("📈 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬 𝐒𝐢𝐠𝐧𝐚𝐥𝐬", callback_data="analysis_signals")],
        [InlineKeyboardButton("🔮 𝐅𝐮𝐭𝐮𝐫𝐞 𝐒𝐢𝐠𝐧𝐚𝐥𝐬", callback_data="future_signals")],
        [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
    ])
    await update.message.reply_text(resp_text, reply_markup=kb, parse_mode="HTML")

# VIP Command Handler (/vip)
async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_text = (
        f"👑 <b>{BOT_NAME}</b> 👑\n\n"
        f"💎 <b>𝐕𝐈𝐏 𝐏𝐑𝐎𝐆𝐑𝐀𝐌 & 𝐉𝐎𝐈𝐍𝐈𝐍𝐆</b>\n\n"
        f"✨ <b>Unlock exclusive advantages and elevate your trading journey with elite membership:</b>\n\n"
        f"📊 Explore Market Analysis, Trading Setups, Signal Updates, and VIP Channel Content.\n\n"
        f"🔗 <b>𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:</b>\n{QUOTEX_LINK} 🌐\n\n"
        f"👇 <b>𝐒𝐄𝐋𝐄𝐂𝐓 𝐀𝐍𝐘 𝐎𝐏𝐓𝐈𝐎𝐍 𝐅𝐑𝐎𝐌 𝐓𝐇𝐄 𝐌𝐄𝐍𝐔 𝐁𝐄𝐋𝐎𝐖:</b>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
        [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start")],
        [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
        [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
    ])
    await update.message.reply_text(resp_text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

# Contact Owner Command Handler (/contact)
async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_text = (
        f"👑 <b>{BOT_NAME}</b> 👑\n\n"
        f"💬 <b>𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌.𝐊 𝐎𝐖𝐍𝐄𝐑</b> 💬\n\n"
        f"✨ <i>If you have any questions, need VIP access approval, or want personal guidance, click the button below to contact the owner directly:</i>\n\n"
        f"🔗 <b>𝐃𝐈𝐑𝐄𝐂𝐓 𝐂𝐎𝐍𝐓𝐀𝐂𝐓:</b>\n{ADMIN_USERNAME} 🌐\n\n"
        f"👇 <i>Tap the \"💬 CONTACT OWNER NOW\" button below!</i> ✅"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 𝐍𝐎𝐖", url=ADMIN_USERNAME)],
        [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
    ])
    await update.message.reply_text(contact_text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

# Admin Stats Command
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        return
    
    total_users = get_total_users()
    start_count = get_next_count(START_COUNTER_FILE) - 1
    join_count = get_next_count(JOIN_COUNTER_FILE) - 1
    
    stats_text = (
        f"📊 <b>𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 & 𝐀𝐍𝐀𝐋𝐘𝐓𝐈𝐂𝐒</b> 📊\n\n"
        f"👥 Total Unique Users: <code>{total_users}</code>\n"
        f"🚀 Total /start Count: <code>{start_count}</code>\n"
        f"📢 Total Join Requests: <code>{join_count}</code>\n\n"
        f"🤖 Bot Status: Online & Running 🟢"
    )
    await update.message.reply_text(stats_text, parse_mode="HTML")

# Admin Broadcast Command
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a message to broadcast. Example: <code>/broadcast Hello everyone!</code>", parse_mode="HTML")
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
                await context.bot.send_message(chat_id=uid, text=broadcast_text, parse_mode="HTML", disable_web_page_preview=True)
                success += 1
                await asyncio.sleep(0.02)
            except:
                failed += 1
        
        await update.message.reply_text(f"✅ <b>𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝!</b>\n\n📨 Success: <code>{success}</code>\n❌ Failed: <code>{failed}</code>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Broadcast error: {e}")

# Automatic Forwarder from Upcoming Postings Channel
async def forward_channel_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.channel_post or update.edited_channel_post
        if message and message.chat.id == BROADCAST_CHANNEL_ID:
            users = set()
            if os.path.exists(USERS_DB_FILE):
                with open(USERS_DB_FILE, "r") as f:
                    content = f.read().strip()
                    if content:
                        users = set(json.loads(content))
            
            for uid in users:
                try:
                    await context.bot.copy_message(
                        chat_id=uid,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                    await asyncio.sleep(0.01)
                except Exception as ex:
                    print(f"Forward error to user {uid}: {ex}")
    except Exception as e:
        print(f"Channel forward handler error: {e}")

# Trader ID Verification Flow
async def verify_id_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        f"👑 <b>{BOT_NAME}</b> 👑\n\n"
        f"🔐 <b>𝐕𝐄𝐑𝐈𝐅𝐘 𝐘𝐎𝐔𝐑 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃</b> 🔐\n\n"
        f"Please reply to this message with your 8-digit Quotex Trader ID.\n\n"
        f"<i>(Example: <code>12345678</code>)</i>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
        [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
    ])
    await context.bot.edit_message_text(text, chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=kb, parse_mode="HTML")
    return WAITING_FOR_TRADER_ID

async def receive_trader_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    trader_id = html.escape(update.message.text.strip())
    
    admin_log_msg = (
        f"🚨 <b>𝐍𝐄𝐖 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐒𝐔𝐁𝐌𝐈𝐓𝐓𝐄𝐃 𝐅𝐎𝐑 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍</b> 🚨\n\n"
        f"👤 User: {html.escape(str(user.full_name))} (@{html.escape(str(user.username if user.username else 'No Username'))})\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"🔢 Submitted Trader ID: <code>{trader_id}</code>"
    )
    await context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=admin_log_msg, parse_mode="HTML")
    
    success_text = (
        f"👑 <b>{BOT_NAME}</b> 👑\n\n"
        f"✅ <b>𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘!</b>\n\n"
        f"Your Trader ID (<code>{trader_id}</code>) has been sent to M.K Trader admin for verification. You will be granted VIP access shortly upon review!"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
        [InlineKeyboardButton("🚀 𝐎𝐏𝐄𝐍 𝐁𝐎𝐓 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃", callback_data="back_home")]
    ])
    await update.message.reply_text(success_text, reply_markup=kb, parse_mode="HTML")
    return ConversationHandler.END

async def cancel_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start_command(update, context)
    return ConversationHandler.END

# ==========================================
# 📄 BUTTON CALLBACK HANDLER (EXACT LOGIC REQUESTED)
# ==========================================
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    data = query.data

    # 1. OTC LIVE SIGNALS (NEW MESSAGE WITH DELETE ANIMATION)
    if data == "otc_live":
        loading_msg = await context.bot.send_message(
            chat_id=chat_id,
            text="🔄 <b>Scanning Market Volatility & Technical Indicators...</b> Please wait ⏳",
            parse_mode="HTML"
        )
        await asyncio.sleep(1)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
        except:
            pass
        
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"📊 <b>𝐎𝐓𝐂 𝐋𝐈𝐕𝐄 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐄𝐍𝐆𝐈𝐍𝐄</b> 📊\n\n"
            f"✨ Welcome to the professional OTC live trading hub. Here you receive high-accuracy real-time signals optimized for current market session.\n\n"
            f"💎 <b>Asset:</b> USD/PHP (OTC)\n"
            f"🟢 <b>Direction:</b> CALL (BUY) 📈\n"
            f"🕒 <b>Entry Time:</b> Next Candle / 1 Minute Expiry\n"
            f"🌐 <b>Time Zone:</b> Pakistan Standard Time (PKT)\n"
            f"⚠️ <b>Rule:</b> 1 Step MTG Allowed\n\n"
            f"👤 <b>Analyst:</b> {ADMIN_USERNAME}\n\n"
            f"👇 <b>Rate your trade performance below:</b>"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 𝐖𝐈𝐍 (𝐈𝐓𝐌)", callback_data="signal_win"), InlineKeyboardButton("👎 𝐋𝐎𝐒𝐒 (𝐎𝐓𝐌)", callback_data="signal_loss")],
            [InlineKeyboardButton("🔄 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐄 𝐍𝐄𝐖 𝐒𝐈𝐆𝐍𝐀𝐋", callback_data="otc_live")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home_delete")]
        ])
        await context.bot.send_message(chat_id=chat_id, text=resp_text, reply_markup=kb, parse_mode="HTML")

    # 2. ANALYSIS SIGNALS (NEW MESSAGE WITH DELETE ANIMATION)
    elif data == "analysis_signals":
        loading_msg = await context.bot.send_message(
            chat_id=chat_id,
            text="🔄 <b>Analyzing OTC Market Trends & Price Action...</b> Please wait ⏳",
            parse_mode="HTML"
        )
        await asyncio.sleep(1)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
        except:
            pass
        
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"📈 <b>𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐇𝐔𝐁</b> 📈\n\n"
            f"✨ Detailed technical and price action market analysis signals for digital options trading.\n\n"
            f"💎 <b>Asset:</b> EUR/USD (Live Market)\n"
            f"🔴 <b>Direction:</b> PUT (SELL) 📉\n"
            f"🕒 <b>Entry:</b> Immediate / 1 Minute Expiry\n"
            f"💡 <b>Setup Explanation:</b> Strong resistance level rejection accompanied by volume exhaustion.\n\n"
            f"👤 <b>Analyst:</b> {ADMIN_USERNAME}\n\n"
            f"👇 <b>Rate your trade performance below:</b>"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 𝐖𝐈𝐍 (𝐈𝐓𝐌)", callback_data="signal_win"), InlineKeyboardButton("👎 𝐋𝐎𝐒𝐒 (𝐎𝐓𝐌)", callback_data="signal_loss")],
            [InlineKeyboardButton("🔄 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐄 𝐍𝐄𝐖 𝐒𝐈𝐆𝐍𝐀𝐋", callback_data="analysis_signals")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home_delete")]
        ])
        await context.bot.send_message(chat_id=chat_id, text=resp_text, reply_markup=kb, parse_mode="HTML")

    # 3. FUTURE SIGNALS (NEW MESSAGE WITH DELETE ANIMATION)
    elif data == "future_signals":
        loading_msg = await context.bot.send_message(
            chat_id=chat_id,
            text="🔄 <b>Syncing Pakistan Local Time & Future Market Predictions...</b> Please wait ⏳",
            parse_mode="HTML"
        )
        await asyncio.sleep(1)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
        except:
            pass
        
        now_pkt = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        t1 = (now_pkt + datetime.timedelta(minutes=5)).strftime("%I:%M %p")
        t2 = (now_pkt + datetime.timedelta(minutes=15)).strftime("%I:%M %p")
        t3 = (now_pkt + datetime.timedelta(minutes=25)).strftime("%I:%M %p")
        t4 = (now_pkt + datetime.timedelta(minutes=35)).strftime("%I:%M %p")
        t5 = (now_pkt + datetime.timedelta(minutes=45)).strftime("%I:%M %p")
        t6 = (now_pkt + datetime.timedelta(minutes=55)).strftime("%I:%M %p")
        t7 = (now_pkt + datetime.timedelta(minutes=65)).strftime("%I:%M %p")
        t8 = (now_pkt + datetime.timedelta(minutes=75)).strftime("%I:%M %p")
        
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"🔮 <b>𝟖 𝐅𝐔𝐓𝐔𝐑𝐄 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄</b> 🔮\n\n"
            f"📅 <b>Date:</b> Today's Live Active Session\n"
            f"🌐 <b>Timezone:</b> Pakistan Standard Time (PKT)\n\n"
            f"1. 🕒 {t1} | 💎 GBP/USD (OTC) | 📈 UP (CALL)\n"
            f"2. 🕒 {t2} | 💎 EUR/JPY | 📉 DOWN (PUT)\n"
            f"3. 🕒 {t3} | 💎 AUD/CAD (OTC) | 📈 UP (CALL)\n"
            f"4. 🕒 {t4} | 💎 USD/BDT (OTC) | 📉 DOWN (PUT)\n"
            f"5. 🕒 {t5} | 💎 EUR/CAD | 📈 UP (CALL)\n"
            f"6. 🕒 {t6} | 💎 NZD/USD (OTC) | 📉 DOWN (PUT)\n"
            f"7. 🕒 {t7} | 💎 EUR/GBP | 📈 UP (CALL)\n"
            f"8. 🕒 {t8} | 💎 USD/JPY (OTC) | 📉 DOWN (PUT)\n\n"
            f"⚠️ <b>Note:</b> Follow strict risk management and prepare your entries ahead of time."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 𝐑𝐄𝐅𝐑𝐄𝐒𝐇 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄", callback_data="future_signals")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home_delete")]
        ])
        await context.bot.send_message(chat_id=chat_id, text=resp_text, reply_markup=kb, parse_mode="HTML")

    # ==========================================
    # 4. ALL OTHER BUTTONS (REPLACE ON SAME POST, NO DELETE UNTIL BACK)
    # ==========================================
    elif data == "ai_signals_pro":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"🤖 <b>𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎</b> 🤖\n\n"
            f"🚀 <b>𝐄𝐋𝐄𝐕𝐀𝐓𝐄 𝐘𝐎𝐔𝐑 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐆𝐀𝐌𝐄!</b>\n\n"
            f"📊 Explore AI-assisted trading signals and market insights with our premium signals bot, designed for traders who want a smarter trading experience. ⚡🎯\n\n"
            f"💎 <b>𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐀𝐂𝐂𝐄𝐒𝐒:</b>\n"
            f"💵 Subscription Fee: $20 ONLY\n\n"
            f"📌 <b>𝐇𝐎𝐖 𝐓𝐎 𝐉𝐎𝐈𝐍:</b>\n"
            f"1️⃣ 💳 Complete your $20 subscription payment.\n"
            f"2️⃣ 🧾 Send your payment receipt to the owner.\n"
            f"3️⃣ ✅ Wait for instant payment verification.\n"
            f"4️⃣ 🔓 Receive full instructions to access the bot!\n\n"
            f"👑 <b>𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎</b>\n"
            f"✨ <b>𝐒𝐌𝐀𝐑𝐓 𝐈𝐍𝐒𝐈𝐆𝐇𝐓𝐒 • 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐀𝐂𝐂𝐄𝐒𝐒</b> ✨\n\n"
            f"💬 <b>𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏 𝐎𝐑 𝐑𝐄𝐀𝐃𝐘 𝐓𝐎 𝐏𝐀𝐘?</b>\n"
            f"Tap the \"💳 𝐏𝐀𝐘𝐌𝐄𝐍𝐓\" or \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐕𝐈𝐏 𝐋𝐈𝐍𝐊", url=QUOTEX_LINK)],
            [InlineKeyboardButton("💳 𝐏𝐀𝐘𝐌𝐄𝐍𝐓", url=ADMIN_USERNAME), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "future_list":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"📋 <b>𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍 & 𝐅𝐔𝐓𝐔𝐑𝐄 𝐋𝐈𝐒𝐓</b> 📋\n\n"
            f"✨ Everything you need to master the market — essential insights, asset analysis, and pro guidance all in one place:\n\n"
            f"💎 <b>𝐀𝐒𝐒𝐄𝐓 𝐃𝐈𝐑𝐄𝐂𝐓𝐎𝐑𝐘:</b>\nExplore major currency pairs, OTC assets, and high-yield market instruments.\n\n"
            f"🌍 <b>𝐌𝐀𝐑𝐊𝐄𝐓 𝐓𝐈𝐌𝐈𝐍𝐆𝐒:</b>\nOptimize your setups across Asian, London, and New York trading sessions.\n\n"
            f"📈 <b>𝐏𝐑𝐈𝐂𝐄 𝐀𝐂𝐓𝐈𝐎𝐍 𝐆𝐔𝐈𝐃𝐄:</b>\nMaster key chart patterns, market trends, and high-probability price movements.\n\n"
            f"🛡️ <b>𝐑𝐈𝐒𝐊 𝐀𝐖𝐀𝐑𝐄𝐍𝐄𝐒𝐒:</b>\nImplement strict capital protection rules and disciplined decision-making.\n\n"
            f"⏱️ <b>𝐄𝐗𝐏𝐈𝐑𝐘 𝐓𝐈𝐌𝐄 𝐆𝐔𝐈𝐃𝐄:</b>\nUnderstand 1-minute and 5-minute execution strategies and key differences.\n\n"
            f"📚 <b>𝐏𝐑𝐎 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐓𝐄𝐑𝐌𝐒:</b>\nLearn essential market vocabulary, technical terms, and core definitions.\n\n"
            f"🔗 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:</b>\n{QUOTEX_LINK} 🌐\n\n"
            f"💬 <b>𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?</b>\nTap the \"💬 CONTACT OWNER\" button below for direct assistance! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄", callback_data="trading_guidance")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "personal_sessions":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"👤 <b>𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 & 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄</b> 👤\n\n"
            f"✨ Get exclusive one-to-one personal sessions with 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 and experience direct mentorship, individual attention & personalized market guidance.\n\n"
            f"💎 <b>𝐎𝐍𝐄-𝐓𝐎-𝐎𝐍𝐄 𝐌𝐄𝐍𝐓𝐎𝐑𝐒𝐇𝐈𝐏</b>\nEnjoy private sessions with direct interaction and personal guidance.\n\n"
            f"📊 <b>𝐈𝐍𝐃𝐈𝐕𝐈𝐃𝐔𝐀𝐋 𝐌𝐀𝐑𝐊𝐄𝐓 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒</b>\nDiscuss chart patterns, market movements & trading strategies personally.\n\n"
            f"🎯 <b>𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋𝐈𝐙𝐄𝐃 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐏𝐋𝐀𝐍</b>\nSessions arranged according to your availability and learning requirements.\n\n"
            f"🧠 <b>𝐃𝐈𝐑𝐄𝐂𝐓 𝐏𝐑𝐎𝐅𝐄𝐒𝐒𝐈𝐎𝐍𝐀𝐋 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄</b>\nGet personal attention on trading psychology, discipline & risk management.\n\n"
            f"👑 <b>𝐄𝐗𝐂𝐋𝐔𝐒𝐈𝐕𝐄 𝐕𝐈𝐏 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐀𝐂𝐂𝐄𝐒𝐒</b>\nA private learning experience with direct communication and dedicated mentorship.\n\n"
            f"🔥 <b>𝐘𝐎𝐔𝐑 𝐒𝐄𝐒𝐒𝐈𝐎𝐍. 𝐘𝐎𝐔𝐑 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄. 𝐘𝐎𝐔𝐑 𝐋𝐄𝐀𝐑𝐍𝐈𝐍𝐆.</b>\n\n"
            f"👇 <b>𝐂𝐋𝐈𝐂𝐊 𝐁𝐄𝐋𝐎𝐖 𝐓𝐎 𝐔𝐍𝐋𝐎𝐂𝐊 𝐕𝐈𝐏 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 𝐎𝐑 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐅𝐎𝐑 𝐘𝐎𝐔𝐑 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍:</b>"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐅𝐎𝐑 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "loss_recovery":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"💸 <b>𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 & 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄</b> 💸\n\n"
            f"✨ Faced trading losses? Get dedicated one-to-one recovery guidance with 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑. Review previous trades, understand what went wrong & learn a more disciplined approach before making your next decision.\n\n"
            f"📉 <b>𝐏𝐑𝐄𝐕𝐈𝐎𝐔𝐒 𝐋𝐎𝐒𝐒 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒</b>\n• Detailed review of previous trades and mistakes.\n\n"
            f"💎 <b>𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 𝐏𝐋𝐀𝐍𝐍𝐈𝐍𝐆</b>\n• Individual guidance to review your situation and plan your next steps responsibly.\n\n"
            f"🧠 <b>𝐄𝐌𝐎𝐓𝐈𝐎𝐍𝐀𝐋 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 & 𝐃𝐈𝐒𝐂𝐈𝐏𝐋𝐈𝐍𝐄</b>\n• Learn to avoid revenge trading and impulsive decisions.\n\n"
            f"🛡️ <b>𝐑𝐈𝐒𝐊 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓</b>\n• Understand risk limits and protect yourself from further unnecessary exposure.\n\n"
            f"👤 <b>𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐕𝐈𝐏 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄</b>\n• Get one-to-one educational support and individual trade reviews.\n\n"
            f"💎 <b>𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 — 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄</b>\n\n"
            f"👇 <b>𝐂𝐋𝐈𝐂𝐊 𝐁𝐄𝐋𝐎𝐖 𝐓𝐎 𝐄𝐗𝐏𝐋𝐎𝐑𝐄 𝐕𝐈𝐏 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 𝐎𝐑 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐓𝐇𝐄 𝐎𝐖𝐍𝐄𝐑</b>"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "how_to_create":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"🎩 <b>𝐇𝐎𝐖 𝐓𝐎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐀𝐍𝐃 𝐕𝐄𝐑𝐈𝐅𝐘 𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓</b> 🎩\n\n"
            f"✨ Follow these simple steps to activate your VIP access:\n\n"
            f"1️⃣ <b>𝐂𝐑𝐄𝐀𝐓𝐄 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:</b>\nRegister your new account using the secure link provided below.\n\n"
            f"2️⃣ <b>𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄 𝐒𝐄𝐓𝐔𝐏:</b>\nFinish your profile setup and complete your KYC identity verification.\n\n"
            f"3️⃣ <b>𝐂𝐎𝐏𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:</b>\nGo to your account dashboard and copy your official 8-digit Trader ID.\n\n"
            f"4️⃣ <b>𝐒𝐔𝐁𝐌𝐈𝐓 𝐅𝐎𝐑 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍:</b>\nTap \"🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃\" below and submit your ID to the bot.\n\n"
            f"5️⃣ <b>𝐔𝐍𝐋𝐎𝐂𝐊 𝐕𝐈𝐏 𝐀𝐂𝐂𝐄𝐒𝐒:</b>\nOnce verified by the team, your full VIP membership will be activated automatically!\n\n"
            f"🔗 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:</b>\n{QUOTEX_LINK} 🌐\n\n"
            f"💬 <b>𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?</b>\nTap the \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below to message support directly! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "vip_joining":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"💎 <b>𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 & 𝐄𝐋𝐈𝐆𝐈𝐁𝐈𝐋𝐈𝐓𝐘 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄</b> 💎\n\n"
            f"✨ Unlock elite financial benefits with M.K VIP Membership:\n\n"
            f"🎯 <b>𝟐𝟒/𝟕 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐇𝐢𝐠𝐡-𝐀𝐜𝐜𝐮𝐫𝐚𝐜𝐲 𝐒𝐢𝐠𝐧𝐚𝐥𝐬 𝐅𝐞𝐞𝐝</b>\n"
            f"🤖 <b>𝐀𝐮𝐭𝐨𝐦𝐚𝐭𝐞𝐝 𝐀𝐈 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐁𝐨𝐭 𝐅𝐮𝐥𝐥 𝐀𝐜𝐜𝐞𝐬𝐬</b>\n"
            f"📈 <b>𝐄𝐱𝐜𝐥𝐮𝐬𝐢𝐯𝐞 𝐂𝐨𝐦𝐩𝐨𝐮𝐧𝐝 𝐒𝐞𝐬𝐬𝐢𝐨𝐧𝐬 & 𝐌𝐞𝐧𝐭𝐨𝐫𝐬𝐡𝐢𝐩</b>\n\n"
            f"📌 <b>𝐒𝐓𝐄𝐏-𝐁𝐘-𝐒𝐓𝐄𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 𝐆𝐔𝐈𝐃𝐄:</b>\n\n"
            f"1️⃣ <b>𝐂𝐑𝐄𝐀𝐓𝐄 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:</b>\nRegister your new account using the secure link provided below.\n\n"
            f"2️⃣ <b>𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:</b>\nComplete profile setup, then tap \"🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃\" below to submit your 8-digit ID.\n\n"
            f"3️⃣ <b>𝐈𝐍𝐒𝐓𝐀𝐍𝐓 𝐀𝐂𝐂𝐄𝐒𝐒:</b>\nGet instant approval and unlock full VIP trading privileges!\n\n"
            f"🔗 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:</b>\n{QUOTEX_LINK} 🌐\n\n"
            f"💬 <b>𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?</b>\nTap the \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below for direct assistance! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "trading_rules":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"📜 <b>𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐑𝐔𝐋𝐄𝐒 & 𝐏𝐒𝐘𝐂𝐇𝐎𝐋𝐎𝐆𝐘 𝐆𝐔𝐈𝐃𝐄</b> 📜\n\n"
            f"✨ Build a professional trading mindset and protect your capital with core discipline:\n\n"
            f"🧠 <b>𝐄𝐌𝐎𝐓𝐈𝐎𝐍𝐀𝐋 𝐂𝐎𝐍𝐓𝐑𝐎𝐋:</b>\nNever trade with revenge mindset after a loss. Stay calm and stick to your strategy.\n\n"
            f"🛡️ <b>𝐓𝐇𝐑𝐄𝐄-𝐋𝐎𝐒𝐒 𝐒𝐓𝐎𝐏 𝐑𝐔𝐋𝐄:</b>\nIf you hit 3 consecutive losses, close your charts immediately and take a break.\n\n"
            f"🎯 <b>𝐃𝐀𝐈𝐋𝐘 𝐓𝐀𝐑𝐆𝐄𝐓 𝐃𝐈𝐒𝐂𝐈𝐏𝐋𝐈𝐍𝐄:</b>\nSet daily profit goals. Once your target is achieved, stop trading and protect your gains.\n\n"
            f"📊 <b>𝐂𝐀𝐏𝐈𝐓𝐀𝐋 𝐏𝐑𝐎𝐓𝐄𝐂𝐓𝐈𝐎𝐍:</b>\nNever risk more than 2% to 5% of your total account balance on a single trade.\n\n"
            f"💬 <b>𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?</b>\nTap the \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below for direct assistance! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME), InlineKeyboardButton("💎 𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆", callback_data="vip_joining")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "mk_premium_vip":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"💎 <b>𝐌.𝐊 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐕𝐈𝐏 𝐌𝐄𝐌𝐁𝐄𝐑𝐒𝐇𝐈𝐏</b> 💎\n\n"
            f"✨ Elevate your trading with exclusive VIP access, high-precision signals, and daily market analysis!\n\n"
            f"📊 <b>𝐕𝐈𝐏 𝐄𝐗𝐂𝐋𝐔𝐒𝐈𝐕𝐄 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒:</b>\n"
            f"🎯 Daily 90%+ Accuracy Signal Setups\n"
            f"📈 Private Risk & Money Management Plan\n"
            f"🛡️ One-on-One Direct Trading Support\n\n"
            f"📌 <b>𝐒𝐓𝐄𝐏-𝐁𝐘-𝐒𝐓𝐄𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 𝐆𝐔𝐈𝐃𝐄:</b>\n\n"
            f"1️⃣ <b>𝐂𝐑𝐄𝐀𝐓𝐄 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:</b>\nRegister your new account using the secure link provided below.\n\n"
            f"2️⃣ <b>𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:</b>\nComplete profile setup, then tap \"🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃\" below to submit your 8-digit ID.\n\n"
            f"3️⃣ <b>𝐈𝐍𝐒𝐓𝐀𝐍𝐓 𝐀𝐂𝐂𝐄𝐒𝐒:</b>\nGet instant approval and unlock full VIP trading privileges!\n\n"
            f"🔗 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:</b>\n{QUOTEX_LINK} 🌐\n\n"
            f"💬 <b>𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?</b>\nTap the \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below for direct assistance! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "daily_compounding":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"🚨 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐂𝐎𝐌𝐏𝐎𝐔𝐍𝐃𝐈𝐍𝐆 𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓</b> 🚨\n\n"
            f"⚡️ <b>𝐃𝐀𝐈𝐋𝐘 𝟑-𝐒𝐓𝐄𝐏 𝐂𝐎𝐌𝐏𝐎𝐔𝐍𝐃𝐈𝐍𝐆 𝐒𝐘𝐒𝐓𝐄𝐌</b> ⚡️\n\n"
            f"✨ Ready to scale your capital with strict discipline? Join our compounding project today!\n\n"
            f"📊 <b>𝐒𝐘𝐒𝐓𝐄𝐌 𝐑𝐔𝐋𝐄𝐒:</b>\n"
            f"❌ No random entries & zero overtrading\n"
            f"🎯 Accurate entry selection & risk control\n"
            f"📈 Profit lock & capital growth strategy\n"
            f"🛡️ Strict discipline & planned execution\n\n"
            f"📊 <b>𝐖𝐇𝐀𝐓 𝐘𝐎𝐔 𝐖𝐈𝐋𝐋 𝐆𝐄𝐓:</b>\n"
            f"✅ Daily high-accuracy signal setups\n"
            f"✅ Professional risk control protocols\n"
            f"✅ Structured step-by-step compounding plan\n\n"
            f"⭐️ VIP access to private compounding group included\n"
            f"⚡️ Only serious traders should join this project\n\n"
            f"🌐 <b>𝐇𝐎𝐖 𝐓𝐎 𝐉𝐎𝐈𝐍 𝐓𝐇𝐈𝐒 𝐏𝐑𝐎𝐉𝐄𝐂𝐓:</b>\n\n"
            f"1️⃣ <b>𝐑𝐄𝐆𝐈𝐒𝐓𝐄𝐑 𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:</b>\n{QUOTEX_LINK} 🌐\n\n"
            f"2️⃣ <b>𝐃𝐄𝐏𝐎𝐒𝐈𝐓 & 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:</b>\nTap the \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "tour_challenge":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"🚨 <b>𝐈𝐌𝐏𝐎𝐑𝐓𝐀𝐍𝐓 𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓 𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓</b> 🚨\n\n"
            f"🤑 <b>𝐒𝐓𝐀𝐑𝐓: $𝟑𝟎  ➔  🎯 𝐓𝐀𝐑𝐆𝐄𝐓: $𝟓𝟎𝟎 𝐈𝐍  (𝟕-𝐃𝐀𝐘 𝐂𝐇𝐀𝐋𝐋𝐄𝐍𝐆𝐄)</b>\n\n"
            f"✨ Think you have strong trading skills? Join our exclusive 7-day challenge and grow your capital!\n\n"
            f"📊 <b>𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓 𝐑𝐔𝐋𝐄𝐒:</b>\n"
            f"↗️ Starting balance: $30\n"
            f"🎯 Target balance: $500\n"
            f"⏱️ Duration: 7 days\n"
            f"🛡️ Screenshot proof of progress required\n\n"
            f"📊 <b>𝐖𝐇𝐀𝐓 𝐘𝐎𝐔 𝐖𝐈𝐋𝐋 𝐆𝐄𝐓:</b>\n"
            f"✅ Exclusive 7-day challenge signals\n"
            f"✅ Direct account growth guidance\n"
            f"✅ Private community support\n\n"
            f"⭐️ VIP access to private signals included\n"
            f"⚡️ Only serious traders should join this challenge\n\n"
            f"🌐 <b>𝐇𝐎𝐖 𝐓𝐎 𝐉𝐎𝐈𝐍 𝐓𝐇𝐈𝐒 𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓:</b>\n\n"
            f"1️⃣ <b>𝐑𝐄𝐆𝐈𝐒𝐓𝐄𝐑 𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:</b>\n{QUOTEX_LINK} 🌐\n\n"
            f"2️⃣ <b>𝐃𝐄𝐏𝐎𝐒𝐈𝐓 $𝟑𝟎 & 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:</b>\nTap the \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "session_timings":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"⏱️ <b>𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐃𝐀𝐈𝐋𝐘 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 𝐓𝐈𝐌𝐈𝐍𝐆𝐒</b> ⏱️\n\n"
            f"✨ Follow our official trading timeline to stay active and join every live setup on time:\n\n"
            f"☀️ <b>𝟏𝐒𝐓 — 𝐌𝐎𝐑𝐍𝐈𝐍𝐆 𝐏𝐔𝐁𝐋𝐈𝐂 𝐒𝐄𝐒𝐒𝐈𝐎𝐍</b>\n"
            f"🕚 <b>𝐓𝐈𝐌𝐄:</b> 𝟏𝟏:𝟎𝟎 𝐀𝐌\n"
            f"• Live Market Trends & Free Public Signals\n\n"
            f"👑 <b>𝟐𝐍𝐃 — 𝐌.𝐊 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍</b>\n"
            f"🕐 <b>𝐓𝐈𝐌𝐄:</b> 𝟎𝟏:𝟎𝟎 𝐏𝐌\n"
            f"• High-Accuracy Signals & Private VIP Guidance\n\n"
            f"🤑 <b>𝟑𝐑𝐃 — 𝟕-𝐃𝐀𝐘 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐂𝐇𝐀𝐋𝐋𝐄𝐍𝐆𝐄</b>\n"
            f"🎯 <b>𝐓𝐀𝐑𝐆𝐄𝐓:</b> $𝟑𝟎 ➔ $𝟓𝟎𝟎\n"
            f"🕓 <b>𝐓𝐈𝐌𝐄:</b> 𝟎𝟒:𝟎𝟎 𝐏𝐌\n"
            f"• Step-By-Step Account Growth Challenge Signals\n\n"
            f"📈 <b>𝟒𝐓𝐇 — 𝐃𝐀𝐈𝐋𝐘 𝟑-𝐒𝐓𝐄𝐏 𝐂𝐎𝐌𝐏𝐎𝐔𝐍𝐃𝐈𝐍𝐆</b>\n"
            f"🕖 <b>𝐓𝐈𝐌𝐄:</b> 𝟎𝟕:𝟎𝟎 𝐏𝐌\n"
            f"• Exclusive High-Yield Compounding Session\n\n"
            f"🌙 <b>𝟓𝐓𝐇 — 𝐍𝐈𝐆𝐇𝐓 𝐏𝐔𝐁𝐋𝐈𝐂 𝐒𝐄𝐒𝐒𝐈𝐎𝐍</b>\n"
            f"🕘 <b>𝐓𝐈𝐌𝐄:</b> 𝟎𝟗:𝟎𝟎 𝐏𝐌\n"
            f"• Night Market Analysis & Free Signal Updates\n\n"
            f"🔥 <b>𝟔𝐓𝐇 — 𝐌.𝐊 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍</b>\n"
            f"🕚 <b>𝐓𝐈𝐌𝐄:</b> 𝟏𝟏:𝟎𝟎 𝐏𝐌\n"
            f"• Late Night VIP Signal Blast & Account Support\n\n"
            f"🔔 <b>𝐍𝐎𝐓𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍 𝐀𝐋𝐄𝐑𝐓:</b>\nTurn on channel notifications to receive instant alerts before each session goes live!\n\n"
            f"💬 <b>𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?</b>\nTap the \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below for direct support! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME), InlineKeyboardButton("📢 𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=CHANNEL_LINK)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "acc_deleting":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"🗑️ <b>𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐃𝐄𝐋𝐄𝐓𝐈𝐎𝐍 & 𝐑𝐄𝐒𝐄𝐓 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄</b> 🗑️\n\n"
            f"✨ Follow these secure steps to close or reset your trading account:\n\n"
            f"1️⃣ <b>𝐂𝐋𝐄𝐀𝐑 𝐁𝐀𝐋𝐀𝐍𝐂𝐄:</b>\nCheck your active balance and clear all pending financial transactions.\n\n"
            f"2️⃣ <b>𝐑𝐄𝐕𝐈𝐄𝐖 𝐃𝐀𝐓𝐀:</b>\nNote that closing your account will permanently reset your trading history.\n\n"
            f"3️⃣ <b>𝐃𝐄𝐋𝐄𝐓𝐄 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:</b>\nGo to Profile Settings ➡️ Delete Account, or contact official platform support if unavailable.\n\n"
            f"⚠️ <b>𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘 𝐖𝐀𝐑𝐍𝐈𝐍𝐆:</b>\nNever share your passwords or verification codes with anyone under any circumstances!\n\n"
            f"🔗 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:</b>\n{QUOTEX_LINK} 🌐\n\n"
            f"💬 <b>𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?</b>\nTap the \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below for direct assistance! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💎 𝐇𝐎𝐖 𝐓𝐎 𝐉𝐎𝐈𝐍 𝐕𝐈𝐏", callback_data="vip_joining")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "acc_creation_guidance":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"📖 <b>𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐖𝐀𝐋𝐊𝐓𝐇𝐑𝐎𝐔𝐆𝐇</b> 📖\n\n"
            f"✨ Follow this detailed guide to ensure seamless identity verification:\n\n"
            f"1️⃣ <b>𝐀𝐂𝐂𝐄𝐒𝐒 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐏𝐎𝐑𝐓𝐀𝐋:</b>\nOpen the official registration page using the secure link provided below.\n\n"
            f"2️⃣ <b>𝐄𝐍𝐓𝐄𝐑 𝐀𝐂𝐂𝐔𝐑𝐀𝐓𝐄 𝐃𝐄𝐓𝐀𝐈𝐋𝐒:</b>\nInput your real details matching your legal government ID to prevent verification issues.\n\n"
            f"3️⃣ <b>𝐒𝐀𝐕𝐄 𝐘𝐎𝐔𝐑 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:</b>\nComplete your profile confirmation and copy your unique 8-digit Trader ID.\n\n"
            f"4️⃣ <b>𝐒𝐔𝐁𝐌𝐈𝐓 𝐅𝐎𝐑 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍:</b>\nTap the \"🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃\" button below and send your ID directly into the bot.\n\n"
            f"🔗 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:</b>\n{QUOTEX_LINK} 🌐\n\n"
            f"💬 <b>𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?</b>\nTap the \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below for direct assistance! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "trading_guidance":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"📚 <b>𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐄𝐃𝐔𝐂𝐀𝐓𝐈𝐎𝐍 & 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄 𝐇𝐔𝐁</b> 📚\n\n"
            f"✨ Master the fundamentals of digital trading with professional insights:\n\n"
            f"📊 <b>𝐌𝐀𝐑𝐊𝐄𝐓 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒 & 𝐎𝐓𝐂 𝐒𝐈𝐆𝐍𝐀𝐋𝐒:</b>\nMaster candlestick patterns, market trends, support/resistance, and live OTC setups.\n\n"
            f"🛡️ <b>𝐑𝐈𝐒𝐊 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓 & 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘:</b>\nApply strict capital protection rules, loss recovery strategies, and emotional discipline.\n\n"
            f"💎 <b>𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 & 𝐄𝐋𝐈𝐓𝐄 𝐀𝐂𝐂𝐄𝐒𝐒:</b>\nUnlock 24/7 high-accuracy signals, automated AI bot access, and exclusive trading setups.\n\n"
            f"👤 <b>𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 & 𝐌𝐄𝐍𝐓𝐎𝐑𝐒𝐇𝐈𝐏:</b>\nGet private 1-on-1 guidance, customized session planning, and direct account support.\n\n"
            f"💡 <b>𝐃𝐄𝐌𝐎 𝐏𝐑𝐀𝐂𝐓𝐈𝐂𝐄 & 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐓𝐑𝐀𝐏𝐒:</b>\nRefine strategies safely while avoiding revenge trading, greed, and market pitfalls.\n\n"
            f"🔮 <b>𝐅𝐔𝐓𝐔𝐑𝐄 𝐋𝐈𝐒𝐓 & 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐓𝐎𝐎𝐋𝐒:</b>\nExplore market session timings, OTC asset directories, and technical expiry strategies.\n\n"
            f"👇 <b>𝐒𝐄𝐋𝐄𝐂𝐓 𝐀𝐍𝐘 𝐎𝐏𝐓𝐈𝐎𝐍 𝐅𝐑𝐎𝐌 𝐓𝐇𝐄 𝐌𝐄𝐍𝐔 𝐁𝐄𝐋𝐎𝐖:</b>"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆", callback_data="vip_joining"), InlineKeyboardButton("👤 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒", callback_data="personal_sessions")],
            [InlineKeyboardButton("💸 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘", callback_data="loss_recovery"), InlineKeyboardButton("📊 𝐎𝐓𝐂 𝐒𝐈𝐆𝐍𝐀𝐋𝐒", callback_data="otc_live")],
            [InlineKeyboardButton("📈 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒", callback_data="analysis_signals"), InlineKeyboardButton("🔮 𝐅𝐔𝐓𝐔𝐑𝐄", callback_data="future_signals")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "tournament_joining":
        resp_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"🏆 <b>𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 & 𝐏𝐑𝐈𝐙𝐄𝐒 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄</b> 🏆\n\n"
            f"✨ Participate in official platform trading tournaments to win massive cash prizes:\n\n"
            f"💎 <b>𝐄𝐋𝐈𝐆𝐈𝐁𝐈𝐋𝐈𝐓𝐘 & 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍:</b>\nCheck requirements and register your account via our official broker link.\n\n"
            f"📊 <b>𝐒𝐓𝐑𝐀𝐓𝐄𝐆𝐘 & 𝐀𝐃𝐌𝐈𝐍 𝐒𝐔𝐏𝐏𝐎𝐑𝐓:</b>\nGet direct guidance, specialized tournament setups, and competition tips.\n\n"
            f"🏆 <b>𝐂𝐀𝐒𝐇 𝐏𝐑𝐈𝐙𝐄 𝐏𝐎𝐎𝐋:</b>\nCompete on leaderboards and secure top positions for exclusive reward distribution.\n\n"
            f"🔗 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:</b>\n{QUOTEX_LINK} 🌐\n\n"
            f"💬 <b>𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?</b>\nTap the \"💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑\" button below for direct assistance! ✅"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data in ["signal_win", "signal_loss"]:
        result_title = "🎉 <b>𝐂𝐎𝐍𝐆𝐑𝐀𝐓𝐔𝐋𝐀𝐓𝐈𝐎𝐍𝐒! 𝐏𝐑𝐎𝐅𝐈𝐓 𝐑𝐄𝐂𝐎𝐑𝐃𝐄𝐃 (𝐖𝐈𝐍 🏆)</b>" if data == "signal_win" else "⚠️ <b>𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 𝐍𝐄𝐄𝐃𝐄𝐃 - 𝐑𝐄𝐂𝐎𝐕𝐄𝐑 𝐈𝐍 𝐍𝐄𝐗𝐓 𝐒𝐄𝐒𝐒𝐈𝐎𝐍</b>"
        feedback_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"{result_title}\n\n"
            f"✅ <b>𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘!</b>\n"
            f"Thank you for helping us track signal accuracy and improve community performance."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home_delete")]
        ])
        await context.bot.edit_message_text(feedback_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    # BACK TO HOME (REPLACE EDIT FOR NORMAL MENUS)
    elif data == "back_home":
        user_name = html.escape(query.from_user.first_name if query.from_user and query.from_user.first_name else "Trader")
        welcome_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"✨ <b>𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐁𝐀𝐂𝐊, {user_name.upper()}!</b>\n\n"
            f"🌐 <b>𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐇𝐔𝐁</b> 💎\n\n"
            f"📊 <b>𝐀𝐜𝐜𝐞𝐬𝐬 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐒𝐢𝐠𝐧𝐚𝐥𝐬, 𝐌𝐚𝐫𝐤𝐞𝐭 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐆𝐮𝐢𝐝𝐞𝐬, 𝐕𝐈𝐏 𝐀𝐜𝐜𝐞𝐬𝐬, 𝐚𝐧𝐝 𝐁𝐨𝐭 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 — 𝐀𝐥𝐥 𝐈𝐧 𝐎𝐧𝐞 𝐏𝐥𝐚𝐜𝐞.</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"🔗 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐂𝐇𝐀𝐍𝐍𝐄𝐋:</b>\n"
            f"{CHANNEL_LINK}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"⚡ <b>𝐒𝐭𝐚𝐲 𝐂𝐨𝐧𝐧𝐞𝐜𝐭𝐞𝐝 • 𝐒𝐭𝐚𝐲 𝐈𝐧𝐟𝐨𝐫𝐦𝐞𝐝</b>\n\n"
            f"👇 <b>𝐒𝐄𝐋𝐄𝐂𝐓 𝐘𝐎𝐔𝐑 𝐃𝐄𝐒𝐈𝐑𝐄𝐃 𝐎𝐏𝐓𝐈𝐎𝐍</b>\n\n"
            f"🛡️ <i>Trading involves financial risk. Signals are not guaranteed profits.</i>"
        )
        await context.bot.edit_message_text(welcome_text, chat_id=chat_id, message_id=message_id, reply_markup=main_menu_keyboard(), parse_mode="HTML", disable_web_page_preview=True)

    # BACK TO HOME WITH DELETE (FOR SIGNALS / NEW MESSAGES)
    elif data == "back_home_delete":
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"Delete message error: {e}")

        user_name = html.escape(query.from_user.first_name if query.from_user and query.from_user.first_name else "Trader")
        welcome_text = (
            f"👑 <b>{BOT_NAME}</b> 👑\n\n"
            f"✨ <b>𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐁𝐀𝐂𝐊, {user_name.upper()}!</b>\n\n"
            f"🌐 <b>𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐇𝐔𝐁</b> 💎\n\n"
            f"📊 <b>𝐀𝐜𝐜𝐞𝐬𝐬 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐒𝐢𝐠𝐧𝐚𝐥𝐬, 𝐌𝐚𝐫𝐤𝐞𝐭 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐆𝐮𝐢𝐝𝐞𝐬, 𝐕𝐈𝐏 𝐀𝐜𝐜𝐞𝐬𝐬, 𝐚𝐧𝐝 𝐁𝐨𝐭 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 — 𝐀𝐥𝐥 𝐈𝐧 𝐎𝐧𝐞 𝐏𝐥𝐚𝐜𝐞.</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"🔗 <b>𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐂𝐇𝐀𝐍𝐍𝐄𝐋:</b>\n"
            f"{CHANNEL_LINK}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"⚡ <b>𝐒𝐭𝐚𝐲 𝐂𝐨𝐧𝐧𝐞𝐜𝐭𝐞𝐝 • 𝐒𝐭𝐚𝐲 𝐈𝐧𝐟𝐨𝐫𝐦𝐞𝐝</b>\n\n"
            f"👇 <b>𝐒𝐄𝐋𝐄𝐂𝐓 𝐘𝐎𝐔𝐑 𝐃𝐄𝐒𝐈𝐑𝐄𝐃 𝐎𝐏𝐓𝐈𝐎𝐍</b>\n\n"
            f"🛡️ <i>Trading involves financial risk. Signals are not guaranteed profits.</i>"
        )
        await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=main_menu_keyboard(), parse_mode="HTML", disable_web_page_preview=True)

# Vercel Serverless Webhook Handler
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            json_data = json.loads(post_data.decode('utf-8'))
            
            async def process():
                application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
                
                try:
                    await application.bot.set_my_commands([
                        BotCommand("start", "🚀 𝐒𝐓𝐀𝐑𝐓  𝐓𝐇𝐄 𝐁𝐎𝐓 & 𝐎𝐏𝐄𝐍 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 🚀"),
                        BotCommand("channel", "📢 𝐉𝐎𝐈𝐍 𝐌.𝐊 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋"),
                        BotCommand("contact", "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑"),
                        BotCommand("signals", "📊 𝐆𝐄𝐓 𝐋𝐈𝐕𝐄 𝐎𝐓𝐂 𝐒𝐈𝐆𝐍𝐀𝐋𝐒"),
                        BotCommand("vip", "💎 𝐉𝐎𝐈𝐍 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐕𝐈𝐏")
                    ])
                except Exception as cmd_err:
                    print(f"Set commands error: {cmd_err}")
                
                conv_handler = ConversationHandler(
                    entry_points=[CallbackQueryHandler(verify_id_start_handler, pattern="^verify_id_start$")],
                    states={
                        WAITING_FOR_TRADER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_trader_id_handler)]
                    },
                    fallbacks=[CallbackQueryHandler(cancel_verification, pattern="^back_home$")]
                )
                application.add_handler(conv_handler)
                
                application.add_handler(ChatJoinRequestHandler(handle_join_request))
                application.add_handler(CommandHandler("start", start_command))
                application.add_handler(CommandHandler("channel", channel_command))
                application.add_handler(CommandHandler("signals", signals_command))
                application.add_handler(CommandHandler("vip", vip_command))
                application.add_handler(CommandHandler("contact", contact_command))
                application.add_handler(CommandHandler("stats", stats_command))
                application.add_handler(CommandHandler("broadcast", broadcast_command))
                application.add_handler(CallbackQueryHandler(button_callback_handler))
                application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST | filters.UpdateType.EDITED_CHANNEL_POST, forward_channel_posts))
                
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
