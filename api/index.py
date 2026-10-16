import os
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8698303434:AAHN9ccgl5u3ZoIh0RKNRTIh55DiSbCJO-g"
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown", threaded=False)

app = Flask(__name__)

def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🟢 Otc Live Signal", callback_data="otc_live"),
        InlineKeyboardButton("🟢 Real Pairs Signal", callback_data="real_pairs"),
        InlineKeyboardButton("🟣 Otc Future Signals", callback_data="otc_future"),
        InlineKeyboardButton("🟣 Real Future List", callback_data="real_future"),
        InlineKeyboardButton("🟡 AUTO LIVE", callback_data="auto_live"),
        InlineKeyboardButton("🟢 FS FILTER", callback_data="fs_filter"),
        InlineKeyboardButton("🔵 Currency Pairs (PKR/BRL/BDT)", callback_data="currency_pairs"),
        InlineKeyboardButton("🔵 Live Market Pairs (EUR/CAD)", callback_data="live_market_pairs"),
        InlineKeyboardButton("🤖 M.K AI SIGNALS PRO", callback_data="ai_signals_pro"),
        InlineKeyboardButton("📢 SIGNALS PROVIDE M.K PREMIUM CHANNEL", url="https://t.me/+FdbFgVgsoT41ZGU8"),
        InlineKeyboardButton("👑 Get VIP Via Quotex", url="https://broker-qx.pro/?lid=1614511"),
        InlineKeyboardButton("💬 Contact Admin Support", url="https://t.me/MK_TRADER586")
    )
    return keyboard

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Invalid", 403

@app.route('/')
def index():
    return "Bot is running perfectly!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name or "Trader"
    welcome_text = (
        "👑 **𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓** 👑\n\n"
        f"✨ Hello {user_name}!\n"
        "🌐 Welcome to M.K Trader Official Hub. Select your desired option below:\n\n"
        "📊 **Signals Provide Channel:**\n"
        "🔗 https://t.me/+FdbFgVgsoT41ZGU8\n\n"
        "🌈 Join now for free daily signals & advanced AI tools!\n"
        "🚦 Admin Support: t.me/MK_TRADER586\n\n"
        "👇 **Choose an option below:**"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data

    if data == "otc_live":
        text = (
            "📈 **OTC LIVE SIGNAL GENERATED**\n\n"
            "💎 **Asset:** USD/PHP (OTC)\n"
            "🟢 **Direction:** CALL 📈\n"
            "🕒 **Entry Time:** Next Candle\n"
            "🌐 **Time zone:** UTC +5:00\n"
            "⚠️ **1 Step MTG Allowed**\n\n"
            "👤 **OWNER:** t.me/MK_TRADER586"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🔄 GET ANOTHER SIGNAL", callback_data="otc_live"))
        kb.add(InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home"))
        bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)

    elif data == "real_pairs":
        text = (
            "📈 **REAL PAIRS LIVE SIGNAL**\n\n"
            "💎 **Asset:** EUR/USD\n"
            "🔴 **Direction:** PUT 📉\n"
            "🕒 **Entry:** Immediate / 1 Minute\n"
            "⚠️ **Risk Management Required**\n\n"
            "👤 **OWNER:** t.me/MK_TRADER586"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🔄 GET ANOTHER SIGNAL", callback_data="real_pairs"))
        kb.add(InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home"))
        bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)

    elif data == "otc_future":
        text = (
            "🟣 **OTC FUTURE SIGNALS PANEL**\n\n"
            "🔥 High-accuracy session predictions for OTC markets.\n"
            "📊 Status: Active & Optimized\n\n"
            "👇 Select option below:"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("⭐ CREATE QX ACCOUNT", url="https://broker-qx.pro/?lid=1614511"))
        kb.add(InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home"))
        bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)

    elif data == "real_future":
        text = (
            "🟣 **REAL FUTURE LIST & SETUP**\n\n"
            "📊 Major news setups and real market future predictions.\n"
            "💬 Contact admin for VIP access: t.me/MK_TRADER586"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💬 CONTACT ADMIN", url="https://t.me/MK_TRADER586"))
        kb.add(InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home"))
        bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)

    elif data == "auto_live":
        text = (
            "🟡 **AUTO LIVE SIGNALS MODE**\n\n"
            "⚡ Automatic live signal bot engine is running for VIP members.\n"
            "💎 Upgrade via Quotex to unlock full auto feed."
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("👑 GET VIP VIA QUOTEX", url="https://broker-qx.pro/?lid=1614511"))
        kb.add(InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home"))
        bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)

    elif data == "fs_filter":
        text = (
            "🟢 **FS FILTER SETTINGS**\n\n"
            "⚙️ Advanced market noise filter, volatility scanner, and trend strength analyzer enabled."
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home"))
        bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)

    elif data == "currency_pairs":
        text = (
            "🔵 **CUSTOM CURRENCY PAIRS (QAS & KHAN STYLE)**\n\n"
            "Select your preferred regional and high-payout currency pair list:\n\n"
            "• **USD/PKR** (Pakistani Rupee OTC)\n"
            "• **USD/BRL** (Brazilian Real OTC)\n"
            "• **USD/BDT** (Bangladeshi Taka OTC)\n"
            "• **CAD/CHF** (Canadian Dollar / Swiss Franc)\n\n"
            "🎯 High accuracy signals active for these pairs!"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🟢 GENERATE PKR/BRL SIGNAL", callback_data="otc_live"))
        kb.add(InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home"))
        bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)

    elif data == "live_market_pairs":
        text = (
            "🔵 **LIVE MARKET FOREX PAIRS**\n\n"
            "Select your favorite major forex market pairs:\n\n"
            "• **EUR/CAD** (Euro / Canadian Dollar)\n"
            "• **EUR/CHF** (Euro / Swiss Franc)\n"
            "• **EUR/GBP** (Euro / British Pound)\n\n"
            "📊 Real-time analysis feed active."
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🟢 GENERATE LIVE PAIR SIGNAL", callback_data="real_pairs"))
        kb.add(InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home"))
        bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)

    elif data == "ai_signals_pro":
        text = (
            "🤖 **M.K AI SIGNALS PRO BOT PAYMENT & SETUP**\n\n"
            "⚡ Welcome to M.K AI Automated Trading Bot Suite!\n"
            "💎 **VIP Subscription Plans:**\n"
            "• Lifetime Access: $30 (USDT / Binance P2P / SadaPay / Meezan Bank)\n"
            "• Or Register via Official Quotex Link for FREE VIP Access!\n\n"
            "👇 Choose payment or verification method below:"
        )
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("👑 GET VIP VIA QUOTEX (FREE)", url="https://broker-qx.pro/?lid=1614511"))
        kb.add(InlineKeyboardButton("💬 CONTACT ADMIN FOR PAYMENT DETAILS", url="https://t.me/MK_TRADER586"))
        kb.add(InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_home"))
        bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)

    elif data == "back_home":
        welcome_text = (
            "👑 **𝐌.𝐊 𝐓𝐑𝐀𝐃𝐄𝐑 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐁𝐎𝐓** 👑\n\n"
            "🌐 Welcome to M.K Trader Official Hub. Select your desired option below:\n\n"
            "📊 **Signals Provide Channel:**\n"
            "🔗 https://t.me/+FdbFgVgsoT41ZGU8\n\n"
            "🌈 Join now for free daily signals & advanced AI tools!\n"
            "🚦 Admin Support: t.me/MK_TRADER586\n\n"
            "👇 **Choose an option below:**"
        )
        bot.edit_message_text(welcome_text, chat_id, message_id, reply_markup=main_menu_keyboard())
