from . import start, help, settings, image, video

def setup_user_handlers(dp):
    """Setup all user handlers"""
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(settings.router)
    dp.include_router(image.router)
    dp.include_router(video.router)