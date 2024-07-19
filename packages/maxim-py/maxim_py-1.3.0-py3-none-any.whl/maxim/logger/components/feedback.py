from dataclasses import dataclass


@dataclass
class Feedback():
    score: int
    comment: str