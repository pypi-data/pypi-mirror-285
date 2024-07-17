from enum import Enum
from typing import Optional
from pydantic import BaseModel


class AnimationType(Enum):
    """The type of animation to use for the subtitles."""

    SIMPLE = "SIMPLE"
    KARAOKE = "KARAOKE"


class SubtitleSettings(BaseModel):
    font: str = "DejaVu Serif"
    font_size: int = 20
    font_primary_color: str = "#ffffff"

    animation_type: Optional[AnimationType] = None

    font_background_color: str = "#000000"
    highlight_font_color: str = "#ffffff"

    def to_json(self):
        return {
            "font": self.font,
            "font_size": self.font_size,
            "font_primary_color": self.font_primary_color,
            "animation_type": (
                self.animation_type.value if self.animation_type else None
            ),
            "font_background_color": self.font_background_color,
            "highlight_font_color": self.highlight_font_color,
        }

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, SubtitleSettings):
            return False

        return (
            self.font == value.font
            and self.font_size == value.font_size
            and self.font_primary_color == value.font_primary_color
            and self.animation_type == value.animation_type
            and self.font_background_color == value.font_background_color
        )
