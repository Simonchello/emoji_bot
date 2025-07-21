import cv2
import numpy as np
from typing import List, Optional
import logging
from pathlib import Path
import zipfile
import json
import time

from exceptions import ImageProcessingError
from .helpers import safe_filename, ProgressTracker
from .image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class EmojiGenerator:
    """Generate Telegram-compatible emoji packs"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
    
    def create_emoji_pack(
        self, 
        images: List[np.ndarray], 
        pack_name: str,
        user_id: int,
        output_dir: Path,
        progress_tracker: Optional[ProgressTracker] = None
    ) -> List[Path]:
        """
        Generate Telegram sticker pack from images
        
        Args:
            images: List of processed emoji images
            pack_name: Name for the emoji pack
            user_id: User ID for file naming
            output_dir: Directory to save emoji files
            progress_tracker: Optional progress tracking
            
        Returns:
            List of saved emoji file paths
        """
        try:
            if not images:
                raise ImageProcessingError("No images provided for emoji pack")
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate safe pack name
            safe_pack_name = safe_filename(pack_name)
            
            saved_files = []
            total_images = len(images)
            
            logger.info(f"Creating emoji pack '{safe_pack_name}' with {total_images} emojis")
            
            for i, image in enumerate(images):
                # Optimize image for Telegram
                optimized_image = self.optimize_emoji_size(image)
                
                # Generate filename
                emoji_filename = f"{safe_pack_name}_emoji_{i+1:03d}.png"
                emoji_path = output_dir / emoji_filename
                
                # Save emoji
                success = self.image_processor.save_image(optimized_image, emoji_path, quality=95)
                if success:
                    saved_files.append(emoji_path)
                    logger.debug(f"Saved emoji: {emoji_path}")
                else:
                    logger.warning(f"Failed to save emoji: {emoji_path}")
                
                if progress_tracker:
                    progress_tracker.update(1, f"Generated emoji {i+1}/{total_images}")
            
            # Create pack metadata
            metadata_path = output_dir / f"{safe_pack_name}_metadata.json"
            self._create_pack_metadata(saved_files, pack_name, user_id, metadata_path)
            
            logger.info(f"Successfully created emoji pack with {len(saved_files)} emojis")
            return saved_files
            
        except Exception as e:
            # Clean up any partially created files
            if 'output_dir' in locals() and output_dir.exists():
                try:
                    # Clean up individual emoji files
                    if 'saved_files' in locals():
                        for file_path in saved_files:
                            try:
                                if file_path.exists():
                                    file_path.unlink()
                            except:
                                pass
                    
                    # Clean up metadata file if it exists
                    if 'safe_pack_name' in locals():
                        metadata_path = output_dir / f"{safe_pack_name}_metadata.json"
                        if metadata_path.exists():
                            metadata_path.unlink()
                    
                    logger.debug(f"Cleaned up partially created emoji files in: {output_dir}")
                    
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup emoji files after error: {cleanup_error}")
            
            raise ImageProcessingError(f"Failed to create emoji pack: {e}")
    
    def optimize_emoji_size(self, image: np.ndarray, target_size: int = 100) -> np.ndarray:
        """
        Optimize image size and quality for Telegram custom emoji
        
        Args:
            image: Input image
            target_size: Target size (100x100 for custom emoji)
            
        Returns:
            Optimized image
        """
        try:
            # Ensure image is the right size
            if image.shape[:2] != (target_size, target_size):
                optimized = cv2.resize(image, (target_size, target_size), interpolation=cv2.INTER_LANCZOS4)
            else:
                optimized = image.copy()
            
            # Ensure image has proper format (BGR or BGRA)
            if len(optimized.shape) == 3:
                if optimized.shape[2] == 3:
                    # BGR image - add alpha channel for PNG
                    optimized = cv2.cvtColor(optimized, cv2.COLOR_BGR2BGRA)
                elif optimized.shape[2] == 4:
                    # Already BGRA
                    pass
                else:
                    raise ImageProcessingError(f"Unexpected image format: {optimized.shape}")
            else:
                # Grayscale - convert to BGRA
                optimized = cv2.cvtColor(optimized, cv2.COLOR_GRAY2BGRA)
            
            return optimized
            
        except Exception as e:
            raise ImageProcessingError(f"Failed to optimize emoji size: {e}")
    
    def add_transparency(
        self, 
        image: np.ndarray, 
        method: str = "white",
        threshold: int = 240
    ) -> np.ndarray:
        """
        Add transparency to emoji by removing background
        
        Args:
            image: Input image
            method: Background removal method ("white", "black", "edge")
            threshold: Threshold for background detection
            
        Returns:
            Image with transparency
        """
        try:
            # Ensure image has alpha channel
            if len(image.shape) == 3 and image.shape[2] == 3:
                bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            else:
                bgra = image.copy()
            
            if method == "white":
                # Remove white/light backgrounds
                gray = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
                bgra[:, :, 3] = 255 - mask
                
            elif method == "black":
                # Remove black/dark backgrounds
                gray = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray, 255 - threshold, 255, cv2.THRESH_BINARY_INV)
                bgra[:, :, 3] = 255 - mask
                
            elif method == "edge":
                # Use edge detection for better background removal
                gray = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2GRAY)
                
                # Apply Gaussian blur to reduce noise
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                
                # Edge detection
                edges = cv2.Canny(blurred, 50, 150)
                
                # Dilate edges to create mask
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.dilate(edges, kernel, iterations=2)
                
                # Fill holes in the mask
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.fillPoly(mask, contours, 255)
                
                bgra[:, :, 3] = mask
            
            return bgra
            
        except Exception as e:
            logger.warning(f"Transparency addition failed: {e}")
            return image
    
    def enhance_emoji_quality(self, image: np.ndarray) -> np.ndarray:
        """
        Apply quality enhancements specific to emoji
        
        Args:
            image: Input emoji image
            
        Returns:
            Enhanced emoji image
        """
        try:
            enhanced = image.copy()
            
            # Sharpen the image slightly for better emoji clarity
            kernel = np.array([[-0.5, -0.5, -0.5],
                              [-0.5,  5.0, -0.5],
                              [-0.5, -0.5, -0.5]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            # Slight contrast enhancement
            alpha = 1.1  # Contrast control
            beta = 10    # Brightness control
            enhanced = cv2.convertScaleAbs(enhanced, alpha=alpha, beta=beta)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Emoji enhancement failed: {e}")
            return image
    
    def create_animated_emoji_sequence(
        self, 
        frame_sequences: List[List[np.ndarray]],
        pack_name: str,
        user_id: int,
        output_dir: Path,
        fps: int = 10,
        progress_tracker: Optional[ProgressTracker] = None
    ) -> List[Path]:
        """
        Create animated emoji sequence from video frames
        
        Args:
            frame_sequences: List of frame sequences (each sequence is a list of grid cells)
            pack_name: Name for the emoji pack
            user_id: User ID for file naming
            output_dir: Directory to save emoji files
            fps: Frames per second for animation
            progress_tracker: Optional progress tracking
            
        Returns:
            List of saved animated emoji paths
        """
        try:
            if not frame_sequences:
                raise ImageProcessingError("No frame sequences provided")
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate safe pack name
            safe_pack_name = safe_filename(pack_name)
            
            # Organize frames by cell position
            grid_size = len(frame_sequences[0]) if frame_sequences else 0
            cell_sequences = [[] for _ in range(grid_size)]
            
            for frame_sequence in frame_sequences:
                for cell_idx, cell in enumerate(frame_sequence):
                    if cell_idx < len(cell_sequences):
                        cell_sequences[cell_idx].append(cell)
            
            saved_files = []
            
            logger.info(f"Creating {grid_size} animated emojis from {len(frame_sequences)} frames")
            
            for cell_idx, cell_frames in enumerate(cell_sequences):
                if not cell_frames:
                    continue
                
                # Create GIF-like sequence (save as individual frames for now)
                # In a full implementation, you might use a GIF library or WebM
                cell_dir = output_dir / f"{safe_pack_name}_cell_{cell_idx+1:03d}"
                cell_dir.mkdir(exist_ok=True)
                
                cell_files = []
                for frame_idx, frame in enumerate(cell_frames):
                    frame_filename = f"frame_{frame_idx:03d}.png"
                    frame_path = cell_dir / frame_filename
                    
                    optimized_frame = self.optimize_emoji_size(frame)
                    self.image_processor.save_image(optimized_frame, frame_path)
                    cell_files.append(frame_path)
                
                saved_files.extend(cell_files)
                
                if progress_tracker:
                    progress_tracker.update(1, f"Generated animated emoji {cell_idx+1}/{grid_size}")
            
            logger.info(f"Successfully created animated emoji sequence with {len(saved_files)} frames")
            return saved_files
            
        except Exception as e:
            raise ImageProcessingError(f"Failed to create animated emoji sequence: {e}")
    
    def _create_pack_metadata(
        self, 
        emoji_files: List[Path], 
        pack_name: str, 
        user_id: int, 
        metadata_path: Path
    ):
        """Create metadata file for emoji pack"""
        try:
            metadata = {
                "pack_name": pack_name,
                "user_id": user_id,
                "emoji_count": len(emoji_files),
                "emoji_files": [str(f.name) for f in emoji_files],
                "created_at": int(time.time()),
                "format": "static_png",
                "size": "512x512"
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to create pack metadata: {e}")
    
    def create_pack_archive(
        self, 
        emoji_files: List[Path], 
        pack_name: str, 
        output_path: Path
    ) -> Path:
        """
        Create ZIP archive of emoji pack
        
        Args:
            emoji_files: List of emoji file paths
            pack_name: Name of the pack
            output_path: Path for output ZIP file
            
        Returns:
            Path to created ZIP file
        """
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for emoji_file in emoji_files:
                    if emoji_file.exists():
                        zipf.write(emoji_file, emoji_file.name)
                
                # Add README
                readme_content = f"""
# {pack_name} Emoji Pack

This pack contains {len(emoji_files)} emoji images.

## Usage
Extract the PNG files and upload them to Telegram as stickers.

## Files
{chr(10).join([f"- {f.name}" for f in emoji_files])}
"""
                zipf.writestr("README.txt", readme_content)
            
            logger.info(f"Created emoji pack archive: {output_path}")
            return output_path
            
        except Exception as e:
            # Clean up partially created archive file
            if 'output_path' in locals() and output_path.exists():
                try:
                    output_path.unlink()
                    logger.debug(f"Cleaned up partially created archive: {output_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup partial archive: {cleanup_error}")
            
            raise ImageProcessingError(f"Failed to create pack archive: {e}")