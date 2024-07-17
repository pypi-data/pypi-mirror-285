from enum import Enum


class ClipDuration(Enum):
    """Duration options for the duration of a clip."""

    UNDER_30 = "UNDER_30"
    BETWEEN_30_AND_60 = "BETWEEN_30_AND_60"
    BETWEEN_60_AND_90 = "BETWEEN_60_AND_90"
    BETWEEN_90_AND_180 = "BETWEEN_90_AND_180"

    @staticmethod
    def is_within_range(clip_duration: "ClipDuration", duration: int) -> bool:
        """Check if the duration is within the range of this enum.
        Args:
            clip_duration (ClipDuration): The enum to check against.
            duration (int): The duration to check.
        Returns:
            bool: True if the duration is within the range, False otherwise.
        """

        match clip_duration:
            case ClipDuration.UNDER_30:
                return duration < 30
            case ClipDuration.BETWEEN_30_AND_60:
                return 30 <= duration <= 60
            case ClipDuration.BETWEEN_60_AND_90:
                return 60 <= duration <= 90
            case ClipDuration.BETWEEN_90_AND_180:
                return 90 <= duration <= 180

        raise ValueError(f"Invalid ClipDuration enum value: {clip_duration}")

    @staticmethod
    def is_over_range(clip_duration: "ClipDuration", duration: int) -> bool:
        """Check if the duration is over the range of this enum.
        Args:
            clip_duration (ClipDuration): The enum to check against.
            duration (int): The duration to check.
        Returns:
            bool: True if the duration is over the range, False otherwise.
        """

        match clip_duration:
            case ClipDuration.UNDER_30:
                return duration > 30
            case ClipDuration.BETWEEN_30_AND_60:
                return duration > 60
            case ClipDuration.BETWEEN_60_AND_90:
                return duration > 90
            case ClipDuration.BETWEEN_90_AND_180:
                return duration > 180
