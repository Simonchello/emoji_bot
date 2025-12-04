import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from models import UserSettings

logger = logging.getLogger(__name__)
router = Router()

# User settings storage (in production, use database)
user_settings = {}


@router.message(CommandStart())
async def start_command(message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "User"

    # Initialize user settings if not exists
    if user_id not in user_settings:
        user_settings[user_id] = UserSettings(user_id=user_id)
        logger.info(f"Created new user settings for {user_id}")

    welcome_text = f"""
🎨 <b>Welcome to Emoji Pack Bot, {user_name}!</b>

Transform your images and videos into custom emoji packs!

<b>How to use:</b>
1️⃣ Send me an image or video
2️⃣ Choose your grid size and settings
3️⃣ Get your emoji pack ready for Telegram!

<b>Supported formats:</b>
• Images: JPG, PNG, WebP (up to 50MB)
• Videos: MP4, MOV, AVI ⚠️ <i>BETA</i>

<b>Ready?</b> Just send me an image or video! 📷
"""

    await message.answer(
        welcome_text,
        parse_mode="HTML"
    )


@router.message(F.text == "🔄 Start Over")
async def restart_command(message: Message):
    """Handle restart request"""
    await start_command(message)
