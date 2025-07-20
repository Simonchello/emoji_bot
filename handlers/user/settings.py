import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards import (
    get_settings_keyboard, get_grid_size_keyboard, get_adaptation_method_keyboard,
    get_quality_settings_keyboard, get_background_settings_keyboard,
    get_statistics_keyboard
)
from .start import user_settings

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("settings"))
@router.message(F.text == "⚙️ Settings")
@router.callback_query(F.data == "settings")
async def settings_menu(event):
    """Handle settings menu"""
    if isinstance(event, CallbackQuery):
        user_id = event.from_user.id
        await event.message.edit_text(
            "⚙️ **Settings Menu**\n\nChoose what you'd like to configure:",
            reply_markup=get_settings_keyboard(),
            parse_mode="Markdown"
        )
        await event.answer()
    else:
        user_id = event.from_user.id
        await event.answer(
            "⚙️ **Settings Menu**\n\nChoose what you'd like to configure:",
            reply_markup=get_settings_keyboard(),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "set_grid_size")
async def set_grid_size(callback: CallbackQuery):
    """Handle grid size setting"""
    user_id = callback.from_user.id
    settings = user_settings.get(user_id)
    
    current_grid = f"{settings.grid_x}×{settings.grid_y}" if settings else "2×2"
    
    text = f"""
📐 **Grid Size Configuration**

Current: `{current_grid}`

Choose a new grid size or create a custom one:
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_grid_size_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "set_adaptation")
async def set_adaptation(callback: CallbackQuery):
    """Handle adaptation method setting"""
    user_id = callback.from_user.id
    settings = user_settings.get(user_id)
    
    current_method = settings.adaptation_method if settings else "pad"
    method_names = {"pad": "Pad", "stretch": "Stretch", "crop": "Crop"}
    
    text = f"""
🔄 **Adaptation Method Configuration**

Current: `{method_names.get(current_method, current_method)}`

How should images be adapted to fit the grid?
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_adaptation_method_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "set_quality")
async def set_quality(callback: CallbackQuery):
    """Handle quality setting"""
    user_id = callback.from_user.id
    settings = user_settings.get(user_id)
    
    current_quality = settings.quality_level if settings else "high"
    
    text = f"""
🎨 **Quality Settings**

Current: `{current_quality.title()}`

Choose processing quality:
• **High** - Best quality, slower processing
• **Medium** - Good balance  
• **Low** - Fast processing, lower quality
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_quality_settings_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "set_background")
async def set_background(callback: CallbackQuery):
    """Handle background setting"""
    user_id = callback.from_user.id
    settings = user_settings.get(user_id)
    
    current_bg = "Enabled" if (settings and settings.background_removal) else "Disabled"
    
    text = f"""
🔍 **Background Removal Settings**

Current: `{current_bg}`

