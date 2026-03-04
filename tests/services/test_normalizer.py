from app.services.normalizer import clean_html_to_text


def test_clean_html_to_text_strips_tags_and_entities():
    raw = '<p><strong>Hello&nbsp;World</strong> <span>INPA</span></p>'
    cleaned = clean_html_to_text(raw)
    assert cleaned == "Hello World INPA"
