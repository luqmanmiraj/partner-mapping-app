#!/usr/bin/env python3
"""Add page-specific CSS class prefixes to .prototype/member_pages/*.html."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".prototype" / "member_pages"


def replace_classes(content: str, mapping: dict[str, str]) -> str:
    """Replace class names longest-first to avoid partial overlaps."""
    for old, new in sorted(mapping.items(), key=lambda x: -len(x[0])):
        # CSS selectors: .old, .old:hover, .old.mod, .old::before
        content = re.sub(
            rf"\.{re.escape(old)}(?=[\s,{{.:)#\[]|$)",
            f".{new}",
            content,
        )
        # HTML class attributes (word boundaries inside quotes)
        content = re.sub(
            rf'(?<=["\s]){re.escape(old)}(?=["\s])',
            new,
            content,
        )
    return content


def prefix_css_vars(content: str, scope_class: str, var_prefix: str) -> str:
    """Move :root custom properties to a scoped block with prefixed names."""
    root_match = re.search(
        r":root\s*\{([^}]*)\}",
        content,
        flags=re.DOTALL,
    )
    if not root_match:
        return content

    block = root_match.group(1)
    new_block = block
    for m in re.finditer(r"--([a-zA-Z0-9_-]+)\s*:", block):
        name = m.group(1)
        if not name.startswith(var_prefix):
            new_block = new_block.replace(f"--{name}", f"--{var_prefix}-{name}")

    scoped = f".{scope_class} {{\n{new_block}\n}}"
    content = content[: root_match.start()] + scoped + content[root_match.end() :]

    # var(--foo) -> var(--prefix-foo) for unprefixed vars in this file
    def var_repl(match: re.Match[str]) -> str:
        name = match.group(1)
        if name.startswith(var_prefix):
            return match.group(0)
        return f"var(--{var_prefix}-{name})"

    content = re.sub(r"var\(--([a-zA-Z0-9_-]+)\)", var_repl, content)
    return content


def scope_globals(
    content: str,
    scope_class: str,
    *,
    body_class: str | None = None,
) -> str:
    """Scope universal/body rules under the page root class."""
    content = re.sub(
        r"^\s*\*\s*\{",
        f"        .{scope_class},\n        .{scope_class} * {{",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if body_class:
        content = re.sub(
            r"body\.member-company-body",
            f".{body_class}",
            content,
        )
        content = re.sub(
            r"<body>",
            f'<body class="{body_class}">',
            content,
            count=1,
        )
    else:
        content = re.sub(
            r"^\s*body\s*\{",
            f"        .{scope_class} {{",
            content,
            count=1,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r"^\s*body\s*\{",
            f"        .{scope_class} {{",
            content,
            flags=re.MULTILINE,
        )
        if f'class="{scope_class}"' not in content and "<body>" in content:
            content = content.replace(
                "<body>",
                f'<body>\n    <div class="{scope_class}">',
                1,
            )
            content = content.replace("</body>", "    </div>\n</body>", 1)
    return content


def rename_prefix(content: str, old_prefix: str, new_prefix: str) -> str:
    """Rename offer-* style prefixes in class names and selectors."""
    content = content.replace(f".{old_prefix}", f".{new_prefix}")
    content = content.replace(f'class="{old_prefix}', f'class="{new_prefix}')
    content = content.replace(f" {old_prefix}", f" {new_prefix}")
    content = re.sub(
        rf"--{re.escape(old_prefix)}",
        f"--{new_prefix}",
        content,
    )
    return content


def process_file(path: Path) -> None:
    """
    Generic processor: use the HTML file name (without extension) as the
    prefix / scope class for all selectors so they never conflict.
    """
    prefix = path.stem  # e.g. 'member-dashboard', 'supplier-profile'
    content = path.read_text(encoding="utf-8")

    # 1) Scope :root custom properties (if any) under .<prefix>
    content = prefix_css_vars(content, prefix, prefix)

    # 2) Scope global selectors (*, body) under .<prefix> and wrap body
    content = scope_globals(content, prefix)

    path.write_text(content, encoding="utf-8")


def main() -> None:
    for html_path in ROOT.glob("*.html"):
        process_file(html_path)
    print("Done prefixing member_pages HTML files.")


if __name__ == "__main__":
    main()
