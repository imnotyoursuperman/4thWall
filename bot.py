import logging
import random
import spacy
import en_core_web_sm
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize spaCy with the English language model
nlp = spacy.load('en_core_web_sm')
nlp = en_core_web_sm.load()

# Define genres with descriptions and thumbnails
genres = {
    "Fantasy": {
        "description": "Fantasy novels often feature magical worlds, mythical creatures, and epic quests.",
        "thumbnail_url": "https://source.unsplash.com/featured/?fantasy"
    },
    "Science Fiction": {
        "description": "Science fiction explores futuristic concepts, advanced technology, and space exploration.",
        "thumbnail_url": "https://source.unsplash.com/featured/?scifi"
    },
    "Mystery": {
        "description": "Mystery novels involve solving crimes, uncovering secrets, and navigating suspenseful plot twists.",
        "thumbnail_url": "https://source.unsplash.com/featured/?mystery"
    },
    "Romance": {
        "description": "Romance novels focus on love, relationships, and emotional connections between characters.",
        "thumbnail_url": "https://source.unsplash.com/featured/?romance"
    },
    "Thriller": {
        "description": "Thrillers are suspenseful and fast-paced, often involving danger, suspense, and plot twists.",
        "thumbnail_url": "https://source.unsplash.com/featured/?thriller"
    },
    "Historical Fiction": {
        "description": "Historical fiction is set in the past and incorporates real historical events and settings.",
        "thumbnail_url": "https://source.unsplash.com/featured/?historical"
    },
    "Horror": {
        "description": "Horror novels aim to evoke fear and suspense, often featuring supernatural elements or psychological horror.",
        "thumbnail_url": "https://source.unsplash.com/featured/?horror"
    },
    "Adventure": {
        "description": "Adventure novels involve exciting journeys, exploration, and thrilling escapades.",
        "thumbnail_url": "https://source.unsplash.com/featured/?adventure"
    },
    "Young Adult": {
        "description": "Young adult novels target teenage readers, exploring themes of identity, friendship, and coming-of-age.",
        "thumbnail_url": "https://source.unsplash.com/featured/?youngadult"
    },
    "Literary Fiction": {
        "description": "Literary fiction focuses on character development, themes, and introspective storytelling.",
        "thumbnail_url": "https://source.unsplash.com/featured/?literary"
    },
    # Add more genres if needed
}

# Conversation state constants
SELECT_GENRE, EDIT_TEXT = range(2)

# Command handlers

def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message and prompt the user to select a genre."""
    update.message.reply_text(
        "Welcome to the Novel Writer Bot! Please choose a genre to get started.",
        reply_markup=build_genre_keyboard(),
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a help message explaining available commands."""
    update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/cancel - Cancel the current operation\n"
        "/edittext - Edit text based on genre preferences",
    )

def cancel(update: Update, context: CallbackContext) -> int:
    """End the conversation."""
    update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Inline keyboard builders

def build_genre_keyboard() -> InlineKeyboardMarkup:
    """Build an inline keyboard with genre options."""
    keyboard = [
        [InlineKeyboardButton(genre, callback_data=genre)] for genre in genres
    ]
    return InlineKeyboardMarkup(keyboard)

def build_rating_keyboard() -> InlineKeyboardMarkup:
    """Build an inline keyboard for rating."""
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(1, 6)]
    ]
    return InlineKeyboardMarkup(keyboard)

# Conversation handlers

def select_genre(update: Update, context: CallbackContext) -> int:
    """Prompt the user to enter text for editing based on the selected genre."""
    query = update.callback_query
    genre = query.data
    query.answer()

    context.user_data['selected_genre'] = genre
    query.edit_message_text(
        text=f"You've selected *{genre}*.\n\n{genres[genre]['description']}\n\nPlease enter the text you want to edit.",
        parse_mode='Markdown',
    )
    return EDIT_TEXT

def edit_text(update: Update, context: CallbackContext) -> int:
    """Perform text editing based on the selected genre."""
    text = update.message.text
    genre = context.user_data.get('selected_genre')
    
    # Apply genre-specific text modifications
    edited_text = apply_genre_specific_edits(text, genre)
    update.message.reply_text(f"Edited text ({genre} style):\n{edited_text}")

    # Prompt the user to rate the experience
    update.message.reply_text("Rate your experience with this edit:", reply_markup=build_rating_keyboard())
    return ConversationHandler.END

# Genre-specific text editing

def apply_genre_specific_edits(text: str, genre: str) -> str:
    """Apply genre-specific text modifications based on the selected genre."""
    doc = nlp(text)
    
    # Placeholder logic for text editing based on genre
    if genre == "Fantasy":
        # Example: Replace "magic" with "sorcery"
        edited_text = text.replace("magic", "sorcery")
    elif genre == "Science Fiction":
        # Example: Replace "space" with "galaxy"
        edited_text = text.replace("space", "galaxy")
    elif genre == "Mystery":
        # Example: Add mysterious elements or keywords
        edited_text = text + " (Mysterious additions)"
    # Add more genre-specific modifications as needed...
    else:
        edited_text = text  # Default to original text if genre not recognized

    return edited_text

# Rating and notification handlers

def rate_experience(update: Update, context: CallbackContext) -> None:
    """Handle user rating and send notification."""
    query = update.callback_query
    rating = query.data
    user = update.effective_user
    username = user.username if user.username else f"User ID: {user.id}"

    # Send rating to group or save it to a database
    context.bot.send_message(
        chat_id='YOUR_GROUP_CHAT_ID',  # Replace with your group chat ID
        text=f"New rating received!\nUser: [{username}](tg://user?id={user.id})\nRating: {rating} ⭐"
    )

    query.answer()
    query.edit_message_text(f"Thank you for rating your experience: {rating} ⭐")

# Main function

def main() -> None:
    """Run the bot."""
    updater = Updater(token='TELEGRAM_BOT_TOKEN', use_context=True)

    # Define handlers
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_genre)],
        states={
            EDIT_TEXT: [MessageHandler(Filters.text & ~Filters.command, edit_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("edittext", start))  # Redirect /edittext to /start to select genre
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(rate_experience))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
