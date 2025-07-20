import asyncio
import logging
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from filters import IsImageFilter, FileSizeFilter, SupportedFormatFilter
from keyboards import get_processing_confirmation_keyboard, get_processing_complete_keyboard
from states import UserStates
from utils import (
    ImageProcessor, EmojiGenerator, FileManager, ProgressTracker, StickerPackManager,
    validate_file_format, validate_file_size
)
from exceptions import ImageProcessingError, FileSizeError, FileFormatError
from config import load_config, CACHE_DIR
from .start import user_settings

logger = logging.getLogger(__name__)
router = Router()

# Initialize processors
image_processor = ImageProcessor()
emoji_generator = EmojiGenerator()


@router.message(
    IsImageFilter(),
    FileSizeFilter(max_size_mb=50),
    SupportedFormatFilter()
)
async def handle_image_upload(message: Message, state: FSMContext, bot: Bot):
    """Handle image upload for processing"""
    user_id = message.from_user.id
    
    # Check if user has settings configured
    if user_id not in user_settings:
        await message.answer(
            "⚙️ Please configure your settings first!\n\nUse /start to begin setup.",
            reply_markup=None
        )
        return
    
    settings = user_settings[user_id]
    
    # Show processing confirmation
    config_text = f"""
🖼️ **Image Received!**

**Your Settings:**
• Grid Size: `{settings.grid_x}×{settings.grid_y}`
• Adaptation: `{settings.adaptation_method.title()}`  
• Quality: `{settings.quality_level.title()}`
• Background Removal: `{'Yes' if settings.background_removal else 'No'}`

Ready to process your image into {settings.grid_x * settings.grid_y} emojis?
"""
    
    # Store image info in state
    await state.update_data(
        file_id=message.photo[-1].file_id if message.photo else message.document.file_id,
        message_id=message.message_id
    )
    await state.set_state(UserStates.confirming_processing)
    
    await message.answer(
        config_text,
        reply_markup=get_processing_confirmation_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "start_processing", UserStates.confirming_processing)
