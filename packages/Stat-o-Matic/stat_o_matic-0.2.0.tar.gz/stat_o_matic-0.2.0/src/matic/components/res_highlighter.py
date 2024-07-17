from rich.highlighter import RegexHighlighter
from rich.text import Text, Span
from rich.style import Style
from typing import List, Tuple
import re


class ResHighlighter(RegexHighlighter):
    """Highlights lines based on multiple regex patterns with different styles."""

    highlights: List[str] = []
    base_style: str = ""

    def __init__(self, rules: List[Tuple[str, str, Style]]):
        super().__init__()
        self.rules = rules
        self.highlights = [f"^({pattern}.*)" for pattern, _, _ in rules]

    def highlight(self, text: Text) -> None:
        super().highlight(text)

        plain = text.plain
        append = text.spans.append

        for pattern, style_name, style in self.rules:
            for match in re.finditer(f"^({pattern}.*)", plain, re.MULTILINE):
                start, end = match.span()
                append(Span(start, end, style_name))
                # Apply the custom style directly
                text.stylize(style, start, end)

    @classmethod
    def create(cls, rules: List[Tuple[str, str, Style]]) -> 'ResHighlighter':
        return cls(rules)