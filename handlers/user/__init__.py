from . import start, help, settings, image, video

def setup_user_handlers(dp):
    """Setup all user handlers"""
    dp.include_router(start.router)
    dp.include_router(help.router)
    # Image and video handlers must be before settings
    # because they have state-specific handlers for start_processing
    # that should be matched before the fallback in settings
    dp.include_router(image.router)
    dp.include_router(video.router)
    dp.include_router(settings.router)
