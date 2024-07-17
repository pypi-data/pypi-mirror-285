from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.widgets import Footer
from textual import events
import asyncio
import configparser
import os
from pathlib import Path
from rich.style import Style
from .components.cmd_input import CmdInput
from .components.cmd_log import CmdLog
from .components.history_table import HistoryTable
from .output_manager import OutputManager, OutputItem
from .components.res_highlighter import ResHighlighter

STATA_READY_SIGNAL = b'. \n'
MATA_READY_SIGNAL = b': \n'


class StatMatic(App, inherit_bindings=False):
    CSS_PATH = "./dom.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
    ]

    highlighting_rules = [
        (r"(\.|>) ", "dot", Style(color="green", bold=True)),
        (r": ", "colon", Style(color="yellow", italic=True)),
        (r"^r\(\d+\).*$", "error", Style(color="red", bgcolor="yellow", bold=True)),
    ]

    def __init__(self):
        super().__init__()
        self.cmd_input = CmdInput()
        self.cmd_log = CmdLog(stata_highlighter=ResHighlighter(rules=self.highlighting_rules))
        self.footer = Footer()
        self.history = HistoryTable(cssid="history")
        self.process = None
        self.cmd_input.focus()
        self.cmd_input_default_border_title = "Ready for next command"
        self.cmd_input.border_title = self.cmd_input_default_border_title
        self.output_manager = OutputManager()
        self.load_config()

    def load_config(self):
        # if there is a binary CLI file available now in `$HOME/projects/{project_name}`
        current_path = Path.cwd()
        home_dir = Path.home()
        path_parts = current_path.parts
        if len(path_parts) >= 5 and path_parts[3] == 'projects':
            project_name = path_parts[4]
            if len(project_name) > 0:
                for bin_name in ('stata-mp', 'stata-se', 'stata'):
                    binary_path = Path.joinpath(home_dir, 'projects', project_name,
                                                "distn", "linux64", bin_name)
                    if binary_path.is_file():
                        self.stata_exec_path = binary_path
                        return
        # User manually define the binary location
        config_file_path = os.path.expanduser('~/.config/stat_o_matic/config.ini')
        if not os.path.exists(config_file_path):
            print("Config file does not exist. ")
            print("Please create a config file at ~/.config/stat_o_matic/config.ini")
            exit(0)
        config = configparser.ConfigParser()
        config.read(config_file_path)
        self.stata_exec_path = config['STATA']['path']

    async def on_mount(self) -> None:
        self.process = await asyncio.create_subprocess_exec(
            self.stata_exec_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE)
        await self.action_submit()

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.history
            with Vertical():
                yield self.cmd_log
                yield self.cmd_input
            yield self.footer

    async def quit(self) -> None:
        self.process.stdin.close()
        await self.process.wait()
        exit(0)

    async def read_output(self, output_item, timeout=0.2):
        """Read output from the process until a timeout occurs."""
        while True:
            try:
                line = await asyncio.wait_for(self.process.stdout.readline(), timeout=timeout)
                processed_line = line.decode().strip("\n")
                self.cmd_log.call_update(processed_line)
                output_item.append(processed_line)
            except asyncio.TimeoutError:
                self.process.stdin.write(b'\n')
                await self.process.stdin.drain()
                prompt_check = await self.process.stdout.readline()
                if prompt_check == STATA_READY_SIGNAL or prompt_check == MATA_READY_SIGNAL:
                    return
            if self.process.returncode is not None:
                exit(self.process.returncode)

    async def action_submit(self):
        # call an independent process
        # Send the string to the shell process
        self.cmd_input.border_title = ""
        self.process.stdin.write(self.cmd_input.value.encode() + b'\n')
        await self.process.stdin.drain()

        output_item = OutputItem(cmd=self.cmd_input.value)
        self.output_manager.append(output_item)

        self.cmd_input.clear()
        self.cmd_input.disabled = True

        # Get the output from the shell process
        await self.read_output(output_item)
        self.cmd_input.disabled = False
        self.cmd_input.focus()
        self.cmd_input.border_title = self.cmd_input_default_border_title

        if len(output_item.cmd) > 0:
            self.history.add_cmd_item(output_item)

    async def on_cmd_input_cmd_submitted(self) -> None:
        await self.action_submit()

    def on_key(self, event: events.Key) -> None:
        if self.focused.__class__ != HistoryTable:
            if event.key == "up":
                self.cmd_input.value = self.history.get_prev_cmd()
            elif event.key == "down":
                self.cmd_input.value = self.history.get_next_cmd()

    def on_data_table_cell_selected(self) -> None:
        self.cmd_input.value = str(self.history.get_cursor_cmd())
