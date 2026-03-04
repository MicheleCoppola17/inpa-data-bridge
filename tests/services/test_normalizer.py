from app.services.normalizer import build_short_title, clean_html_to_text


def test_clean_html_to_text_strips_tags_and_entities():
    raw = '<p><strong>Hello&nbsp;World</strong> <span>INPA</span></p>'
    cleaned = clean_html_to_text(raw)
    assert cleaned == "Hello World INPA"


def test_build_short_title_graceful_partial():
    assert build_short_title("Istruttore", 2, "Roma") == "Istruttore (2), Roma"
    assert build_short_title("Istruttore", None, "Roma") == "Istruttore, Roma"
    assert build_short_title(None, 2, None) == "Concorso (2)"
