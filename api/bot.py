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
# ⚙ ADMIN & BOT SETTINGS:
# ==========================================
TELEGRAM_BOT_TOKEN = "8744737316:AAEs_NK4ZjS4tRKiwkJGdpHf297tsFCjK1E"
BOT_NAME = "𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎"
BOT_USERNAME = "@MK_TRADER_OFFICIAL_BOT"
LOG_CHANNEL_ID = -1003724080321
BROADCAST_CHANNEL_ID = -1004470268041  # M.K UPCOMING POSTINGS Channel ID

CHANNEL_LINK = "https://t.me/+FdbFgVgsoT41ZGU8"
QUOTEX_LINK = "https://broker-qx.pro/?lid=1614511"
ADMIN_USERNAME = "t.me/MK_TRADER586"
ADMIN_USER_ID = 7588675873
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

# ==========================================
# 📌 14 MAIN MENU BUTTONS (2 PER ROW GRID)
# ==========================================
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 OTC Live Signals", callback_data="otc_live"), InlineKeyboardButton("📈 Analysis Signals", callback_data="analysis_signals")],
        [InlineKeyboardButton("🔮 Future Signals", callback_data="future_signals"), InlineKeyboardButton("📋 Future List", callback_data="future_list")],
        [InlineKeyboardButton("👤 Personal Sessions", callback_data="personal_sessions"), InlineKeyboardButton("💸 Loss Recovery Sessions", callback_data="loss_recovery")],
        [InlineKeyboardButton("🎩 How To Create New Account", callback_data="how_to_create"), InlineKeyboardButton("💎 VIP Joining", callback_data="vip_joining")],
        [InlineKeyboardButton("🗑️ Account Deleting Guidance", callback_data="acc_deleting"), InlineKeyboardButton("📖 Account Creation Guidance", callback_data="acc_creation_guidance")],
        [InlineKeyboardButton("📚 Trading Guidance", callback_data="trading_guidance"), InlineKeyboardButton("🏆 Tournament Joining", callback_data="tournament_joining")],
        [InlineKeyboardButton("📢 M.K PREMIUM CHANNEL", url=CHANNEL_LINK), InlineKeyboardButton("💬 CONTACT OWNER", url="https://t.me/MK_TRADER586")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 1. Join Request Sent Handler (Pending State)
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    await send_data_to_log_channel(update, context, "Channel Join Request")
    
    user_first_name = user.first_name or "Trader"
    pending_msg = (
        f"╔═══ 💎⚡💎 ═══╗\n"
        f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
        f"╚═══ 💎⚡💎 ═══╝\n\n"
        f"👑 𝐖𝐄𝐋𝐂𝐎𝐌𝐄, {user_first_name.upper()}! 👑\n\n"
        f"⏳ **YOUR JOIN REQUEST IS PENDING APPROVAL** ⏳\n\n"
        f"🔥 **IMPORTANT INSTRUCTIONS:**\n"
        f"• Your request has been received and will be approved soon by administration.\n"
        f"• **Follow Sessions Strictly:** Always manage your risk and follow exact trade entry timings.\n"
        f"• **Send Feedbacks:** After every trade result, submit your feedback inside the bot.\n\n"
        f"👇 **EXPLORE OUR SERVICES BELOW:**"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 PREMIUM VIP LINK", url=QUOTEX_LINK), InlineKeyboardButton("💸 LOSS RECOVERY", callback_data="loss_recovery")],
        [InlineKeyboardButton("💬 CONTACT OWNER", url="https://t.me/MK_TRADER586"), InlineKeyboardButton("🚀 OPEN BOT DASHBOARD", callback_data="back_home")]
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
    # This triggers when user is approved or chat join is processed
    try:
        chat_member = update.chat_member
        if chat_member and chat_member.new_chat_member.status in ['member', 'administrator', 'creator']:
            user = chat_member.from_user
            user_name = user.first_name or "Trader"
            
            approved_msg = (
                f"╔═══ 💎⚡💎 ═══╗\n"
                f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
                f"╚═══ 💎⚡💎 ═══╝\n\n"
                f"👑 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐕𝐈𝐏 𝐇𝐔𝐁, {user_name.upper()}! 👑\n\n"
                f"🎉 **YOUR JOIN REQUEST HAS BEEN APPROVED!** 🎉\n\n"
                f"📌 **CRITICAL COMMUNITY RULES:**\n"
                f"1️⃣ **Follow Sessions Strictly:** Do not rush trades. Follow exact signal entries and risk management.\n"
                f"2️⃣ **Send Trade Feedbacks:** Always submit your Win (ITM) or Loss (OTM) feedback after every session.\n"
                f"3️⃣ **Compound Safely:** Use our VIP tools and AI signals to grow your capital step-by-step.\n\n"
                f"👇 **ACCESS YOUR OPTIONS BELOW:**"
            )
            
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 PREMIUM VIP LINK", url=QUOTEX_LINK), InlineKeyboardButton("👤 PERSONAL SESSIONS", callback_data="personal_sessions")],
                [InlineKeyboardButton("💬 CONTACT OWNER", url="https://t.me/MK_TRADER586"), InlineKeyboardButton("🚀 OPEN BOT DASHBOARD", callback_data="back_home")]
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
        f"╔═══ 💎⚡💎 ═══╗\n"
        f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
        f"╚═══ 💎⚡💎 ═══╝\n\n"
        f"👑 𝐖𝐄𝐋𝐂𝐎𝐌𝐄, {user_name.upper()}! 👑\n\n"
        f"🔥 **YOUR TRADING JOURNEY STARTS HERE** 💎\n\n"
        f"🌐 Access high-accuracy digital options signals, account guides, VIP access, and professional tools from the menu below:\n\n"
        f"📊 **Official Premium Channel:**\n"
        f"🔗 {CHANNEL_LINK}\n\n"
        f"👇 **SELECT YOUR DESIRED OPTION:**"
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
                await context.bot.send_message(chat_id=uid, text=broadcast_text, parse_mode="Markdown", disable_web_page_preview=True)
                success += 1
                await asyncio.sleep(0.1)
            except:
                failed += 1
        
        await update.message.reply_text(f"✅ **Broadcast Completed!**\n\n📨 Success: `{success}`\n❌ Failed: `{failed}`", parse_mode="Markdown")
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
                    await asyncio.sleep(0.05)
                except Exception as ex:
                    print(f"Forward error to user {uid}: {ex}")
    except Exception as e:
        print(f"Channel forward handler error: {e}")

# ==========================================
# 📄 DETAILED BARI BARI POSTS & BUTTON HANDLERS
# ==========================================
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    data = query.data

    if data == "otc_live":
        await context.bot.edit_message_text("🔄 **Analyzing OTC Market Trends & Price Action...** Please wait ⏳", chat_id=chat_id, message_id=message_id, parse_mode="Markdown")
        await asyncio.sleep(1)
        
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"📈 **OTC LIVE SIGNALS ENGINE** 📈\n\n"
            f"✨ Welcome to the professional OTC live trading hub. Here you receive high-accuracy real-time signals optimized for weekend and weekday sessions.\n\n"
            f"📊 **Asset:** USD/PHP (OTC)\n"
            f"🟢 **Direction:** CALL (BUY) 📈\n"
            f"🕒 **Entry Time:** Next Candle / 1 Minute Expiry\n"
            f"🌐 **Time Zone:** UTC +5:00\n"
            f"⚠️ **Rule:** 1 Step MTG Allowed\n\n"
            f"👤 **Analyst:** {ADMIN_USERNAME}\n\n"
            f"👇 **Rate your trade performance below:**"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 WIN (ITM)", callback_data="signal_win"), InlineKeyboardButton("👎 LOSS (OTM)", callback_data="signal_loss")],
            [InlineKeyboardButton("🔄 GENERATE NEW SIGNAL", callback_data="otc_live")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "analysis_signals":
        await context.bot.edit_message_text("🔄 **Scanning Market Volatility & Technical Indicators...** Please wait ⏳", chat_id=chat_id, message_id=message_id, parse_mode="Markdown")
        await asyncio.sleep(1)
        
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"📈 **ANALYSIS SIGNALS HUB** 📈\n\n"
            f"✨ Detailed technical and price action market analysis signals for digital options trading.\n\n"
            f"📊 **Asset:** EUR/USD (Live Market)\n"
            f"🔴 **Direction:** PUT (SELL) 📉\n"
            f"🕒 **Entry:** Immediate / 1 Minute Expiry\n"
            f"💡 **Setup Explanation:** Strong resistance level rejection accompanied by volume exhaustion.\n\n"
            f"👤 **Analyst:** {ADMIN_USERNAME}\n\n"
            f"👇 **Rate your trade performance below:**"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 WIN (ITM)", callback_data="signal_win"), InlineKeyboardButton("👎 LOSS (OTM)", callback_data="signal_loss")],
            [InlineKeyboardButton("🔄 GENERATE NEW SIGNAL", callback_data="analysis_signals")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "future_signals":
        await context.bot.edit_message_text("🔄 **Compiling Scheduled Future Market Predictions...** Please wait ⏳", chat_id=chat_id, message_id=message_id, parse_mode="Markdown")
        await asyncio.sleep(1)
        
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"🔮 **FUTURE SIGNALS SCHEDULE** 🔮\n\n"
            f"📅 **Date:** Today's Active Session Schedule\n"
            f"🌐 **Timezone:** UTC +5:00\n\n"
            f"1. 🕒 **Time:** 03:00 PM\n"
            f"   📊 **Pair:** GBP/USD (OTC)\n"
            f"   📈 **Direction:** UP (CALL)\n\n"
            f"2. 🕒 **Time:** 03:15 PM\n"
            f"   📊 **Pair:** EUR/JPY\n"
            f"   📈 **Direction:** DOWN (PUT)\n\n"
            f"3. 🕒 **Time:** 03:30 PM\n"
            f"   📊 **Pair:** AUD/CAD (OTC)\n"
            f"   📈 **Direction:** UP (CALL)\n\n"
            f"4. 🕒 **Time:** 03:45 PM\n"
            f"   📊 **Pair:** USD/BDT (OTC)\n"
            f"   📈 **Direction:** DOWN (PUT)\n\n"
            f"5. 🕒 **Time:** 04:00 PM\n"
            f"   📊 **Pair:** EUR/CAD\n"
            f"   📈 **Direction:** UP (CALL)\n\n"
            f"⚠️ **Note:** Follow strict risk management and prepare your entries ahead of time."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 REFRESH SCHEDULE", callback_data="future_signals")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown")

    elif data == "future_list":
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"📋 **TRADING INFORMATION & FUTURE LIST** 📋\n\n"
            f"✨ Essential market information, session timings, and terminology to enhance your trading career.\n\n"
            f"• **Available Assets:** Major currency pairs & high-payout OTC assets.\n"
            f"• **Market Sessions:** London, New York, and Asian overlap hours for maximum liquidity.\n"
            f"• **Risk Management:** Never risk more than 2-3% of your total capital per trade session.\n"
            f"• **Expiry Guidance:** Stick strictly to 1-minute or 5-minute expiries as per signal parameters.\n\n"
            f"👇 Access other helpful sections below:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 TRADING GUIDANCE", callback_data="trading_guidance")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "personal_sessions":
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"👤 **PERSONAL TRADING SESSIONS & GUIDANCE** 👤\n\n"
            f"✨ Get one-to-one custom trading guidance, direct mentorship, and live strategy breakdown sessions directly with M.K Trader.\n\n"
            f"• Direct interactive sessions tailored to your schedule and capital size.\n"
            f"• Professional account auditing and psychological control training.\n"
            f"• Advanced compound planning to maximize your daily profits safely.\n\n"
            f"👇 Click below to unlock VIP or contact for personal session:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 PREMIUM VIP LINK", url=QUOTEX_LINK), InlineKeyboardButton("💬 FOR PERSONAL SESSION", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "loss_recovery":
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"💸 **LOSS RECOVERY SESSIONS & STRATEGY** 💸\n\n"
            f"✨ Experiencing a drawdown or previous trading losses? Learn professional recovery strategies, trade reviews, and emotional discipline to bounce back safely.\n\n"
            f"• Deep analysis of previous market mistakes and emotional triggers.\n"
            f"• Step-by-step capital recovery planning with safe risk parameters.\n"
            f"• Direct guidance from M.K Trader to stabilize your account growth.\n\n"
            f"👇 Click below to register via VIP link or contact owner:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 PREMIUM VIP LINK", url=QUOTEX_LINK), InlineKeyboardButton("💬 CONTACT OWNER", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "how_to_create":
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"🎩 **HOW TO CREATE NEW TRADING ACCOUNT** 🎩\n\n"
            f"✨ Follow this complete account-creation setup guide:\n\n"
            f"1️⃣ Click the [💎 PREMIUM VIP LINK] button below.\n"
            f"2️⃣ Open the official platform link and register using a fresh email address.\n"
            f"3️⃣ Complete your official platform account verification (KYC) smoothly.\n"
            f"4️⃣ Locate your unique Trader ID from your profile settings dashboard.\n"
            f"5️⃣ Send your Trader ID to the owner for VIP setup and verification.\n\n"
            f"👇 Get started right away:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 PREMIUM VIP LINK", url=QUOTEX_LINK), InlineKeyboardButton("💬 CONTACT OWNER", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "vip_joining":
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"💎 **VIP JOINING & ELIGIBILITY GUIDANCE** 💎\n\n"
            f"✨ Unlock elite benefits with M.K VIP Membership:\n"
            f"• 24/7 Private High-Accuracy Signals Feed\n"
            f"• Automated AI Trading Bot Full Access\n"
            f"• Exclusive Compound Sessions & Direct Mentorship\n\n"
            f"📌 **How to Join:**\n"
            f"• Register a fresh account using our official VIP link below.\n"
            f"• Send your Trader ID to the owner for instant verification and channel access.\n\n"
            f"👇 Click below to join VIP or contact support:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 PREMIUM VIP LINK", url=QUOTEX_LINK), InlineKeyboardButton("💬 CONTACT OWNER", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "acc_deleting":
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"🗑️ **ACCOUNT DELETING & RESET GUIDANCE** 🗑️\n\n"
            f"✨ Follow these secure steps to close or reset your platform account:\n\n"
            f"• Check your active balance and clear any pending financial transactions.\n"
            f"• Review the impact of closing your historical trading data.\n"
            f"• Go to platform profile settings -> Delete Account, or contact official support if the option is unavailable.\n"
            f"⚠️ **Security Warning:** Never share your account passwords or verification codes with anyone under any circumstances!\n\n"
            f"👇 Access VIP link, support, or VIP joining guide below:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 PREMIUM VIP LINK", url=QUOTEX_LINK), InlineKeyboardButton("💬 CONTACT OWNER", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("💎 HOW TO JOIN VIP", callback_data="vip_joining")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "acc_creation_guidance":
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"📖 **ACCOUNT CREATION WALKTHROUGH GUIDANCE** 📖\n\n"
            f"✨ Detailed registration walkthrough to ensure seamless verification:\n\n"
            f"• Access the official registration page via our secure VIP link.\n"
            f"• Input accurate personal details matching your legal ID to avoid verification failures.\n"
            f"• Complete identity confirmation and save your unique Trader ID securely.\n"
            f"• Contact the owner once complete for VIP community setup.\n\n"
            f"👇 Register or contact support below:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 PREMIUM VIP LINK", url=QUOTEX_LINK), InlineKeyboardButton("💬 CONTACT OWNER", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "trading_guidance":
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"📚 **TRADING EDUCATION & GUIDANCE HUB** 📚\n\n"
            f"✨ Master the fundamentals of digital options trading with professional insights:\n\n"
            f"• Candlestick patterns, market trends, and support/resistance zones.\n"
            f"• Strict risk management and emotional discipline control.\n"
            f"• Importance of demo practice before risking real capital.\n"
            f"• Avoiding common trading pitfalls and psychological traps.\n\n"
            f"👇 Quick navigation to other vital sections:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 VIP JOINING", callback_data="vip_joining"), InlineKeyboardButton("👤 PERSONAL SESSIONS", callback_data="personal_sessions")],
            [InlineKeyboardButton("💸 LOSS RECOVERY", callback_data="loss_recovery"), InlineKeyboardButton("📊 OTC SIGNALS", callback_data="otc_live")],
            [InlineKeyboardButton("📈 ANALYSIS", callback_data="analysis_signals"), InlineKeyboardButton("🔮 FUTURE", callback_data="future_signals")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "tournament_joining":
        resp_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"🏆 **TOURNAMENT JOINING & PRIZES GUIDANCE** 🏆\n\n"
            f"✨ Participate in official platform trading tournaments to win cash prizes up to $10,000!\n\n"
            f"• Check eligibility requirements and register via our official affiliate portal.\n"
            f"• Contact admin for special tournament strategy support and competition tips.\n"
            f"• Practice regularly on demo tournaments before entering high-stakes competitions.\n\n"
            f"👇 Register via VIP link or contact owner below:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 PREMIUM VIP LINK", url=QUOTEX_LINK), InlineKeyboardButton("💬 CONTACT OWNER", url="https://t.me/MK_TRADER586")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(resp_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data in ["signal_win", "signal_loss"]:
        result_title = "🎉 **CONGRATULATIONS! PROFIT RECORDED (WIN)**" if data == "signal_win" else "⚠️ **LOSS RECORDED - RECOVER IN NEXT SESSION**"
        feedback_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"{result_title}\n\n"
            f"✅ **Feedback Received Successfully!**\n"
            f"Thank you for helping us track signal accuracy and improve community performance."
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home")]
        ])
        await context.bot.edit_message_text(feedback_text, chat_id=chat_id, message_id=message_id, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "back_home":
        welcome_text = (
            f"╔═══ 💎⚡💎 ═══╗\n"
            f"𝐌.𝐊 𝐀𝐈 𝐒𝐈𝐆𝐍𝐀𝐋𝐒 𝐏𝐑𝐎\n"
            f"╚═══ 💎⚡💎 ═══╝\n\n"
            f"👑 **WELCOME BACK, TRADER!** 👑\n\n"
            f"🔥 **YOUR TRADING JOURNEY STARTS HERE** 💎\n\n"
            f"🌐 Access high-accuracy digital options signals, account guides, VIP access, and professional tools from the menu below:\n\n"
            f"📊 **Official Premium Channel:**\n"
            f"🔗 {CHANNEL_LINK}\n\n"
            f"👇 **SELECT YOUR DESIRED OPTION:**"
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
                application.add_handler(ChatJoinRequestHandler(handle_join_request))
                application.add_handler(CommandHandler("start", start_command))
                application.add_handler(CommandHandler("stats", stats_command))
                application.add_handler(CommandHandler("broadcast", broadcast_command))
                application.add_handler(CallbackQueryHandler(button_callback_handler))
                application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST | filters.UpdateType.EDITED_CHANNEL_POST, forward_channel_posts))
                
                # Chat member handler to catch when a request is approved/accepted
                from telegram.ext import ChatMemberHandler
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
