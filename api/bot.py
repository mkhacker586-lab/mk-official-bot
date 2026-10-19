import os
import logging
import asyncio
import datetime
import json
from http.server import BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, ChatJoinRequestHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ChatMemberHandler

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
ADMIN_USERNAME = "t.me/MK_TRADER586"
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

# ==========================================
# 📌 14 MAIN MENU BUTTONS (SERIF FONT STYLE)
# ==========================================
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 𝐎𝐓𝐂 𝐋𝐢𝐯𝐞 𝐒𝐢𝐠𝐧𝐚𝐥𝐬", callback_data="otc_live"), InlineKeyboardButton("📈 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬 𝐒𝐢𝐠𝐧𝐚𝐥𝐬", callback_data="analysis_signals")],
        [InlineKeyboardButton("🔮 𝐅𝐮𝐭𝐮𝐫𝐞 𝐒𝐢𝐠𝐧𝐚𝐥𝐬", callback_data="future_signals"), InlineKeyboardButton("📋 𝐅𝐮𝐭𝐮𝐫𝐞 𝐋𝐢𝐬𝐭", callback_data="future_list")],
        [InlineKeyboardButton("👤 𝐏𝐞𝐫𝐬𝐨𝐧𝐚𝐥 𝐒𝐞𝐬𝐬𝐢𝐨𝐧𝐬", callback_data="personal_sessions"), InlineKeyboardButton("💸 𝐋𝐨𝐬𝐬 𝐑𝐞𝐜𝐨𝐯𝐞𝐫𝐲 𝐒𝐞𝐬𝐬𝐢𝐨𝐧𝐬", callback_data="loss_recovery")],
        [InlineKeyboardButton("🎩 𝐇𝐨𝐰 𝐓𝐨 𝐂𝐫𝐞𝐚𝐭𝐞 𝐍𝐞𝐰 𝐀𝐜𝐜𝐨𝐮𝐧𝐭", callback_data="how_to_create"), InlineKeyboardButton("💎 𝐕𝐈𝐏 𝐉𝐨𝐢𝐧𝐢𝐧𝐠", callback_data="vip_joining")],
        [InlineKeyboardButton("🗑️ 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐃𝐞𝐥𝐞𝐭𝐢𝐧𝐠 𝐆𝐮𝐢𝐝𝐚𝐧𝐜𝐞", callback_data="acc_deleting"), InlineKeyboardButton("📖 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐂𝐫𝐞𝐚𝐭𝐢𝐨𝐧 𝐆𝐮𝐢𝐝𝐚𝐧𝐜𝐞", callback_data="acc_creation_guidance")],
        [InlineKeyboardButton("📚 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐆𝐮𝐢𝐝𝐚𝐧𝐜𝐞", callback_data="trading_guidance"), InlineKeyboardButton("🏆 𝐓𝐨𝐮𝐫𝐧𝐚𝐦𝐞𝐧𝐭 𝐉𝐨𝐢𝐧𝐢𝐧𝐠", callback_data="tournament_joining")],
        [InlineKeyboardButton("📢 𝐌.𝐊 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=CHANNEL_LINK)],
        [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 1. Join Request Sent Handler (Pending State)
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    await send_data_to_log_channel(update, context, "Channel Join Request")
    
    user_first_name = user.first_name if user and user.first_name else "Trader"
    pending_msg = (
        f"👑 **{BOT_NAME}** 👑\n\n"
        f"✨ **𝐇𝐄𝐋𝐋𝐎 {user_first_name.upper()}!**\n\n"
        f"⏳ **𝐘𝐎𝐔𝐑 𝐉𝐎𝐈𝐍 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐈𝐒 𝐏𝐄𝐍𝐃𝐈𝐍𝐆 𝐀𝐏𝐏𝐑𝐎𝐕𝐀𝐋** ⏳\n\n"
        f"🔥 **𝐈𝐌𝐏𝐎𝐑𝐓𝐀𝐍𝐓 𝐈𝐍𝐒𝐓𝐑𝐔𝐂𝐓𝐈𝐎𝐍𝐒:**\n"
        f"• Your request has been received and will be approved soon by administration.\n"
        f"• **Follow Sessions Strictly:** Always manage your risk and follow exact trade entry timings.\n"
        f"• **Send Feedbacks:** After every trade result, submit your feedback inside the bot.\n\n"
        f"👇 **𝐄𝐗𝐏𝐋𝐎𝐑𝐄 𝐎𝐔𝐑 𝐒𝐄𝐑𝐕𝐈𝐂𝐄𝐒 𝐁𝐄𝐋𝐎𝗪:**"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
        [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
        [InlineKeyboardButton("🚀 𝐎𝐏𝐄𝐍 𝐁𝐎𝐓 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃", callback_data="back_home")]
    ])
    
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=pending_msg,
            reply_markup=kb,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Join request message error: {e}")

# 2. Request Accepted Handler (Approved / Chat Join Handler)
async def handle_chat_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_member = update.chat_member
        if chat_member and chat_member.new_chat_member.status in ['member', 'administrator', 'creator']:
            user = chat_member.from_user
            user_name = user.first_name if user and user.first_name else "Trader"
            
            approved_msg = (
                f"👑 **{BOT_NAME}** 👑\n\n"
                f"✨ **𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐕𝐈𝐏 𝐇𝐔𝐁, {user_name.upper()}!**\n\n"
                f"🎉 **𝐘𝐎𝐔𝐑 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐈𝐒 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃!** 🎉\n\n"
                f"📌 **𝐂𝐑𝐈𝐓𝐈𝐂𝐀𝐋 𝐂𝐎𝐌𝐌𝐔𝐍𝐈𝐓𝐘 𝐑𝐔𝐋𝐄𝐒:**\n"
                f"1️⃣ **Follow Sessions Strictly:** Do not rush trades. Follow exact signal entries and risk management.\n"
                f"2️⃣ **Send Trade Feedbacks:** Always submit your Win (ITM) or Loss (OTM) feedback after every session.\n"
                f"3️⃣ **Compound Safely:** Use our VIP tools and AI signals to grow your capital step-by-step.\n\n"
                f"👇 **𝐀𝐂𝐂𝐄𝐒𝐒 𝐘𝐎𝐔𝐑 𝐎𝐏𝐓𝐈𝐎𝐍𝐒 𝐁𝐄𝐋𝐎𝗪:**"
            )
            
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
                [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
                [InlineKeyboardButton("🚀 𝐎𝐏𝐄𝐍 𝐁𝐎𝐓 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃", callback_data="back_home")]
            ])
            
            await context.bot.send_message(
                chat_id=user.id,
                text=approved_msg,
                reply_markup=kb,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"Chat join member error: {e}")

# 3. Start Command Handler (Main Dashboard)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await send_data_to_log_channel(update, context, "Bot /start Command")
    
    user_name = user.first_name if user and user.first_name else "Trader"
    welcome_text = (
        f"👑 **{BOT_NAME}** 👑\n\n"
        f"✨ **𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐁𝐀𝐂𝐊, {user_name.upper()}!**\n\n"
        f"🌐 **𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐇𝐔𝐁** 💎\n\n"
        f"📊 Access high-accuracy digital options signals, account guides, VIP access, and professional tools from the menu below:\n\n"
        f"🔗 **𝐎𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐂𝐡𝐚𝐧𝐧𝐞𝐥:** {CHANNEL_LINK}\n\n"
        f"👇 **𝐒𝐄𝐋𝐄𝐂𝐓 𝐘𝐎𝐔𝐑 𝐃𝐄𝐒𝐈𝐑𝐄𝐃 𝐎𝐏𝐓𝐈𝐎𝐍:**"
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown", disable_web_page_preview=True)

# Admin Stats Command
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        return
    
    total_users = get_total_users()
    start_count = get_next_count(START_COUNTER_FILE) - 1
    join_count = get_next_count(JOIN_COUNTER_FILE) - 1
    
    stats_text = (
        f"📊 **𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 & 𝐀𝐍𝐀𝐋𝐘𝐓𝐈𝐂𝐒** 📊\n\n"
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
                await context.bot.send_message(chat_id=uid, text=broadcast_text, parse_mode="Markdown", disable_web_page_preview=True)
                success += 1
                await asyncio.sleep(0.02)
            except:
                failed += 1
        
        await update.message.reply_text(f"✅ **𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝!**\n\n📨 Success: `{success}`\n❌ Failed: `{failed}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Broadcast error: {e}")

# ==========================================
# 🚀 AUTOMATIC FORWARDER FROM UPCOMING POSTINGS CHANNEL
# ==========================================
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

# ==========================================
# 🔐 TRADER ID VERIFICATION FLOW
# ==========================================
async def verify_id_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        f"👑 **{BOT_NAME}** 👑\n\n"
        f"🔐 **𝐕𝐄𝐑𝐈𝐅𝐘 𝐘𝐎𝐔𝐑 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃** 🔐\n\n"
        f"Please reply to this message with your 8-digit Quotex Trader ID.\n\n"
        f"*(Example: `12345678`)*"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
        [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
    ])
    await context.bot.edit_message_text(text, chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=kb, parse_mode="Markdown")
    return WAITING_FOR_TRADER_ID

async def receive_trader_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    trader_id = update.message.text.strip()
    
    admin_log_msg = (
        f"🚨 **𝐍𝐄𝐖 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐒𝐔𝐁𝐌𝐈𝐓𝐓𝐄𝐃 𝐅𝐎𝐑 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍** 🚨\n\n"
        f"👤 User: {user.full_name} (@{user.username if user.username else 'No Username'})\n"
        f"🆔 User ID: `{user.id}`\n"
        f"🔢 Submitted Trader ID: `{trader_id}`"
    )
    await context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=admin_log_msg, parse_mode="Markdown")
    
    success_text = (
        f"👑 **{BOT_NAME}** 👑\n\n"
        f"✅ **𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘!**\n\n"
        f"Your Trader ID (`{trader_id}`) has been sent to M.K Trader admin for verification. You will be granted VIP access shortly upon review!"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
        [InlineKeyboardButton("🚀 𝐎𝐏𝐄𝐍 𝐁𝐎𝐓 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃", callback_data="back_home")]
    ])
    await update.message.reply_text(success_text, reply_markup=kb, parse_mode="Markdown")
    return ConversationHandler.END

async def cancel_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start_command(update, context)
    return ConversationHandler.END

# ==========================================
# 📄 DETAILED BARI BARI POSTS & BUTTON HANDLERS (WITH LOADING ANIMATIONS)
# ==========================================
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    data = query.data

    if data == "otc_live":
        await context.bot.edit_message_text(
            "🔄 **Scanning Market Volatility & Technical Indicators...** Please wait ⏳",
            chat_id=chat_id, message_id=message_id, parse_mode="Markdown"
        )
        await asyncio.sleep(1)
        
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"📊 **𝐎𝐓𝐂 𝐋𝐈𝐕𝐄 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐄𝐍𝐆𝐈𝐍𝐄** 📊\n\n"
            f"✨ Welcome to the professional OTC live trading hub. Here you receive high-accuracy real-time signals optimized for weekend and weekday sessions.\n\n"
            f"💎 **Asset:** USD/PHP (OTC)\n"
            f"🟢 **Direction:** CALL (BUY) 📈\n"
            f"🕒 **Entry Time:** Next Candle / 1 Minute Expiry\n"
            f"🌐 **Time Zone:** UTC +5:00\n"
            f"⚠️ **Rule:** 1 Step MTG Allowed\n\n"
            f"👤 **Analyst:** {ADMIN_USERNAME}\n\n"
            f"👇 **Rate your trade performance below:**"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 𝐖𝐈𝐍 (𝐈𝐓𝐌)", callback_data="signal_win"), InlineKeyboardButton("👎 𝐋𝐎𝐒𝐒 (𝐎𝐓𝐌)", callback_data="signal_loss")],
            [InlineKeyboardButton("🔄 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐄 𝐍𝐄𝐖 𝐒𝐈𝐆𝐍𝐀𝐋", callback_data="otc_live")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "analysis_signals":
        await context.bot.edit_message_text(
            "🔄 **Analyzing OTC Market Trends & Price Action...** Please wait ⏳",
            chat_id=chat_id, message_id=message_id, parse_mode="Markdown"
        )
        await asyncio.sleep(1)
        
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"📈 **𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐇𝐔𝐁** 📈\n\n"
            f"✨ Detailed technical and price action market analysis signals for digital options trading.\n\n"
            f"💎 **Asset:** EUR/USD (Live Market)\n"
            f"🔴 **Direction:** PUT (SELL) 📉\n"
            f"🕒 **Entry:** Immediate / 1 Minute Expiry\n"
            f"💡 **Setup Explanation:** Strong resistance level rejection accompanied by volume exhaustion.\n\n"
            f"👤 **Analyst:** {ADMIN_USERNAME}\n\n"
            f"👇 **Rate your trade performance below:**"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 𝐖𝐈𝐍 (𝐈𝐓𝐌)", callback_data="signal_win"), InlineKeyboardButton("👎 𝐋𝐎𝐒𝐒 (𝐎𝐓𝐌)", callback_data="signal_loss")],
            [InlineKeyboardButton("🔄 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐄 𝐍𝐄𝐖 𝐒𝐈𝐆𝐍𝐀𝐋", callback_data="analysis_signals")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "future_signals":
        await context.bot.edit_message_text(
            "🔄 **Compiling Scheduled Future Market Predictions...** Please wait ⏳",
            chat_id=chat_id, message_id=message_id, parse_mode="Markdown"
        )
        await asyncio.sleep(1)
        
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"🔮 **𝐅𝐔𝐓𝐔𝐑𝐄 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄** 🔮\n\n"
            f"📅 **Date:** Today's Active Session Schedule\n"
            f"🌐 **Timezone:** UTC +5:00\n\n"
            f"1. 🕒 **Time:** 03:00 PM | 💎 **Pair:** GBP/USD (OTC) | 📈 **Direction:** UP (CALL)\n"
            f"2. 🕒 **Time:** 03:15 PM | 💎 **Pair:** EUR/JPY | 📈 **Direction:** DOWN (PUT)\n"
            f"3. 🕒 **Time:** 03:30 PM | 💎 **Pair:** AUD/CAD (OTC) | 📈 **Direction:** UP (CALL)\n"
            f"4. 🕒 **Time:** 03:45 PM | 💎 **Pair:** USD/BDT (OTC) | 📈 **Direction:** DOWN (PUT)\n"
            f"5. 🕒 **Time:** 04:00 PM | 💎 **Pair:** EUR/CAD | 📈 **Direction:** UP (CALL)\n\n"
            f"⚠️ **Note:** Follow strict risk management and prepare your entries ahead of time."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 𝐑𝐄𝐅𝐑𝐄𝐒𝐇 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄", callback_data="future_signals")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "future_list":
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"📋 **𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍 & 𝐅𝐔𝐓𝐔𝐑𝐄 𝐋𝐈𝐒𝐓** 📋\n\n"
            f"✨ Essential market information, session timings, and terminology to enhance your digital options career.\n\n"
            f"• **Available Assets:** Major currency pairs & high-payout OTC assets.\n"
            f"• **Market Sessions:** London, New York, and Asian overlap hours for maximum liquidity.\n"
            f"• **Risk Management:** Never risk more than 2-3% of your total capital per trade session.\n"
            f"• **Expiry Guidance:** Stick strictly to 1-minute or 5-minute expiries as per signal parameters.\n\n"
            f"👇 Access other helpful sections below:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄", callback_data="trading_guidance")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "personal_sessions":
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"👤 **𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 & 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄** 👤\n\n"
            f"✨ Get one-to-one custom trading guidance, direct mentorship, and live strategy breakdown sessions directly with M.K Trader.\n\n"
            f"• Direct interactive sessions tailored to your schedule and capital size.\n"
            f"• Professional account auditing and psychological control training.\n"
            f"• Advanced compound planning to maximize your daily profits safely.\n\n"
            f"👇 Click below to unlock VIP or contact for personal session:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐅𝐎𝐑 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "loss_recovery":
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"💸 **𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 & 𝐒𝐓𝐑𝐀𝐓𝐄𝐆𝐘** 💸\n\n"
            f"✨ Experiencing a drawdown or previous trading losses? Learn professional recovery strategies, trade reviews, and emotional discipline to bounce back safely.\n\n"
            f"• Deep analysis of previous market mistakes and emotional triggers.\n"
            f"• Step-by-step capital recovery planning with safe risk parameters.\n"
            f"• Direct guidance from M.K Trader to stabilize your account growth.\n\n"
            f"👇 Click below to register via VIP link or contact owner:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "how_to_create":
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"🎩 **𝐇𝐎𝐖 𝐓𝐎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐍𝐄𝐖 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐀𝐂𝐂𝐎𝐔𝐍𝐓** 🎩\n\n"
            f"Follow these steps:\n\n"
            f"1️⃣ Create your Quotex account using the M.K Trader referral link below.\n"
            f"2️⃣ Complete your account setup and KYC verification.\n"
            f"3️⃣ Copy your 8-digit Quotex Trader ID.\n"
            f"4️⃣ Return to this bot.\n"
            f"5️⃣ Press **VERIFY TRADER ID** or send your ID directly to owner.\n"
            f"6️⃣ Your request will be sent to the Admin for manual review.\n"
            f"7️⃣ After approval, you will receive your VIP access.\n\n"
            f"🔗 **𝐂𝐑𝐄𝐀𝐓𝐄 𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:**\n{QUOTEX_LINK}"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "vip_joining":
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"💎 **𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐠 & 𝐄𝐋𝐈𝐆𝐈𝐁𝐈𝐋𝐈𝐓𝐘 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄** 💎\n\n"
            f"✨ Unlock elite benefits with M.K VIP Membership:\n"
            f"• 24/7 Private High-Accuracy Signals Feed\n"
            f"• Automated AI Trading Bot Full Access\n"
            f"• Exclusive Compound Sessions & Direct Mentorship\n\n"
            f"📌 **How to Join:**\n"
            f"1️⃣ Create your account using our official link below.\n"
            f"2️⃣ Verify your profile and submit your Trader ID via the verify button or send directly.\n"
            f"3️⃣ Get instant approval and VIP access.\n\n"
            f"🔗 **𝐂𝐑𝐄𝐀𝐓𝐄 𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:**\n{QUOTEX_LINK}"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "acc_deleting":
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"🗑️ **𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐃𝐄𝐋𝐄𝐓𝐈𝐍𝐆 & 𝐑𝐄𝐒𝐄𝐓 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄** 🗑️\n\n"
            f"✨ Follow these secure steps to close or reset your platform account:\n\n"
            f"• Check your active balance and clear any pending financial transactions.\n"
            f"• Review the impact of closing your historical trading data.\n"
            f"• Go to platform profile settings -> Delete Account, or contact official support if the option is unavailable.\n"
            f"⚠️ **Security Warning:** Never share your account passwords or verification codes with anyone under any circumstances!\n\n"
            f"👇 Access VIP link, support, or VIP joining guide below:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("💎 𝐇𝐎𝐖 𝐓𝐎 𝐉𝐎𝐈𝐍 𝐕𝐈𝐏", callback_data="vip_joining")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "acc_creation_guidance":
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"📖 **𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐖𝐀𝐋𝐊𝐓𝐇𝐑𝐎𝐔𝐆𝐇 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄** 📖\n\n"
            f"✨ Detailed registration walkthrough to ensure seamless verification:\n\n"
            f"1️⃣ Access the official registration page via our secure link.\n"
            f"2️⃣ Input accurate personal details matching your legal ID to avoid verification failures.\n"
            f"3️⃣ Complete identity confirmation and save your unique Trader ID securely.\n"
            f"4️⃣ Press **VERIFY TRADER ID** or send directly to owner.\n\n"
            f"🔗 **𝐂𝐑𝐄𝐀𝐓𝐄 𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:**\n{QUOTEX_LINK}"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "trading_guidance":
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"📚 **𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐄𝐃𝐔𝐂𝐀𝐓𝐈𝐎𝐍 & 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄 𝐇𝐔𝐁** 📚\n\n"
            f"✨ Master the fundamentals of digital options trading with professional insights:\n\n"
            f"• Candlestick patterns, market trends, and support/resistance zones.\n"
            f"• Strict risk management and emotional discipline control.\n"
            f"• Importance of demo practice before risking real capital.\n"
            f"• Avoiding common trading pitfalls and psychological traps.\n\n"
            f"👇 Quick navigation to other vital sections:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆", callback_data="vip_joining"), InlineKeyboardButton("👤 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒", callback_data="personal_sessions")],
            [InlineKeyboardButton("💸 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘", callback_data="loss_recovery"), InlineKeyboardButton("📊 𝐎𝐓𝐂 𝐒𝐈𝐆𝐍𝐀𝐋𝐒", callback_data="otc_live")],
            [InlineKeyboardButton("📈 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒", callback_data="analysis_signals"), InlineKeyboardButton("🔮 𝐅𝐔𝐓𝐔𝐑𝐄", callback_data="future_signals")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "tournament_joining":
        resp_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"🏆 **𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 & 𝐏𝐑𝐈𝐙𝐄𝐒 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄** 🏆\n\n"
            f"✨ Participate in official platform trading tournaments to win cash prizes up to $10,000!\n\n"
            f"• Check eligibility requirements and register via our official affiliate portal.\n"
            f"• Contact admin for special tournament strategy support and competition tips.\n"
            f"• Practice regularly on demo tournaments before entering high-stakes competitions.\n\n"
            f"👇 Register via VIP link or contact owner below:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data in ["signal_win", "signal_loss"]:
        result_title = "🎉 **𝐂𝐎𝐍𝐆𝐑𝐀𝐓𝐔𝐋𝐀𝐓𝐈𝐎𝐍𝐒! 𝐏𝐑𝐎𝐅𝐈𝐓 𝐑𝐄𝐂𝐎𝐑𝐃𝐄𝐃 (𝐖𝐈𝐍)**" if data == "signal_win" else "⚠️ **𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐑𝐃𝐄𝐃 - 𝐑𝐄𝐂𝐎𝐕𝐄𝐑 𝐈𝐍 𝐍𝐄𝐗𝐓 𝐒𝐄𝐒𝐒𝐈𝐎𝐍**"
        feedback_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"{result_title}\n\n"
            f"✅ **𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘!**\n"
            f"Thank you for helping us track signal accuracy and improve community performance."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(feedback_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "back_home":
        user_name = query.from_user.first_name if query.from_user and query.from_user.first_name else "Trader"
        welcome_text = (
            f"👑 **{BOT_NAME}** 👑\n\n"
            f"✨ **𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐁𝐀𝐂𝐊, {user_name.upper()}!**\n\n"
            f"🌐 **𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐇𝐔𝐁** 💎\n\n"
            f"📊 Access high-accuracy digital options signals, account guides, VIP access, and professional tools from the menu below:\n\n"
            f"🔗 **𝐎𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐂𝐡𝐚𝐧𝐧𝐞𝐥:** {CHANNEL_LINK}\n\n"
            f"👇 **𝐒𝐄𝐋𝐄𝐂𝐓 𝐘𝐎𝐔𝐑 𝐃𝐄𝐒𝐈𝐑𝐄𝐃 𝐎𝐏𝐓𝐈𝐎𝐍:**"
        )
        await context.bot.edit_message_text(welcome_text, chat_id=chat_id, message_id=message_id, reply_markup=main_menu_keyboard(), parse_mode="Markdown", disable_web_page_preview=True)

# Vercel Serverless Webhook Handler
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            json_data = json.loads(post_data.decode('utf-8'))
            
            async def process():
                application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
                
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
                application.add_handler(CommandHandler("stats", stats_command))
                application.add_handler(CommandHandler("broadcast", broadcast_command))
                application.add_handler(CallbackQueryHandler(button_callback_handler))
                application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST | filters.UpdateType.EDITED_CHANNEL_POST, forward_channel_posts))
                application.add_handler(ChatMemberHandler(handle_chat_join_request, ChatMemberHandler.CHAT_MEMBER))
                
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
