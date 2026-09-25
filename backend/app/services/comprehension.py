"""Questions about a passage, built from its English translation.

The choices are a sentence or a word that actually occurs in that translation.
"""

from __future__ import annotations

import hashlib
import re

_SENTENCE = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[A-Za-z][A-Za-z']{3,}")


def _rotate(choices: list[str], answer: str, seed: str) -> tuple[list[str], int]:
    unique: list[str] = []
    for choice in choices:
        text = choice.strip()
        if text and text not in unique:
            unique.append(text)
    if answer not in unique:
        unique.insert(0, answer)
    if len(unique) < 2:
        return unique, 0
    shift = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % len(unique)
    rotated = unique[shift:] + unique[:shift]
    return rotated, rotated.index(answer)


def questions_from_english(translation: str, topic: str = "") -> list[dict]:
    sentences = [
        s.strip()
        for s in _SENTENCE.split((translation or "").strip())
        if len(s.strip()) > 12
    ]
    if not sentences and topic.strip():
        sentences = [topic.strip()]
    if not sentences:
        return []

    questions: list[dict] = []
    words = _WORD.findall(sentences[0])
    if words:
        target = words[-1]
        blanked = re.sub(rf"\b{re.escape(target)}\b", "___", sentences[0], count=1)
        pool = [
            w
            for w in _WORD.findall(" ".join(sentences))
            if w.lower() != target.lower()
        ]
        choices = [target]
        for word in pool:
            if word not in choices:
                choices.append(word)
            if len(choices) == 3:
                break
        for filler in ("morning", "station", "water"):
            if len(choices) >= 3:
                break
            if filler.lower() != target.lower() and filler not in choices:
                choices.append(filler)
        rotated, index = _rotate(choices, target, blanked)
        questions.append(
            {
                "id": "q1",
                "prompt": blanked,
                "choices": rotated,
                "answer_index": index,
            }
        )

    happened = sentences[1] if len(sentences) > 1 else sentences[0]
    happened_choices, happened_index = _rotate(
        [
            happened,
            "Someone flies to the moon.",
            "The text is a recipe.",
        ],
        happened,
        happened,
    )
    questions.append(
        {
            "id": "q2",
            "prompt": "Which of these happens in the passage?",
            "choices": happened_choices,
            "answer_index": happened_index,
        }
    )

    if len(sentences) > 2:
        extra = sentences[2]
        extra_choices, extra_index = _rotate(
            [
                extra,
                "The shops stay closed for a year.",
                "Nobody leaves the house.",
            ],
            extra,
            extra,
        )
        questions.append(
            {
                "id": "q3",
                "prompt": "What else does the passage say?",
                "choices": extra_choices,
                "answer_index": extra_index,
            }
        )
    return questions[:3]


def stale_comprehension(raw: str | None) -> bool:
    if not raw:
        return True
    return "too hard" in raw or "What is the title" in raw
