from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import DataTable

from matic.output_manager import OutputItem


class HistoryTable(DataTable):

    def __init__(self, cssid: str):
        super().__init__(id=cssid, zebra_stripes=True)
        self.history = []
        self.add_columns(*OutputItem.get_column_names())

    def add_cmd_item(self, output_item: OutputItem):
        self.add_row(*output_item.get_string_tuple(), label=output_item.get_idx_label())
        self.history.append(output_item)
        self.move_cursor(row=len(self.history))

    def get_cursor_cmd(self):
        if self.cursor_row < 0 or self.cursor_row >= len(self.history):
            return ""
        self.cmd_input_idx = self.cursor_row
        return self.history[self.cursor_row].cmd

    def get_prev_cmd(self) -> str:
        next_cursor_row = self.cursor_row - 1
        if next_cursor_row <= -1:
            next_cursor_row = len(self.history)
        self.move_cursor(row=next_cursor_row)
        return self.get_cursor_cmd()

    def get_next_cmd(self) -> str:
        next_cursor_row = self.cursor_row + 1
        if next_cursor_row >= len(self.history):
            next_cursor_row = 0
        self.move_cursor(row=next_cursor_row)
        return self.get_cursor_cmd()
