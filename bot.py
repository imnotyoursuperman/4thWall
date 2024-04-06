import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from openai_service import OpenAIService
from dalle_service import DALLEService

# Load API keys from config
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DALLE_API_KEY = os.getenv('DALLE_API_KEY')

# Initialize OpenAI and DALL-E services
openai_service = OpenAIService(api_key=OPENAI_API_KEY)
dalle_service = DALLEService(api_key=DALLE_API_KEY)

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to Novel Writer Bot! Use /edit to start writing or /generate_image to create an image.")

# Edit command handler
def edit(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Send me the text you want to edit.")
    context.user_data['mode'] = 'edit'

# Message handler for text editing
def handle_text(update: Update, context: CallbackContext) -> None:
    if 'mode' in context.user_data and context.user_data['mode'] == 'edit':
        text_to_edit = update.message.text
        corrected_text = openai_service.correct_text(text_to_edit)
        update.message.reply_text(f"Corrected text:\n{corrected_text}")
        del context.user_data['mode']

# Generate image command handler
def generate_image(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Describe the image you want to generate.")
    context.user_data['mode'] = 'generate_image'

# Message handler for image generation
def handle_image_description(update: Update, context: CallbackContext) -> None:
    if 'mode' in context.user_data and context.user_data['mode'] == 'generate_image':
        image_description = update.message.text
        image_url = dalle_service.generate_image(image_description)
        update.message.reply_photo(photo=image_url)
        del context.user_data['mode']

def main():
    # Set up bot and handlers
    updater = Updater(token=os.getenv('TELEGRAM_BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    # Register command and message handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("edit", edit))
    dispatcher.add_handler(CommandHandler("generate_image", generate_image))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_image_description))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
