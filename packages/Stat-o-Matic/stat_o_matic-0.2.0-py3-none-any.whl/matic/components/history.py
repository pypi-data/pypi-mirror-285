from rich.syntax import Syntax
from rich.table import Table

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import RichLog, Label, ListItem, ListView

from matic.output_manager import OutputItem


class History(ListView):

    def __init__(self):
        super().__init__()

    def add_cmd_item(self, output_item: OutputItem):
        output_str = output_item.to_colorful_string()
        self.append(ListItem(Label(output_str)))
