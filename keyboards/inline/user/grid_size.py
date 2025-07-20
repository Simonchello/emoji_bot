from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_grid_size_keyboard() -> InlineKeyboardMarkup:
    """Get grid size selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="1×3 📏", callback_data="grid_1_3"),
            InlineKeyboardButton(text="3×1 📐", callback_data="grid_3_1")
        ],
        [
            InlineKeyboardButton(text="2×2 ⬜", callback_data="grid_2_2"),
            InlineKeyboardButton(text="3×3 ⬛", callback_data="grid_3_3")
        ],
        [
            InlineKeyboardButton(text="2×5 ↔️", callback_data="grid_2_5"),
            InlineKeyboardButton(text="5×2 ↕️", callback_data="grid_5_2")
        ],
        [
            InlineKeyboardButton(text="4×4 🔲", callback_data="grid_4_4"),
            InlineKeyboardButton(text="🔧 Custom", callback_data="grid_custom")
        ],
        [
            InlineKeyboardButton(text="⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_custom_grid_keyboard() -> InlineKeyboardMarkup:
    """Get custom grid input keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="1", callback_data="grid_x_1"),
            InlineKeyboardButton(text="2", callback_data="grid_x_2"),
            InlineKeyboardButton(text="3", callback_data="grid_x_3"),
            InlineKeyboardButton(text="4", callback_data="grid_x_4")
        ],
        [
            InlineKeyboardButton(text="5", callback_data="grid_x_5"),
            InlineKeyboardButton(text="6", callback_data="grid_x_6"),
            InlineKeyboardButton(text="7", callback_data="grid_x_7"),
            InlineKeyboardButton(text="8", callback_data="grid_x_8")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="back_to_grid"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_grid_examples_keyboard() -> InlineKeyboardMarkup:
    """Get grid examples keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="📊 Timeline (1×3)", callback_data="example_timeline"),
        ],
        [
            InlineKeyboardButton(text="👤 Portrait (3×1)", callback_data="example_portrait"),
        ],
        [
            InlineKeyboardButton(text="🖼️ Gallery (3×3)", callback_data="example_gallery"),
        ],
        [
            InlineKeyboardButton(text="🎬 Wide Scene (2×5)", callback_data="example_wide"),
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="back_to_grid"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)