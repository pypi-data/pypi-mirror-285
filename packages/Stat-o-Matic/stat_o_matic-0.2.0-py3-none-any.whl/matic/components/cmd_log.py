from rich.console import Console
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from .res_highlighter import ResHighlighter
from textual import events
from textual.app import App, ComposeResult
from textual.widgets import RichLog


class CmdLog(RichLog):

    def __init__(self, stata_highlighter=None):
        super().__init__()
        self.stata_highlighter = stata_highlighter

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True)

    def call_update(self, slog: str):
        text_log = self.query_one(RichLog)
        # Create a Text object from the input string
        text = Text(slog)
        if self.stata_highlighter:
            self.stata_highlighter.highlight(text)
        text_log.write(text)
