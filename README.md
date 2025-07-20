# Telegram Emoji Pack Bot - Technical Documentation

## Project Overview

A Telegram bot that converts user-uploaded images and videos into custom emoji packs with configurable grid dimensions using Python, OpenCV, and NumPy for advanced image/video processing.

## Core Features

- **Image Processing**: Convert static images to emoji grids with OpenCV
- **Video Processing**: Extract frames from videos and convert to emoji sequences
- **Custom Grid Size**: Completely flexible dimensions (any x×y combination)
- **Smart Image Adaptation**: Automatic image reshaping to match target grid ratio
- **Aspect Ratio Handling**: Intelligent padding, stretching, or cropping options
- **Advanced Processing**: OpenCV-powered image enhancement and manipulation
- **Emoji Pack Generation**: Telegram-compliant emoji stickers

## Technology Stack

**Package Manager:**
- `uv` - Ultra-fast Python package installer and resolver

**Core Libraries:**
- `aiogram 3.13.1` - Latest Telegram Bot API 7.10 framework
- `opencv-python` - Advanced image/video processing
- `numpy` - Numerical operations and array handling
- `scikit-image` - Additional image processing algorithms
- `aiofiles` - Asynchronous file operations

**Installation:**
```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv add aiogram==3.13.1
uv add opencv-python
uv add numpy
uv add scikit-image
uv add aiofiles
```

**pyproject.toml:**
```toml
[project]
name = "telegram-emoji-bot"
version = "1.0.0"
description = "Telegram bot for converting images and videos to emoji packs"
requires-python = ">=3.11"
dependencies = [
    "aiogram==3.13.1",
    "opencv-python>=4.8.0",
    "numpy>=1.24.0",
    "scikit-image>=0.21.0",
    "aiofiles>=23.0.0"
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0"
]
```

## Project Structure

```
telegram_emoji_bot/
├── main.py                          # Bot entry point
├── config.py                        # Configuration settings
├── requirements.txt
├── data/
│   ├── __init__.py
│   └── cache/                       # Temporary file storage
│       ├── __init__.py
│       ├── images/                  # Cached processed images
│       └── videos/                  # Cached processed videos
├── exceptions/
│   ├── __init__.py
│   ├── base.py                      # Base exception classes
│   ├── processing.py                # Image/video processing exceptions
│   └── validation.py                # Input validation exceptions
├── filters/
│   ├── __init__.py
│   ├── media.py                     # Media type filters
│   └── user.py                      # User permission filters
├── handlers/
│   └── user/
│       ├── __init__.py
│       ├── start.py                 # /start command handler
│       ├── help.py                  # /help command handler
│       ├── settings.py              # Grid size configuration
│       ├── image.py                 # Image processing handler
│       └── video.py                 # Video processing handler
├── keyboards/
│   ├── __init__.py
│   ├── default/
│   │   ├── __init__.py
│   │   └── main_menu.py             # Main menu keyboard
│   ├── inline/
│   │   └── user/
│   │       ├── __init__.py
│   │       ├── grid_size.py         # Grid size selection
│   │       ├── processing.py        # Processing confirmation
│   │       └── settings.py          # Settings keyboard
│   └── keyboard_utils/
│       ├── __init__.py
│       └── builders.py              # Keyboard builder utilities
├── middlewares/
│   ├── __init__.py
│   ├── throttling.py                # Rate limiting middleware
│   └── logging.py                   # Logging middleware
├── models/
│   ├── __init__.py
│   ├── user.py                      # User model/dataclass
│   └── processing_task.py           # Processing task model
├── states/
│   ├── __init__.py
│   └── user_states.py               # FSM states for user interactions
└── utils/
    ├── __init__.py
    ├── image_processor.py           # Core image processing logic
    ├── video_processor.py           # Core video processing logic
    ├── emoji_generator.py           # Emoji pack creation
    ├── file_manager.py              # File download/upload handling
    ├── validation.py                # Input validation utilities
    └── helpers.py                   # General helper functions
```

## Bot API Features

### Telegram Bot API 7.10 Support
- **Sticker Management**: Full support for sticker pack creation and management
- **Large File Uploads**: Support for files up to 50MB
- **Inline Keyboards**: Advanced keyboard layouts with callback data
- **Message Reactions**: Optional emoji reactions for user feedback
- **Background Type**: Support for background removal in stickers

