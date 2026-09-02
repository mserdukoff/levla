from __future__ import annotations

from app.models.schemas import Calibration, Token
from app.services.data import grammar_rules

ALL_JA_CONSTRUCTIONS = [
    "te_form",
    "plain_past",
    "plain_neg",
    "te_iru",
    "conditional",
    "potential",
    "causative",
    "passive",
    "relative",
    "keigo",
]

CONSTRUCTION_LABELS = {
    "te_form": "て-form",
    "plain_past": "plain past た",
    "plain_neg": "plain negative ない",
    "te_iru": "ている aspect",
    "conditional": "conditionals ば/たら/なら",
    "potential": "potential",
    "causative": "causative",
    "passive": "passive",
    "relative": "relative clauses",
    "keigo": "keigo",
}

RU_CASE_LABELS = {
    "nom": "nominative",
    "gen": "genitive",
    "dat": "dative",
    "acc": "accusative",
    "ins": "instrumental",
    "prep": "prepositional",
}


def construction_label(key: str) -> str:
    return CONSTRUCTION_LABELS.get(key, key.replace("_", " "))


def forbidden_used_from_flags(flags: list[str]) -> list[str]:
    used: list[str] = []
    seen: set[str] = set()
    for flag in flags:
        key = None
        if flag.startswith("ja:"):
            key = flag[3:].split(" ", 1)[0]
        elif flag.startswith("case:"):
            key = "case:" + flag[5:].split(" ", 1)[0]
        elif flag.startswith("tense:"):
            key = "tense:" + flag[6:].split(" ", 1)[0]
        elif flag.startswith("pos:"):
            key = "pos:" + flag[4:].split(" ", 1)[0]
        if key and key not in seen:
            seen.add(key)
            used.append(key)
    return used


def sample_content_lemmas(tokens: list[Token], language: str, n: int = 8) -> list[str]:
    from app.services.learner import unique_content_lemmas

    return unique_content_lemmas(tokens, language)[:n]


def attach_passport(
    calibration: Calibration,
    *,
    language: str,
    level: str,
    tokens: list[Token],
) -> Calibration:
    ruleset = grammar_rules(language)
    rules = ruleset.get(level) or {}
    if language == "ja":
        banned = list(rules.get("forbidden_constructions") or [])
        allowed = [c for c in ALL_JA_CONSTRUCTIONS if c not in banned]
        labels = [construction_label(c) for c in allowed]
        if not labels:
            labels = ["です/ます polite style", "core particles は が を に の"]
        calibration.allowed_constructions = labels
        calibration.banned_constructions = [construction_label(c) for c in banned]
    else:
        allowed_cases = [RU_CASE_LABELS.get(c, c) for c in rules.get("allowed_cases") or []]
        calibration.allowed_constructions = allowed_cases
        forbidden_pos = list(rules.get("forbidden_pos") or [])
        calibration.banned_constructions = forbidden_pos
    calibration.forbidden_used = forbidden_used_from_flags(calibration.flags)
    calibration.sample_lemmas = sample_content_lemmas(tokens, language)
    return calibration
