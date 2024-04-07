from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telegraph import Telegraph
import uuid
from Config import API_ID, API_HASH, BOT_TOKEN
# Initialize your Pyrogram client with your credentials
app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash="API_HASH",
    bot_token="BOT_TOKEN"
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

# Command handlers
@app.on_message(filters.command("start"))
async def start_command(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if the user is the owner (based on user ID)
    if user_id == owner_id:
        await message.reply_photo(
            photo=welcome_photo_url,
            caption="Welcome back, dear owner! How can I assist you today?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Create a new story", callback_data="new_story")]
            ])
        )
    else:
        await message.reply_photo(
            photo=welcome_photo_url,
            caption="Welcome to the Story Bot! Let's create and read amazing stories together.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Start a new story", callback_data="new_story")],
                [InlineKeyboardButton("Read published stories", switch_inline_query_current_chat="")]
            ])
        )

@app.on_callback_query(filters.regex("^new_story$"))
async def new_story_callback(_, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text("Use /newstory to start a new story.")

@app.on_message(filters.command("newstory"))
async def new_story_command(_, message: Message):
    chat_id = message.chat.id
    stories[chat_id] = {'title': None, 'author': None, 'cover_art': None,
                        'genre': None, 'tags': [], 'summary': None, 'chapters': [], 'published': False}

    await message.reply_text("Let's create a new story! Please provide the following details:\n"
                             "1. Title of the story\n"
                             "2. Author's name\n"
                             "3. Cover art URL\n"
                             "4. Genre\n"
                             "5. Tags (comma-separated)\n"
                             "6. Summary")

@app.on_message(filters.text & ~filters.command("start") & ~filters.command("newstory"))
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
            story['cover_art'] = message.text
            await message.reply_text("Cover art URL set successfully! Please specify the genre of the story.")
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
        elif len(story['chapters']) > 0:
            # Prompt to confirm before adding a new chapter
            confirmation_message = "Would you like to finalize the current chapter?"
            await message.reply_text(confirmation_message)

@app.on_message(filters.command("finalizechapter"))
async def finalize_chapter_command(_, message: Message):
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

        response = telegraph.create_page(
            title=title,
            author_name=author,
            html_content=page_content
        )

        telegraph_url = response['url']
        published_stories[chat_id] = {'title': title, 'author': author, 'telegraph_url': telegraph_url}

@app.on_command("readstory")
async def read_story_command(_, message: Message):
    chat_id = message.chat.id

    if chat_id in published_stories:
        story = published_stories[chat_id]
        await message.reply_text(f"Read the story '{story['title']}' by {story['author']} on Telegraph: {story['telegraph_url']}")
    else:
        await message.reply_text("No published story found.")

@app.on_command("help")
async def help_command(_, message: Message):
    help_text = (
        "Welcome to the Story Bot!\n\n"
        "Here are the available commands and what they do:\n"
        "/start - Start the bot and receive a welcome message.\n"
        "/newstory - Start creating a new story.\n"
        "/finalizechapter - Finalize and publish your story.\n"
        "/readstory - Read the published story.\n"
        "/help - Display this help message with command explanations.\n"
        "/about - Learn more about the bot, its uses, and tips."
    )
    await message.reply_text(help_text)

@app.on_command("about")
async def about_command(_, message: Message):
    about_text = (
        "Welcome to the Story Bot!\n\n"
        "This bot allows you to create, publish, and read stories right within Telegram.\n\n"
        "Here's how you can use this bot:\n"
        "- Use /newstory to start a new story. Follow the prompts to add details and chapters.\n"
        "- Use /finalizechapter to finalize and publish your story after adding all chapters.\n"
        "- Use /readstory to view published stories or share them with others.\n\n"
        "Tips and Tricks:\n"
        "- Add cover art, title, author name, genre, tags, and a summary to make your story attractive.\n"
        "- Use proper formatting for chapters to enhance readability.\n"
        "- Share published stories with friends using inline queries or generated links.\n"
        "- Have fun exploring different genres and writing styles!\n\n"
        "Enjoy creating and sharing stories with the Story Bot!"
    )
    await message.reply_text(about_text)

@app.on_inline_query()
async def inline_query_handler(_, inline_query):
    results = []

    for chat_id, story in published_stories.items():
        if story['telegraph_url']:
            title = story['title']
            author = story['author']
            description = f"by {author}"
            input_content = f"Read the story on Telegraph: {story['telegraph_url']}"
            results.append(
                InlineQueryResultArticle(
                    title=title,
                    description=description,
                    input_message_content=InputTextMessageContent(input_content)
                )
            )

    await inline_query.answer(results)

# Start the Pyrogram client
app.run()
