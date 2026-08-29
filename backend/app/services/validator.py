from __future__ import annotations

from dataclasses import dataclass, field

from app.models.schemas import Calibration, Token
from app.services.data import grammar_rules, level_rank, vocab_bands

CONTENT_POS = {"NOUN", "ADJF", "ADJS", "VERB", "INFN", "ADVB", "PRED", "NUMR"}
SUBORDINATE_LEMMAS = {
    "чтобы",
    "хотя",
    "если",
    "который",
    "потому",
    "когда",
}


@dataclass
class ValidationResult:
    passed: bool
    overlevel_lemma_rate: float
    subordinate_rate: float
    forbidden_case_rate: float
    forbidden_tense_rate: float
    forbidden_pos_rate: float
    flags: list[str] = field(default_factory=list)

    def to_calibration(self, attempts: int, warnings: list[str] | None = None) -> Calibration:
        return Calibration(
            passed=self.passed,
            attempts=attempts,
            overlevel_lemma_rate=self.overlevel_lemma_rate,
            subordinate_rate=self.subordinate_rate,
            forbidden_case_rate=self.forbidden_case_rate,
            forbidden_tense_rate=self.forbidden_tense_rate,
            forbidden_pos_rate=self.forbidden_pos_rate,
            flags=self.flags,
            warnings=warnings or [],
        )

    @property
    def severity(self) -> float:
        """Lower is better. Used to pick the less-bad attempt."""
        return (
            len(self.flags)
            + self.overlevel_lemma_rate * 10
            + self.forbidden_case_rate * 20
            + self.forbidden_tense_rate * 20
            + self.forbidden_pos_rate * 30
            + self.subordinate_rate * 8
        )


def _is_sentence_initial(tokens: list[Token], index: int) -> bool:
    for t in reversed(tokens[:index]):
        if not t.is_word:
            if t.text in ".!?…":
                return True
            continue
        return False
    return True


def validate_tokens(tokens: list[Token], level: str, language: str = "ru") -> ValidationResult:
    if language == "ja":
        from app.services.validator_ja import validate_tokens_ja

        return validate_tokens_ja(tokens, level)

    ruleset = grammar_rules(language)
    rules = ruleset[level]
    allowed_cases = set(rules["allowed_cases"])
    allowed_tenses = set(rules["allowed_tenses"])
    forbidden_pos = set(rules["forbidden_pos"])
    forbidden_conjunctions = set(rules["forbidden_conjunctions"])
    bands = vocab_bands(language)
    cap = level_rank(level)

    word_tokens = [t for t in tokens if t.is_word and t.morph]
    n = max(len(word_tokens), 1)

    case_hits = 0
    tense_hits = 0
    pos_hits = 0
    sub_hits = 0
    conj_hits = 0
    overlevel = 0
    content_n = 0
    flags: list[str] = []

    seen: set[str] = set()

    def flag(msg: str) -> None:
        if msg not in seen:
            seen.add(msg)
            flags.append(msg)

    for i, tok in enumerate(tokens):
        if not tok.is_word or not tok.morph:
            continue
        m = tok.morph
        lemma = m.lemma

        if m.case and m.case not in allowed_cases:
            case_hits += 1
            flag(f"case:{m.case} ({tok.text})")

        if m.tense and m.tense not in allowed_tenses:
            tense_hits += 1
            flag(f"tense:{m.tense} ({tok.text})")

        if m.pos and m.pos in forbidden_pos:
            pos_hits += 1
            flag(f"pos:{m.pos} ({tok.text})")

        if lemma in SUBORDINATE_LEMMAS:
            if lemma == "когда" and _is_sentence_initial(tokens, i):
                pass
            else:
                sub_hits += 1

        if lemma in forbidden_conjunctions:
            if lemma == "когда" and _is_sentence_initial(tokens, i):
                pass
            else:
                conj_hits += 1
                flag(f"conj:{lemma}")

        if m.pos in CONTENT_POS:
            content_n += 1
            band = bands.get(lemma)
            if band is None or level_rank(band) > cap:
                # Skip likely proper names
                if tok.text[:1].isupper() and not _is_sentence_initial(tokens, i):
                    continue
                if m.pos == "NOUN" and tok.text[:1].isupper():
                    continue
                overlevel += 1
                if band:
                    flag(f"lemma:{lemma}={band}")
                else:
                    flag(f"lemma:{lemma}=unknown")

    case_rate = case_hits / n
    tense_rate = tense_hits / n
    pos_rate = pos_hits / n
    sub_rate = sub_hits / n
    over_rate = overlevel / max(content_n, 1)

    # Cap lemma flags so the LLM correction prompt stays readable
    lemma_flags = [f for f in flags if f.startswith("lemma:")]
    other_flags = [f for f in flags if not f.startswith("lemma:")]
    flags = other_flags + lemma_flags[:12]

    passed = (
        case_rate <= rules["max_forbidden_case_rate"]
        and tense_rate <= rules["max_forbidden_tense_rate"]
        and pos_rate <= rules["max_forbidden_pos_rate"]
        and sub_rate <= rules["max_subordinate_rate"]
        and over_rate <= rules["max_overlevel_lemma_rate"]
        and conj_hits == 0
    )

    return ValidationResult(
        passed=passed,
        overlevel_lemma_rate=round(over_rate, 4),
        subordinate_rate=round(sub_rate, 4),
        forbidden_case_rate=round(case_rate, 4),
        forbidden_tense_rate=round(tense_rate, 4),
        forbidden_pos_rate=round(pos_rate, 4),
        flags=flags,
    )
