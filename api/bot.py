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
VERIFY_CHANNEL_ID = -1003873965542  # Trader ID Verifications Channel
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
# 🌟 ORIGINAL DATA LOG FUNCTION WITH PREMIUM EMOJIS
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
            count_label = '<emoji id="5231200819986047254">📊</emoji> 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐬'
        else:
            count_val = get_next_count(START_COUNTER_FILE)
            count_label = '<emoji id="5231200819986047254">📊</emoji> 𝐒𝐭𝐚𝐫𝐭𝐬'
        
        pkt_time = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        current_time = pkt_time.strftime("%d %b %Y, %I:%M %p")
        
        log_msg = (
            f'<emoji id="5438496463044752972">⭐</emoji> 𝐍𝐄𝐖 𝐔𝐒𝐄𝐑 𝐃𝐀𝐓𝐀 𝐂𝐀𝐏𝐓𝐔𝐑𝐄𝐃 <emoji id="5438496463044752972">⭐</emoji>\n'
            f"━━━━━━•❅•°•❈•°•❅•━━━━━━\n"
            f'<emoji id="5931415565955503486">🤖</emoji> 𝐁𝐨𝐭 𝐍𝐚𝐦𝐞: {html.escape(str(BOT_NAME))}\n'
            f'<emoji id="5438496463044752972">👑</emoji> 𝐁𝐫𝐚𝐧𝐝: 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑\n'
            f'<emoji id="6005570495603282482">🆔</emoji> 𝐔𝐬𝐞𝐫 𝐈𝐃: {user_id}\n'
            f'<emoji id="5879770735999717115">🕵🏻‍♂️</emoji> 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: {html.escape(str(username))}\n'
            f'<emoji id="5967280668885913944">📛</emoji> 𝐍𝐚𝐦𝐞: {html.escape(str(full_name))}\n'
            f'<emoji id="5424818078833715060">📢</emoji> 𝐂𝐡𝐚𝐧𝐧𝐞𝐥: {html.escape(str(channel_name))}\n'
            f"{count_label}: #{count_val}\n"
            f'<emoji id="5413879192267805083">🕐</emoji> 𝐓𝐢𝐦𝐞: {current_time}\n'
            f'<emoji id="5447410659077661506">📱</emoji> 𝐒𝐨𝐮𝐫𝐜𝐞: {html.escape(str(source_action))}\n'
            f"━━━━━━•❅•°•❈•°•❅•━━━━━━\n"
            f'<emoji id="5424972470023104089">🔥</emoji> 𝐁𝐨𝐭: {html.escape(str(BOT_USERNAME))} <emoji id="4996980495100150380">❤️</emoji>'
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
                    text=log_msg + "\n\n<i>(<emoji id="5447644880824181073">⚠️</emoji> 𝐔𝐒𝐄𝐑 𝐇𝐀𝐒 𝐍𝐎 𝐏𝐑𝐎𝐅𝐈𝐋𝐄 𝐏𝐇𝐎𝐓𝐎 <emoji id="5260293700088511294">☠️</emoji>)</i>",
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
# 📌 MAIN MENU BUTTONS (WITH ALL ORIGINAL BUTTONS & EMOJIS)
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
        [InlineKeyboardButton("⏱️ 𝐌.𝐊 𝐃𝐀𝐈𝐋𝐘 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 𝐓𝐈𝐌𝐈𝐍𝐆𝐒 ⏱️", callback_data="session_timings")],
        [InlineKeyboardButton("🤖 𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎", callback_data="ai_signals_pro")],
        [InlineKeyboardButton("👑 𝐌.𝐊 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓 👑", url="https://t.me/MK_TRADER_OFFICIAL_BOT?start=start")],
        [InlineKeyboardButton("📢 𝐉𝐎𝐈𝐍 𝐌.𝐊 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 🚀", url=CHANNEL_LINK)],
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
    
    real_user_name = html.escape(user.first_name if user and user.first_name else "Trader")
    
    pending_msg = (
        f'<emoji id="5438496463044752972">👑</emoji><emoji id="4996980495100150380">✨</emoji> 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓 <emoji id="4996980495100150380">✨</emoji><emoji id="5438496463044752972">👑</emoji>\n\n'
        f'<emoji id="5409048419211682843">💎</emoji> 𝐇𝐄𝐋𝐋𝐎, {real_user_name}!\n\n'
        f'<emoji id="5440621591387980068">⏳</emoji> 𝐉𝐎𝐈𝐍 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐏𝐄𝐍𝐃𝐈𝐍𝐆 <emoji id="5440621591387980068">⏳</emoji>\n\n'
        f'<emoji id="5967280668885913944">💌</emoji> 𝐘𝐨𝐮𝐫 𝐣𝐨𝐢𝐧 𝐫𝐞𝐪𝐮𝐞𝐬𝐭 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐫𝐞𝐜𝐞𝐢𝐯𝐞𝐝 𝐚𝐧𝐝 𝐢𝐬 𝐜𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐩𝐞𝐧𝐝𝐢𝐧𝐠 𝐚𝐝𝐦𝐢𝐧 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥. 𝐘𝐨𝐮\'𝐥𝐥 𝐠𝐞𝐭 𝐚𝐜𝐜𝐞𝐬𝐬 𝐨𝐧𝐜𝐞 𝐲𝐨𝐮𝐫 𝐫𝐞𝐪𝐮𝐞𝐬𝐭 𝐢𝐬 𝐚𝐜𝐜𝐞𝐩𝐭𝐞𝐝. <emoji id="4996980495100150380">❤️‍🔥</emoji>\n\n'
        f'<emoji id="5877597667231534929">📜</emoji> 𝐂𝐎𝐌𝐌𝐔𝐍𝐈𝐓𝐘 𝐆𝐔𝐈𝐃𝐄𝐋𝐈𝐍𝐄𝐒\n\n'
        f'<emoji id="5397782960512444700">🎯</emoji> 𝐅𝐎𝐋𝐋𝐎𝐖 𝐀𝐋𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒\n'
        f'<emoji id="5330157467781312171">⏰</emoji> 𝐉𝐨𝐢𝐧 𝐨𝐧 𝐭𝐢𝐦𝐞 𝐚𝐧𝐝 𝐬𝐭𝐚𝐲 𝐚𝐜𝐭𝐢𝐯𝐞 𝐝𝐮𝐫𝐢𝐧𝐠 𝐬𝐜𝐡𝐞𝐝𝐮𝐥𝐞𝐝 𝐬𝐞𝐬𝐬𝐢𝐨𝐧𝐬.\n\n'
        f'<emoji id="5395444784611480792">📝</emoji> 𝐒𝐄𝐍𝐃 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊\n'
        f'<emoji id="5805532930662996322">✅</emoji> 𝐒𝐮𝐛𝐦𝐢𝐭 𝐲𝐨𝐮𝐫 𝐬𝐞𝐬𝐬𝐢𝐨𝐧 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐚𝐟𝐭𝐞𝐫 𝐞𝐯𝐞𝐫𝐲 𝐬𝐞𝐬𝐬𝐢𝐨𝐧.\n\n'
        f'<emoji id="5231200819986047254">📊</emoji> 𝐒𝐓𝐀𝐘 𝐔𝐏𝐃𝐀𝐓𝐄𝐃\n'
        f'<emoji id="5224607267797606837">⚡</emoji> 𝐅𝐨𝐥𝐥𝐨𝐰 𝐨𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐚𝐧𝐧𝐨𝐮𝐧𝐜𝐞𝐦𝐞𝐧𝐭𝐬 𝐚𝐧ْد 𝐦𝐚𝐫𝐤𝐞𝐭 𝐮𝐩𝐝𝐚𝐭𝐞𝐬.\n\n'
        f'<emoji id="5942877472163892475">🤝</emoji> 𝐌𝐀𝐈𝐍𝐓𝐀𝐈𝐍 𝐃𝐈𝐒𝐂𝐈𝐏𝐋𝐈𝐍𝐄\n'
        f'<emoji id="5409048419211682843">💎</emoji> 𝐑𝐞𝐬𝐩𝐞𝐜𝐭 𝐜𝐨𝐦𝐦𝐮𝐧𝐢𝐭𝐲 𝐫𝐮𝐥𝐞𝐬 𝐚𝐧𝐝 𝐟𝐨𝐥𝐥𝐨𝐰 𝐭𝐡𝐞 𝐢𝐧𝐬𝐭𝐫𝐮𝐜𝐭𝐢𝐨𝐧𝐬.\n\n'
        f'<emoji id="5296369303661067030">🛡️</emoji> 𝐌𝐀𝐍𝐀𝐆𝐄 𝐑𝐈𝐒𝐊 𝐖𝐈𝐒𝐄𝐋𝐘\n'
        f'𝐍𝐞𝐯𝐞𝐫 𝐦𝐚𝐤𝐞 𝐝𝐞𝐜𝐢𝐬𝐢𝐨𝐧𝐬 𝐰𝐢𝐭𝐡𝐨𝐮𝐭 𝐮𝐧𝐝𝐞𝐫𝐬𝐭𝐚𝐧𝐝𝐢𝐧𝐠 𝐭𝐡𝐞 𝐫𝐢𝐬𝐤𝐬.\n\n'
        f'<emoji id="5875078273775439450">🚀</emoji> 𝐀𝐂𝐂𝐄𝐒𝐒 𝐀𝐋𝐋 𝐁𝐎𝐓 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒\n\n'
        f'<emoji id="5875008416132370818">👇</emoji> 𝐂𝐋𝐈𝐂𝐊 𝐓𝐎 𝐎𝐏𝐄𝐍 𝐁𝐎𝐓 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃'
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
        [
            InlineKeyboardButton("👤 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍", url="https://t.me/m/jY55Z4p_Yzhk"),
            InlineKeyboardButton("💸 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘", url="https://t.me/m/i7Y4TWPaMWZk")
        ],
        [
            InlineKeyboardButton("💎 𝐕𝐈𝐏 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐀𝐂𝐂𝐄𝐒𝐒", url="https://t.me/m/7LE78wShYTc0"),
            InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)
        ],
        [InlineKeyboardButton("👀 𝐕𝐈𝐄𝐖 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🚀 𝐎𝐏𝐄𝐍 𝐁𝐎𝐓 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃", callback_data="pending_open_dashboard")]
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
        f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
        f'<emoji id="4996980495100150380">✨</emoji> 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐁𝐀𝐂𝐊, {user_name.upper()}!\n\n'
        f'<emoji id="5447410659077661506">🌐</emoji> 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐇𝐔𝐁 <emoji id="5409048419211682843">💎</emoji>\n\n'
        f'<emoji id="5231200819986047254">📊</emoji> 𝐀𝐜𝐜𝐞𝐬𝐬 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐒𝐢𝐠𝐧𝐚𝐥𝐬, 𝐌𝐚𝐫𝐤𝐞𝐭 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐆𝐮𝐢𝐝𝐞𝐬, 𝐕𝐈𝐏 𝐀𝐜𝐜𝐞𝐬𝐬, 𝐚𝐧𝐝 𝐁𝐨𝐭 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 — 𝐀𝐥𝐥 𝐈𝐧 𝐎𝐧𝐞 𝐏𝐥𝐚𝐜𝐞.\n\n'
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f'<emoji id="5271604874419647061">🔗</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐂𝐇𝐀𝐍𝐍𝐄𝐋:\n'
        f"{CHANNEL_LINK}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f'<emoji id="5224607267797606837">⚡</emoji> 𝐒𝐭𝐚𝐲 𝐂𝐨𝐧𝐧𝐞𝐜𝐭𝐞𝐝 • 𝐒𝐭𝐚𝐲 𝐈𝐧𝐟𝐨𝐫𝐦𝐞𝐝\n\n'
        f'<emoji id="5875008416132370818">👇</emoji> 𝐒𝐄𝐋𝐄𝐂𝐓 𝐘𝐎𝐔𝐑 𝐃𝐄𝐒𝐈𝐑𝐄𝐃 𝐎𝐏𝐓𝐈𝐎𝐍\n\n'
        f'<emoji id="5296369303661067030">🛡️</emoji> 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐢𝐧𝐯𝐨𝐥𝐯𝐞𝐬 𝐟𝐢𝐧𝐚𝐧𝐜𝐢𝐚𝐥 𝐫𝐢𝐬𝐤. 𝐒𝐢𝐠𝐧𝐚𝐥𝐬 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐠𝐮𝐚𝐫𝐚𝐧𝐭𝐞𝐞𝐝 𝐩𝐫𝐨𝐟𝐢𝐭𝐬.'
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="HTML", disable_web_page_preview=True)