## Core Components

### Image Processing (`utils/image_processor.py`)

**Key Functions:**
- `adapt_image_to_grid(image: np.ndarray, grid_x: int, grid_y: int, method: str) -> np.ndarray` - Reshape image to match grid aspect ratio
- `calculate_target_dimensions(grid_x: int, grid_y: int, base_size: int = 512) -> Tuple[int, int]` - Calculate optimal image dimensions
- `split_image_grid(image: np.ndarray, grid_x: int, grid_y: int) -> List[np.ndarray]` - Grid-based image splitting
- `resize_for_emoji(image: np.ndarray) -> np.ndarray` - Resize to 512×512 for Telegram compliance
- `apply_padding(image: np.ndarray, target_ratio: float, fill_color: Tuple[int, int, int]) -> np.ndarray` - Smart padding with color fill
- `apply_stretching(image: np.ndarray, target_ratio: float) -> np.ndarray` - Non-uniform scaling
- `apply_crop_center(image: np.ndarray, target_ratio: float) -> np.ndarray` - Center-focused cropping

**Aspect Ratio Adaptation Methods:**
```python
def adapt_image_to_grid(image: np.ndarray, grid_x: int, grid_y: int, method: str = "pad") -> np.ndarray:
    """
    Adapt image aspect ratio to match grid dimensions
    
    Args:
        image: Input image as numpy array
        grid_x: Number of columns in grid
        grid_y: Number of rows in grid
        method: Adaptation method - "pad", "stretch", "crop"
    
    Returns:
        Adapted image matching grid aspect ratio
    """
    current_height, current_width = image.shape[:2]
    current_ratio = current_width / current_height
    target_ratio = grid_x / grid_y
    
    if method == "pad":
        return apply_padding(image, target_ratio)
    elif method == "stretch":
        return apply_stretching(image, target_ratio)
    elif method == "crop":
        return apply_crop_center(image, target_ratio)
    else:
        raise ValueError(f"Unknown adaptation method: {method}")

def apply_padding(image: np.ndarray, target_ratio: float, fill_color: Tuple[int, int, int] = (255, 255, 255)) -> np.ndarray:
    """Smart padding to achieve target aspect ratio"""
    height, width = image.shape[:2]
    current_ratio = width / height
    
    if current_ratio < target_ratio:
        # Need to widen image
        new_width = int(height * target_ratio)
        padding_width = (new_width - width) // 2
        padded = cv2.copyMakeBorder(
            image, 0, 0, padding_width, padding_width,
            cv2.BORDER_CONSTANT, value=fill_color
        )
    else:
        # Need to heighten image
        new_height = int(width / target_ratio)
        padding_height = (new_height - height) // 2
        padded = cv2.copyMakeBorder(
            image, padding_height, padding_height, 0, 0,
            cv2.BORDER_CONSTANT, value=fill_color
        )
    
    return padded

def apply_stretching(image: np.ndarray, target_ratio: float) -> np.ndarray:
    """Non-uniform scaling to match target ratio"""
    height, width = image.shape[:2]
    new_width = int(height * target_ratio)
    return cv2.resize(image, (new_width, height), interpolation=cv2.INTER_LANCZOS4)
```

**OpenCV Operations:**
```python
import cv2
import numpy as np

# Image enhancement
cv2.GaussianBlur()          # Noise reduction
cv2.bilateralFilter()       # Edge-preserving smoothing
cv2.equalizeHist()          # Histogram equalization
cv2.createCLAHE()           # Adaptive histogram equalization

# Resizing with interpolation
cv2.INTER_LANCZOS4          # High-quality downscaling
cv2.INTER_CUBIC             # Smooth interpolation
```

### Video Processing (`utils/video_processor.py`)

**Key Functions:**
- `extract_frames(video_path: str, frame_count: int) -> List[np.ndarray]` - Smart frame extraction
- `process_video_sequence(frames: List[np.ndarray], grid_size: Tuple[int, int]) -> List[List[np.ndarray]]` - Process video frames
- `detect_scene_changes(frames: List[np.ndarray]) -> List[int]` - Scene change detection

