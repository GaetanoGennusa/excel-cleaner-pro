"""Guard the local-only, accessible stylesheet and the HTML helpers."""
import re

from ui.presentation import THEME, workflow


def test_theme_loads_no_external_resources():
    css = THEME.read_text(encoding="utf-8")
    assert "@import" not in css
    urls = re.findall(r"url\(\s*['\"]?([^'\")]+)", css)
    assert urls and all(url.startswith("data:") for url in urls)


def test_reduced_motion_rule_is_scoped_to_project_elements():
    # A global `*` override stops Streamlit's own select dropdowns from opening.
    css = THEME.read_text(encoding="utf-8")
    block = css[css.index("@media (prefers-reduced-motion: reduce)"):]
    assert not re.search(r"(^|[\s,{])\*\s*[,{]", block)


def test_workflow_marks_progress_and_current_step():
    html = workflow(2)
    assert html.count("<li") == 5
    assert html.count('aria-current="step"') == 1
    assert html.count("(completata)") == 2
