import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards import get_help_keyboard, get_main_menu

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("help"))
@router.message(F.text == "🆘 Help")
async def help_command(message: Message):
    """Handle /help command"""
    help_text = """
🆘 **Emoji Pack Bot Help**

**How to Use:**
1. Choose grid size (how many emojis to create)
2. Select adaptation method (how to fit your image)
3. Send image or video
4. Get your emoji pack!

**Grid Sizes:**
• `1×3` - Timeline/progress bars
• `3×1` - Tall subjects/portraits  
• `2×2` - Basic 4-emoji pack
• `3×3` - Classic 9-emoji pack
• `2×5` - Wide scenes/landscapes
• Custom - Any size up to 8×8

**Adaptation Methods:**
• `Pad` - Adds borders, keeps everything ✅
• `Stretch` - Changes proportions 
• `Crop` - Cuts edges, focuses center

**Commands:**
/start - Start the bot
/help - Show this help
/setgrid X Y - Set grid size directly
/adapt method - Set adaptation method
/settings - Open settings menu
/cancel - Cancel current operation

Need more specific help? Use the buttons below! 👇
"""
    
    await message.answer(
        help_text,
        reply_markup=get_help_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "help_quickstart")
async def help_quickstart(callback: CallbackQuery):
    """Quick start guide"""
    text = """
🚀 **Quick Start Guide**

**Step 1: Choose Grid Size**
• For beginners: Try 2×2 or 3×3
• For timelines: Use 1×3 
• For portraits: Use 3×1

**Step 2: Pick Adaptation**
• New users: Use "Pad" (recommended)
• Advanced: Try "Stretch" or "Crop"

**Step 3: Send Media**
• Images: JPG, PNG, WebP (up to 50MB)
• Videos: MP4, AVI, MOV (up to 5 minutes)

**Step 4: Get Results**
• Download ZIP file
• Or send directly to Telegram

**Pro Tip:** Start with a square image (1:1 ratio) for best results!
"""
    
    await callback.message.edit_text(text, reply_markup=get_help_keyboard(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "help_grid")
async def help_grid(callback: CallbackQuery):
    """Grid size guide"""
    text = """
📐 **Grid Size Guide**

**Common Sizes:**
• `1×3` - Perfect for progress bars, timelines
• `3×1` - Great for tall objects, portraits
• `2×2` - Simple 4-piece puzzles
• `3×3` - Classic grid, most versatile
• `4×4` - Detailed images, 16 emojis

**Custom Sizes:**
• Any combination from 1×1 to 8×8
• Examples: 1×5, 2×7, 6×2, etc.

**Choosing the Right Size:**
• More cells = more detail
• Fewer cells = simpler, clearer emojis
• Match your image's aspect ratio

**Tips:**
• Wide images → Use 1×X or 2×X grids
• Tall images → Use X×1 or X×2 grids  
• Square images → Use X×X grids
• Complex images → Use larger grids (4×4+)
"""
    
    await callback.message.edit_text(text, reply_markup=get_help_keyboard(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "help_adaptation")
async def help_adaptation(callback: CallbackQuery):
    """Adaptation method guide"""
    text = """
🔄 **Adaptation Method Guide**

**Pad (Recommended) 📏**
• Adds white borders to fit grid ratio
• Keeps all original content
• Best for: Most images, beginners
• Result: No distortion, complete image

**Stretch ↔️**
• Changes image proportions 
• Fits exactly to grid ratio
• Best for: Abstract images, patterns
• Result: May look distorted

**Crop ✂️**  
• Cuts edges to fit grid ratio
• Focuses on center content
• Best for: Images with important centers
• Result: May lose edge content

**When to Use What:**
• Portrait photo → Pad or Crop
• Landscape photo → Pad
• Logo/text → Pad
• Pattern/texture → Stretch
• Face/person → Crop (focuses on face)
"""
    
    await callback.message.edit_text(text, reply_markup=get_help_keyboard(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "help_tips")
async def help_tips(callback: CallbackQuery):
    """Tips and tricks"""
    text = """
💡 **Tips & Tricks**

**Image Quality:**
• Use high-resolution images (1000×1000+)
• Avoid very blurry or dark images
• PNG files preserve quality better

**Grid Selection:**
• Start small (2×2) for testing
• Match image orientation (wide=1×X, tall=X×1)
• More cells = longer processing time

**Adaptation Tips:**
• Use Pad for text/logos (keeps readability)
• Use Crop for faces (centers on subject)
• Preview before processing!

**Video Processing:**
• Keep videos under 2 minutes for best results
• Good lighting improves frame quality
• Bot automatically picks best frames

**Performance:**
• Process during off-peak hours
• Use "Fast Mode" for quick tests
• Clean cache regularly for better speed

**Telegram Stickers:**
• Each emoji is 512×512 pixels
• PNG format with transparency
• Perfect for Telegram sticker packs!
"""
    
    await callback.message.edit_text(text, reply_markup=get_help_keyboard(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "help_faq")
async def help_faq(callback: CallbackQuery):
    """Frequently asked questions"""
    text = """
❓ **Frequently Asked Questions**

**Q: What file formats are supported?**
A: Images: JPG, PNG, WebP, BMP, TIFF
   Videos: MP4, AVI, MOV, WebM, MKV

**Q: What's the maximum file size?**
A: 50MB for images, same for videos up to 5 minutes

**Q: How long does processing take?**  
A: Usually 10-60 seconds depending on size and grid

**Q: Can I use the emojis commercially?**
A: Yes, but ensure you have rights to original image

**Q: Why is my image blurry?**
A: Try higher resolution input or smaller grid size

**Q: Bot not responding?**
A: Try /cancel then /start to reset

**Q: Can I process multiple images?**
A: Process one at a time for best results

**Q: How to create animated emojis?**
A: Send a video - bot extracts frames automatically

**Q: Where are my files stored?**
A: Temporarily cached, auto-deleted after 1 hour

**Still need help?** Contact support!
"""
    
    await callback.message.edit_text(text, reply_markup=get_help_keyboard(), parse_mode="Markdown")
    await callback.answer()