**OpenCV Video Operations:**
```python
import cv2

# Video capture and frame extraction
cv2.VideoCapture()          # Video file reading
cv2.CAP_PROP_FRAME_COUNT    # Total frame count
cv2.CAP_PROP_FPS            # Frames per second
cv2.absdiff()               # Frame difference for scene detection
```

### Emoji Generation (`utils/emoji_generator.py`)

**Functions:**
- `create_emoji_pack(images: List[np.ndarray], pack_name: str) -> str` - Generate Telegram sticker pack
- `optimize_emoji_size(image: np.ndarray) -> np.ndarray` - Size optimization
- `add_transparency(image: np.ndarray) -> np.ndarray` - Background removal

### File Management (`utils/file_manager.py`)

**Asynchronous Operations:**
- `download_media(file_info: Dict) -> str` - Download files from Telegram
- `cleanup_cache()` - Automatic temporary file cleanup
- `validate_file_size(file_path: str) -> bool` - File size validation

## Image Processing Workflow

### Flexible Grid Processing Pipeline
1. **Input Validation**: File format, size, and type checking
2. **Image Loading**: Load with OpenCV (`cv2.imread()`)
3. **Grid Analysis**: Analyze target grid dimensions (x×y)
4. **Aspect Ratio Calculation**: Compare image ratio vs grid ratio
5. **Image Adaptation**: Apply selected adaptation method:
   - **Padding**: Add borders to match ratio (preserves all content)
   - **Stretching**: Non-uniform scaling (may distort content)
   - **Cropping**: Center crop to match ratio (may lose content)
6. **Preprocessing**: 
   - Noise reduction with Gaussian blur
   - Contrast enhancement with CLAHE
   - Color space conversion if needed
7. **Grid Splitting**: Divide adapted image into grid cells using NumPy slicing
8. **Cell Processing**: Resize each cell to 512×512 with high-quality interpolation
9. **Emoji Formatting**: Convert to PNG with optional transparency
10. **Pack Generation**: Create Telegram-compatible sticker pack

### Grid Adaptation Examples
```python
# Example: Square image (1000×1000) → 1×3 grid
original_ratio = 1000/1000 = 1.0
target_ratio = 1/3 = 0.33

# Method 1: Padding (recommended)
# Result: 333×1000 image with white borders on sides
adapted_image = apply_padding(image, 0.33, fill_color=(255, 255, 255))

# Method 2: Stretching 
# Result: 333×1000 image (horizontally compressed)
adapted_image = apply_stretching(image, 0.33)

# Method 3: Cropping
# Result: 333×1000 image (sides cropped off)
adapted_image = apply_crop_center(image, 0.33)
```

### Smart Grid Cell Extraction
```python
def split_adapted_image(image: np.ndarray, grid_x: int, grid_y: int) -> List[np.ndarray]:
    """Split adapted image into perfect grid cells"""
    height, width = image.shape[:2]
    
    cell_width = width // grid_x
    cell_height = height // grid_y
    
    cells = []
    for row in range(grid_y):
        for col in range(grid_x):
            y_start = row * cell_height
            y_end = (row + 1) * cell_height
            x_start = col * cell_width
            x_end = (col + 1) * cell_width
            
            cell = image[y_start:y_end, x_start:x_end]
            # Resize to emoji standard
            emoji_cell = cv2.resize(cell, (512, 512), interpolation=cv2.INTER_LANCZOS4)
            cells.append(emoji_cell)
    
    return cells
```

### Advanced Processing Options
- **Edge Enhancement**: Using `cv2.filter2D()` with custom kernels
- **Background Removal**: Using color-based or edge-based segmentation
- **Adaptive Resizing**: Maintaining aspect ratio with padding
- **Quality Optimization**: Smart compression for file size limits

## Video Processing Workflow

### Frame Extraction Strategy
1. **Video Analysis**: Extract video metadata (duration, FPS, resolution)
2. **Smart Sampling**: 
   - Uniform frame extraction for short videos
   - Scene-based extraction for longer videos
   - Key frame detection using motion analysis
3. **Frame Processing**: Apply image processing pipeline to each frame
4. **Sequence Generation**: Create numbered emoji sequence

### Scene Detection Algorithm
```python
def detect_scene_changes(frames, threshold=30):
    scene_frames = []
    for i in range(1, len(frames)):
        diff = cv2.absdiff(frames[i-1], frames[i])
        non_zero_count = np.count_nonzero(diff)
        if non_zero_count > threshold:
            scene_frames.append(i)
    return scene_frames
```

