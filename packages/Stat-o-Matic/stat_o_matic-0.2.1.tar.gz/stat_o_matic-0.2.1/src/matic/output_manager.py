from rich.text import Text


class OutputItem:

    def __init__(self, cmd):
        self.lines = []
        self.cmd = cmd
        self.index = -1

    @staticmethod
    def get_column_names():
        return "Command", "Status"

    def append(self, line):
        self.lines.append(line)

    def get_string_tuple(self):
        return self.cmd, str("None")

    def get_idx_label(self):
        return str(self.index)

    def to_colorful_string(self):
        txt_1 = Text()
        txt_1.append(str(self.index), style="bold magenta")
        txt_1.append(":\t")
        txt_1.append(str(self.cmd), style="italic")
        return txt_1


class OutputManager:

    def __init__(self):
        self.arr = []
        self.cnt = 0

    def append(self, output_item: OutputItem):
        output_item.index = self.cnt
        self.cnt += 1
        self.arr.append(output_item)
