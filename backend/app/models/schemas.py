from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

CefrLevel = Literal["A1", "A2", "B1", "B2"]
LangCode = Literal["ru", "ja"]
FeedbackRating = Literal["too_easy", "too_hard", "just_right"]
GENRES = ("daily_life", "travel", "news", "folklore", "work")


class GenerateRequest(BaseModel):
    level: CefrLevel
    topic: str = Field(..., min_length=1, max_length=200)
    genre: str | None = Field(default=None, max_length=40)
    language: LangCode = "ja"


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
    series_id: str | None = None
    chapter_index: int | None = None
    has_audio: bool = False
    new_lemma_pct: float = 0.0


class StarredWord(BaseModel):
    lemma: str
    gloss: str | None = None
    passage_id: str | None = None
    title: str | None = None
    language: LangCode


class StarRequest(BaseModel):
    lemma: str = Field(..., min_length=1, max_length=120)
    gloss: str | None = Field(default=None, max_length=200)
    passage_id: str | None = None
    language: LangCode | None = None


class UnstarRequest(BaseModel):
    lemma: str = Field(..., min_length=1, max_length=120)
    language: LangCode


class LibraryResponse(BaseModel):
    language: LangCode
    placement: CefrLevel
    next_id: str | None = None
    seen_lemmas: int = 0
    items: list[LibraryItem]
    words: list[StarredWord] = []


class PassageStats(BaseModel):
    passage_id: str
    language: LangCode
    placement: CefrLevel
    read: bool = False
    new_lemmas: int = 0
    recycled_lemmas: int = 0
    next_id: str | None = None
    known_lemmas: list[str] = []
    starred_lemmas: list[str] = []


class KanjiPart(BaseModel):
    char: str
    reading: str | None = None
    on: list[str] = []
    kun: list[str] = []
    meaning: str = ""
    strokes: int | None = None
    jlpt: int | None = None
    grade: int | None = None
    freq: int | None = None
    radical: str | None = None
    radical_name: str | None = None
    parts: list[str] = []
    nanori: list[str] = []


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
    pos_detail: str | None = None
    conj_type: str | None = None


class ConjPiece(BaseModel):
    text: str
    label: str


class Token(BaseModel):
    text: str
    ws: str = " "
    is_word: bool = True
    lemma: str | None = None
    morph: MorphInfo | None = None
    gloss: str | None = None
    level: str | None = None
    kanji: list[KanjiPart] = []
    role: str | None = None
    conj: list[ConjPiece] = []
    conj_id: int | None = None


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
    allowed_constructions: list[str] = []
    forbidden_used: list[str] = []
    banned_constructions: list[str] = []
    sample_lemmas: list[str] = []


class AudioCue(BaseModel):
    index: int
    start_ms: int
    end_ms: int
    text: str


class ComprehensionChoice(BaseModel):
    id: str
    text: str


class ComprehensionQuestion(BaseModel):
    id: str
    prompt: str
    choices: list[str]
    answer_index: int


class PassageResponse(BaseModel):
    id: str
    language: LangCode = "ja"
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
    shelf_status: str = "public"
    audio_url: str | None = None
    audio_cues: list[AudioCue] = []
    series_id: str | None = None
    chapter_index: int | None = None
    comprehension: list[ComprehensionQuestion] = []


class GlossResponse(BaseModel):
    word: str
    lemma: str
    morph: MorphInfo
    gloss: str | None
    level: str | None
    kanji: list[KanjiPart] = []
    role: str | None = None
    conj: list[ConjPiece] = []


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


class MeResponse(BaseModel):
    authenticated: bool
    user_id: int | None = None
    email: str | None = None
    display_name: str | None = None
    guest: bool = True
    show_russian: bool = False
    generate_remaining: int | None = None
    require_auth: bool = False


class MagicLinkRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=320)


class ReviewCard(BaseModel):
    id: int
    lemma: str
    gloss: str | None = None
    reading: str | None = None
    context: str | None = None
    language: LangCode
    due_at: datetime


class ReviewSubmit(BaseModel):
    card_id: int
    rating: Literal["again", "hard", "good", "easy"]


class ComprehensionSubmit(BaseModel):
    passage_id: str
    answers: list[int]


class TrialEventRequest(BaseModel):
    kind: str = Field(..., min_length=1, max_length=40)
    passage_id: str | None = None
    payload: dict | None = None
