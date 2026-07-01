import json

import pytest

from app.kb_loader import load_kb


def test_load_kb_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_kb(str(tmp_path / "does_not_exist.json"))


def test_load_kb_rejects_missing_fields(tmp_path):
    bad_file = tmp_path / "kb.json"
    bad_file.write_text(json.dumps([{"id": "a", "title": "t"}]), encoding="utf-8")
    with pytest.raises(ValueError, match="missing fields"):
        load_kb(str(bad_file))


def test_load_kb_rejects_duplicate_ids(tmp_path):
    bad_file = tmp_path / "kb.json"
    entry = {"id": "dup", "category": "c", "title": "t", "content": "x"}
    bad_file.write_text(json.dumps([entry, entry]), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        load_kb(str(bad_file))


def test_load_kb_rejects_empty(tmp_path):
    empty_file = tmp_path / "kb.json"
    empty_file.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        load_kb(str(empty_file))


def test_load_kb_success(tmp_path):
    good_file = tmp_path / "kb.json"
    entry = {"id": "a", "category": "c", "title": "t", "content": "x"}
    good_file.write_text(json.dumps([entry]), encoding="utf-8")
    docs = load_kb(str(good_file))
    assert len(docs) == 1
    assert docs[0].id == "a"
