import os
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "users.json"
REFERRAL_BONUS = 5


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    users = load_users()

    if user_id not in users:
        users[user_id] = {
            "name": user.first_name,
            "balance": 0,
            "referrals": 0
        }

        # Referral check
        if context.args:
            referrer_id = context.args[0]

            if referrer_id != user_id and referrer_id in users:
                users[referrer_id]["balance"] += REFERRAL_BONUS
                users[referrer_id]["referrals"] += 1

        save_users(users)

    await update.message.reply_text(
        "👋 স্বাগতম!\n\n"
        "🤖 My Digital Services Bot\n\n"
        "আপনার অ্যাকাউন্ট তৈরি হয়েছে।\n\n"
        "💰 ব্যালেন্স দেখতে লিখুন:\n"
        "/balance\n\n"
        "👥 আপনার Referral Link পেতে লিখুন:\n"
        "/refer"
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    users = load_users()

    if user_id not in users:
        await update.message.reply_text(
            "আগে /start দিন।"
        )
        return

    balance_amount = users[user_id]["balance"]

    await update.message.reply_text(
        f"💰 আপনার ব্যালেন্স: {balance_amount} টাকা"
    )


async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    bot = await context.bot.get_me()

    referral_link = (
        f"https://t.me/{bot.username}?start={user_id}"
    )

    await update.message.reply_text(
        "👥 আপনার Referral Link:\n\n"
        f"{referral_link}\n\n"
        f"🎁 প্রতি সফল রেফারে {REFERRAL_BONUS} টাকা বোনাস।"
    )


def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN পাওয়া যায়নি!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("refer", refer))

    print("Bot চলছে...")

    app.run_polling()


if __name__ == "__main__":
    main()
