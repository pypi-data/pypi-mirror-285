from inquirer import errors, Text
from inquirer.render.console.base import BaseConsoleRender
from readchar import key


class ModifiedTextRender(BaseConsoleRender):
    title_inline = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = self.question.default or ""
        self.cursor_offset = 0

    def get_current_value(self):
        return self.current

    def process_input(self, pressed):
        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()

        if pressed in (key.CR, key.LF, key.ENTER):
            raise errors.EndOfInput(self.current)

        if pressed == key.BACKSPACE:
            if self.current and self.cursor_offset != len(self.current):
                if self.cursor_offset > 0:
                    n = -self.cursor_offset
                    self.current = self.current[: n - 1] + self.current[n:]
                else:
                    self.current = self.current[:-1]
        elif pressed == key.LEFT:
            if self.cursor_offset < len(self.current):
                self.cursor_offset += 1
        elif pressed == key.RIGHT:
            self.cursor_offset = max(self.cursor_offset - 1, 0)
        elif len(pressed) != 1:
            return
        else:
            if self.cursor_offset == 0:
                self.current += pressed
            else:
                n = -self.cursor_offset
                self.current = "".join((self.current[:n], pressed, self.current[n:]))


class TempTextRender(ModifiedTextRender):
    dont_leave_trace = ...


class TempText(Text):
    kind = "temp_text"
