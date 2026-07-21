from django.template import Context, Template

from dj_markdown.templatetags.dj_markdownify import (
    markdown,
    markdown_code,
    markdown_code_css,
    markdown_code_js,
    markdown_code_js_init,
    markdown_math,
)


def test_markdown_filter_renders_heading():
    assert "<h1>Hi</h1>" in markdown("# Hi")


def test_markdown_filter_renders_emphasis_and_links():
    html = markdown("Some *text* with a [link](https://example.com).")
    assert "<em>text</em>" in html
    assert '<a href="https://example.com">link</a>' in html


def test_markdown_code_filter_renders_heading():
    assert "<h1>Hi</h1>" in markdown_code("# Hi")


def test_markdown_code_highlights_python_fence():
    html = markdown_code('```python\nprint("hello")\n```')
    assert '<div class="highlight">' in html
    assert "print" in html


def test_markdown_code_handles_extra_info_after_language():
    """mistune 3 hands the whole info string to block_code."""
    html = markdown_code('```python title=example.py\nprint("hello")\n```')
    assert '<div class="highlight">' in html


def test_markdown_code_without_language_escapes_content():
    html = markdown_code("```\n<script>alert(1)</script>\n```")
    assert "<pre><code>" in html
    assert "&lt;script&gt;" in html
    assert "<script>" not in html


def test_markdown_code_css_default_theme():
    tag = markdown_code_css()
    assert 'rel="stylesheet"' in tag
    assert "dj_markdown/css/styles/default.css" in tag


def test_markdown_code_css_known_theme():
    assert "dj_markdown/css/styles/monokai.css" in markdown_code_css("monokai")


def test_markdown_code_css_unknown_theme_falls_back_to_default():
    assert "dj_markdown/css/styles/default.css" in markdown_code_css("nope")


def test_markdown_code_js_cdn_and_local():
    assert "highlight.min.js" in markdown_code_js()
    assert "dj_markdown/js/highlight.js" in markdown_code_js(cdn=False)


def test_markdown_code_js_init_returns_script():
    tag = markdown_code_js_init()
    assert "<script>" in tag
    assert "hljs.highlightBlock" in tag


def test_markdown_math_returns_mathjax_script():
    assert "MathJax.js" in markdown_math()


def test_filters_and_tags_work_from_a_template():
    template = Template(
        "{% load dj_markdownify %}"
        "{{ text|markdown|safe }}{{ text|markdown_code|safe }}"
        "{% markdown_code_css 'monokai' %}{% markdown_math %}"
    )
    rendered = template.render(Context({"text": "# Hi"}))
    assert rendered.count("<h1>Hi</h1>") == 2
    assert "monokai.css" in rendered
    assert "MathJax.js" in rendered


def test_markdown_code_unknown_language_falls_back_to_plain_code():
    rendered = markdown_code("```notalanguage\nx < 1 & y > 2\n```")
    assert "<pre><code>" in rendered
    assert "&lt; 1 &amp; y &gt; 2" in rendered
    assert "highlight" not in rendered
