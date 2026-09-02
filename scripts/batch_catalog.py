#!/usr/bin/env python3
"""Batch-generate Japanese catalog passages via the live LLM loop.

Usage (from repo root, with OPENROUTER_API_KEY set):

    PYTHONPATH=backend python scripts/batch_catalog.py --count 20 --level A2

Failed calibrations are quarantined and never seeded to the public shelf.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.models.db import SessionLocal, init_db  # noqa: E402
from app.services.generate import generate_passage  # noqa: E402
from app.services.tts import synthesize_passage  # noqa: E402
from app.models.db import PassageRow  # noqa: E402
import json  # noqa: E402

TOPICS = [
    ("a quiet kitchen", "daily_life"),
    ("the last train", "travel"),
    ("a small festival", "folklore"),
    ("Monday at the office", "work"),
    ("rain in the city", "news"),
    ("a letter from home", "daily_life"),
    ("buying fruit", "daily_life"),
    ("a walk by the river", "travel"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--level", default="A2", choices=["A1", "A2", "B1", "B2"])
    parser.add_argument("--language", default="ja")
    parser.add_argument("--audio", action="store_true")
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    passed = 0
    quarantined = 0
    try:
        for i in range(args.count):
            topic, genre = TOPICS[i % len(TOPICS)]
            topic = f"{topic} ({i + 1})"
            result = generate_passage(db, args.level, topic, genre, args.language)
            if result.calibration.passed:
                passed += 1
                print(f"OK  {result.level} {result.title}")
                if args.audio:
                    row = db.get(PassageRow, result.id)
                    if row is not None:
                        synth = synthesize_passage(row)
                        if synth:
                            url, cues = synth
                            row.audio_url = url
                            row.audio_cues_json = json.dumps(cues, ensure_ascii=False)
                            db.commit()
            else:
                quarantined += 1
                print(f"QUARANTINE  {result.title} flags={result.calibration.flags[:4]}")
    finally:
        db.close()
    print(f"passed={passed} quarantined={quarantined}")


if __name__ == "__main__":
    main()
