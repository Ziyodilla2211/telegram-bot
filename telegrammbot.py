from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import random
import nest_asyncio

nest_asyncio.apply()

TOKEN = "8315784964:AAFsO4r06oOePRhg6lROUw1gCuooCNVwt-4"

games = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    games[chat_id] = {"ran": random.randint(1, 100), "tries": 0, "await_restart": False, "phase": "user_guesses"}

    keyboard = [[InlineKeyboardButton("1-50", callback_data="range_50"),
                 InlineKeyboardButton("1-100", callback_data="range_100")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "HELLO😃! This is the GUESS NUMBER game. Which range would you like to play?😎", reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    await query.answer()

    if query.data == "range_50":
        games[chat_id]["ran"] = random.randint(1, 50)
        await query.edit_message_text("I chose a number from 1 to 50. Try to find, buddy!😌")
    elif query.data == "range_100":
        games[chat_id]["ran"] = random.randint(1, 100)
        await query.edit_message_text("I chose a number from 1 to 100. Try to find, buddy!😏")

async def start_pc_guessing(chat_id, context, update_obj):
    """PC starts guessing user's number using binary search."""
    game = games[chat_id]
    game["phase"] = "pc_guesses"
    game["pc_low"] = 1
    game["pc_high"] = 100
    game["pc_tries"] = 0
    mid = (game["pc_low"] + game["pc_high"]) // 2
    game["pc_current"] = mid

    keyboard = [
        [InlineKeyboardButton("HIGHER ⬆️", callback_data="pc_higher"),
         InlineKeyboardButton("LOWER ⬇️", callback_data="pc_lower"),
         InlineKeyboardButton("CORRECT ✅", callback_data="pc_correct")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"So, now I will try to find your number!🧐\n1 Choose a number from 1 to 100.\n\nI would say🙂‍↕️: {mid}",
        reply_markup=reply_markup
    )

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id

    if chat_id not in games:
        await update.message.reply_text("FIRST, click /start button🫢.")
        return

    game = games[chat_id]

    if game.get("phase") == "pc_guesses":
        await update.message.reply_text("It is my turn to find your number! Use buttons😙.")
        return

    if game.get("await_restart"):
        await update.message.reply_text("Game over. Begin with /start again.")
        return

    try:
        num = int(update.message.text)
    except:
        await update.message.reply_text("Please, enter only number😤.")
        return

    game["tries"] += 1

    if num > game["ran"]:
        await update.message.reply_text("NOPE, my number is lower🤏")
    elif num < game["ran"]:
        await update.message.reply_text("Nahh, my number is higher👆.")
    else:
        await update.message.reply_text(
            f"You FOUND! I choose exactly {game['ran']} . You found in {game['tries']} try. 🎉\n\n"
            "It is your turn now!🙄 — I will find your number!"
        )
        await start_pc_guessing(chat_id, context, update)

async def pc_guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    await query.answer()

    game = games[chat_id]

    if query.data == "pc_correct":
        game["pc_tries"] += 1
        keyboard = [[InlineKeyboardButton("YES ✅", callback_data="play_again"),
                     InlineKeyboardButton("NO ❌", callback_data="quit")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🎉 I found it! It was {game['pc_current']}! I found in {game['pc_tries']} try!\n\n"
            "Would you like to play more?🤭",
            reply_markup=reply_markup
        )
        game["phase"] = "done"

    elif query.data == "pc_higher":
        game["pc_tries"] += 1
        game["pc_low"] = game["pc_current"] + 1
        if game["pc_low"] > game["pc_high"]:
            await query.edit_message_text("Error or it is higher than 100!")
            return
        mid = (game["pc_low"] + game["pc_high"]) // 2
        game["pc_current"] = mid
        keyboard = [
            [InlineKeyboardButton("HIGHER ⬆️", callback_data="pc_higher"),
             InlineKeyboardButton("LOWER ⬇️", callback_data="pc_lower"),
             InlineKeyboardButton("CORRECT ✅", callback_data="pc_correct")]
        ]
        await query.edit_message_text(
            f"Mening taxminim: {mid}", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "pc_lower":
        game["pc_tries"] += 1
        game["pc_high"] = game["pc_current"] - 1
        if game["pc_high"] < game["pc_low"]:
            await query.edit_message_text("Error or it is higher than 100!!")
            return
        mid = (game["pc_low"] + game["pc_high"]) // 2
        game["pc_current"] = mid
        keyboard = [
            [InlineKeyboardButton("HIGHER ⬆️", callback_data="pc_higher"),
             InlineKeyboardButton("LOWER ⬇️", callback_data="pc_lower"),
             InlineKeyboardButton("CORRECT ✅", callback_data="pc_correct")]
        ]
        await query.edit_message_text(
            f"Mening taxminim: {mid}", reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def play_again_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    await query.answer()

    if query.data == "play_again":
        games[chat_id] = {"ran": random.randint(1, 100), "tries": 0, "await_restart": False, "phase": "user_guesses"}
        await query.edit_message_text("New game has began! I chose a number from 1 to 100. Try to find, buddy!😏")
    elif query.data == "quit":
        await query.edit_message_text("Game over. To start again click /start!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - o'yinni boshlash\n<son> - taxmin qilish")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))
    app.add_handler(CallbackQueryHandler(button, pattern="^range_"))
    app.add_handler(CallbackQueryHandler(pc_guess_handler, pattern="^pc_"))
    app.add_handler(CallbackQueryHandler(play_again_handler, pattern="^(play_again|quit)$"))

    print("Bot ishga tushdi...")
    app.run_polling()
