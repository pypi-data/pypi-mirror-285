from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.document._document import EditResult
from textual.widgets import TextArea
from textual.widgets import Input
from textual.message import Message
from textual.widgets.text_area import Selection


class CmdInput(Input):

    DEFAULT_PLACEHOLDER = "Type <enter> to submit"

    class UseHistory(Message):

        def __init__(self, direction: str):
            self.direction = direction
            super().__init__()

    def __init__(self) -> None:
        super().__init__(value="", placeholder=self.DEFAULT_PLACEHOLDER)

    class CmdSubmitted(Message):

        def __init__(self) -> None:
            super().__init__()

    def clear(self) -> None:
        self.value = ""
        self.placeholder = self.DEFAULT_PLACEHOLDER

    def action_submit(self) -> None:
        self.post_message(self.CmdSubmitted())

    def input_cursor_up(self):
        self.post_message(self.UseHistory(direction="up"))

    def input_cursor_down(self):
        self.post_message(self.UseHistory(direction="down"))
