import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import (
    get_settings_keyboard, get_grid_selection_keyboard, get_adaptation_keyboard,
    get_help_keyboard
)
from states import UserStates
from .start import user_settings

logger = logging.getLogger(__name__)
router = Router()


def get_settings_text(user_id: int) -> str:
    """Generate settings text for a user"""
    settings = user_settings.get(user_id)
    if not settings:
        return "No settings configured yet."

    method_names = {"pad": "Pad (Keep All)", "stretch": "Stretch", "crop": "Crop"}
    return f"""
⚙️ <b>Configure Your Settings</b>

<b>Current Settings:</b>
• Grid Size: {settings.grid_x}×{settings.grid_y}
• Adaptation: {method_names.get(settings.adaptation_method, settings.adaptation_method)}

<b>Total emojis:</b> {settings.grid_x * settings.grid_y}

Adjust the settings below, then click "Done" to process your image.
"""


@router.message(Command("settings"))
@router.message(F.text == "⚙️ Settings")
async def settings_command(message: Message):
    """Handle /settings command"""
    user_id = message.from_user.id

    if user_id not in user_settings:
        from models import UserSettings
        user_settings[user_id] = UserSettings(user_id=user_id)

    await message.answer(
        get_settings_text(user_id),
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings")
async def settings_menu(callback: CallbackQuery, state: FSMContext):
    """Handle settings menu callback"""
    user_id = callback.from_user.id

    if user_id not in user_settings:
        from models import UserSettings
        user_settings[user_id] = UserSettings(user_id=user_id)

    await callback.message.edit_text(
        get_settings_text(user_id),
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery, state: FSMContext):
    """Go back to settings menu"""
    user_id = callback.from_user.id

    await callback.message.edit_text(
        get_settings_text(user_id),
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "set_grid_size")
async def set_grid_size(callback: CallbackQuery):
    """Handle grid size setting"""
    user_id = callback.from_user.id
    settings = user_settings.get(user_id)

    current_grid = f"{settings.grid_x}×{settings.grid_y}" if settings else "2×2"

    text = f"""
📐 <b>Grid Size Configuration</b>

Current: <code>{current_grid}</code>

Choose a grid size or select "Custom" to enter your own:
"""

    await callback.message.edit_text(
        text,
        reply_markup=get_grid_selection_keyboard(),
        parse_mode="HTML"
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
🔄 <b>Adaptation Method</b>

Current: <code>{method_names.get(current_method, current_method)}</code>

How should the image be adapted to fit the grid?

• <b>Pad</b> - Adds borders, keeps everything visible
• <b>Stretch</b> - Changes proportions to fit exactly
• <b>Crop</b> - Cuts edges, focuses on center
"""

    await callback.message.edit_text(
        text,
        reply_markup=get_adaptation_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_help")
async def show_help(callback: CallbackQuery):
    """Show help menu"""
    text = """
🆘 <b>Help</b>

Choose a topic to learn more:
"""

    await callback.message.edit_text(
        text,
        reply_markup=get_help_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# Grid size handlers
@router.callback_query(F.data.startswith("grid_"))
async def handle_grid_selection(callback: CallbackQuery, state: FSMContext):
    """Handle grid size selection"""
    user_id = callback.from_user.id

    if user_id not in user_settings:
        from models import UserSettings
        user_settings[user_id] = UserSettings(user_id=user_id)

    data = callback.data

    if data == "grid_custom":
        await state.set_state(UserStates.setting_grid_size_x)
        await callback.message.edit_text(
            "🔧 <b>Custom Grid Size</b>\n\nPlease send your custom grid size in format: <code>X Y</code>\nExample: <code>4 3</code> for 4×3 grid\n\n(Values must be between 1 and 8)",
            parse_mode="HTML"
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
                get_settings_text(user_id),
                reply_markup=get_settings_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer(f"Grid size set to {grid_x}×{grid_y}")

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
        get_settings_text(user_id),
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer(f"Adaptation set to {method_name}")


# Handler for "Done - Process" when no image is uploaded
@router.callback_query(F.data == "start_processing")
async def start_processing_no_image(callback: CallbackQuery, state: FSMContext):
    """Handle start_processing when no image has been uploaded"""
    # This handler catches start_processing clicks when NOT in confirming_processing state
    # (the image.py and video.py handlers have state filters, so this catches the rest)
    await callback.answer("Please send an image or video first!", show_alert=True)


# Navigation handlers
@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Cancel current action and clear state"""
    await state.clear()
    await callback.message.edit_text(
        "❌ <b>Cancelled</b>\n\nSend me an image or video when you're ready to try again.",
        parse_mode="HTML"
    )
    await callback.answer("Cancelled")


# Handle custom grid size input
@router.message(F.text.regexp(r'^\d+\s+\d+$'), UserStates.setting_grid_size_x)
async def handle_custom_grid_input(message: Message, state: FSMContext):
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

        await state.clear()
        await message.answer(
            get_settings_text(user_id),
            reply_markup=get_settings_keyboard(),
            parse_mode="HTML"
        )

    except (ValueError, IndexError):
        await message.answer("❌ Invalid format. Please use: <code>X Y</code> (e.g., <code>4 3</code>)", parse_mode="HTML")


# Handle invalid input during custom grid state
@router.message(UserStates.setting_grid_size_x)
async def handle_invalid_grid_input(message: Message):
    """Handle invalid custom grid input"""
    await message.answer(
        "❌ Invalid format. Please enter two numbers separated by space.\n\nExample: <code>4 3</code> for a 4×3 grid",
        parse_mode="HTML"
    )
