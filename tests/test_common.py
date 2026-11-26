import pytest

from agents.common import clean_topic, extract_json, slugify


def test_slugify_blocks_path_traversal():
    slug = slugify("../../etc/passwd")
    assert "/" not in slug and ".." not in slug
    assert slug == "etc_passwd"


def test_slugify_falls_back_for_symbols_only():
    assert slugify("!!!") == "topic"


@pytest.mark.parametrize("bad", ["", "   ", "x" * 101])
def test_clean_topic_rejects_empty_and_long(bad):
    with pytest.raises(ValueError):
        clean_topic(bad)


def test_clean_topic_collapses_whitespace():
    assert clean_topic("  sql   injection \n") == "sql injection"


def test_extract_json_handles_fences_and_chatter():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('Here you go: {"a": 2} hope it helps') == {"a": 2}
    assert extract_json('{"a": 3}') == {"a": 3}


def test_extract_json_raises_value_error_on_garbage():
    with pytest.raises(ValueError):
        extract_json("no json here")
