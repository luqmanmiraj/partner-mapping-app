"""Load supplier My Company tab prototypes from ``.prototype/company/``."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from theme.html_utils import render_inline_html_page

_ROOT = Path(__file__).resolve().parents[1]
_TEMPLATES_DIR = _ROOT / ".prototype" / "company"

_FONT_AWESOME_CDN = (
    '<link rel="stylesheet" '
    'href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
)

_TAB_SCOPES: dict[str, tuple[str, str]] = {
    "company_contacts-tab": ("nexus-company-contacts-tab", "nexus-company-contacts-tab"),
    "company_news_media-tab": ("nexus-company-news-tab", "nexus-company-news-tab"),
}

# Overrides when a tab panel is embedded under Streamlit tab buttons (not standalone page).
SUPPLIER_COMPANY_TAB_EMBED_CSS = """
body {
  padding: 0 !important;
  margin: 0 !important;
  background: transparent !important;
}

.dashboard-container {
  max-width: none !important;
  width: 100% !important;
  margin: 0 !important;
}

.tab-navigation {
  display: none !important;
}
"""


def _read_company_prototype(slug: str) -> str:
    path = _TEMPLATES_DIR / f"{slug}.html"
    if not path.is_file():
        raise FileNotFoundError(f"Company prototype not found: {path}")
    return path.read_text(encoding="utf-8")


def _extract_all_styles(html: str) -> str:
    blocks = re.findall(
        r"<style[^>]*>(.*?)</style>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return "\n".join(block.strip() for block in blocks if block.strip())


def _scope_selector_list(selectors: str, scope: str) -> str:
    scoped: list[str] = []
    for part in selectors.split(","):
        sel = part.strip()
        if not sel:
            continue
        if sel == "body":
            scoped.append(scope)
        elif sel == "*":
            scoped.append(f"{scope} *")
        elif sel.startswith("@"):
            scoped.append(sel)
        else:
            scoped.append(f"{scope} {sel}")
    return ", ".join(scoped)


def _scope_stylesheet(css: str, scope: str) -> str:
    """Prefix CSS rule selectors with ``scope``; recurse into @-blocks such as @media."""

    def parse_rules(text: str) -> str:
        result: list[str] = []
        i = 0
        n = len(text)
        while i < n:
            whitespace = re.match(r"\s+", text[i:])
            if whitespace:
                result.append(whitespace.group(0))
                i += whitespace.end()
                continue

            comment = re.match(r"/\*.*?\*/", text[i:], re.DOTALL)
            if comment:
                result.append(comment.group(0))
                i += comment.end()
                continue

            if text[i] == "@":
                header_match = re.match(r"@[^{]+\{", text[i:])
                if not header_match:
                    break
                header = header_match.group(0)
                start = i + len(header)
                depth = 1
                j = start
                while j < n and depth > 0:
                    if text[j] == "{":
                        depth += 1
                    elif text[j] == "}":
                        depth -= 1
                    j += 1
                inner = text[start : j - 1]
                at_name = header.split("{", 1)[0].strip().lower()
                if at_name.startswith("@keyframes"):
                    result.append(header + inner + "}")
                else:
                    result.append(header[:-1] + "{" + parse_rules(inner) + "}")
                i = j
                continue

            selector_match = re.match(r"[^{]+", text[i:])
            if not selector_match:
                break
            selectors = selector_match.group(0)
            i += len(selectors)
            if i >= n or text[i] != "{":
                break
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                j += 1
            body = text[i + 1 : j - 1]
            result.append(f"{_scope_selector_list(selectors, scope)} {{{body}}}")
            i = j
        return "".join(result)

    return parse_rules(css.strip())


@lru_cache(maxsize=None)
def _load_company_tab_css(slug: str) -> str:
    return _extract_all_styles(_read_company_prototype(slug))


def build_scoped_tab_styles(slug: str, scope_class: str) -> str:
    """Prototype CSS scoped under ``.{scope_class}`` for parent-document injection."""
    scope = f".{scope_class}"
    css = _load_company_tab_css(slug)
    scoped = _scope_stylesheet(css, scope)
    embed = _scope_stylesheet(SUPPLIER_COMPANY_TAB_EMBED_CSS, scope)
    return f"{scoped}\n{embed}"


def company_contacts_tab_styles() -> str:
    return build_scoped_tab_styles("company_contacts-tab", "nexus-company-contacts-tab")


def company_news_media_tab_styles() -> str:
    return build_scoped_tab_styles("company_news_media-tab", "nexus-company-news-tab")


def render_company_tab_document(
    slug: str,
    body_html: str,
    *,
    extra_css: str = "",
) -> None:
    """
    Render a supplier company tab in the main Streamlit document.

    Styles are injected into the parent ``<head>`` (like the About tab) because
    ``st.html`` iframes do not reliably apply tab-panel CSS in this app.
    """
    scope_class, style_id = _TAB_SCOPES[slug]
    css = build_scoped_tab_styles(slug, scope_class)
    if extra_css.strip():
        css = f"{css}\n{extra_css.strip()}"
    wrapped = f'<div class="{scope_class}">{body_html.strip()}</div>'
    render_inline_html_page(
        css,
        wrapped,
        head_markup=_FONT_AWESOME_CDN,
        style_id=style_id,
    )