# Channel Command Handler (/channel)
async def channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_text = (
        f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
        f'<emoji id="5424818078833715060">📢</emoji> 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋\n\n'
        f'<emoji id="4996980495100150380">✨</emoji> 𝐒𝐭𝐚𝐲 𝐂𝐨𝐧𝐧𝐞𝐜𝐭𝐞𝐝 • 𝐒𝐭𝐚𝐲 𝐈𝐧𝐟𝐨𝐫𝐦𝐞𝐝\n\n'
        f'<emoji id="5424972470023104089">🔥</emoji> 𝐆𝐞𝐭 𝐭𝐡𝐞 𝐋𝐚𝐭𝐞𝐬𝐭 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐔𝐩𝐝𝐚𝐭𝐞𝐬, 𝐌𝐚𝐫𝐤𝐞𝐭 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐒𝐢𝐠𝐧𝐚𝐥 𝐔𝐩𝐝𝐚𝐭𝐞𝐬, 𝐚𝐧𝐝 𝐎𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐀𝐧𝐧𝐨𝐮𝐧𝐜𝐞𝐦𝐞𝐧𝐭𝐬.\n\n'
        f'<emoji id="5875008416132370818">👇</emoji> 𝐓𝐚𝐩 𝐭𝐡𝐞 𝐁𝐮𝐭𝐭𝐨𝐧 𝐁𝐞𝐥𝐨𝐰 𝐭𝐨 𝐉𝐨𝐢𝐧 𝐎𝐮𝐫 𝐎𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐂𝐇𝐀𝐍𝐍𝐄𝐋! <emoji id="5424818078833715060">📢</emoji>'
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 𝐉𝐎𝐈𝐍 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
    ])
    await update.message.reply_text(resp_text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

# Signals Command Handler (/signals)
async def signals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp_text = (
        f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
        f'<emoji id="5231200819986047254">📊</emoji> 𝐋𝐈𝐕𝐄 𝐎𝐓𝐂 & 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐇𝐔𝐁 <emoji id="5231200819986047254">📊</emoji>\n\n'
        f'<emoji id="4996980495100150380">✨</emoji> 𝐀𝐜𝐜𝐞𝐬𝐬 𝐡𝐢𝐠𝐡-𝐚𝐜𝐜𝐮𝐫𝐚𝐜𝐲 𝐦𝐚𝐫𝐤𝐞𝐭 𝐩𝐫𝐞𝐝𝐢𝐜𝐭𝐢𝐨𝐧𝐬 𝐚𝐧𝐝 𝐩𝐫𝐨𝐟𝐞𝐬𝐬𝐢𝐨𝐧𝐚𝐥 𝐭𝐞𝐜𝐡𝐧𝐢𝐜𝐚𝐥 𝐬𝐞𝐭𝐮𝐩𝐬:\n\n'
        f'<emoji id="5224607267797606837">⚡</emoji> 𝐋𝐈𝐕𝐄 𝐌𝐀𝐑𝐊𝐄𝐓 𝐓𝐑𝐄𝐍𝐃𝐒:\n𝐆𝐞𝐭 𝐢𝐧𝐬𝐭𝐚𝐧𝐭 𝐮𝐩𝐝𝐚𝐭𝐞𝐬 𝐨𝐧 𝐫𝐮𝐧𝐧𝐢𝐧𝐠 𝐦𝐚𝐫𝐤𝐞𝐭 𝐬𝐞𝐬𝐬𝐢𝐨𝐧𝐬 𝐚𝐧𝐝 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐬𝐬𝐞𝐭 𝐦𝐨𝐯𝐞𝐦𝐞𝐧𝐭𝐬.\n\n'
        f'<emoji id="5449683594425410231">📈</emoji> 𝐏𝐑𝐈𝐂𝐄 𝐀𝐂𝐓𝐈𝐎𝐍 & 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒:\n𝐄𝐱𝐩𝐥𝐨𝐫𝐞 𝐝𝐞𝐭𝐚𝐢𝐥𝐞𝐝 𝐬𝐮𝐩𝐩𝐨𝐫𝐭/𝐫𝐞𝐬𝐢𝐬𝐭𝐚𝐧𝐜𝐞 𝐥𝐞𝐯𝐞𝐥𝐬 𝐚𝐧𝐝 𝐩𝐫𝐨𝐟𝐞𝐬𝐬𝐢𝐨𝐧𝐚𝐥 𝐜𝐡𝐚𝐫𝐭 𝐛𝐫𝐞𝐚𝐤𝐝𝐨𝐰𝐧𝐬.\n\n'
        f'<emoji id="5397782960512444700">🎯</emoji> 𝐒𝐈𝐆𝐍𝐀𝐋 𝐎𝐏𝐓𝐈𝐎𝐍𝐒:\n𝐂𝐡𝐨𝐨𝐬𝐞 𝐛𝐞𝐭𝐰𝐞𝐞𝐧 𝐎𝐓𝐂 𝐥𝐢𝐯𝐞 𝐬𝐢𝐠𝐧𝐚𝐥𝐬, 𝐭𝐫𝐞𝐧𝐝 𝐚𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐚𝐧𝐝 𝐟𝐮𝐭𝐮𝐫𝐞 𝐩𝐫𝐞𝐝𝐢𝐜𝐭𝐢𝐨𝐧𝐬.\n\n'
        f'<emoji id="5875008416132370818">👇</emoji> 𝐒𝐄𝐋𝐄𝐂𝐓 𝐘𝐎𝐔𝐑 𝐏𝐑𝐄𝐅𝐄𝐑𝐑𝐄𝐃 𝐎𝐏𝐓𝐈𝐎𝐍 𝐅𝐑𝐎𝐌 𝐓𝐇𝐄 𝐌𝐄𝐍𝐔 𝐁𝐄𝐋𝐎𝐖:'
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
        f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
        f'<emoji id="5409048419211682843">💎</emoji> 𝐕𝐈𝐏 𝐏𝐑𝐎𝐆𝐑𝐀𝐌 & 𝐉𝐎𝐈𝐍𝐈𝐍𝐆\n\n'
        f'<emoji id="4996980495100150380">✨</emoji> 𝐔𝐧𝐥𝐨𝐜𝐤 𝐞𝐱𝐜𝐥𝐮𝐬𝐢𝐯𝐞 𝐚𝐝𝐯𝐚𝐧𝐭𝐚𝐠𝐞𝐬 𝐚𝐧𝐝 𝐞𝐥𝐞𝐯𝐚𝐭𝐞 𝐲𝐨𝐮𝐫 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐣𝐨𝐮𝐫𝐧𝐞𝐲 𝐰𝐢𝐭𝐡 𝐞𝐥𝐢𝐭𝐞 𝐦𝐞𝐦𝐛𝐞𝐫𝐬𝐡𝐢𝐩:\n\n'
        f'<emoji id="5231200819986047254">📊</emoji> 𝐄𝐱𝐩𝐥𝐨𝐫𝐞 𝐌𝐚𝐫𝐤𝐞𝐭 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐒𝐞𝐭𝐮𝐩𝐬, 𝐒𝐢𝐠𝐧𝐚𝐥 𝐔𝐩𝐝𝐚𝐭𝐞𝐬, 𝐚𝐧𝐝 𝐕𝐈𝐏 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐂𝐨𝐧𝐭𝐞𝐧𝐭.\n\n'
        f'<emoji id="5271604874419647061">🔗</emoji> 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:\n{QUOTEX_LINK} <emoji id="5447410659077661506">🌐</emoji>\n\n'
        f'<emoji id="5875008416132370818">👇</emoji> 𝐒𝐄𝐋𝐄𝐂𝐓 𝐀𝐍𝐘 𝐎𝐏𝐓𝐈𝐎𝐍 𝐅𝐑𝐎𝐌 𝐓𝐇𝐄 𝐌𝐄𝐍𝐔 𝐁𝐄𝐋𝐎𝐖:'
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
        [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start")],
        [InlineKeyboardButton("💎 𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆", callback_data="vip_joining")],
        [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
        [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
    ])
    await update.message.reply_text(resp_text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

# Contact Owner Command Handler (/contact)
async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_text = (
        f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
        f'<emoji id="5443038326535759644">💬</emoji> 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌.𝐊 𝐎𝐖𝐍𝐄𝐑 <emoji id="5443038326535759644">💬</emoji>\n\n'
        f'<emoji id="4996980495100150380">✨</emoji> 𝐈𝐟 𝐲𝐨𝐮 𝐡𝐚𝐯𝐞 𝐚𝐧𝐲 𝐪𝐮𝐞𝐬𝐭𝐢𝐨𝐧𝐬, 𝐧𝐞𝐞𝐝 𝐕𝐈𝐏 𝐚𝐜𝐜𝐞𝐬𝐬 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥, 𝐨𝐫 𝐰𝐚𝐧𝐭 𝐩𝐞𝐫𝐬𝐨𝐧𝐚𝐥 𝐠𝐮𝐢𝐝𝐚𝐧𝐜𝐞, 𝐜𝐥𝐢𝐜𝐤 𝐭𝐡𝐞 𝐛𝐮𝐭𝐭𝐨𝐧 𝐛𝐞𝐥𝐨𝐰 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫 𝐝𝐢𝐫𝐞𝐜𝐭𝐥𝐲:\n\n'
        f'<emoji id="5271604874419647061">🔗</emoji> 𝐃𝐈𝐑𝐄𝐂𝐓 𝐂𝐎𝐍𝐓𝐀𝐂𝐓:\n{ADMIN_USERNAME} <emoji id="5447410659077661506">🌐</emoji>\n\n'
        f'<emoji id="5875008416132370818">👇</emoji> 𝐓𝐚𝐩 𝐭𝐡𝐞 "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 𝐍𝐎𝐖 👑" 𝐛𝐮𝐭𝐭𝐨𝐧 𝐛𝐞𝐥𝐨𝐰! <emoji id="5805532930662996322">✅</emoji>'
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 𝐍𝐎𝐖 👑", url=ADMIN_USERNAME)],
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
        f'<emoji id="5231200819986047254">📊</emoji> 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 & 𝐀𝐍𝐀𝐋𝐘𝐓𝐈𝐂𝐒 <emoji id="5231200819986047254">📊</emoji>\n\n'
        f'<emoji id="5942877472163892475">👥</emoji> 𝐓𝐨𝐭𝐚𝐥 𝐔𝐧𝐢𝐪𝐮𝐞 𝐔𝐬𝐞𝐫𝐬: {total_users}\n'
        f'<emoji id="5875078273775439450">🚀</emoji> 𝐓𝐨𝐭𝐚𝐥 /𝐬𝐭𝐚𝐫𝐭 𝐂𝐨𝐮𝐧𝐭: {start_count}\n'
        f'<emoji id="5424818078833715060">📢</emoji> 𝐓𝐨𝐭𝐚𝐥 𝐉𝐨𝐢𝐧 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐬: {join_count}\n\n'
        f'<emoji id="5931415565955503486">🤖</emoji> 𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐎𝐧𝐥𝐢𝐧𝐞 & 𝐑𝐮𝐧𝐧𝐢𝐧𝐠 <emoji id="5805532930662996322">🟢</emoji>'
    )
    await update.message.reply_text(stats_text, parse_mode="HTML")

# Admin Broadcast Command
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        return
    
    if not context.args:
        await update.message.reply_text('<emoji id="5447644880824181073">⚠️</emoji> 𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐚 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭. 𝐄𝐱𝐚𝐦𝐩𝐥𝐞: /𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐇𝐞𝐥𝐥𝐨 𝐞𝐯𝐞𝐫𝐲𝐨𝐧𝐞!', parse_mode="HTML")
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
        
        await update.message.reply_text(f'<emoji id="5805532930662996322">✅</emoji> 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝!\n\n<emoji id="5967280668885913944">📨</emoji> 𝐒𝐮𝐜𝐜𝐞𝐬𝐬: {success}\n<emoji id="5210952531676504517">❌</emoji> 𝐅𝐚𝐢𝐥𝐞𝐝: {failed}', parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f'<emoji id="5210952531676504517">❌</emoji> 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐞𝐫𝐫𝐨𝐫: {e}')

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

# Trader ID Verification Flow via Button
async def verify_id_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
        f'<emoji id="5296369303661067030">🔐</emoji> 𝐕𝐄𝐑𝐈𝐅𝐘 𝐘𝐎𝐔𝐑 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 <emoji id="5296369303661067030">🔐</emoji>\n\n'
        f'𝐏𝐥𝐞𝐚𝐬𝐞 𝐫𝐞𝐩𝐥𝐲 𝐭𝐨 𝐭𝐡𝐢𝐬 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐰𝐢𝐭𝐡 𝐲𝐨𝐮𝐫 𝟖-𝐝𝐢𝐠𝐢𝐭 𝐐𝐮𝐨𝐭𝐞𝐱 𝐓𝐫𝐚𝐝𝐞𝐫 𝐈𝐃.\n\n'
        f'(𝐄𝐱𝐚𝐦𝐩𝐥𝐞: <code>12345678</code>)'
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
        [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
    ])
    await context.bot.send_message(chat_id=query.message.chat.id, text=text, reply_markup=kb, parse_mode="HTML")
    return WAITING_FOR_TRADER_ID

async def receive_trader_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text_input = update.message.text.strip()
    
    if not text_input.isdigit() or len(text_input) < 5:
        return
        
    trader_id = html.escape(text_input)
    
    try:
        await update.message.delete()
    except Exception as e:
        print(f"Delete user message error: {e}")
    
    verify_channel_msg = (
        f'<emoji id="5438496463044752972">👑</emoji> 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓 <emoji id="5438496463044752972">👑</emoji>\n\n'
        f'<emoji id="5224607267797606837">⚡</emoji> ✦ 𝐍𝐄𝐖 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃 𝐒𝐔𝐁𝐌𝐈𝐓𝐓𝐄𝐃 ✦ <emoji id="5224607267797606837">⚡</emoji>\n\n'
        f'<emoji id="5879770735999717115">👤</emoji> 𝐍𝐚𝐦𝐞: {html.escape(str(user.full_name))}\n'
        f'<emoji id="5879770735999717115">🕵🏻‍♂️</emoji> 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: @{html.escape(str(user.username if user.username else "No Username"))}\n'
        f'<emoji id="6005570495603282482">🆔</emoji> 𝐔𝐬𝐞𝐫 𝐈𝐃: <code>{user.id}</code>\n'
        f'<emoji id="5397916757333654639">🔢</emoji> 𝐓𝐫𝐚𝐝𝐞𝐫 𝐈𝐃: <code>{trader_id}</code>\n'
        f'<emoji id="5440621591387980068">⏳</emoji> 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐏𝐄𝐍𝐃𝐈𝐍𝐆 𝐑𝐄𝐕𝐈𝐄𝐖\n\n'
        f'<emoji id="5875008416132370818">👇</emoji> 𝐂𝐥𝐢𝐜𝐤 𝐛𝐞𝐥𝐨𝐰 𝐭𝐨 𝐜𝐡𝐚𝐭 𝐰𝐢𝐭𝐡 𝐮𝐬𝐞𝐫 𝐨𝐫 𝐨𝐩𝐞𝐧 𝐛𝐨𝐭:'
    )
    
    admin_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 𝐂𝐇𝐀𝐓 𝐖𝐈𝐓𝐇 𝐔𝐒𝐄𝐑", url=f"tg://user?id={user.id}")],
        [InlineKeyboardButton("🤖 𝐎𝐏𝐄𝐍 𝐓𝐇𝐄 𝐁𝐎𝐓", url=f"https://t.me/MK_TRADER_OFFICIAL_BOT")]
    ])
    
    try:
        photos = await context.bot.get_user_profile_photos(user_id=user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            await context.bot.send_photo(chat_id=VERIFY_CHANNEL_ID, photo=file_id, caption=verify_channel_msg, reply_markup=admin_kb, parse_mode="HTML")
        else:
            await context.bot.send_message(chat_id=VERIFY_CHANNEL_ID, text=verify_channel_msg, reply_markup=admin_kb, parse_mode="HTML")
    except Exception as e:
        print(f"Verify channel send error: {e}")
    
    user_success_text = (
        f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
        f'✦ 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍 𝐈𝐍 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒 ✦\n\n'
        f'𝐘𝐨𝐮𝐫 𝐬𝐮𝐛𝐦𝐢𝐬𝐬𝐢𝐨𝐧 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐫𝐞𝐜𝐞𝐢𝐯𝐞𝐝!\n\n'
        f'<emoji id="5409048419211682843">💎</emoji> 𝐒𝐔𝐁𝐌𝐈𝐒𝐒𝐈𝐎𝐍 𝐃𝐄𝐓𝐀𝐈𝐋𝐒\n\n'
        f'<emoji id="6005570495603282482">🆔</emoji> 𝐓𝐫𝐚𝐝𝐞𝐫 𝐈𝐃: <code>{trader_id}</code>\n'
        f'<emoji id="5440621591387980068">⏳</emoji> 𝐑𝐞𝐯𝐢𝐞𝐰 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐏𝐄𝐍𝐃𝐈𝐍𝐆\n'
        f'<emoji id="5296369303661067030">🛡️</emoji> 𝐕𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧: 𝐀𝐝𝐦𝐢𝐧 𝐑𝐞𝐯𝐢𝐞𝐰\n\n'
        f'<emoji id="4996980495100150380">✨</emoji> 𝐘𝐨𝐮𝐫 𝐝𝐞𝐭𝐚𝐢𝐥𝐬 𝐚𝐫𝐞 𝐧𝐨𝐰 𝐚𝐰𝐚𝐢𝐭𝐢𝐧𝐠 𝐚𝐝𝐦𝐢𝐧 𝐫𝐞𝐯𝐢𝐞𝐰. 𝐘𝐨𝐮 𝐰𝐢𝐥𝐥 𝐫𝐞𝐜𝐞𝐢𝐯𝐞 𝐚𝐧 𝐮𝐩𝐝𝐚𝐭𝐞 𝐨𝐧𝐜𝐞 𝐭𝐡𝐞 𝐯𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧 𝐩𝐫𝐨𝐜𝐞𝐬𝐬 𝐢𝐬 𝐜𝐨𝐦𝐩𝐥𝐞𝐭𝐞.\n\n'
        f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐀𝐒𝐒𝐈𝐒𝐓𝐀𝐍𝐂𝐄?\n\n'
        f'𝐖𝐚𝐧𝐭 𝐝𝐢𝐫𝐞𝐜𝐭 𝐬𝐮𝐩𝐩𝐨𝐫𝐭 𝐟𝐫𝐨𝐦 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫? 𝐓𝐚𝐩 𝐭𝐡𝐞 𝐛𝐮𝐭𝐭𝐨𝐧 𝐛𝐞𝐥𝐨𝐰 𝐭𝐨 𝐠𝐞𝐭 𝐢𝐧 𝐭𝐨𝐮𝐜𝐡! <emoji id="5438496463044752972">👑</emoji>\n\n'
        f'𝐖𝐀𝐈𝐓𝐈𝐍𝐆 𝐅𝐎𝐑 𝐑𝐄𝐕𝐈𝐄𝐖'
    )
    
    user_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
        [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home_delete")]
    ])
    
    await context.bot.send_message(chat_id=user.id, text=user_success_text, reply_markup=user_kb, parse_mode="HTML")
    return ConversationHandler.END

async def cancel_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except:
        pass
    return ConversationHandler.END

async def global_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    if text.isdigit() and len(text) >= 5:
        await receive_trader_id_handler(update, context)

# ==========================================
# 📄 BUTTON CALLBACK HANDLER (ALL ORIGINAL CALLBACKS)
# ==========================================
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    data = query.data

    if data == "pending_open_dashboard":
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"Delete pending message error: {e}")
        
        user_name = html.escape(query.from_user.first_name if query.from_user and query.from_user.first_name else "Trader")
        welcome_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐁𝐀𝐂𝐊, {user_name.upper()}!\n\n'
            f'<emoji id="5447410659077661506">🌐</emoji> 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐇𝐔𝐁 <emoji id="5409048419211682843">💎</emoji>\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐀𝐜𝐜𝐞𝐬𝐬 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐒𝐢𝐠𝐧𝐚𝐥𝐬, 𝐌𝐚𝐫𝐤𝐞𝐭 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐆𝐮𝐢𝐝𝐞𝐬, 𝐕𝐈𝐏 𝐀𝐜𝐜𝐞𝐬𝐬, 𝐚𝐧𝐝 𝐁𝐨𝐭 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 — 𝐀𝐥𝐥 𝐈𝐧 𝐎𝐧𝐞 𝐏𝐥𝐚𝐜𝐞.\n\n'
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f'<emoji id="5271604874419647061">🔗</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐂𝐇𝐀𝐍𝐍𝐄𝐋:\n'
            f"{CHANNEL_LINK}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f'<emoji id="5224607267797606837">⚡</emoji> 𝐒𝐭𝐚𝐲 𝐂𝐨𝐧𝐧𝐞𝐜𝐭𝐞𝐝 • 𝐒𝐭𝐚𝐲 𝐈𝐧𝐟𝐨𝐫𝐦𝐞𝐝\n\n'
            f'<emoji id="5875008416132370818">👇</emoji> 𝐒𝐄𝐋𝐄𝐂𝐓 𝐘𝐎𝐔𝐑 𝐃𝐄𝐒𝐈𝐑𝐄𝐃 𝐎𝐏𝐓𝐈𝐎𝐍\n\n'
            f'<emoji id="5296369303661067030">🛡️</emoji> 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐢𝐧𝐯𝐨𝐥𝐯𝐞𝐬 𝐟𝐢𝐧𝐚𝐧𝐜𝐢𝐚𝐥 𝐫𝐢𝐬𝐤. 𝐒𝐢𝐠𝐧𝐚𝐥𝐬 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐠𝐮𝐚𝐫𝐚𝐧𝐭𝐞𝐞𝐝 𝐩𝐫𝐨𝐟𝐢𝐭𝐬.'
        )
        await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=main_menu_keyboard(), parse_mode="HTML", disable_web_page_preview=True)

    elif data == "otc_live":
        loading_msg = await context.bot.send_message(
            chat_id=chat_id,
            text='<emoji id="5375338737028841420">🔄</emoji> 𝐀𝐧𝐚𝐥𝐲𝐳𝐢𝐧𝐠 𝐎𝐓𝐂 𝐌𝐚𝐫𝐤𝐞𝐭 𝐓𝐫𝐞𝐧𝐝𝐬 & 𝐏𝐫𝐢𝐜𝐞 𝐀𝐜𝐭𝐢𝐨𝐧... 𝐏𝐥𝐞𝐚𝐬𝐞 𝐖𝐚𝐢𝐭 <emoji id="5440621591387980068">⏳</emoji>',
            parse_mode="HTML"
        )
        await asyncio.sleep(2)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
        except:
            pass
        
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓 <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐎𝐓𝐂 𝐋𝐈𝐕𝐄 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐄𝐍𝐆𝐈𝐍𝐄 <emoji id="5231200819986047254">📊</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐭𝐡𝐞 𝐩𝐫𝐨𝐟𝐞𝐬𝐬𝐢𝐨𝐧𝐚𝐥 𝐎𝐓𝐂 𝐥𝐢𝐯𝐞 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐡𝐮𝐛. 𝐇𝐞𝐫𝐞 𝐲𝐨𝐮 𝐫𝐞𝐜𝐞𝐢𝐯𝐞 𝐡𝐢𝐠𝐡-𝐚𝐜𝐜𝐮𝐫𝐚𝐜𝐲 𝐫𝐞𝐚𝐥-𝐭𝐢𝐦𝐞 𝐬𝐢𝐠𝐧𝐚𝐥𝐬 𝐨𝐩𝐭𝐢𝐦𝐢𝐳𝐞𝐝 𝐟𝐨𝐫 𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐦𝐚𝐫𝐤𝐞𝐭 𝐬𝐞𝐬𝐬𝐢𝐨𝐧.\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐀𝐬𝐬𝐞𝐭: USD/PHP (OTC)\n'
            f'<emoji id="5805532930662996322">🟢</emoji> 𝐃𝐢𝐫𝐞𝐜𝐭𝐢𝐨𝐧: CALL (BUY) <emoji id="5449683594425410231">📈</emoji>\n'
            f'<emoji id="5330157467781312171">🕒</emoji> 𝐄𝐧𝐭𝐫𝐲 𝐓𝐢𝐦𝐞: Next Candle / 1 Minute Expiry\n'
            f'<emoji id="5447410659077661506">🌐</emoji> 𝐓𝐢𝐦𝐞𝐳𝐨𝐧𝐞: Pakistan Standard Time (UTC+05:00)\n'
            f'<emoji id="5447644880824181073">⚠️</emoji> 𝐑𝐮𝐥𝐞: 1 Step MTG Allowed\n\n'
            f'<emoji id="5879770735999717115">👤</emoji> 𝐀𝐧𝐚𝐥𝐲𝐬𝐭: @MK_TRADER586 <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5875008416132370818">👇</emoji> 𝐑𝐚𝐭𝐞 𝐲𝐨𝐮𝐫 𝐭𝐫𝐚𝐝𝐞 𝐩𝐞𝐫𝐟𝐨𝐫𝐦𝐚𝐧𝐜𝐞 𝐛𝐞𝐥𝐨𝐰:'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 𝐖𝐈𝐍 (𝐈𝐓𝐌)", callback_data="signal_win"), InlineKeyboardButton("👎 𝐋𝐎𝐒𝐒 (𝐎𝐓𝐌)", callback_data="signal_loss")],
            [InlineKeyboardButton("🔄 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐄 𝐍𝐄𝐖 𝐒𝐈𝐆𝐍𝐀𝐋", callback_data="otc_live")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home_delete")]
        ])
        await context.bot.send_message(chat_id=chat_id, text=resp_text, reply_markup=kb, parse_mode="HTML")

    elif data == "analysis_signals":
        loading_msg = await context.bot.send_message(
            chat_id=chat_id,
            text='<emoji id="5375338737028841420">🔄</emoji> 𝐀𝐧𝐚𝐥𝐲𝐳𝐢𝐧𝐠 𝐎𝐓𝐂 𝐌𝐚𝐫𝐤𝐞𝐭 𝐓𝐫𝐞𝐧𝐝𝐬 & 𝐏𝐫𝐢𝐜𝐞 𝐀𝐜𝐭𝐢𝐨𝐧... 𝐏𝐥𝐞𝐚𝐬𝐞 𝐖𝐚𝐢𝐭 <emoji id="5440621591387980068">⏳</emoji>',
            parse_mode="HTML"
        )
        await asyncio.sleep(2)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
        except:
            pass
        
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓 <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5449683594425410231">📈</emoji> 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐇𝐔𝐁 <emoji id="5449683594425410231">📈</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐃𝐞𝐭𝐚𝐢𝐥𝐞𝐝 𝐭𝐞𝐜𝐡𝐧𝐢𝐜𝐚𝐥 𝐚𝐧𝐝 𝐩𝐫𝐢𝐜𝐞 𝐚𝐜𝐭𝐢𝐨𝐧 𝐦𝐚𝐫𝐤𝐞𝐭 𝐚𝐧𝐚𝐥𝐲𝐬𝐢𝐬 𝐬𝐢𝐠𝐧𝐚𝐥𝐬 𝐟𝐨𝐫 𝐝𝐢𝐠𝐢𝐭𝐚𝐥 𝐨𝐩𝐭𝐢𝐨𝐧𝐬 𝐭𝐫𝐚𝐝𝐢𝐧𝐠.\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐀𝐬𝐬𝐞𝐭: EUR/USD (Live Market)\n'
            f'<emoji id="5420323339723881652">🔴</emoji> 𝐃𝐢𝐫𝐞𝐜𝐭𝐢𝐨𝐧: PUT (SELL) <emoji id="5447183459602669338">📉</emoji>\n'
            f'<emoji id="5330157467781312171">🕒</emoji> 𝐄𝐧𝐭𝐫𝐲: Immediate / 1 Minute Expiry\n'
            f'<emoji id="5447410659077661506">🌐</emoji> 𝐓𝐢𝐦𝐞𝐳𝐨𝐧𝐞: Pakistan Standard Time (UTC+05:00)\n'
            f'<emoji id="5422439311196834318">💡</emoji> 𝐒𝐞𝐭𝐮𝐩 𝐄𝐱𝐩𝐥𝐚𝐧𝐚𝐭𝐢𝐨𝐧: Strong resistance level rejection accompanied by volume exhaustion.\n\n'
            f'<emoji id="5879770735999717115">👤</emoji> 𝐀𝐧𝐚𝐥𝐲𝐬𝐭: @MK_TRADER586 <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5875008416132370818">👇</emoji> 𝐑𝐚𝐭𝐞 𝐲𝐨𝐮𝐫 𝐭𝐫𝐚𝐝𝐞 𝐩𝐞𝐫𝐟𝐨𝐫𝐦𝐚𝐧𝐜𝐞 𝐛𝐞𝐥𝐨𝐰:'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 𝐖𝐈𝐍 (𝐈𝐓𝐌)", callback_data="signal_win"), InlineKeyboardButton("👎 𝐋𝐎𝐒𝐒 (𝐎𝐓𝐌)", callback_data="signal_loss")],
            [InlineKeyboardButton("🔄 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐄 𝐍𝐄𝐖 𝐒𝐈𝐆𝐍𝐀𝐋", callback_data="analysis_signals")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home_delete")]
        ])
        await context.bot.send_message(chat_id=chat_id, text=resp_text, reply_markup=kb, parse_mode="HTML")

    elif data == "future_signals":
        loading_msg = await context.bot.send_message(
            chat_id=chat_id,
            text='<emoji id="5375338737028841420">🔄</emoji> 𝐀𝐧𝐚𝐥𝐲𝐳𝐢𝐧𝐠 𝐎𝐓𝐂 𝐌𝐚𝐫𝐤𝐞𝐭 𝐓𝐫𝐞𝐧𝐝𝐬 & 𝐏𝐫𝐢𝐜𝐞 𝐀𝐜𝐭𝐢𝐨𝐧... 𝐏𝐥𝐞𝐚𝐬𝐞 𝐖𝐚𝐢𝐭 <emoji id="5440621591387980068">⏳</emoji>',
            parse_mode="HTML"
        )
        await asyncio.sleep(2)
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
            f'<emoji id="5438496463044752972">👑</emoji> 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓 <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5436113877181941026">🔮</emoji> 𝟖 𝐅𝐔𝐓𝐔𝐑𝐄 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄 <emoji id="5436113877181941026">🔮</emoji>\n\n'
            f'<emoji id="5413879192267805083">📅</emoji> 𝐃𝐚𝐭𝐞: Today\'s Live Active Session\n'
            f'<emoji id="5447410659077661506">🌐</emoji> 𝐓𝐢𝐦𝐞𝐳𝐨𝐧𝐞: Pakistan Standard Time (UTC+05:00)\n\n'
            f"1. <emoji id=\"5330157467781312171\">🕒</emoji> {t1} | <emoji id=\"5409048419211682843\">💎</emoji> GBP/USD (OTC) | <emoji id=\"5449683594425410231\">📈</emoji> UP (CALL)\n"
            f"2. <emoji id=\"5330157467781312171\">🕒</emoji> {t2} | <emoji id=\"5409048419211682843\">💎</emoji> EUR/JPY | <emoji id=\"5447183459602669338\">📉</emoji> DOWN (PUT)\n"
            f"3. <emoji id=\"5330157467781312171\">🕒</emoji> {t3} | <emoji id=\"5409048419211682843\">💎</emoji> AUD/CAD (OTC) | <emoji id=\"5449683594425410231\">📈</emoji> UP (CALL)\n"
            f"4. <emoji id=\"5330157467781312171\">🕒</emoji> {t4} | <emoji id=\"5409048419211682843\">💎</emoji> USD/BDT (OTC) | <emoji id=\"5447183459602669338\">📉</emoji> DOWN (PUT)\n"
            f"5. <emoji id=\"5330157467781312171\">🕒</emoji> {t5} | <emoji id=\"5409048419211682843\">💎</emoji> EUR/CAD | <emoji id=\"5449683594425410231\">📈</emoji> UP (CALL)\n"
            f"6. <emoji id=\"5330157467781312171\">🕒</emoji> {t6} | <emoji id=\"5409048419211682843\">💎</emoji> NZD/USD (OTC) | <emoji id=\"5447183459602669338\">📉</emoji> DOWN (PUT)\n"
            f"7. <emoji id=\"5330157467781312171\">🕒</emoji> {t7} | <emoji id=\"5409048419211682843\">💎</emoji> EUR/GBP | <emoji id=\"5449683594425410231\">📈</emoji> UP (CALL)\n"
            f"8. <emoji id=\"5330157467781312171\">🕒</emoji> {t8} | <emoji id=\"5409048419211682843\">💎</emoji> USD/JPY (OTC) | <emoji id=\"5447183459602669338\">📉</emoji> DOWN (PUT)\n\n"
            f'<emoji id="5879770735999717115">👤</emoji> 𝐀𝐧𝐚𝐥𝐲𝐬𝐭: @MK_TRADER586 <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5447644880824181073">⚠️</emoji> 𝐍𝐨𝐭𝐞: Follow strict risk management and prepare your entries ahead of time.'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 𝐑𝐄𝐅𝐑𝐄𝐒𝐇 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄", callback_data="future_signals")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home_delete")]
        ])
        await context.bot.send_message(chat_id=chat_id, text=resp_text, reply_markup=kb, parse_mode="HTML")

    elif data == "ai_signals_pro":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5931415565955503486">🤖</emoji> 𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎 <emoji id="5931415565955503486">🤖</emoji>\n\n'
            f'<emoji id="5875078273775439450">🚀</emoji> 𝐄𝐋𝐄𝐕𝐀𝐓𝐄 𝐘𝐎𝐔𝐑 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐆𝐀𝐌𝐄!\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐄𝐱𝐩𝐥𝐨𝐫𝐞 𝐀𝐈-𝐚𝐬𝐬𝐢𝐬𝐭𝐞𝐝 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐬𝐢𝐠𝐧𝐚𝐥𝐬 𝐚𝐧𝐝 𝐦𝐚𝐫𝐤𝐞𝐭 𝐢𝐧𝐬𝐢𝐠𝐡𝐭𝐬 𝐰𝐢𝐭𝐡 𝐨𝐮𝐫 𝐩𝐫𝐞𝐦𝐢𝐮𝐦 𝐬𝐢𝐠𝐧𝐚𝐥𝐬 𝐛𝐨𝐭, 𝐝𝐞𝐬𝐢𝐠𝐧𝐞𝐝 𝐟𝐨𝐫 𝐭𝐫𝐚𝐝𝐞𝐫𝐬 𝐰𝐡𝐨 𝐰𝐚𝐧𝐭 𝐚 𝐬𝐦𝐚𝐫𝐭𝐞𝐫 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐞𝐱𝐩𝐞𝐫𝐢𝐞𝐧𝐜𝐞. <emoji id="5224607267797606837">⚡</emoji><emoji id="5397782960512444700">🎯</emoji>\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐀𝐂𝐂𝐄𝐒𝐒:\n'
            f'<emoji id="5411225014148014586">⏺</emoji> <emoji id="5409048419211682843">💵</emoji> 𝐒𝐔𝐁𝐒𝐂𝐑𝐈𝐏𝐓𝐈𝐎𝐍 𝐅𝐄𝐄: $𝟐𝟎 𝐎𝐍𝐋𝐘 <emoji id="5409048419211682843">💎</emoji>\n\n'
            f'<emoji id="5877597667231534929">📌</emoji> 𝐇𝐎𝐖 𝐓𝐎 𝐉𝐎𝐈𝐍:\n'
            f"1️⃣ <emoji id=\"5206636501860893075\">💳</emoji> 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞 𝐲𝐨𝐮𝐫 $𝟐𝟎 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 𝐩𝐚𝐲𝐦𝐞𝐧𝐭.\n"
            f"2️⃣ <emoji id=\"5967280668885913944\">🧾</emoji> 𝐒𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐩𝐚𝐲𝐦𝐞𝐧𝐭 𝐫𝐞𝐜𝐞𝐢𝐩𝐭 𝐭𝐨 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫.\n"
            f"3️⃣ <emoji id=\"5805532930662996322\">✅</emoji> 𝐖𝐚𝐢𝐭 𝐟𝐨𝐫 𝐢𝐧𝐬𝐭𝐚𝐧𝐭 𝐩𝐚𝐲𝐦𝐞𝐧𝐭 𝐯𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧.\n"
            f"4️⃣ <emoji id=\"5296369303661067030\">🔓</emoji> 𝐑𝐞𝐜𝐞𝐢𝐯𝐞 𝐟𝐮𝐥𝐥 𝐢𝐧𝐬𝐭𝐫𝐮𝐜𝐭𝐢𝐨𝐧𝐬 𝐭𝐨 𝐚𝐜𝐜𝐞𝐬𝐬 𝐭𝐡𝐞 𝐛𝐨𝐭!\n\n"
            f'<emoji id="5438496463044752972">👑</emoji> 𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐒𝐌𝐀𝐑𝐓 𝐈𝐍𝐒𝐈𝐆𝐇𝐓𝐒 • 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐀𝐂𝐂𝐄𝐒𝐒 <emoji id="4996980495100150380">✨</emoji>\n\n'
            f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏 𝐎𝐑 𝐑𝐄𝐀𝐃𝐘 𝐓𝐎 𝐏𝐀𝐘?\n'
            f'𝐓𝐚𝐩 𝐭𝐡𝐞 "💳 𝐏𝐀𝐘𝐌𝐄𝐍𝐓" 𝐨𝐫 "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑" 𝐛𝐮𝐭𝐭𝐨𝐧 𝐛𝐞𝐥𝐨𝐰! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐕𝐈𝐏 𝐋𝐈𝐍𝐊", url=QUOTEX_LINK)],
            [InlineKeyboardButton("💳 𝐏𝐀𝐘𝐌𝐄𝐍𝐓", url=ADMIN_USERNAME), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "future_list":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5877597667231534929">📋</emoji> 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍 & 𝐅𝐔𝐓𝐔𝐑𝐄 𝐋𝐈𝐒𝐓 <emoji id="5877597667231534929">📋</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐄𝐯𝐞𝐫𝐲𝐭𝐡𝐢𝐧𝐠 𝐲𝐨𝐮 𝐧𝐞𝐞𝐝 𝐭𝐨 𝐦𝐚𝐬𝐭𝐞𝐫 𝐭𝐡𝐞 𝐦𝐚𝐫𝐤𝐞𝐭 — 𝐞𝐬𝐬𝐞𝐧𝐭𝐢𝐚𝐥 𝐢𝐧𝐬𝐢𝐠𝐡𝐭𝐬, 𝐚𝐬𝐬𝐞𝐭 𝐚𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐚𝐧𝐝 𝐩𝐫𝐨 𝐠𝐮𝐢𝐝𝐚𝐧𝐜𝐞 𝐚𝐥𝐥 𝐢𝐧 𝐨𝐧𝐞 𝐩𝐥𝐚𝐜𝐞:\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐀𝐒𝐒𝐄𝐓 𝐃𝐈𝐑𝐄𝐂𝐓𝐎𝐑𝐘:\n𝐄𝐱𝐩𝐥𝐨𝐫𝐞 𝐦𝐚𝐣𝐨𝐫 𝐜𝐮𝐫𝐫𝐞𝐧𝐜𝐲 𝐩𝐚𝐢𝐫𝐬, 𝐎𝐓𝐂 𝐚𝐬𝐬𝐞𝐭𝐬, 𝐚𝐧𝐝 𝐡𝐢𝐠𝐡-𝐲𝐢𝐞𝐥𝐝 𝐦𝐚𝐫𝐤𝐞𝐭 𝐢𝐧𝐬𝐭𝐫𝐮𝐦𝐞𝐧𝐭𝐬.\n\n'
            f'<emoji id="5447410659077661506">🌍</emoji> 𝐌𝐀𝐑𝐊𝐄𝐓 𝐓𝐈𝐌𝐈𝐍𝐆𝐒:\n𝐎𝐩𝐭𝐢𝐦𝐢𝐳𝐞 𝐲𝐨𝐮𝐫 𝐬𝐞𝐭𝐮𝐩𝐬 𝐚𝐜𝐫𝐨𝐬𝐬 𝐀𝐬𝐢𝐚𝐧, 𝐋𝐨𝐧𝐝𝐨𝐧, 𝐚𝐧𝐝 𝐍𝐞𝐰 𝐘𝐨𝐫𝐤 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐬𝐞𝐬𝐬𝐢𝐨𝐧𝐬.\n\n'
            f'<emoji id="5449683594425410231">📈</emoji> 𝐏𝐑𝐈𝐂𝐄 𝐀𝐂𝐓𝐈𝐎𝐍 𝐆𝐔𝐈𝐃𝐄:\n𝐌𝐚𝐬𝐭𝐞𝐫 𝐤𝐞𝐲 𝐜𝐡𝐚𝐫𝐭 𝐩𝐚𝐭𝐭𝐞𝐫𝐧𝐬, 𝐦𝐚𝐫𝐤𝐞𝐭 𝐭𝐫𝐞𝐧𝐝𝐬, 𝐚𝐧𝐝 𝐡𝐢𝐠𝐡-𝐩𝐫𝐨𝐛𝐚𝐛𝐢𝐥𝐢𝐭𝐲 𝐩𝐫𝐢𝐜𝐞 𝐦𝐨𝐯𝐞𝐦𝐞𝐧𝐭𝐬.\n\n'
            f'<emoji id="5296369303661067030">🛡️</emoji> 𝐑𝐈𝐒𝐊 𝐀𝐖𝐀𝐑𝐄𝐍𝐄𝐒𝐒:\n𝐈𝐦𝐩𝐥𝐞𝐦𝐞𝐧𝐭 𝐬𝐭𝐫𝐢𝐜𝐭 𝐜𝐚𝐩𝐢𝐭𝐚𝐥 𝐩𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧 𝐫𝐮𝐥𝐞𝐬 𝐚𝐧𝐝 𝐝𝐢𝐬𝐜𝐢𝐩𝐥𝐢𝐧𝐞𝐝 𝐝𝐞𝐜𝐢𝐬𝐢𝐨𝐧-𝐦𝐚𝐤𝐢𝐧𝐠.\n\n'
            f'<emoji id="5330157467781312171">⏱️</emoji> 𝐄𝐗𝐏𝐈𝐑𝐘 𝐓𝐈𝐌𝐄 𝐆𝐔𝐈𝐃𝐄:\n𝐔𝐧𝐝𝐞𝐫𝐬𝐭𝐚𝐧𝐝 𝟏-𝐦𝐢𝐧𝐮𝐭𝐞 𝐚𝐧𝐝 𝟓-𝐦𝐢𝐧𝐮𝐭𝐞 𝐞𝐱𝐞𝐜𝐮𝐭𝐢𝐨𝐧 𝐬𝐭𝐫𝐚𝐭𝐞𝐠𝐢𝐞𝐬 𝐚𝐧𝐝 𝐤𝐞𝐲 𝐝𝐢𝐟𝐟𝐞𝐫𝐞𝐧𝐜𝐞𝐬.\n\n'
            f'<emoji id="5992157823838984339">📚</emoji> 𝐏𝐑𝐎 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐓𝐄𝐑𝐌𝐒:\n𝐋𝐞𝐚𝐫𝐧 𝐞𝐬𝐬𝐞𝐧𝐭𝐢𝐚𝐥 𝐦𝐚𝐫𝐤𝐞𝐭 𝐯𝐨𝐜𝐚𝐛𝐮𝐥𝐚𝐫𝐲, 𝐭𝐞𝐜𝐡𝐧𝐢𝐜𝐚𝐥 𝐭𝐞𝐫𝐦𝐬, 𝐚𝐧𝐝 𝐜𝐨𝐫𝐞 𝐝𝐞𝐟𝐢𝐧𝐢𝐭𝐢𝐨𝐧𝐬.\n\n'
            f'<emoji id="5271604874419647061">🔗</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:\n{QUOTEX_LINK} <emoji id="5447410659077661506">🌐</emoji>\n\n'
            f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?\n𝐓𝐚𝐩 𝐭𝐡𝐞 "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑" 𝐛𝐮𝐭𝐭𝐨𝐧 𝐛𝐞𝐥𝐨𝐰 𝐟𝐨𝐫 𝐝𝐢𝐫𝐞𝐜𝐭 𝐚𝐬𝐬𝐢𝐬𝐭𝐚𝐧𝐜𝐞! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄", callback_data="trading_guidance")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "personal_sessions":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5879770735999717115">👤</emoji> 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 & 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄 <emoji id="5879770735999717115">👤</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐆𝐞𝐭 𝐞𝐱𝐜𝐥𝐮𝐬𝐢𝐯𝐞 𝐨𝐧𝐞-𝐭𝐨-𝐨𝐧𝐞 𝐩𝐞𝐫𝐬𝐨𝐧𝐚𝐥 𝐬𝐞𝐬𝐬𝐢𝐨𝐧𝐬 𝐰𝐢𝐭𝐡 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐚𝐧𝐝 𝐞𝐱𝐩𝐞𝐫𝐢𝐞𝐧𝐜𝐞 𝐝𝐢𝐫𝐞𝐜𝐭 𝐦𝐞𝐧𝐭𝐨𝐫𝐬𝐡𝐢𝐩, 𝐢𝐧𝐝𝐢𝐯𝐢𝐝𝐮𝐚𝐥 𝐚𝐭𝐭𝐞𝐧𝐭𝐢𝐨𝐧 & 𝐩𝐞𝐫𝐬𝐨𝐧𝐚𝐥𝐢𝐳𝐞𝐝 𝐦𝐚𝐫𝐤𝐞𝐭 𝐠𝐮𝐢𝐝𝐚𝐧𝐜𝐞.\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐎𝐍𝐄-𝐓𝐎-𝐎𝐍𝐄 𝐌𝐄𝐍𝐓𝐎𝐑𝐒𝐇𝐈𝐏\n𝐄𝐧𝐣𝐨𝐲 𝐩𝐫𝐢𝐯𝐚𝐭𝐞 𝐬𝐞𝐬𝐬𝐢𝐨𝐧𝐬 𝐰𝐢𝐭𝐡 𝐝𝐢𝐫𝐞𝐜𝐭 𝐢𝐧𝐭𝐞𝐫𝐚𝐜𝐭𝐢𝐨𝐧 𝐚𝐧𝐝 𝐩𝐞𝐫𝐬𝐨𝐧𝐚𝐥 𝐠𝐮𝐢𝐝𝐚𝐧𝐜𝐞.\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐈𝐍𝐃𝐈𝐕𝐈𝐃𝐔𝐀𝐋 𝐌𝐀𝐑𝐊𝐄𝐓 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒\n𝐃𝐢𝐬𝐜𝐮𝐬𝐬 𝐜𝐡𝐚𝐫𝐭 𝐩𝐚𝐭𝐭𝐞𝐫𝐧𝐬, 𝐦𝐚𝐫𝐤𝐞𝐭 𝐦𝐨𝐯𝐞𝐦𝐞𝐧𝐭𝐬 & 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐬𝐭𝐫𝐚𝐭𝐞𝐠𝐢𝐞𝐬 𝐩𝐞𝐫𝐬𝐨𝐧𝐚𝐥𝐥𝐲.\n\n'
            f'<emoji id="5397782960512444700">🎯</emoji> 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋𝐈𝐙𝐄𝐃 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐏𝐋𝐀𝐍\n𝐒𝐞𝐬𝐬𝐢𝐨𝐧𝐬 𝐚𝐫𝐫𝐚𝐧𝐠𝐞𝐝 𝐚𝐜𝐜𝐨𝐫𝐝𝐢𝐧𝐠 𝐭𝐨 𝐲𝐨𝐮𝐫 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐢𝐥𝐢𝐭𝐲 𝐚𝐧𝐝 𝐥𝐞𝐚𝐫𝐧𝐢𝐧𝐠 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐦𝐞𝐧𝐭𝐬.\n\n'
            f'<emoji id="5422439311196834318">🧠</emoji> 𝐃𝐈𝐑𝐄𝐂𝐓 𝐏𝐑𝐎𝐅𝐄𝐒𝐒𝐈𝐎𝐍𝐀𝐋 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄\n𝐆𝐞𝐭 𝐩𝐞𝐫𝐬𝐨𝐧𝐚𝐥 𝐚𝐭𝐭𝐞𝐧𝐭𝐢𝐨𝐧 𝐨𝐧 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐩𝐬𝐲𝐜𝐡𝐨𝐥𝐨𝐠𝐲, 𝐝𝐢𝐬𝐜𝐢𝐩𝐥𝐢𝐧𝐞 & 𝐫𝐢𝐬𝐤 𝐦𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭.\n\n'
            f'<emoji id="5438496463044752972">👑</emoji> 𝐄𝐗𝐂𝐋𝐔𝐒𝐈𝐕𝐄 𝐕𝐈𝐏 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐀𝐂𝐂𝐄𝐒𝐒\nA private learning experience with direct communication and dedicated mentorship.\n\n'
            f'<emoji id="5424972470023104089">🔥</emoji> 𝐘𝐎𝐔𝐑 𝐒𝐄𝐒𝐒𝐈𝐎𝐍. 𝐘𝐎𝐔𝐑 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄. 𝐘𝐎𝐔𝐑 𝐋𝐄𝐀𝐑𝐍𝐈𝐍𝐆.\n\n'
            f'<emoji id="5875008416132370818">👇</emoji> 𝐂𝐋𝐈𝐂𝐊 𝐁𝐄𝐋𝐎𝐖 𝐓𝐎 𝐔𝐍𝐋𝐎𝐂𝐊 𝐕𝐈𝐏 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 𝐎𝐑 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐅𝐎𝐑 𝐘𝐎𝐔𝐑 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍:'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐅𝐎𝐑 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "loss_recovery":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5409048419211682843">💸</emoji> 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 & 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄 <emoji id="5409048419211682843">💸</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐅𝐚𝐜𝐞𝐝 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐥𝐨𝐬𝐬𝐞𝐬? 𝐆𝐞𝐭 𝐝𝐞𝐝𝐢𝐜𝐚𝐭𝐞𝐝 𝐨𝐧𝐞-𝐭𝐨-𝐨𝐧𝐞 𝐫𝐞𝐜𝐨𝐯𝐞𝐫𝐲 𝐠𝐮𝐢𝐝𝐚𝐧𝐜𝐞 𝐰𝐢𝐭𝐡 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑. 𝐑𝐞𝐯𝐢𝐞𝐰 𝐩𝐫𝐞𝐯𝐢𝐨𝐮𝐬 𝐭𝐫𝐚𝐝𝐞𝐬, 𝐮𝐧𝐝𝐞𝐫𝐬𝐭𝐚𝐧𝐝 𝐰𝐡𝐚𝐭 𝐰𝐞𝐧𝐭 𝐰𝐫𝐨𝐧𝐠 & 𝐥𝐞𝐚𝐫𝐧 𝐚 𝐦𝐨𝐫𝐞 𝐝𝐢𝐬𝐜𝐢𝐩𝐥𝐢𝐧𝐞𝐝 𝐚𝐩𝐩𝐫𝐨𝐚𝐜𝐡 𝐛𝐞𝐟𝐨𝐫𝐞 𝐦𝐚𝐤𝐢𝐧𝐠 𝐲𝐨𝐮𝐫 𝐧𝐞𝐱𝐭 𝐝𝐞𝐜𝐢𝐬𝐢𝐨𝐧.\n\n'
            f'<emoji id="5447183459602669338">📉</emoji> 𝐏𝐑𝐄𝐕𝐈𝐎𝐔𝐒 𝐋𝐎𝐒𝐒 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒\n• Detailed review of previous trades and mistakes.\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 𝐏𝐋𝐀𝐍𝐍𝐈𝐍𝐆\n• Individual guidance to review your situation and plan your next steps responsibly.\n\n'
            f'<emoji id="5422439311196834318">🧠</emoji> 𝐄𝐌𝐎𝐓𝐈𝐎𝐍𝐀𝐋 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 & 𝐃𝐈𝐒𝐂𝐈𝐏𝐋𝐈𝐍𝐄\n• Learn to avoid revenge trading and impulsive decisions.\n\n'
            f'<emoji id="5296369303661067030">🛡️</emoji> 𝐑𝐈𝐒𝐊 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓\n• Understand risk limits and protect yourself from further unnecessary exposure.\n\n'
            f'<emoji id="5879770735999717115">👤</emoji> 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐕𝐈𝐏 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄\n• Get one-to-one educational support and individual trade reviews.\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 — 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄\n\n'
            f'<emoji id="5875008416132370818">👇</emoji> 𝐂𝐋𝐈𝐂𝐊 𝐁𝐄𝐋𝐎𝐖 𝐓𝐎 𝐄𝐗𝐏𝐋𝐎𝐑𝐄 𝐕𝐈𝐏 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 𝐎𝐑 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐓𝐇𝐄 𝐎𝐖𝐍𝐄𝐑'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "how_to_create":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5967389567781703494">🎩</emoji> 𝐇𝐎𝐖 𝐓𝐎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐀𝐍𝐃 𝐕𝐄𝐑𝐈𝐅𝐘 𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓 <emoji id="5967389567781703494">🎩</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐅𝐨𝐥𝐥𝐨𝐰 𝐭𝐡𝐞𝐬𝐞 𝐬𝐢𝐦𝐩𝐥𝐞 𝐬𝐭𝐞𝐩𝐬 𝐭𝐨 𝐚𝐜𝐭𝐢𝐯𝐚𝐭𝐞 𝐲𝐨𝐮𝐫 𝐕𝐈𝐏 𝐚𝐜𝐜𝐞𝐬𝐬:\n\n'
            f"1️⃣ 𝐂𝐑𝐄𝐀𝐓𝐄 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:\nRegister your new account using the secure link provided below.\n\n"
            f"2️⃣ 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄 𝐒𝐄𝐓𝐔𝐏:\nFinish your profile setup and complete your KYC identity verification.\n\n"
            f"3️⃣ 𝐂𝐎𝐏𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:\nGo to your account dashboard and copy your official 8-digit Trader ID.\n\n"
            f"4️⃣ 𝐒𝐔𝐁𝐌𝐈𝐓 𝐅𝐎𝐑 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍:\nTap \"🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃\" below and submit your ID to the bot.\n\n"
            f"5️⃣ 𝐔𝐍𝐋𝐎𝐂𝐊 𝐕𝐈𝐏 𝐀𝐂𝐂𝐄𝐒𝐒:\nOnce verified by the team, your full VIP membership will be activated automatically!\n\n"
            f'<emoji id="5271604874419647061">🔗</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:\n{QUOTEX_LINK} <emoji id="5447410659077661506">🌐</emoji>\n\n'
            f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?\nTap the "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑" button below to message support directly! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "vip_joining":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 & 𝐄𝐋𝐈𝐆𝐈𝐁𝐈𝐋𝐈𝐓𝐘 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄 <emoji id="5409048419211682843">💎</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐔𝐧𝐥𝐨𝐜𝐤 𝐞𝐥𝐢𝐭𝐞 𝐟𝐢𝐧𝐚𝐧𝐜𝐢𝐚𝐥 𝐛𝐞𝐧𝐞𝐟𝐢𝐭𝐬 𝐰𝐢𝐭𝐡 𝐌.𝐊 𝐕𝐈𝐏 𝐌𝐞𝐦𝐛𝐞𝐫𝐬𝐡𝐢𝐩:\n\n'
            f'<emoji id="5397782960512444700">🎯</emoji> 𝟐𝟒/𝟕 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐇𝐢𝐠𝐡-𝐀𝐜𝐜𝐮𝐫𝐚𝐜𝐲 𝐒𝐢𝐠𝐧𝐚𝐥𝐬 𝐅𝐞𝐞𝐝\n'
            f'<emoji id="5931415565955503486">🤖</emoji> 𝐀𝐮𝐭𝐨𝐦𝐚𝐭𝐞𝐝 𝐀𝐈 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐁𝐨𝐭 𝐅𝐮𝐥𝐥 𝐀𝐜𝐜𝐞𝐬𝐬\n'
            f'<emoji id="5449683594425410231">📈</emoji> 𝐄𝐱𝐜𝐥𝐮𝐬𝐢𝐯𝐞 𝐂𝐨𝐦𝐩𝐨𝐮𝐧𝐝 𝐒𝐞𝐬𝐬𝐢𝐨𝐧𝐬 & 𝐌𝐞𝐧𝐭𝐨𝐫𝐬𝐡𝐢𝐩\n\n'
            f'<emoji id="5877597667231534929">📌</emoji> 𝐒𝐓𝐄𝐏-𝐁𝐘-𝐒𝐓𝐄𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 𝐆𝐔𝐈𝐃𝐄:\n\n'
            f"1️⃣ 𝐂𝐑𝐄𝐀𝐓𝐄 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:\nRegister your new account using the secure link provided below.\n\n"
            f"2️⃣ 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:\nComplete profile setup, then tap \"🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃\" below to submit your 8-digit ID.\n\n"
            f"3️⃣ 𝐈𝐍𝐒𝐓𝐀𝐍𝐓 𝐀𝐂𝐂𝐄𝐒𝐒:\nGet instant approval and unlock full VIP trading privileges!\n\n"
            f'<emoji id="5271604874419647061">🔗</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:\n{QUOTEX_LINK} <emoji id="5447410659077661506">🌐</emoji>\n\n'
            f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?\nTap the "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑" button below for direct assistance! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "trading_rules":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5877597667231534929">📜</emoji> 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐑𝐔𝐋𝐄𝐒 & 𝐏𝐒𝐘𝐂𝐇𝐎𝐋𝐎𝐆𝐘 𝐆𝐔𝐈𝐃𝐄 <emoji id="5877597667231534929">📜</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐁𝐮𝐢𝐥𝐝 𝐚 𝐩𝐫𝐨𝐟𝐞𝐬𝐬𝐢𝐨𝐧𝐚𝐥 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐦𝐢𝐧𝐝𝐬𝐞𝐭 𝐚𝐧𝐝 𝐩𝐫𝐨𝐭𝐞𝐜𝐭 𝐲𝐨𝐮𝐫 𝐜𝐚𝐩𝐢𝐭𝐚𝐥 𝐰𝐢𝐭𝐡 𝐜𝐨𝐫𝐞 𝐝𝐢𝐬𝐜𝐢𝐩𝐥𝐢𝐧𝐞:\n\n'
            f'<emoji id="5422439311196834318">🧠</emoji> 𝐄𝐌𝐎𝐓𝐈𝐎𝐍𝐀𝐋 𝐂𝐎𝐍𝐓𝐑𝐎𝐋:\nNever trade with revenge mindset after a loss. Stay calm and stick to your strategy.\n\n'
            f'<emoji id="5296369303661067030">🛡️</emoji> 𝐓𝐇𝐑𝐄𝐄-𝐋𝐎𝐒𝐒 𝐒𝐓𝐎𝐏 𝐑𝐔𝐋𝐄:\nIf you hit 3 consecutive losses, close your charts immediately and take a break.\n\n'
            f'<emoji id="5397782960512444700">🎯</emoji> 𝐃𝐀𝐈𝐋𝐘 𝐓𝐀𝐑𝐆𝐄𝐓 𝐃𝐈𝐒𝐂𝐈𝐏𝐋𝐈𝐍𝐄:\nSet daily profit goals. Once your target is achieved, stop trading and protect your gains.\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐂𝐀𝐏𝐈𝐓𝐀𝐋 𝐏𝐑𝐎𝐓𝐄𝐂𝐓𝐈𝐎𝐍:\nNever risk more than 2% to 5% of your total account balance on a single trade.\n\n'
            f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?\nTap the "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑" button below for direct assistance! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME), InlineKeyboardButton("💎 𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆", callback_data="vip_joining")],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "mk_premium_vip":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐌.𝐊 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐕𝐈𝐏 𝐌𝐄𝐌𝐁𝐄𝐑𝐒𝐇𝐈𝐏 <emoji id="5409048419211682843">💎</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐄𝐥𝐞𝐯𝐚𝐭𝐞 𝐲𝐨𝐮𝐫 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐰𝐢𝐭𝐡 𝐞𝐱𝐜𝐥𝐮𝐬𝐢𝐯𝐞 𝐕𝐈𝐏 𝐚𝐜𝐜𝐞𝐬𝐬, 𝐡𝐢𝐠𝐡-𝐩𝐫𝐞𝐜𝐢𝐬𝐢𝐨𝐧 𝐬𝐢𝐠𝐧𝐚𝐥𝐬, 𝐚𝐧𝐝 𝐝𝐚𝐢𝐥𝐲 𝐦𝐚𝐫𝐤𝐞𝐭 𝐚𝐧𝐚𝐥𝐲𝐬𝐢𝐬!\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐕𝐈𝐏 𝐄𝐗𝐂𝐋𝐔𝐒𝐈𝐕𝐄 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒:\n'
            f'<emoji id="5397782960512444700">🎯</emoji> Daily 90%+ Accuracy Signal Setups\n'
            f'<emoji id="5449683594425410231">📈</emoji> Private Risk & Money Management Plan\n'
            f'<emoji id="5296369303661067030">🛡️</emoji> One-on-One Direct Trading Support\n\n'
            f'<emoji id="5877597667231534929">📌</emoji> 𝐒𝐓𝐄𝐏-𝐁𝐘-𝐒𝐓𝐄𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 𝐆𝐔𝐈𝐃𝐄:\n\n'
            f"1️⃣ 𝐂𝐑𝐄𝐀𝐓𝐄 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:\nRegister your new account using the secure link provided below.\n\n"
            f"2️⃣ 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:\nComplete profile setup, then tap \"🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃\" below to submit your 8-digit ID.\n\n"
            f"3️⃣ 𝐈𝐍𝐒𝐓𝐀𝐍𝐓 𝐀𝐂𝐂𝐄𝐒𝐒:\nGet instant approval and unlock full VIP trading privileges!\n\n"
            f'<emoji id="5271604874419647061">🔗</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:\n{QUOTEX_LINK} <emoji id="5447410659077661506">🌐</emoji>\n\n'
            f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?\nTap the "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑" button below for direct assistance! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "daily_compounding":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5447644880824181073">🚨</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐂𝐎𝐌𝐏𝐎𝐔𝐍𝐃𝐈𝐍𝐆 𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓 <emoji id="5447644880824181073">🚨</emoji>\n\n'
            f'<emoji id="5224607267797606837">⚡️</emoji> 𝐃𝐀𝐈𝐋𝐘 𝟑-𝐒𝐓𝐄𝐏 𝐂𝐎𝐌𝐏𝐎𝐔𝐍𝐃𝐈𝐍𝐆 𝐒𝐘𝐒𝐓𝐄𝐌 <emoji id="5224607267797606837">⚡️</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐑𝐞𝐚𝐝𝐲 𝐭𝐨 𝐬𝐜𝐚𝐥𝐞 𝐲𝐨𝐮𝐫 𝐜𝐚𝐩𝐢𝐭𝐚𝐥 𝐰𝐢𝐭𝐡 𝐬𝐭𝐫𝐢𝐜𝐭 𝐝𝐢𝐬𝐜𝐢𝐩𝐥𝐢𝐧𝐞? 𝐉𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐨𝐦𝐩𝐨𝐮𝐧𝐝𝐢𝐧𝐠 𝐩𝐫𝐨𝐣𝐞𝐜𝐭 𝐭𝐨𝐝𝐚𝐲!\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐒𝐘𝐒𝐓𝐄𝐌 𝐑𝐔𝐋𝐄𝐒:\n'
            f'<emoji id="5210952531676504517">❌</emoji> No random entries & zero overtrading\n'
            f'<emoji id="5397782960512444700">🎯</emoji> Accurate entry selection & risk control\n'
            f'<emoji id="5449683594425410231">📈</emoji> Profit lock & capital growth strategy\n'
            f'<emoji id="5296369303661067030">🛡️</emoji> Strict discipline & planned execution\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐖𝐇𝐀𝐓 𝐘𝐎𝐔 𝐖𝐈𝐋𝐋 𝐆𝐄𝐓:\n'
            f'<emoji id="5805532930662996322">✅</emoji> Daily high-accuracy signal setups\n'
            f'<emoji id="5805532930662996322">✅</emoji> Professional risk control protocols\n'
            f'<emoji id="5805532930662996322">✅</emoji> Structured step-by-step compounding plan\n\n'
            f'<emoji id="5438496463044752972">⭐️</emoji> VIP access to private compounding group included\n'
            f'<emoji id="5224607267797606837">⚡️</emoji> Only serious traders should join this project\n\n'
            f'<emoji id="5447410659077661506">🌐</emoji> 𝐇𝐎𝐖 𝐓𝐎 𝐉𝐎𝐈𝐍 𝐓𝐇𝐈𝐒 𝐏𝐑𝐎𝐉𝐄𝐂𝐓:\n\n'
            f"1️⃣ 𝐑𝐄𝐆𝐈𝐒𝐓𝐄𝐑 𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:\n{QUOTEX_LINK} <emoji id=\"5447410659077661506\">🌐</emoji>\n\n"
            f'2️⃣ 𝐃𝐄𝐏𝐎𝐒𝐈𝐓 & 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:\nTap the "🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃" button below! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "tour_challenge":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5447644880824181073">🚨</emoji> 𝐈𝐌𝐏𝐎𝐑𝐓𝐀𝐍𝐓 𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓 𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓 <emoji id="5447644880824181073">🚨</emoji>\n\n'
            f'<emoji id="5409048419211682843">🤑</emoji> 𝐒𝐓𝐀𝐑𝐓: $𝟑𝟎  ➔  <emoji id="5397782960512444700">🎯</emoji> 𝐓𝐀𝐑𝐆𝐄𝐓: $𝟓𝟎𝟎 𝐈𝐍  (𝟕-𝐃𝐀𝐘 𝐂𝐇𝐀𝐋𝐋𝐄𝐍𝐆𝐄)\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐓𝐡𝐢𝐧𝐤 𝐲𝐨𝐮 𝐡𝐚𝐯𝐞 𝐬𝐭𝐫𝐨𝐧𝐠 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐬𝐤𝐢𝐥𝐥𝐬? 𝐉𝐨𝐢𝐧 𝐨𝐮𝐫 𝐞𝐱𝐜𝐥𝐮𝐬𝐢𝐯𝐞 𝟕-𝐝𝐚𝐲 𝐜𝐡𝐚𝐥𝐥𝐞𝐧𝐠𝐞 𝐚𝐧𝐝 𝐠𝐫𝐨𝐰 𝐲𝐨𝐮𝐫 𝐜𝐚𝐩𝐢𝐭𝐚𝐥!\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓 𝐑𝐔𝐋𝐄𝐒:\n'
            f"↗️ Starting balance: $30\n"
            f'<emoji id="5397782960512444700">🎯</emoji> Target balance: $500\n'
            f'<emoji id="5330157467781312171">⏱️</emoji> Duration: 7 days\n'
            f'<emoji id="5296369303661067030">🛡️</emoji> Screenshot proof of progress required\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐖𝐇𝐀𝐓 𝐘𝐎𝐔 𝐖𝐈𝐋𝐋 𝐆𝐄𝐓:\n'
            f'<emoji id="5805532930662996322">✅</emoji> Exclusive 7-day challenge signals\n'
            f'<emoji id="5805532930662996322">✅</emoji> Direct account growth guidance\n'
            f'<emoji id="5805532930662996322">✅</emoji> Private community support\n\n'
            f'<emoji id="5438496463044752972">⭐️</emoji> VIP access to private signals included\n'
            f'<emoji id="5224607267797606837">⚡️</emoji> Only serious traders should join this challenge\n\n'
            f'<emoji id="5447410659077661506">🌐</emoji> 𝐇𝐎𝐖 𝐓𝐎 𝐉𝐎𝐈𝐍 𝐓𝐇𝐈𝐒 𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓:\n\n'
            f"1️⃣ 𝐑𝐄𝐆𝐈𝐒𝐓𝐄𝐑 𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:\n{QUOTEX_LINK} <emoji id=\"5447410659077661506\">🌐</emoji>\n\n"
            f'2️⃣ 𝐃𝐄𝐏𝐎𝐒𝐈𝐓 $𝟑𝟎 & 𝐒𝐄𝐍𝐃 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:\nTap the "🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃" button below! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "session_timings":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5330157467781312171">⏱️</emoji> 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐃𝐀𝐈𝐋𝐘 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 𝐓𝐈𝐌𝐈𝐍𝐆𝐒 <emoji id="5330157467781312171">⏱️</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐅𝐨𝐥𝐥𝐨𝐰 𝐨𝐮𝐫 𝐨𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐭𝐢𝐦𝐞𝐥𝐢𝐧𝐞 𝐭𝐨 𝐬𝐭𝐚𝐲 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐧𝐝 𝐣𝐨𝐢𝐧 𝐞𝐯𝐞𝐫𝐲 𝐥𝐢𝐯𝐞 𝐬𝐞𝐭𝐮𝐩 𝐨𝐧 𝐭𝐢𝐦𝐞:\n\n'
            f'<emoji id="5438496463044752972">☀️</emoji> 𝟏𝐒𝐓 — 𝐌𝐎𝐑𝐍𝐈𝐍𝐆 𝐏𝐔𝐁𝐋𝐈𝐂 𝐒𝐄𝐒𝐒𝐈𝐎𝐍\n'
            f'<emoji id="5330157467781312171">🕚</emoji> 𝐓𝐈𝐌𝐄: 𝟏𝟏:𝟎𝟎 𝐀𝐌\n'
            f'• Live Market Trends & Free Public Signals\n\n'
            f'<emoji id="5438496463044752972">👑</emoji> 𝟐𝐍𝐃 — 𝐌.𝐊 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍\n'
            f'<emoji id="5330157467781312171">🕐</emoji> 𝐓𝐈𝐌𝐄: 𝟎𝟏:𝟎𝟎 𝐏𝐌\n'
            f'• High-Accuracy Signals & Private VIP Guidance\n\n'
            f'<emoji id="5409048419211682843">🤑</emoji> 𝟑𝐑𝐃 — 𝟕-𝐃𝐀𝐘 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐂𝐇𝐀𝐋𝐋𝐄𝐍𝐆𝐄\n'
            f'<emoji id="5397782960512444700">🎯</emoji> 𝐓𝐀𝐑𝐆𝐄𝐓: $𝟑𝟎 ➔ $𝟓𝟎𝟎\n'
            f'<emoji id="5330157467781312171">🕓</emoji> 𝐓𝐈𝐌𝐄: 𝟎𝟒:𝟎𝟎 𝐏𝐌\n'
            f'• Step-By-Step Account Growth Challenge Signals\n\n'
            f'<emoji id="5449683594425410231">📈</emoji> 𝟒𝐓𝐇 — 𝐃𝐀𝐈𝐋𝐘 𝟑-𝐒𝐓𝐄𝐏 𝐂𝐎𝐌𝐏𝐎𝐔𝐍𝐃𝐈𝐍𝐆\n'
            f'<emoji id="5330157467781312171">🕖</emoji> 𝐓𝐈𝐌𝐄: 𝟎𝟕:𝟎𝟎 𝐏𝐌\n'
            f'• Exclusive High-Yield Compounding Session\n\n'
            f'<emoji id="5879770735999717115">🌙</emoji> 𝟓𝐓𝐇 — 𝐍𝐈𝐆𝐇𝐓 𝐏𝐔𝐁𝐋𝐈𝐂 𝐒𝐄𝐒𝐒𝐈𝐎𝐍\n'
            f'<emoji id="5330157467781312171">🕘</emoji> 𝐓𝐈𝐌𝐄: 𝟎𝟗:𝟎𝟎 𝐏𝐌\n'
            f'• Night Market Analysis & Free Signal Updates\n\n'
            f'<emoji id="5424972470023104089">🔥</emoji> 𝟔𝐓𝐇 — 𝐌.𝐊 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍\n'
            f'<emoji id="5330157467781312171">🕚</emoji> 𝐓𝐈𝐌𝐄: 𝟏𝟏:𝟎𝟎 𝐏𝐌\n'
            f'• Late Night VIP Signal Blast & Account Support\n\n'
            f'<emoji id="5458603043203327669">🔔</emoji> 𝐍𝐎𝐓𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍 𝐀𝐋𝐄𝐑𝐓:\nTurn on channel notifications to receive instant alerts before each session goes live!\n\n'
            f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?\nTap the "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑" button below for direct support! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME), InlineKeyboardButton("📢 𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=CHANNEL_LINK)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "acc_deleting":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5879896690210639947">🗑️</emoji> 𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐃𝐄𝐋𝐄𝐓𝐈𝐎𝐍 & 𝐑𝐄𝐒𝐄𝐓 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄 <emoji id="5879896690210639947">🗑️</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐅𝐨𝐥𝐥𝐨𝐰 𝐭𝐡𝐞𝐬𝐞 𝐬𝐞𝐜𝐮𝐫𝐞 𝐬𝐭𝐞𝐩𝐬 𝐭𝐨 𝐜𝐥𝐨𝐬𝐞 𝐨𝐫 𝐫𝐞𝐬𝐞𝐭 𝐲𝐨𝐮𝐫 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐚𝐜𝐜𝐨𝐮𝐧𝐭:\n\n'
            f"1️⃣ 𝐂𝐋𝐄𝐀𝐑 𝐁𝐀𝐋𝐀𝐍𝐂𝐄:\nCheck your active balance and clear all pending financial transactions.\n\n"
            f"2️⃣ 𝐑𝐄𝐕𝐈𝐄𝐖 𝐃𝐀𝐓𝐀:\nNote that closing your account will permanently reset your trading history.\n\n"
            f"3️⃣ 𝐃𝐄𝐋𝐄𝐓𝐄 𝐀𝐂𝐂𝐎𝐔𝐍𝐓:\nGo to Profile Settings ➡️ Delete Account, or contact official platform support if unavailable.\n\n"
            f'<emoji id="5447644880824181073">⚠️</emoji> 𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘 𝐖𝐀𝐑𝐍𝐈𝐍𝐆:\nNever share your passwords or verification codes with anyone under any circumstances!\n\n'
            f'<emoji id="5271604874419647061">🔗</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:\n{QUOTEX_LINK} <emoji id="5447410659077661506">🌐</emoji>\n\n'
            f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?\nTap the "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑" button below for direct assistance! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💎 𝐇𝐎𝐖 𝐓𝐎 𝐉𝐎𝐈𝐍 𝐕𝐈𝐏", callback_data="vip_joining")],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "acc_creation_guidance":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5395444784611480792">📖</emoji> 𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐖𝐀𝐋𝐊𝐓𝐇𝐑𝐎𝐔𝐆𝐇 <emoji id="5395444784611480792">📖</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐅𝐨𝐥𝐥𝐨𝐰 𝐭𝐡𝐢𝐬 𝐝𝐞𝐭𝐚𝐢𝐥𝐞𝐝 𝐠𝐮𝐢𝐝𝐞 𝐭𝐨 𝐞𝐧𝐬𝐮𝐫𝐞 𝐬𝐞𝐚𝐦𝐥𝐞𝐬𝐬 𝐢𝐝𝐞𝐧𝐭𝐢𝐭𝐲 𝐯𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧:\n\n'
            f"1️⃣ 𝐀𝐂𝐂𝐄𝐒𝐒 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐏𝐎𝐑𝐓𝐀𝐋:\nOpen the official registration page using the secure link provided below.\n\n"
            f"2️⃣ 𝐄𝐍𝐓𝐄𝐑 𝐀𝐂𝐂𝐔𝐑𝐀𝐓𝐄 𝐃𝐄𝐓𝐀𝐈𝐋𝐒:\nInput your real details matching your legal government ID to prevent verification issues.\n\n"
            f"3️⃣ 𝐒𝐀𝐕𝐄 𝐘𝐎𝐔𝐑 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃:\nComplete your profile confirmation and copy your unique 8-digit Trader ID.\n\n"
            f"4️⃣ 𝐒𝐔𝐁𝐌𝐈𝐓 𝐅𝐎𝐑 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍:\nTap the \"🔓 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃\" below and send your ID directly into the bot.\n\n"
            f'<emoji id="5271604874419647061">🔗</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:\n{QUOTEX_LINK} <emoji id="5447410659077661506">🌐</emoji>\n\n'
            f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?\nTap the "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑" button below for direct assistance! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "trading_guidance":
        resp_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5992157823838984339">📚</emoji> 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐄𝐃𝐔𝐂𝐀𝐓𝐈𝐎𝐍 & 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄 𝐇𝐔𝐁 <emoji id="5992157823838984339">📚</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐌𝐚𝐬𝐭𝐞𝐫 𝐭𝐡𝐞 𝐟𝐮𝐧𝐝𝐚𝐦𝐞𝐧𝐭𝐚𝐥𝐬 𝐨𝐟 𝐝𝐢𝐠𝐢𝐭𝐚𝐥 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐰𝐢𝐭𝐡 𝐩𝐫𝐨𝐟𝐞𝐬𝐬𝐢𝐨𝐧𝐚𝐥 𝐢𝐧𝐬𝐢𝐠𝐡𝐭𝐬:\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐌𝐀𝐑𝐊𝐄𝐓 𝐀𝐍𝐀𝐋𝐘𝐒𝐈𝐒 & 𝐎𝐓𝐂 𝐒𝐈𝐆𝐍𝐀𝐋𝐒:\nMaster candlestick patterns, market trends, support/resistance, and live OTC setups.\n\n'
            f'<emoji id="5296369303661067030">🛡️</emoji> 𝐑𝐈𝐒𝐊 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓 & 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘:\nApply strict capital protection rules, loss recovery strategies, and emotional discipline.\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐕𝐈𝐏 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 & 𝐄𝐋𝐈𝐓𝐄 𝐀𝐂𝐂𝐄𝐒𝐒:\nUnlock 24/7 high-accuracy signals, automated AI bot access, and exclusive trading setups.\n\n'
            f'<emoji id="5879770735999717115">👤</emoji> 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋 𝐒𝐄𝐒𝐒𝐈𝐎𝐍𝐒 & 𝐌𝐄𝐍𝐓𝐎𝐑𝐒𝐇𝐈𝐏:\nGet private 1-on-1 guidance, customized session planning, and direct account support.\n\n'
            f'<emoji id="5422439311196834318">💡</emoji> 𝐃𝐄𝐌𝐎 𝐏𝐑𝐀𝐂𝐓𝐈𝐂𝐄 & 𝐓𝐑𝐀𝐃𝐈𝐍𝐆 𝐓𝐑𝐀𝐏𝐒:\nRefine strategies safely while avoiding revenge trading, greed, and market pitfalls.\n\n'
            f'<emoji id="5436113877181941026">🔮</emoji> 𝐅𝐔𝐓𝐔𝐑𝐄 𝐋𝐈𝐒𝐓 & 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐓𝐎𝐎𝐋𝐒:\nExplore market session timings, OTC asset directories, and technical expiry strategies.\n\n'
            f'<emoji id="5875008416132370818">👇</emoji> 𝐒𝐄𝐋𝐄𝐂𝐓 𝐀𝐍𝐘 𝐎𝐏𝐓𝐈𝐎𝐍 𝐅𝐑𝐎𝐌 𝐓𝐇𝐄 𝐌𝐄𝐍𝐔 𝐁𝐄𝐋𝐎𝐖:'
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
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="5935847413859225147">🏆</emoji> 𝐓𝐎𝐔𝐑𝐍𝐀𝐌𝐄𝐍𝐓 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 & 𝐏𝐑𝐈𝐙𝐄𝐒 𝐆𝐔𝐈𝐃𝐀𝐍𝐂𝐄 <emoji id="5935847413859225147">🏆</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐏𝐚𝐫𝐭𝐢𝐜𝐢𝐩𝐚𝐭𝐞 𝐢𝐧 𝐨𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐩𝐥𝐚𝐭𝐟𝐨𝐫𝐦 𝐭𝐫𝐚𝐝𝐢𝐧𝐠 𝐭𝐨𝐮𝐫𝐧𝐚𝐦𝐞𝐧𝐭𝐬 𝐭𝐨 𝐰𝐢𝐧 𝐦𝐚𝐬𝐬𝐢𝐯𝐞 𝐜𝐚𝐬𝐡 𝐩𝐫𝐢𝐳𝐞𝐬:\n\n'
            f'<emoji id="5409048419211682843">💎</emoji> 𝐄𝐋𝐈𝐆𝐈𝐁𝐈𝐋𝐈𝐓𝐘 & 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍:\nCheck requirements and register your account via our official broker link.\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐒𝐓𝐑𝐀𝐓𝐄𝐆𝐘 & 𝐀𝐃𝐌𝐈𝐍 𝐒𝐔𝐏𝐏𝐎𝐑𝐓:\nGet direct guidance, specialized tournament setups, and competition tips.\n\n'
            f'<emoji id="5935847413859225147">🏆</emoji> 𝐂𝐀𝐒𝐇 𝐏𝐑𝐈𝐙𝐄 𝐏𝐎𝐎𝐋:\nCompete on leaderboards and secure top positions for exclusive reward distribution.\n\n'
            f'<emoji id="5271604874419647061">🔗</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐋𝐈𝐍𝐊:\n{QUOTEX_LINK} <emoji id="5447410659077661506">🌐</emoji>\n\n'
            f'<emoji id="5443038326535759644">💬</emoji> 𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏?\nTap the "💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑" button below for direct assistance! <emoji id="5805532930662996322">✅</emoji>'
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 𝐂𝐑𝐄𝐀𝐓𝐄 𝐐𝐔𝐎𝐓𝐄𝐗 𝐀𝐂𝐂𝐎𝐔𝐍𝐓", url=QUOTEX_LINK)],
            [InlineKeyboardButton("🔐 𝐕𝐄𝐑𝐈𝐅𝐘 𝐓𝐑𝐀𝐃𝐄𝐑 𝐈𝐃", callback_data="verify_id_start"), InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("💬 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 👑", url=ADMIN_USERNAME)],
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data in ["signal_win", "signal_loss"]:
        result_title = "🎉 𝐂𝐎𝐍𝐆𝐑𝐀𝐓𝐔𝐋𝐀𝐓𝐈𝐎𝐍𝐒! 𝐏𝐑𝐎𝐅𝐈𝐓 𝐑𝐄𝐂𝐎𝐑𝐃𝐄𝐃 (𝐖𝐈𝐍 🏆)" if data == "signal_win" else "⚠️ 𝐋𝐎𝐒𝐒 𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 𝐍𝐄𝐄𝐃𝐄𝐃 - 𝐑𝐄𝐂𝐎𝐕𝐄𝐑 𝐈𝐍 𝐍𝐄𝐗𝐓 𝐒𝐄𝐒𝐒𝐈𝐎𝐍"
        feedback_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f"{result_title}\n\n"
            f'<emoji id="5805532930662996322">✅</emoji> 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘!\n'
            f"Thank you for helping us track signal accuracy and improve community performance."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔", callback_data="back_home_delete")]
        ])
        await context.bot.edit_message_text(feedback_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    elif data == "back_home":
        user_name = html.escape(query.from_user.first_name if query.from_user and query.from_user.first_name else "Trader")
        welcome_text = (
            f'<emoji id="5438496463044752972">👑</emoji> {BOT_NAME} <emoji id="5438496463044752972">👑</emoji>\n\n'
            f'<emoji id="4996980495100150380">✨</emoji> 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐁𝐀𝐂𝐊, {user_name.upper()}!\n\n'
            f'<emoji id="5447410659077661506">🌐</emoji> 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐇𝐔𝐁 <emoji id="5409048419211682843">💎</emoji>\n\n'
            f'<emoji id="5231200819986047254">📊</emoji> 𝐀𝐜𝐜𝐞𝐬𝐬 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐒𝐢𝐠𝐧𝐚𝐥𝐬, 𝐌𝐚𝐫𝐤𝐞𝐭 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬, 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐆𝐮𝐢𝐝𝐞𝐬, 𝐕𝐈𝐏 𝐀𝐜𝐜𝐞𝐬𝐬, 𝐚𝐧𝐝 𝐁𝐨𝐭 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 — 𝐀𝐥𝐥 𝐈𝐧 𝐎𝐧𝐞 𝐏𝐥𝐚𝐜𝐞.\n\n'
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f'<emoji id="5271604874419647061">🔗</emoji> 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐂𝐇𝐀𝐍𝐍𝐄𝐋:\n'
            f"{CHANNEL_LINK}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f'<emoji id="5224607267797606837">⚡</emoji> 𝐒𝐭𝐚𝐲 𝐂𝐨𝐧𝐧𝐞𝐜𝐭𝐞𝐝 • 𝐒𝐭𝐚𝐲 𝐈𝐧𝐟𝐨𝐫𝐦𝐞𝐝\n\n'
            f'<emoji id="5875008416132370818">👇</emoji> 𝐒𝐄𝐋𝐄𝐂𝐓 𝐘𝐎𝐔𝐑 𝐃𝐄𝐒𝐈𝐑𝐄𝐃 𝐎𝐏𝐓𝐈𝐎𝐍\n\n'
            f'<emoji id="5296369303661067030">🛡️</emoji> 𝐓𝐫𝐚𝐝𝐢𝐧𝐠 𝐢𝐧𝐯𝐨𝐥𝐯𝐞𝐬 𝐟𝐢𝐧𝐚𝐧𝐜𝐢𝐚𝐥 𝐫𝐢𝐬𝐤. 𝐒𝐢𝐠𝐧𝐚𝐥𝐬 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐠𝐮𝐚𝐫𝐚𝐧𝐭𝐞𝐞𝐝 𝐩𝐫𝐨𝐟𝐢𝐭𝐬.'
        )
        await context.bot.edit_message_text(welcome_text, chat_id=chat_id, message_id=message_id, reply_markup=main_menu_keyboard(), parse_mode="HTML", disable_web_page_preview=True)

    elif data == "back_home_delete":
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"Delete message error: {e}")

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
                    entry_points=[CallbackQueryHandler(verify_id_start_handler, pattern="^verify_id_start$"), CallbackQueryHandler(button_callback_handler, pattern="^vip_joining$")],
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
                application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, global_text_handler))
                
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
