from app.services.safety_filter import SafetyFilter


def test_safe_content():
    text = "Em yêu anh!"
    assert SafetyFilter.is_safe(text) is True


def test_unsafe_content():
    text = "This contains violence"
    assert SafetyFilter.is_safe(text) is False


def test_filter_text():
    text = "Normal text"
    filtered = SafetyFilter.filter_text(text)
    assert filtered == text
