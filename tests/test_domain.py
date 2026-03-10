from ai_class.gemini import parse_model_output
from ai_class.models import normalize_tags
from ai_class.repository import Note, rank_notes


def test_normalize_tags_dedupes_strips_and_sorts():
    assert normalize_tags([" AI ", "python", "ai", "", "Python "]) == ["ai", "python"]


def test_rank_notes_prefers_higher_overlap_then_older_id():
    notes = [
        Note(id=1, text="python ai fundamentals", tags=[]),
        Note(id=2, text="python basics", tags=[]),
        Note(id=3, text="gardening basics", tags=[]),
    ]
    ranked = rank_notes("python ai", notes)
    assert [n.id for n in ranked] == [1, 2, 3]


def test_rank_notes_ignores_punctuation_during_tokenization():
    notes = [
        Note(id=1, text="python, ai!", tags=[]),
        Note(id=2, text="python", tags=[]),
    ]
    ranked = rank_notes("python ai", notes)
    assert [n.id for n in ranked] == [1, 2]


def test_parse_model_output_handles_malformed_json_safely():
    parsed = parse_model_output("{not-json")
    assert parsed["parse_error"] is True
    assert parsed["answer"] == ""
    assert parsed["citations"] == []


def test_parse_model_output_accepts_fenced_json():
    parsed = parse_model_output('```json\n{"answer":"ok","citations":["1"]}\n```')
    assert parsed["parse_error"] is False
    assert parsed["answer"] == "ok"
    assert parsed["citations"] == ["1"]
