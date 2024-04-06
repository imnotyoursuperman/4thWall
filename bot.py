import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import language_tool_python

# Load environment variables
load_dotenv()

# Telegram Bot token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize LanguageTool for grammar corrections
tool = language_tool_python.LanguageTool('en-US')

# Command handlers
def start(update: Update, context: CallbackContext) -> None:
    user_name = update.effective_user.first_name
    welcome_message = f"Welcome, {user_name}! I'm the Novel Writer Bot. Send me a story or text to check grammar."
    update.message.reply_text(welcome_message)

def process_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    # Perform grammar corrections using LanguageTool
    corrected_text = tool.correct(text)

    update.message.reply_text(f"Corrected Text:\n{corrected_text}")

def help_command(update: Update, context: CallbackContext) -> None:
    commands_text = "Here are the available commands:\n\n" \
                    "/start - Start the bot and receive a welcome message.\n" \
                    "/help - Show this help message.\n\n" \
                    "Simply send me a story or text message, and I'll check the grammar for you!"
    
    # Create inline keyboard with 'Close' button
    keyboard = [[InlineKeyboardButton("Close", callback_data='close')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(commands_text, reply_markup=reply_markup)

def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'close':
        query.message.delete()

def main() -> None:
    # Set up logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # Create the Updater and pass it the bot's token
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_text))

    # Register callback handler for inline keyboard button
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop it
    updater.idle()

if __name__ == '__main__':
    main()