Choose background handling for your emojis:
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_background_settings_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "show_stats")
async def show_stats(callback: CallbackQuery):
    """Handle statistics display"""
    text = """
📊 **Statistics**

Choose what statistics you'd like to view:
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_statistics_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# Grid size handlers
@router.callback_query(F.data.startswith("grid_"))
async def handle_grid_selection(callback: CallbackQuery):
    """Handle grid size selection"""
    user_id = callback.from_user.id
    
    if user_id not in user_settings:
        from models import UserSettings
        user_settings[user_id] = UserSettings(user_id=user_id)
    
    data = callback.data
    
    if data == "grid_custom":
        await callback.message.edit_text(
            "🔧 **Custom Grid Size**\n\nPlease send your custom grid size in format: `X Y`\nExample: `4 3` for 4×3 grid",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    # Parse grid size from callback data
    parts = data.split("_")
    if len(parts) >= 3:
        try:
            grid_x = int(parts[1])
            grid_y = int(parts[2])
            
            user_settings[user_id].grid_x = grid_x
            user_settings[user_id].grid_y = grid_y
            
            await callback.message.edit_text(
                f"✅ **Grid size set to {grid_x}×{grid_y}**\n\nNow choose your adaptation method:",
                reply_markup=get_adaptation_method_keyboard(),
                parse_mode="Markdown"
            )
            await callback.answer("Grid size updated!")
            
        except ValueError:
            await callback.answer("Invalid grid size format", show_alert=True)


# Adaptation method handlers
@router.callback_query(F.data.startswith("adapt_"))
async def handle_adaptation_selection(callback: CallbackQuery):
    """Handle adaptation method selection"""
    user_id = callback.from_user.id
    
    if user_id not in user_settings:
        from models import UserSettings
        user_settings[user_id] = UserSettings(user_id=user_id)
    
    method = callback.data.split("_")[1]
    user_settings[user_id].adaptation_method = method
    
    method_names = {"pad": "Pad", "stretch": "Stretch", "crop": "Crop"}
    method_name = method_names.get(method, method)
    
    await callback.message.edit_text(
        f"✅ **Adaptation method set to {method_name}**\n\n🎯 Perfect! Now send me an image or video to process.",
        parse_mode="Markdown"
    )
    await callback.answer(f"Adaptation method set to {method_name}")


# Quality handlers
@router.callback_query(F.data.startswith("quality_"))
async def handle_quality_selection(callback: CallbackQuery):
    """Handle quality selection"""
    user_id = callback.from_user.id
    
    if user_id not in user_settings:
        from models import UserSettings
        user_settings[user_id] = UserSettings(user_id=user_id)
    
    quality = callback.data.split("_")[1]
    user_settings[user_id].quality_level = quality
    
    await callback.message.edit_text(
        f"✅ **Quality set to {quality.title()}**",
        reply_markup=get_settings_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer(f"Quality set to {quality}")


# Background removal handlers  
@router.callback_query(F.data.startswith("bg_"))
async def handle_background_selection(callback: CallbackQuery):
    """Handle background removal selection"""
    user_id = callback.from_user.id
    
    if user_id not in user_settings:
        from models import UserSettings
        user_settings[user_id] = UserSettings(user_id=user_id)
    
    bg_action = callback.data.split("_", 1)[1]
    
    if bg_action == "keep":
        user_settings[user_id].background_removal = False
        message = "Background will be kept"
    else:
        user_settings[user_id].background_removal = True
        message = f"Background removal enabled: {bg_action.replace('_', ' ')}"
    
    await callback.message.edit_text(
        f"✅ **{message}**",
        reply_markup=get_settings_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer(message)


# Navigation handlers
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Go back to main menu"""
    await callback.message.edit_text(
        "🏠 **Main Menu**\n\nWhat would you like to do?",
        reply_markup=get_grid_size_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery):
    """Cancel current action"""
    await callback.message.delete()
    await callback.answer("Cancelled")


# Handle custom grid size input
@router.message(F.text.regexp(r'^\d+\s+\d+$'))
async def handle_custom_grid_input(message: Message):
    """Handle custom grid size input"""
    user_id = message.from_user.id
    
    try:
        parts = message.text.split()
        grid_x, grid_y = int(parts[0]), int(parts[1])
        
        if not (1 <= grid_x <= 8 and 1 <= grid_y <= 8):
            await message.answer("❌ Grid size must be between 1×1 and 8×8")
            return
        
        if user_id not in user_settings:
            from models import UserSettings
            user_settings[user_id] = UserSettings(user_id=user_id)
        
        user_settings[user_id].grid_x = grid_x
        user_settings[user_id].grid_y = grid_y
        
        await message.answer(
            f"✅ **Custom grid size set to {grid_x}×{grid_y}**\n\nNow choose your adaptation method:",
            reply_markup=get_adaptation_method_keyboard(),
            parse_mode="Markdown"
        )
        
    except (ValueError, IndexError):
        await message.answer("❌ Invalid format. Please use: `X Y` (e.g., `4 3`)", parse_mode="Markdown")