async def start_image_processing(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Start image processing"""
    user_id = callback.from_user.id
    settings = user_settings[user_id]
    data = await state.get_data()
    
    try:
        await state.set_state(UserStates.processing_media)
        
        # Update message to show processing started
        await callback.message.edit_text(
            "🔄 **Processing your image...**\n\nThis may take a few moments.",
            parse_mode="Markdown"
        )
        await callback.answer()
        
        # Initialize file manager
        config = load_config()
        file_manager = FileManager(bot, config.max_file_size_mb)
        
        # Get file info and download
        file_info = await bot.get_file(data['file_id'])
        local_path = await file_manager.download_media(file_info, user_id)
        
        # Validate file
        validate_file_size(local_path, config.max_file_size_mb)
        media_type = validate_file_format(local_path)
        
        if media_type != "image":
            raise FileFormatError("Expected image file")
        
        # Progress tracking
        total_steps = 4 + (settings.grid_x * settings.grid_y)
        progress_tracker = ProgressTracker(total_steps)
        
        # Load and process image
        progress_tracker.update(1, "Loading image...")
        image = image_processor.load_image(local_path)
        
        # Enhance image if needed
        if settings.quality_level == "high":
            progress_tracker.update(1, "Enhancing image quality...")
            image = image_processor.enhance_image(image, "high")
        else:
            progress_tracker.update(1, "Basic processing...")
        
        # Adapt image to grid ratio
        progress_tracker.update(1, "Adapting image to grid...")
        adapted_image = image_processor.adapt_image_to_grid(
            image, settings.grid_x, settings.grid_y, settings.adaptation_method
        )
        
        # Split into grid cells
        progress_tracker.update(1, "Splitting into emoji cells...")
        emoji_cells = image_processor.split_image_grid(
            adapted_image, settings.grid_x, settings.grid_y, progress_tracker
        )
        
        # Apply background removal if enabled
        if settings.background_removal:
            for i, cell in enumerate(emoji_cells):
                emoji_cells[i] = emoji_generator.add_transparency(cell, method="white")
        
        # Generate emoji pack
        pack_name = f"emoji_pack_{user_id}"
        output_dir = CACHE_DIR / f"user_{user_id}_output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = emoji_generator.create_emoji_pack(
            emoji_cells, pack_name, user_id, output_dir, progress_tracker
        )
        
        # Create ZIP archive
        zip_path = output_dir / f"{pack_name}.zip"
        emoji_generator.create_pack_archive(saved_files, pack_name, zip_path)
        
        # Create Telegram sticker pack
        sticker_manager = StickerPackManager(bot)
        user_name = callback.from_user.first_name or "User"
        
        pack_result = await sticker_manager.create_sticker_pack(
            user_id=user_id,
            user_name=user_name,
            emoji_files=saved_files,
            grid_size=(settings.grid_x, settings.grid_y),
            pack_type="emoji"
        )
        
        # Success message with sticker pack link
        if pack_result["success"]:
            success_text = f"""
✅ **Processing Complete!**

**Results:**
• Created: `{len(saved_files)}` emojis
• Grid: `{settings.grid_x}×{settings.grid_y}`
• Quality: `{settings.quality_level.title()}`

🎉 **Your Telegram sticker pack is ready!**

**Pack:** `{pack_result["pack_title"]}`
**Link:** {pack_result["pack_link"]}

Click the link above to add your custom emoji pack to Telegram! 🚀
"""
        else:
            success_text = f"""
✅ **Processing Complete!**

**Results:**
• Created: `{len(saved_files)}` emojis
• Grid: `{settings.grid_x}×{settings.grid_y}`
• Quality: `{settings.quality_level.title()}`

⚠️ **Sticker pack creation failed:** `{pack_result.get("error", "Unknown error")}`

You can still download the ZIP file with your emojis below.
"""
        
        # Store results in state
        await state.update_data(
            emoji_files=[str(f) for f in saved_files],
            zip_path=str(zip_path),
            pack_name=pack_name,
            sticker_pack_result=pack_result
        )
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_processing_complete_keyboard(has_sticker_pack=pack_result["success"]),
            parse_mode="Markdown"
        )
        
        # Send first few emojis as preview
        await send_emoji_preview(callback.message, saved_files[:4])
        
        # Clean up original file
        try:
            local_path.unlink()
        except:
            pass
        
        logger.info(f"Successfully processed image for user {user_id}: {len(saved_files)} emojis")
        
    except Exception as e:
        logger.error(f"Image processing failed for user {user_id}: {e}")
        
        error_text = f"""
❌ **Processing Failed**

Error: `{str(e)[:100]}...` 

Please try again with a different image or settings.
"""
        
        await callback.message.edit_text(
            error_text,
            parse_mode="Markdown"
        )
        await state.clear()


async def send_emoji_preview(message: Message, emoji_files: list, max_preview: int = 4):
    """Send preview of generated emojis"""
    try:
        preview_files = emoji_files[:max_preview]
        
        if not preview_files:
            return
        
        await message.answer(f"📱 **Preview** (showing {len(preview_files)}/{len(emoji_files)} emojis):")
        
        # Send emojis as photos
        for i, emoji_path in enumerate(preview_files):
            if Path(emoji_path).exists():
                try:
                    from aiogram.types import FSInputFile
                    await message.answer_photo(
                        FSInputFile(emoji_path),
                        caption=f"Emoji {i+1}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send emoji preview {i+1}: {e}")
    
    except Exception as e:
        logger.warning(f"Failed to send emoji preview: {e}")


@router.callback_query(F.data == "download_zip")
async def download_zip_file(callback: CallbackQuery, state: FSMContext):
    """Send ZIP file to user"""
    data = await state.get_data()
    zip_path = data.get('zip_path')
    
    if not zip_path or not Path(zip_path).exists():
        await callback.answer("❌ ZIP file not found", show_alert=True)
        return
    
    try:
        from aiogram.types import FSInputFile
        await callback.message.answer_document(
            FSInputFile(zip_path),
            caption="📦 **Your Emoji Pack**\n\nExtract and use these PNG files as Telegram stickers!"
        )
        await callback.answer("📦 ZIP file sent!")
        
    except Exception as e:
        logger.error(f"Failed to send ZIP file: {e}")
        await callback.answer("❌ Failed to send ZIP file", show_alert=True)


@router.callback_query(F.data == "send_stickers")
async def send_individual_stickers(callback: CallbackQuery, state: FSMContext):
    """Send individual emoji files"""
    data = await state.get_data()
    emoji_files = data.get('emoji_files', [])
    
    if not emoji_files:
        await callback.answer("❌ No emoji files found", show_alert=True)
        return
    
    await callback.answer("📱 Sending individual emojis...")
    
    try:
        for i, emoji_path in enumerate(emoji_files):
            if Path(emoji_path).exists():
                from aiogram.types import FSInputFile
                await callback.message.answer_document(
                    FSInputFile(emoji_path),
                    caption=f"Emoji {i+1}/{len(emoji_files)}"
                )
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
        
        await callback.message.answer("✅ All emojis sent individually!")
        
    except Exception as e:
        logger.error(f"Failed to send individual stickers: {e}")
        await callback.message.answer("❌ Some emojis failed to send")


@router.callback_query(F.data == "process_another")
async def process_another_image(callback: CallbackQuery, state: FSMContext):
    """Process another image"""
    await state.clear()
    await callback.message.edit_text(
        "🖼️ **Ready for another image!**\n\nSend me your next image to process.",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "add_sticker_pack")
async def add_sticker_pack_to_telegram(callback: CallbackQuery, state: FSMContext):
    """Provide sticker pack link for adding to Telegram"""
    data = await state.get_data()
    pack_result = data.get('sticker_pack_result')
    
    if not pack_result or not pack_result.get("success"):
        await callback.answer("❌ Sticker pack not available", show_alert=True)
        return
    
    pack_link = pack_result["pack_link"]
    pack_title = pack_result["pack_title"]
    
    message_text = f"""
🎯 **Add Your Sticker Pack to Telegram**

**Pack Name:** `{pack_title}`

**How to add:**
1. Click the link below
2. Press "Add Stickers" in Telegram
3. Start using your custom emojis!

**Link:** {pack_link}

🎉 Enjoy your personalized emoji pack!
"""
    
    # Create inline button with direct link
    keyboard = [
        [
            InlineKeyboardButton(
                text="🎯 Add Sticker Pack to Telegram",
                url=pack_link
            )
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="back_to_results")
        ]
    ]
    
    await callback.message.edit_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="Markdown"
    )
    await callback.answer("🎯 Sticker pack link ready!")


@router.callback_query(F.data == "back_to_results")
async def back_to_results(callback: CallbackQuery, state: FSMContext):
    """Go back to processing results"""
    data = await state.get_data()
    pack_result = data.get('sticker_pack_result', {})
    
    if pack_result.get("success"):
        message_text = f"""
✅ **Processing Complete!**

🎉 **Your Telegram sticker pack is ready!**

**Pack:** `{pack_result["pack_title"]}`
**Link:** {pack_result["pack_link"]}

Click the link above to add your custom emoji pack to Telegram! 🚀
"""
    else:
        message_text = "✅ **Processing Complete!**\n\nYour emojis are ready for download."
    
    await callback.message.edit_text(
        message_text,
        reply_markup=get_processing_complete_keyboard(has_sticker_pack=pack_result.get("success", False)),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "delete_files") 
async def delete_processing_files(callback: CallbackQuery, state: FSMContext):
    """Delete generated files"""
    data = await state.get_data()
    
    try:
        # Delete emoji files
        emoji_files = data.get('emoji_files', [])
        for file_path in emoji_files:
            try:
                Path(file_path).unlink()
            except:
                pass
        
        # Delete ZIP file
        zip_path = data.get('zip_path')
        if zip_path:
            try:
                Path(zip_path).unlink()
            except:
                pass
        
        await callback.message.edit_text(
            "🗑️ **Files deleted successfully!**",
            parse_mode="Markdown"
        )
        await callback.answer("Files deleted!")
        await state.clear()
        
    except Exception as e:
        logger.error(f"Failed to delete files: {e}")
        await callback.answer("❌ Some files could not be deleted", show_alert=True)