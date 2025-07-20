import asyncio
import logging
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from filters import IsVideoFilter, FileSizeFilter, SupportedFormatFilter
from keyboards import get_processing_confirmation_keyboard, get_processing_complete_keyboard
from states import UserStates
from utils import (
    VideoProcessor, ImageProcessor, EmojiGenerator, FileManager, ProgressTracker,
    validate_file_format, validate_file_size
)
from exceptions import VideoProcessingError, FileSizeError, FileFormatError
from config import load_config, CACHE_DIR
from .start import user_settings

logger = logging.getLogger(__name__)
router = Router()

# Initialize processors
video_processor = VideoProcessor()
image_processor = ImageProcessor()
emoji_generator = EmojiGenerator()


@router.message(
    IsVideoFilter(),
    FileSizeFilter(max_size_mb=50),
    SupportedFormatFilter()
)
async def handle_video_upload(message: Message, state: FSMContext, bot: Bot):
    """Handle video upload for processing"""
    user_id = message.from_user.id
    
    # Check if user has settings configured
    if user_id not in user_settings:
        await message.answer(
            "⚙️ Please configure your settings first!\n\nUse /start to begin setup.",
            reply_markup=None
        )
        return
    
    settings = user_settings[user_id]
    
    # Get video info for display
    file_size_mb = 0
    duration = 0
    
    if message.video:
        file_size_mb = (message.video.file_size or 0) / (1024 * 1024)
        duration = message.video.duration or 0
    elif message.document:
        file_size_mb = (message.document.file_size or 0) / (1024 * 1024)
    
    # Calculate estimated emoji count
    estimated_frames = min(20, max(5, int(duration / 2))) if duration > 0 else 10
    total_emojis = estimated_frames * (settings.grid_x * settings.grid_y)
    
    config_text = f"""
🎥 **Video Received!**

**Video Info:**
• Size: `{file_size_mb:.1f} MB`
• Duration: `{duration}s`
• Estimated frames: `~{estimated_frames}`

**Your Settings:**
• Grid Size: `{settings.grid_x}×{settings.grid_y}`
• Adaptation: `{settings.adaptation_method.title()}`
• Quality: `{settings.quality_level.title()}`

**Estimated Output:** `~{total_emojis}` emojis

Ready to process your video?
"""
    
    # Store video info in state
    await state.update_data(
        file_id=message.video.file_id if message.video else message.document.file_id,
        message_id=message.message_id,
        estimated_frames=estimated_frames
    )
    await state.set_state(UserStates.confirming_processing)
    
    await message.answer(
        config_text,
        reply_markup=get_processing_confirmation_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "start_processing", UserStates.confirming_processing)
