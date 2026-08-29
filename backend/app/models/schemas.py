from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

CefrLevel = Literal["A1", "A2", "B1", "B2"]
LangCode = Literal["ru", "ja"]
FeedbackRating = Literal["too_easy", "too_hard"]
GENRES = ("daily_life", "travel", "news", "folklore", "work")


class GenerateRequest(BaseModel):
    level: CefrLevel
    topic: str = Field(..., min_length=1, max_length=200)
    genre: str | None = Field(default=None, max_length=40)
    language: LangCode = "ru"


class GlossRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=80)
    passage_id: str | None = None


class FeedbackRequest(BaseModel):
    passage_id: str
    rating: FeedbackRating


class LibraryItem(BaseModel):
    id: str
    language: LangCode
    level: CefrLevel
    topic: str
    genre: str | None
    title: str
    word_count: int
    created_at: datetime
    passed: bool
    read: bool = False
    recommended: bool = False
    new_lemmas: int = 0
    recycled_lemmas: int = 0


class LibraryResponse(BaseModel):
    language: LangCode
    placement: CefrLevel
    next_id: str | None = None
    seen_lemmas: int = 0
    items: list[LibraryItem]


class PassageStats(BaseModel):
    passage_id: str
    language: LangCode
    placement: CefrLevel
    read: bool = False
    new_lemmas: int = 0
    recycled_lemmas: int = 0
    next_id: str | None = None


class KanjiPart(BaseModel):
    char: str
    reading: str | None = None
    on: list[str] = []
    kun: list[str] = []
    meaning: str = ""


class MorphInfo(BaseModel):
    lemma: str
    pos: str | None = None
    case: str | None = None
    gender: str | None = None
    number: str | None = None
    tense: str | None = None
    aspect: str | None = None
    mood: str | None = None
    reading: str | None = None
    form: str | None = None


class Token(BaseModel):
    text: str
    ws: str = " "
    is_word: bool = True
    lemma: str | None = None
    morph: MorphInfo | None = None
    gloss: str | None = None
    level: str | None = None
    kanji: list[KanjiPart] = []


class Calibration(BaseModel):
    passed: bool
    attempts: int
    overlevel_lemma_rate: float
    subordinate_rate: float
    forbidden_case_rate: float
    forbidden_tense_rate: float
    forbidden_pos_rate: float
    flags: list[str]
    warnings: list[str]


class PassageResponse(BaseModel):
    id: str
    language: LangCode = "ru"
    level: CefrLevel
    topic: str
    genre: str | None
    title: str
    text: str
    tokens: list[Token]
    calibration: Calibration
    word_count: int
    created_at: datetime
    translation: str | None = None


class GlossResponse(BaseModel):
    word: str
    lemma: str
    morph: MorphInfo
    gloss: str | None
    level: str | None
    kanji: list[KanjiPart] = []


class TranslationResponse(BaseModel):
    passage_id: str
    translation: str


class FeedbackResponse(BaseModel):
    ok: bool
    passage_id: str
    rating: FeedbackRating
    placement: CefrLevel | None = None
    next_id: str | None = None
    new_lemmas: int = 0
    recycled_lemmas: int = 0