## Configuration

### Environment Variables
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
MAX_GRID_SIZE=8
MIN_GRID_SIZE=2
MAX_FILE_SIZE_MB=50
MAX_VIDEO_DURATION=300
PROCESSING_TIMEOUT=120
CACHE_CLEANUP_INTERVAL=3600
LOG_LEVEL=INFO
```

### Grid Size Constraints
- **Minimum**: 1×1 (single emoji)
- **Maximum**: 20×20 (400 emojis) - limited by processing time and Telegram pack limits
- **Flexible Ratios**: Support any aspect ratio (1×3, 2×5, 7×2, etc.)
- **Common Examples**:
  - **1×3**: Horizontal strip (timeline, progress bar)
  - **3×1**: Vertical strip (tall objects, portraits)
  - **2×5**: Rectangular grid (wide scenes)
  - **4×4**: Square grid (balanced composition)
- **Telegram Limits**: 120 static stickers per pack, 50 animated per pack

### File Format Support
- **Images**: JPEG, PNG, WebP, BMP, TIFF
- **Videos**: MP4, AVI, MOV, WebM, MKV
- **Output**: PNG format for all emojis

## Error Handling

### Custom Exceptions (`exceptions/`)
```python
class ProcessingError(Exception):
    """Base processing exception"""
    
class ImageProcessingError(ProcessingError):
    """Image processing specific errors"""
    
class VideoProcessingError(ProcessingError):
    """Video processing specific errors"""
    
class ValidationError(ProcessingError):
    """Input validation errors"""
```

### Error Types
- **File Format Errors**: Unsupported formats, corrupted files
- **Size Limit Errors**: File too large, duration too long
- **Processing Errors**: OpenCV failures, memory issues
- **Timeout Errors**: Processing takes too long
- **Telegram API Errors**: Upload failures, rate limits

## Performance Optimization

### Memory Management
- **Chunked Processing**: Process large videos in segments
- **Memory Monitoring**: Track memory usage during processing
- **Garbage Collection**: Explicit cleanup of large NumPy arrays
- **Async Processing**: Non-blocking operations with asyncio

### OpenCV Optimizations
```python
# Optimized image resizing
cv2.resize(image, (512, 512), interpolation=cv2.INTER_AREA)

# Memory-efficient operations
image = np.ascontiguousarray(image)  # Optimize memory layout
cv2.setNumThreads(4)  # Control thread usage
```

### Caching Strategy
- **Processed Images**: Cache resized grid cells
- **Video Frames**: Cache extracted frames for reprocessing
- **User Settings**: Cache grid preferences
- **Cleanup Policy**: Automatic cleanup after 1 hour

## Bot Commands

### User Commands
- `/start` - Initialize bot and show welcome message
- `/help` - Display usage instructions and examples
- `/setgrid <x> <y>` - Set flexible grid dimensions (e.g., `/setgrid 1 3`, `/setgrid 4 2`)
- `/adapt <method>` - Set image adaptation method (`pad`, `stretch`, `crop`)
- `/settings` - Show current configuration and preview adaptation methods
- `/examples` - Show example grid layouts and use cases
- `/cancel` - Cancel current processing operation

### Grid Examples
- `/setgrid 1 3` - Create horizontal strip (great for timelines)
- `/setgrid 3 1` - Create vertical strip (perfect for tall subjects)
- `/setgrid 2 5` - Create wide rectangular layout
- `/setgrid 5 2` - Create tall rectangular layout

### Inline Keyboards
- **Grid Size Selection**: Quick selection of common flexible layouts (1×3, 3×1, 2×5, 4×4, etc.)
- **Custom Grid Input**: Inline keyboard for entering any x×y combination
- **Adaptation Method**: Choose between padding, stretching, or cropping
- **Processing Options**: Quality settings, background removal
- **Preview Mode**: Show how image will be adapted before processing

## State Management

### FSM States (`states/user_states.py`)
```python
from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    waiting_for_media = State()
    setting_grid_size_x = State()
    setting_grid_size_y = State()
    choosing_adaptation_method = State()
    previewing_adaptation = State()
    confirming_processing = State()
    processing_media = State()
```