async def start_video_processing(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Start video processing"""
    user_id = callback.from_user.id
    settings = user_settings[user_id]
    data = await state.get_data()
    
    try:
        await state.set_state(UserStates.processing_media)
        
        # Update message to show processing started
        await callback.message.edit_text(
            "🔄 **Processing your video...**\n\nExtracting frames and creating emojis. This may take a few minutes.",
            parse_mode="Markdown"
        )
        await callback.answer()
        
        # Initialize file manager and config
        config = load_config()
        file_manager = FileManager(bot, config.max_file_size_mb)
        
        # Get file info and download
        file_info = await bot.get_file(data['file_id'])
        local_path = await file_manager.download_media(file_info, user_id)
        
        # Validate file
        validate_file_size(local_path, config.max_file_size_mb)
        media_type = validate_file_format(local_path)
        
        if media_type != "video":
            raise FileFormatError("Expected video file")
        
        # Validate video constraints
        video_processor.validate_video(local_path, config.max_video_duration)
        
        # Get video info
        video_info = video_processor.get_video_info(local_path)
        logger.info(f"Processing video: {video_info}")
        
        # Calculate processing steps
        estimated_frames = data.get('estimated_frames', 10)
        total_steps = 3 + estimated_frames + (estimated_frames * settings.grid_x * settings.grid_y)
        progress_tracker = ProgressTracker(total_steps)
        
        # Extract key frames from video
        progress_tracker.update(1, "Analyzing video...")
        max_frames = min(20, max(5, int(video_info['duration'] / 2))) if video_info['duration'] > 0 else 10
        
        frames = video_processor.extract_key_frames(
            local_path, 
            max_frames=max_frames,
            progress_tracker=progress_tracker
        )
        
        logger.info(f"Extracted {len(frames)} frames from video")
        
        # Process each frame into emoji grids
        progress_tracker.update(1, "Processing frames...")
        
        all_emoji_files = []
        frame_sequences = []
        
        for frame_idx, frame in enumerate(frames):
            # Enhance frame if needed
            if settings.quality_level == "high":
                frame = image_processor.enhance_image(frame, "medium")
            
            # Adapt frame to grid ratio
            adapted_frame = image_processor.adapt_image_to_grid(
                frame, settings.grid_x, settings.grid_y, settings.adaptation_method
            )
            
            # Split into grid cells
            emoji_cells = image_processor.split_image_grid(
                adapted_frame, settings.grid_x, settings.grid_y
            )
            
            # Apply background removal if enabled
            if settings.background_removal:
                for i, cell in enumerate(emoji_cells):
                    emoji_cells[i] = emoji_generator.add_transparency(cell, method="white")
            
            frame_sequences.append(emoji_cells)
            progress_tracker.update(len(emoji_cells), f"Processed frame {frame_idx+1}/{len(frames)}")
        
        # Generate emoji packs for each frame
        progress_tracker.update(1, "Generating emoji packs...")
        
        output_dir = CACHE_DIR / f"user_{user_id}_video_output"
        output_dir.mkdir(exist_ok=True)
        
        for frame_idx, emoji_cells in enumerate(frame_sequences):
            pack_name = f"video_frame_{frame_idx+1:03d}"
            
            saved_files = emoji_generator.create_emoji_pack(
                emoji_cells, pack_name, user_id, output_dir / f"frame_{frame_idx+1:03d}"
            )
            all_emoji_files.extend(saved_files)
        
        # Create master ZIP archive with all frames
        master_zip_path = output_dir / f"video_emoji_pack_{user_id}.zip"
        emoji_generator.create_pack_archive(all_emoji_files, f"video_pack_{user_id}", master_zip_path)
        
        # Success message
        success_text = f"""
✅ **Video Processing Complete!**

**Results:**
• Processed: `{len(frames)}` frames
• Created: `{len(all_emoji_files)}` emojis total
• Grid: `{settings.grid_x}×{settings.grid_y}` per frame
• Quality: `{settings.quality_level.title()}`

Your video emoji collection is ready! 🎉
"""
        
        # Store results in state
        await state.update_data(
            emoji_files=[str(f) for f in all_emoji_files],
            zip_path=str(master_zip_path),
            pack_name=f"video_pack_{user_id}",
            frame_count=len(frames),
            frame_sequences=frame_sequences
        )
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_processing_complete_keyboard(),
            parse_mode="Markdown"
        )
        
        # Send preview of first frame emojis
        if frame_sequences:
            first_frame_files = all_emoji_files[:settings.grid_x * settings.grid_y]
            await send_video_emoji_preview(callback.message, first_frame_files, frame_idx=1)
        
        # Clean up original file
        try:
            local_path.unlink()
        except:
            pass
        
        logger.info(f"Successfully processed video for user {user_id}: {len(frames)} frames, {len(all_emoji_files)} emojis")
        
    except Exception as e:
        logger.error(f"Video processing failed for user {user_id}: {e}")
        
        error_text = f"""
❌ **Video Processing Failed**

Error: `{str(e)[:100]}...`

**Common issues:**
• Video too long (max 5 minutes)
• Unsupported format
• File corrupted

Please try with a shorter, high-quality video.
"""
        
        await callback.message.edit_text(
            error_text,
            parse_mode="Markdown"
        )
        await state.clear()


async def send_video_emoji_preview(message: Message, emoji_files: list, frame_idx: int = 1, max_preview: int = 4):
    """Send preview of generated video emojis"""
    try:
        preview_files = emoji_files[:max_preview]
        
        if not preview_files:
            return
        
        await message.answer(f"📱 **Frame {frame_idx} Preview** (showing {len(preview_files)}/{len(emoji_files)} emojis):")
        
        # Send emojis as photos
        for i, emoji_path in enumerate(preview_files):
            if Path(emoji_path).exists():
                try:
                    from aiogram.types import FSInputFile
                    await message.answer_photo(
                        FSInputFile(emoji_path),
                        caption=f"Frame {frame_idx} - Emoji {i+1}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send video emoji preview {i+1}: {e}")
    
    except Exception as e:
        logger.warning(f"Failed to send video emoji preview: {e}")


@router.callback_query(F.data == "view_details")
async def view_video_details(callback: CallbackQuery, state: FSMContext):
    """Show detailed video processing results"""
    data = await state.get_data()
    
    frame_count = data.get('frame_count', 0)
    emoji_count = len(data.get('emoji_files', []))
    pack_name = data.get('pack_name', 'Unknown')
    
    details_text = f"""
📊 **Processing Details**

**Video Analysis:**
• Frames extracted: `{frame_count}`
• Total emojis: `{emoji_count}`
• Pack name: `{pack_name}`

**Frame Breakdown:**
"""
    
    # Add frame-by-frame info
    user_id = callback.from_user.id
    settings = user_settings.get(user_id)
    if settings:
        emojis_per_frame = settings.grid_x * settings.grid_y
        for i in range(frame_count):
            details_text += f"• Frame {i+1}: {emojis_per_frame} emojis\n"
    
    details_text += f"\n**Files:** ZIP archive with all frames ready for download!"
    
    await callback.message.edit_text(
        details_text,
        reply_markup=get_processing_complete_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "send_stickers")
async def send_video_stickers_by_frame(callback: CallbackQuery, state: FSMContext):
    """Send video emojis organized by frame"""
    data = await state.get_data()
    emoji_files = data.get('emoji_files', [])
    frame_count = data.get('frame_count', 0)
    
    if not emoji_files or frame_count == 0:
        await callback.answer("❌ No emoji files found", show_alert=True)
        return
    
    await callback.answer("📱 Sending emojis by frame...")
    
    try:
        user_id = callback.from_user.id
        settings = user_settings.get(user_id)
        
        if not settings:
            await callback.message.answer("❌ Settings not found")
            return
        
        emojis_per_frame = settings.grid_x * settings.grid_y
        
        for frame_idx in range(frame_count):
            start_idx = frame_idx * emojis_per_frame
            end_idx = start_idx + emojis_per_frame
            frame_emojis = emoji_files[start_idx:end_idx]
            
            if frame_emojis:
                await callback.message.answer(f"🎬 **Frame {frame_idx + 1}/{frame_count}**")
                
                for i, emoji_path in enumerate(frame_emojis):
                    if Path(emoji_path).exists():
                        from aiogram.types import FSInputFile
                        await callback.message.answer_document(
                            FSInputFile(emoji_path),
                            caption=f"Frame {frame_idx + 1} - Emoji {i+1}/{len(frame_emojis)}"
                        )
                        # Small delay to avoid rate limits
                        await asyncio.sleep(0.3)
        
        await callback.message.answer("✅ All video emojis sent by frame!")
        
    except Exception as e:
        logger.error(f"Failed to send video stickers: {e}")
        await callback.message.answer("❌ Some emojis failed to send")


@router.callback_query(F.data == "create_animated")
async def create_animated_emojis(callback: CallbackQuery, state: FSMContext):
    """Create animated emojis from video frames (placeholder)"""
    await callback.answer("🔄 Animated emoji creation is coming soon!", show_alert=True)
    
    # In a full implementation, this would:
    # 1. Group frames by cell position
    # 2. Create GIF or WebM animations
    # 3. Generate animated sticker packs