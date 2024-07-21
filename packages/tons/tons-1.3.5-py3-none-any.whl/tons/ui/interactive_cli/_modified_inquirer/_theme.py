from blessed import Terminal
from inquirer.themes import Default

terminal = Terminal()


class ModifiedTheme(Default):
    def __init__(self):
        super(ModifiedTheme, self).__init__()
        self.List.selection_color = terminal.bold
        self.List.selection_cursor = ">"
        self.List.unselected_color = terminal.normal
