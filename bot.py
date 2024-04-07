import logging
import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from telegraph import Telegraph

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pyrogram client
app = Client(
    "my_bot",
    api_id=21927988,
    api_hash="e18f720acdff1e5b0ec80616aecd8a5a",
    bot_token="6540514531:AAF7LdzWLOEhckVNM7xFKVK8MgR_os6n_lc"
)

# Owner's user ID (Replace with your Telegram user ID)
owner_id = 2064735436  # Replace with your Telegram user ID

# Welcome message photo URL
welcome_photo_url = "https://raw.githubusercontent.com/imnotyoursuperman/databasepics/main/IMG_20240406_224853_664.png"  # Replace with your welcome photo URL

# Initialize Telegraph
telegraph = Telegraph()
telegraph.create_account(short_name="my_bot")

# Dictionary to store story details
stories = {}
published_stories = {}

# Command handlers using message filters
@app.on_message(filters.command("start"))
async def start_command(_, message: Message):
    user_id = message.from_user.id

    if user_id == owner_id:
        await message.reply_photo(
            photo=welcome_photo_url,
            caption="Welcome back, dear owner! How can I assist you today?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Create a new story", callback_data="new_story")],
                [InlineKeyboardButton("ℹ️ About", callback_data="about"), InlineKeyboardButton("❓ Help", callback_data="help")]
            ])
        )
    else:
        await message.reply_photo(
            photo=welcome_photo_url,
            caption="Welcome to the Story Bot! Let's create and read amazing stories together.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Start a new story", callback_data="new_story")],
                [InlineKeyboardButton("Read published stories", switch_inline_query_current_chat="")],
                [InlineKeyboardButton("ℹ️ About", callback_data="about"), InlineKeyboardButton("❓ Help", callback_data="help")]
            ])
        )

@app.on_callback_query()
async def callback_handler(_, callback_query):
    chat_id = callback_query.message.chat.id
    data = callback_query.data

    if data == "new_story":
        stories[chat_id] = {'title': None, 'author': None, 'cover_art': None,
                            'genre': None, 'tags': [], 'summary': None, 'chapters': []}
        await callback_query.answer("Let's create a new story! Please provide the following details:\n"
                                    "1. Title of the story\n"
                                    "2. Author's name\n"
                                    "3. Cover art URL\n"
                                    "4. Genre\n"
                                    "5. Tags (comma-separated)\n"
                                    "6. Summary")

    elif data == "help":
        await callback_query.answer()
        await app.send_message(chat_id, "Welcome to Story Bot!\n"
                                         "Commands available:\n"
                                         "/start - Start the bot\n"
                                         "/new_story - Create a new story\n"
                                         "/addchapter - Add a chapter to your story\n"
                                         "/publish - Publish your story\n"
                                         "/help - Show available commands\n"
                                         "/about - Show bot information and tips")

    elif data == "about":
        await callback_query.answer()
        about_text = (
            "Story Bot - Create and read stories!\n"
            "Features:\n"
            "- Create custom stories with cover art, title, genre, tags, and summary\n"
            "- Add chapters to your stories\n"
            "- Publish and share your stories with others\n"
            "- Read published stories via inline queries\n"
            "- Stories are presented using Telegraph instant view\n"
            "Enjoy storytelling with Story Bot!"
        )
        await app.send_message(chat_id, about_text)

@app.on_message(filters.text & ~filters.command("start"))
async def handle_text_message(_, message: Message):
    chat_id = message.chat.id

    if chat_id in stories:
        story = stories[chat_id]

        if story['title'] is None:
            story['title'] = message.text
            await message.reply_text("Title set successfully! Now, please provide the author's name.")
        elif story['author'] is None:
            story['author'] = message.text
            await message.reply_text("Author's name set successfully! Please provide the cover art URL.")
        elif story['cover_art'] is None:
            cover_art_url = message.text.strip()
            if validate_url(cover_art_url):
                story['cover_art'] = cover_art_url
                await message.reply_text("Cover art URL set successfully! Please specify the genre of the story.")
            else:
                await message.reply_text("Invalid URL format. Please provide a valid cover art URL.")
        elif story['genre'] is None:
            story['genre'] = message.text
            await message.reply_text("Genre set successfully! Please enter the tags (comma-separated).")
        elif not story['tags']:
            tags = [tag.strip() for tag in message.text.split(',')]
            story['tags'] = tags
            await message.reply_text("Tags set successfully! Please provide a brief summary of your story.")
        elif story['summary'] is None:
            story['summary'] = message.text
            await message.reply_text("Summary set successfully! You can now start writing the first chapter.")

@app.on_message(filters.command("addchapter"))
async def add_chapter_command(_, message: Message):
    chat_id = message.chat.id

    if chat_id in stories and stories[chat_id]['summary'] is not None:
        story = stories[chat_id]
        await message.reply_text("Please type the next chapter of your story.")
    else:
        await message.reply_text("Please create a new story first and complete the details.")

@app.on_message(filters.text & ~filters.command("start") & ~filters.command("addchapter"))
async def handle_chapter_message(_, message: Message):
    chat_id = message.chat.id

    if chat_id in stories and stories[chat_id]['summary'] is not None:
        story = stories[chat_id]
        story['chapters'].append(message.text)
        await message.reply_text("Chapter added successfully!")

@app.on_message(filters.command("publish"))
async def publish_story_command(_, message: Message):
    chat_id = message.chat.id

    if chat_id in stories and len(stories[chat_id]['chapters']) > 0:
        story = stories[chat_id]
        story['published'] = True  # Mark story as published
        await message.reply_text("Story published successfully!")
        await create_telegraph_page(chat_id)

async def create_telegraph_page(chat_id):
    if chat_id in stories and stories[chat_id]['published']:
        story = stories[chat_id]
        title = story['title']
        author = story['author']
        cover_art = story['cover_art']
        genre = story['genre']
        tags = ', '.join(story['tags'])
        summary = story['summary']
        chapters = "\n\n".join(f"<p>{chapter}</p>" for chapter in story['chapters'])

        # Create a Telegraph page
        page_content = (
            f"<h3>{title}</h3>"
            f"<p><i>by {author}</i></p>"
            f"<p><b>Genre:</b> {genre}</p>"
            f"<p><b>Tags:</b> {tags}</p>"
            f"<p><b>Summary:</b> {summary}</p>"
            f"<img src='{cover_art}' />"
            f"{chapters}"
        )

        try:
            response = telegraph.create_page(
                title=title,
                author_name=author,
                html_content=page_content
            )
            telegraph_url = response['url']
            published_stories[chat_id] = {'title': title, 'author': author, 'telegraph_url': telegraph_url}
            await app.send_message(chat_id, f"Your story has been published! Read it here: {telegraph_url}")
        except Exception as e:
            logger.error(f"Error creating Telegraph page: {e}")

def validate_url(url):
    # Regular expression pattern to validate URL format
    url_pattern = re.compile(r"https?://\S+")
    return bool(re.match(url_pattern, url))

# Start the Pyrogram client
if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
