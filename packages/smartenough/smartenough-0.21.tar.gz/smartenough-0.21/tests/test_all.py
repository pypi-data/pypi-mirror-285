import pytest

from src.smartenough.llm import fetch_llm_response, text_to_chunks, find_json, find_urls, find_html

#TODO test these tests :)!

# Test text_to_chunks function
def test_text_to_chunks():
    text = "This is a test text."
    chunk_size = 5
    expected_output = ["This ", "is a ", "test ", "text."]
    assert text_to_chunks(text, chunk_size) == expected_output

# Test find_json function
def test_find_json():
    text_with_json = "Some text before {\"key\": \"value\"} and some text after."
    assert find_json(text_with_json) == {"key": "value"}

    text_without_json = "Some text without JSON."
    assert find_json(text_without_json) == []

# Test find_urls function
def test_find_urls():
    text_with_urls = "Visit https://example.com and http://test.org/path."
    assert find_urls(text_with_urls) == ["https://example.com", "http://test.org/path"]

    text_without_urls = "Some text without URLs."
    assert find_urls(text_without_urls) == []


# Test find_html function
def test_find_html():
    html_text = "<html><body><div>Some content</div></body></html>"
    expected_output = "<div>\n Some content\n</div>"
    assert find_html(html_text) == expected_output

    non_html_text = "Some plain text."
    assert find_html(non_html_text) == ""


# Test UnsupportedModelException
def test_unsupported_model_exception():
    with pytest.raises(UnsupportedModelException):
        fetch_llm_response("Some text", "Instructions", "UnsupportedModel")

# Test UnsupportedValidationException  
def test_unsupported_validation_exception():
    with pytest.raises(UnsupportedValidationException):
        fetch_llm_response("Some text", "Instructions", "Anthropic", validation="unsupported")

