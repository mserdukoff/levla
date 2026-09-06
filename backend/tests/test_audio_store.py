from app.core import config
from app.services import audio_store


def test_local_audio_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(config.settings, "audio_dir", str(tmp_path))
    monkeypatch.setattr(config.settings, "s3_audio_bucket", "")
    audio_store.put_mp3("abc", b"id3-bytes")
    assert audio_store.exists("abc")
    assert audio_store.get_mp3("abc") == b"id3-bytes"
    assert audio_store.get_mp3("missing") is None
