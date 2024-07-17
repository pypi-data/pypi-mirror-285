from pydantic import BaseModel


class ClipInterface(BaseModel):
    """Interface that describes a clip"""

    id: int
    url: str
    duration: int
    # Represents the transcript of the non-extended clip
    transcript: str
    # TODO: Deprecate after the trimmer feature
    transcription: str

    # Represents the start and end time of the clip relative to the extended clip
    start: float
    end: float

    def to_json(self):
        return {
            "id": self.id,
            "transcript": self.transcript,
            "transcription": self.transcription,
            "url": self.url,
            "duration": self.duration,
            "start": self.start,
            "end": self.end,
        }
