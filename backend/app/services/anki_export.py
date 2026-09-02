from __future__ import annotations

import csv
import io
import json
import zipfile

from app.services.srs import export_rows
from sqlalchemy.orm import Session

from app.services.identity import Identity


def csv_bytes(db: Session, identity: Identity, language: str) -> bytes:
    rows = export_rows(db, identity, language)
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=["lemma", "reading", "gloss", "context", "language"]
    )
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def apkg_bytes(db: Session, identity: Identity, language: str) -> bytes:
    """A packaged Anki-like zip: CSV + a simple deck note JSON."""
    rows = export_rows(db, identity, language)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        csv_buf = io.StringIO()
        writer = csv.DictWriter(
            csv_buf, fieldnames=["lemma", "reading", "gloss", "context"]
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "lemma": row["lemma"],
                    "reading": row["reading"],
                    "gloss": row["gloss"],
                    "context": row["context"],
                }
            )
        zf.writestr("levla.csv", csv_buf.getvalue())
        notes = [
            {
                "fields": [r["lemma"], r["reading"], r["gloss"], r["context"]],
                "tags": ["levla", language],
            }
            for r in rows
        ]
        zf.writestr(
            "notes.json",
            json.dumps(
                {"name": "Levla", "flds": ["Lemma", "Reading", "Gloss", "Context"], "notes": notes},
                ensure_ascii=False,
                indent=2,
            ),
        )
    return buf.getvalue()
