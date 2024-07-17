from fastclip.schemas.AbstractTranscriptComponent import (
    AbstractTranscriptComponent,
)


class Word(AbstractTranscriptComponent):
    """Represents a word in a transcript."""

    word: str
    punctuated_word: str
    start: float
    end: float
    is_keyword: bool = False

    def __eq__(self, other: "Word"):
        if not isinstance(other, Word):
            return False

        return (
            self.word == other.word
            and self.punctuated_word == other.punctuated_word
            and self.start == other.start
            and self.end == other.end
        )

    def __repr__(self):
        return f"Word(word='{self.word}', punctuated_word='{self.punctuated_word}', start={self.start}, end={self.end})"

    def to_json(self):
        return {
            "word": self.word,
            "punctuated_word": self.punctuated_word,
            "start": self.start,
            "end": self.end,
            "is_keyword": self.is_keyword,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            word=d["word"],
            punctuated_word=d["punctuated_word"],
            start=d["start"],
            end=d["end"],
            is_keyword=d["is_keyword"] if "is_keyword" in d else False,
        )
