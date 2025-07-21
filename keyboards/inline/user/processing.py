from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_processing_confirmation_keyboard(is_video: bool = False) -> InlineKeyboardMarkup:
    """Get processing confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Start Processing", callback_data="start_processing"),
        ]
    ]
    
    if is_video:
        keyboard.append([
            InlineKeyboardButton(text="🎬 Create Animated", callback_data="create_animated"),
        ])
    
    keyboard.extend([
        [
            InlineKeyboardButton(text="👁️ Preview", callback_data="preview_adaptation"),
            InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")
        ],
        [
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
        ]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_adaptation_method_keyboard() -> InlineKeyboardMarkup:
    """Get adaptation method selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="📏 Pad (Keep All)", callback_data="adapt_pad"),
        ],
        [
            InlineKeyboardButton(text="↔️ Stretch (Distort)", callback_data="adapt_stretch"),
        ],
        [
            InlineKeyboardButton(text="✂️ Crop (Cut Edges)", callback_data="adapt_crop"),
        ],
        [
            InlineKeyboardButton(text="❓ What's This?", callback_data="explain_adaptation"),
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_processing_options_keyboard() -> InlineKeyboardMarkup:
    """Get processing options keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="🎨 High Quality", callback_data="quality_high"),
            InlineKeyboardButton(text="⚡ Fast Mode", callback_data="quality_low")
        ],
        [
            InlineKeyboardButton(text="🖼️ Keep Background", callback_data="bg_keep"),
            InlineKeyboardButton(text="🔍 Remove Background", callback_data="bg_remove")
        ],
        [
            InlineKeyboardButton(text="📊 Show Progress", callback_data="progress_show"),
            InlineKeyboardButton(text="🔕 Silent Mode", callback_data="progress_hide")
        ],
        [
            InlineKeyboardButton(text="✅ Continue", callback_data="options_done"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_processing_progress_keyboard() -> InlineKeyboardMarkup:
    """Get processing progress keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="❌ Cancel Processing", callback_data="cancel_processing"),
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_processing_complete_keyboard(has_sticker_pack: bool = False, is_animated: bool = False) -> InlineKeyboardMarkup:
    """Get processing complete keyboard"""
    keyboard = []
    
    if has_sticker_pack:
        emoji_text = "🎬 Add Animated Pack" if is_animated else "🎯 Add Emoji Pack"
        keyboard.append([
            InlineKeyboardButton(text=emoji_text, callback_data="add_sticker_pack")
        ])
    
    download_text = "💾 Download ZIP"
    individual_text = "📱 Send Individual"
    
    if is_animated:
        download_text = "💾 Download WebM Pack"
        individual_text = "🎬 Send Animated"
    
    keyboard.extend([
        [
            InlineKeyboardButton(text=download_text, callback_data="download_zip"),
            InlineKeyboardButton(text=individual_text, callback_data="send_stickers")
        ],
        [
            InlineKeyboardButton(text="🔄 Process Another", callback_data="process_another"),
            InlineKeyboardButton(text="⚙️ Different Settings", callback_data="change_settings")
        ],
        [
            InlineKeyboardButton(text="📊 View Details", callback_data="view_details"),
            InlineKeyboardButton(text="🗑️ Delete Files", callback_data="delete_files")
        ],
        [
            InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
        ]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_animation_options_keyboard() -> InlineKeyboardMarkup:
    """Get animation options keyboard for video processing"""
    keyboard = [
        [
            InlineKeyboardButton(text="⚡ 15 FPS (Smooth)", callback_data="fps_15"),
            InlineKeyboardButton(text="🚀 30 FPS (Ultra)", callback_data="fps_30")
        ],
        [
            InlineKeyboardButton(text="⏱️ 1s Duration", callback_data="duration_1"),
            InlineKeyboardButton(text="⏱️ 2s Duration", callback_data="duration_2")
        ],
        [
            InlineKeyboardButton(text="⏱️ 3s Duration (Max)", callback_data="duration_3")
        ],
        [
            InlineKeyboardButton(text="✅ Create Animated", callback_data="confirm_animated"),
            InlineKeyboardButton(text="📱 Static Mode", callback_data="start_processing")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="back_to_video"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)