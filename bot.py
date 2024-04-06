import telebot
import spacy

# Initialize spaCy with the English language model
nlp = spacy.load('en_core_web_sm')

# Initialize your Telegram bot using the bot token
bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN')

# Define the available genres for novel writing along with their typical styles
genres = {
    "Fantasy": "Fantasy novels often feature magical worlds, mythical creatures, and epic quests.",
    "Science Fiction": "Science fiction explores futuristic concepts, advanced technology, and space exploration.",
    "Mystery": "Mystery novels involve solving crimes, uncovering secrets, and navigating suspenseful plot twists.",
    "Romance": "Romance novels focus on love, relationships, and emotional connections between characters.",
    "Thriller": "Thrillers are suspenseful and fast-paced, often involving danger, suspense, and plot twists.",
    "Historical Fiction": "Historical fiction is set in the past and incorporates real historical events and settings.",
    "Horror": "Horror novels aim to evoke fear and suspense, often featuring supernatural elements or psychological horror.",
    "Adventure": "Adventure novels involve exciting journeys, exploration, and thrilling escapades.",
    "Young Adult": "Young adult novels target teenage readers, exploring themes of identity, friendship, and coming-of-age.",
    "Literary Fiction": "Literary fiction focuses on character development, themes, and introspective storytelling."
}

# Handle /start command to send a welcome message and picture
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Define the welcome message
    welcome_message = "Welcome to the Novel Writer Bot! Type /help for more info."

    # Send the welcome message
    bot.reply_to(message, welcome_message)

    # Send an introductory picture along with the welcome message as the caption
    photo_url = 'https://raw.githubusercontent.com/imnotyoursuperman/databasepics/main/IMG_20240406_224853_664.png'  # Replace with your image URL
    bot.send_photo(message.chat.id, photo_url, caption=welcome_message)

# Handle /help command to display help options with inline keyboard
@bot.message_handler(commands=['help'])
def send_help(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Commands', callback_data='commands'))
    bot.send_message(message.chat.id, "How may I help you?", reply_markup=markup)

# Handle inline keyboard callbacks
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'commands':
        response = "Available commands:\n"
        response += "/start - Starts the bot\n"
        response += "/help - Display this help message\n"
        response += "/checkgrammar - Performs a grammar check\n"
        response += "/checkspelling - Performs a spelling check\n"
        response += "/edittext - Edits text according to the preference of the writer\n"
        bot.send_message(call.message.chat.id, response)
    elif call.data.startswith('genre_'):
        selected_genre = call.data.split('_')[1]
        if selected_genre in genres:
            genre_description = genres[selected_genre]
            bot.send_message(call.message.chat.id, f"Selected genre: {selected_genre}\n{genre_description}")

            # Perform text editing based on the selected genre
            bot.send_message(call.message.chat.id, "Please enter the text you want to edit:")
            bot.register_next_step_handler(call.message, process_edit_text, selected_genre)

# Handle /edittext command to edit text based on user preferences
@bot.message_handler(commands=['edittext'])
def edit_text(message):
    # Create an inline keyboard with genre options
    markup = telebot.types.InlineKeyboardMarkup()
    for genre in genres:
        markup.add(telebot.types.InlineKeyboardButton(text=genre, callback_data=f'genre_{genre}'))

    bot.send_message(message.chat.id, "Choose a genre:", reply_markup=markup)

# Handle all incoming messages
@bot.message_handler(func=lambda message: True)
def process_message(message):
    text = message.text
    
    # Process the text using spaCy
    doc = nlp(text)
    
    # Perform grammar corrections and word suggestions based on genre
    corrections = []
    for token in doc:
        if token.text != token.text.lower() and not token.is_stop:
            # Example: Implement custom logic to suggest corrections based on genre and premise
            # For demonstration, let's just suggest lowercased versions of tokens
            corrections.append(token.text.lower())
    
    if corrections:
        response = f"Potential corrections: {' '.join(corrections)}"
    else:
        response = "No grammar corrections needed. Type /help for more options."
    
    bot.reply_to(message, response)

# Handle text editing process based on selected genre
def process_edit_text(message, selected_genre):
    text = message.text
    edited_text = apply_genre_specific_edits(text, selected_genre)
    bot.send_message(message.chat.id, f"Edited text ({selected_genre} style):\n{edited_text}")

    # Prompt the user to rate the experience with a star rating popup
    send_rating_prompt(message)

def apply_genre_specific_edits(text, selected_genre):
    # Apply genre-specific text modifications based on the selected genre
    edited_text = text.lower()  # Placeholder logic (e.g., convert text to lowercase)
    
    # Modify the edited_text based on the selected_genre
    if selected_genre == "Fantasy":
        # Apply fantasy genre-specific modifications
        # Example: Replace "magic" with "sorcery"
        edited_text = edited_text.replace("magic", "sorcery")
    elif selected_genre == "Science Fiction":
        # Apply science fiction genre-specific modifications
        # Example: Replace "space" with "galaxy"
        edited_text = edited_text.replace("space", "galaxy")
    # Add more genre-specific modifications as needed...

    return edited_text

# Send a star rating prompt (inline keyboard) to gather user feedback
def send_rating_prompt(message):
    markup = telebot.types.InlineKeyboardMarkup()
    for i in range(1, 6):  # Create buttons for ratings from 1 to 5 stars
        markup.add(telebot.types.InlineKeyboardButton(text=f'{i} ⭐', callback_data=f'rating_{i}'))

    bot.send_message(message.chat.id, "Rate your experience:", reply_markup=markup)

# Handle callback queries for rating responses
@bot.callback_query_handler(func=lambda call: call.data.startswith('rating_'))
def handle_rating_response(call):
    rating = int(call.data.split('_')[1])
    bot.send_message(call.message.chat.id, f"Thank you for rating your experience: {rating} ⭐")

# Main function to run the bot
def main():
    try:
        print("Novel Bot is running. Press Ctrl+C to exit.")
        bot.polling()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Add custom error handling or logging as needed

# Run the bot
if __name__ == "__main__":
    main()
