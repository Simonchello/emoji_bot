import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards import get_main_menu, get_grid_size_keyboard
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
🎨 **Welcome to Emoji Pack Bot, {user_name}!**

Transform your images and videos into custom emoji packs! 

**Quick Start:**
1️⃣ Choose your grid size (e.g., 2×2, 3×1, 1×3)
2️⃣ Select how to adapt your image (pad, stretch, crop)  
3️⃣ Send me an image or video
4️⃣ Get your emoji pack ready for Telegram!

**Features:**
• 📐 Flexible grid sizes (1×1 to 8×8)
• 🔄 Smart image adaptation
• 🎥 Video frame extraction  
• 🎨 Quality enhancement
• 📱 Telegram-ready emoji packs

Ready to start? Choose your grid size below! 👇
"""
    
    await message.answer(
        welcome_text,
        reply_markup=get_grid_size_keyboard(),
        parse_mode="Markdown"
    )


@router.message(F.text == "🔄 Start Over")
async def restart_command(message: Message):
    """Handle restart request"""
    await start_command(message)