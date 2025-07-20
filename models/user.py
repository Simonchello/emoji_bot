from dataclasses import dataclass
from typing import Optional


@dataclass
class UserSettings:
    user_id: int
    grid_x: int = 2
    grid_y: int = 2
    adaptation_method: str = "pad"
    quality_level: str = "high"
    background_removal: bool = False
    
    def __post_init__(self):
        if self.adaptation_method not in ["pad", "stretch", "crop"]:
            self.adaptation_method = "pad"
        if self.quality_level not in ["low", "medium", "high"]:
            self.quality_level = "high"