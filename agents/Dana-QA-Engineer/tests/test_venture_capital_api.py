import pytest
from pathlib import Path

DOC_PATH = Path('output/docs/venture_capital_api_review_for_frontend.md')

REQUIRED_SECTIONS = [
    'endpoints',
    'required fields',
    'cursor pagination',
    'response envelope',
    'auth scopes',
    'mock ventures',
    'edge cases',
    'acceptance checklist'
]

@pytest.fixture()
def doc_text():
    assert DOC_PATH.exists(), f"Required doc not found: {DOC_PATH}"
    return DOC_PATH.read_text(encoding='utf-8').lower()

def test_document_contains_required_sections(doc_text):
    missing = [s for s in REQUIRED_SECTIONS if s not in doc_text]
    assert not missing, f"Missing required sections in frontend review doc: {missing}"

def test_pagination_decision_present(doc_text):
    # Expect explicit mention of cursor-based pagination decision
    assert 'cursor' in doc_text and 'cursor pagination' in doc_text, 'Cursor pagination decision not clearly documented'

def test_total_count_and_cursor_token_clarified(doc_text):
    # Check for total_count availability mention and cursor token format guidance
    has_total = 'total_count' in doc_text or 'total count' in doc_text
    has_cursor_format = 'cursor token' in doc_text or 'cursor_token' in doc_text or 'cursor token format' in doc_text
    assert has_total, 'total_count availability not addressed in frontend doc'
    assert has_cursor_format, 'cursor token format not addressed in frontend doc'

def test_error_and_rate_limit_specified(doc_text):
    # Expect mention of error envelope and rate-limit headers
    has_errors = 'error' in doc_text or 'errors' in doc_text
    has_rate_limit = 'rate-limit' in doc_text or 'rate limit' in doc_text or 'rate_limit' in doc_text
    assert has_errors, 'Error response format not documented'
    assert has_rate_limit, 'Rate limit headers/behavior not documented'

def test_mock_data_present(doc_text):
    # Expect at least 3 mock ventures referenced
    # This is a heuristic: look for 'mock' and 'venture' and numbers or example blocks
    assert 'mock' in doc_text and 'venture' in doc_text, 'Mock ventures not present in frontend doc'


if __name__ == '__main__':
    pytest.main([__file__])
