"""Tests for OpenAI-compatible LLM helpers."""

from app.services.http import join_url
from app.services.llm.client import extract_content


class TestExtractContent:
    def test_plain_content(self):
        choice = {"message": {"content": "Hello there"}}
        assert extract_content(choice) == "Hello there"

    def test_falls_back_to_reasoning_content(self):
        choice = {"message": {"content": "", "reasoning_content": "The answer is 42"}}
        assert extract_content(choice) == "The answer is 42"

    def test_multipart_content(self):
        choice = {"message": {"content": [{"type": "text", "text": "A"}, {"type": "text", "text": "B"}]}}
        assert extract_content(choice) == "AB"

    def test_empty_choice(self):
        assert extract_content(None) == ""
        assert extract_content({}) == ""


class TestJoinUrl:
    def test_strips_slashes(self):
        assert join_url("http://localhost:1234/v1/", "/chat/completions") == (
            "http://localhost:1234/v1/chat/completions"
        )
