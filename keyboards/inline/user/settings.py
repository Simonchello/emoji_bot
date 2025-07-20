from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Get main settings keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="📐 Grid Size", callback_data="set_grid_size"),
            InlineKeyboardButton(text="🔄 Adaptation", callback_data="set_adaptation")
        ],
        [
            InlineKeyboardButton(text="🎨 Quality", callback_data="set_quality"),
            InlineKeyboardButton(text="🔍 Background", callback_data="set_background")
        ],
        [
            InlineKeyboardButton(text="📊 Statistics", callback_data="show_stats"),
            InlineKeyboardButton(text="🆘 Help", callback_data="show_help")
        ],
        [
            InlineKeyboardButton(text="🔄 Reset All", callback_data="reset_settings"),
            InlineKeyboardButton(text="📋 Export Settings", callback_data="export_settings")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main"),
            InlineKeyboardButton(text="❌ Close", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_quality_settings_keyboard() -> InlineKeyboardMarkup:
    """Get quality settings keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="🔴 High Quality", callback_data="quality_high"),
        ],
        [
            InlineKeyboardButton(text="🟡 Medium Quality", callback_data="quality_medium"),
        ],
        [
            InlineKeyboardButton(text="🟢 Low Quality (Fast)", callback_data="quality_low"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Quality Info", callback_data="quality_info"),
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="settings"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_background_settings_keyboard() -> InlineKeyboardMarkup:
    """Get background settings keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="🖼️ Keep Original", callback_data="bg_keep"),
        ],
        [
            InlineKeyboardButton(text="⚪ Remove White", callback_data="bg_remove_white"),
        ],
        [
            InlineKeyboardButton(text="⚫ Remove Black", callback_data="bg_remove_black"),
        ],
        [
            InlineKeyboardButton(text="🔍 Smart Removal", callback_data="bg_remove_smart"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Background Info", callback_data="bg_info"),
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="settings"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_statistics_keyboard() -> InlineKeyboardMarkup:
    """Get statistics keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="📈 Usage Stats", callback_data="stats_usage"),
            InlineKeyboardButton(text="💾 Cache Stats", callback_data="stats_cache")
        ],
        [
            InlineKeyboardButton(text="🔄 Processing History", callback_data="stats_history"),
            InlineKeyboardButton(text="⏱️ Performance", callback_data="stats_performance")
        ],
        [
            InlineKeyboardButton(text="🗑️ Clear History", callback_data="clear_history"),
            InlineKeyboardButton(text="🧹 Clean Cache", callback_data="clean_cache")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="settings"),
            InlineKeyboardButton(text="❌ Close", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Get help keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="🚀 Quick Start", callback_data="help_quickstart"),
            InlineKeyboardButton(text="📐 Grid Guide", callback_data="help_grid")
        ],
        [
            InlineKeyboardButton(text="🔄 Adaptation Guide", callback_data="help_adaptation"),
            InlineKeyboardButton(text="🎨 Quality Guide", callback_data="help_quality")
        ],
        [
            InlineKeyboardButton(text="💡 Tips & Tricks", callback_data="help_tips"),
            InlineKeyboardButton(text="❓ FAQ", callback_data="help_faq")
        ],
        [
            InlineKeyboardButton(text="📋 Examples", callback_data="help_examples"),
            InlineKeyboardButton(text="🐛 Report Bug", callback_data="help_bug")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="settings"),
            InlineKeyboardButton(text="❌ Close", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)