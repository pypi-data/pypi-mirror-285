from inquirer import errors, List
from inquirer.render.console import List as ListRender
from readchar import key


class MenuWithHotkeysRender(ListRender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = self.question.starting_pos

    def process_input(self, pressed):
        question = self.question
        if pressed == key.UP:
            if question.carousel and self.current == 0:
                self.current = len(question.choices) - 1
            else:
                self.current = max(0, self.current - 1)
        elif pressed == key.DOWN:
            if question.carousel and self.current == len(question.choices) - 1:
                self.current = 0
            else:
                self.current = min(len(self.question.choices) - 1, self.current + 1)
        elif pressed == key.ENTER:
            value = self.question.choices[self.current]
            raise errors.EndOfInput(getattr(value, "value", value))
        elif pressed == key.CTRL_C:
            raise KeyboardInterrupt()
        elif pressed in question.hotkeys:
            self.current = question.hotkeys[pressed]
            idx = question.hotkeys[pressed]
            value = self.question.choices[idx]
            raise errors.EndOfInput(getattr(value, "value", value))


class MenuWithHotkeys(List):
    kind = "menu_with_hotkeys"

    def __init__(self, name, message="", choices=None, default=None, ignore=False, validate=True,
                 hotkeys=None, carousel=False, starting_pos=0):
        super().__init__(name, message, choices, default, ignore, validate, carousel)
        self.starting_pos = starting_pos
        self.hotkeys = {hotkey: i for i, hotkey in enumerate(hotkeys)}
