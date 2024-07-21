from inquirer import errors, Confirm
from inquirer.render.console import Confirm as ConfirmRender
from readchar import key

from tons.ui.interactive_cli._modified_inquirer._utils import text_to_not_formatted_displayed_lines


class ModifiedConfirmRender(ConfirmRender):
    def __init__(self, *args, **kwargs):
        super(ModifiedConfirmRender, self).__init__(*args, **kwargs)
        self.current = ""

    def get_current_value(self):
        return self.current

    def process_input(self, pressed):
        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()

        if pressed.lower() == key.ENTER:
            raise errors.EndOfInput(self.question.default)

        if pressed in "yY":
            self.current = pressed
            raise errors.EndOfInput(True)
        if pressed in "nN":
            self.current = pressed
            raise errors.EndOfInput(False)


class ModifiedConfirm(Confirm):
    kind = "modified_confirm"


class RemovePrevAfterEnterRender(ConfirmRender):
    dont_leave_trace = ...

    def get_header(self):
        return f"{self.question.message}"

    def get_lines_count_to_erase(self) -> int:
        lines_count = len(text_to_not_formatted_displayed_lines(self.question.text_to_erase.rstrip('\n'),
                                                                self.terminal.width))
        return lines_count


class RemovePrevAfterEnter(Confirm):
    def __init__(self, name, text_to_erase, default=False, **kwargs):
        self.text_to_erase = text_to_erase
        super().__init__(name, default=default, **kwargs)
    kind = "remove_prev_after_enter"
