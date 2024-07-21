import typing as t
import string

from inquirer import errors, List
from inquirer.questions import TaggedValue
from inquirer.render.console import List as ListRender
from readchar import key


class ListWithFilterRender(ListRender):
    """
    Custom renderer for a list prompt with filtering capability.

    This renderer extends the functionality of the ListRender class from the `inquirer` library.
    It allows filtering of choices based on user input, providing additional navigation capabilities.
    It also uses `.question.values` instead of `.question.choices` to raise the selection result,
    in case `.question.values` is specified.

    Key Bindings:
        - UP: Move selection up one item.
        - DOWN: Move selection down one item.
        - ENTER: Confirm the selection and raise an EndOfInput exception with the selected value.
        - CTRL_C: Raise a KeyboardInterrupt exception to exit the prompt.
        - BACKSPACE: Remove the last character from the filter.
        - Other characters: Append the pressed character to the filter.

    Attributes:
        filter (str): The current filter string.

    Methods:
        process_input(pressed: str): Process the user input and perform the corresponding action.

    Note:
        This class is intended only for use with the ListWithFilter prompt, which is stored in `.question` field.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter = ""

    def process_input(self, pressed: str):
        """
        Process the user input and perform the corresponding action.

        Args:
            pressed (str): The character or key combination pressed by the user.

        Raises:
            errors.EndOfInput: If the ENTER key is pressed, indicating the selection is confirmed.
            KeyboardInterrupt: If the CTRL_C key is pressed, indicating an interruption to exit the prompt.
            errors.ValidationError: If the filter is non-empty, shows up the filter in the validation status bar.

        """
        old_filter = self.filter

        if pressed == key.UP:
            if self.question.carousel and self.current == 0:
                self.current = len(self.question.choices) - 1
            else:
                self.current = max(0, self.current - 1)
        elif pressed == key.DOWN:
            if self.question.carousel and self.current == len(self.question.choices) - 1:
                self.current = 0
            else:
                self.current = min(len(self.question.choices) - 1, self.current + 1)
        elif pressed == key.ENTER:
            if not self.question.choices:
                raise errors.ValidationError(f"No options found with the '{self.filter}' string")

            value = self.question.choices[self.current]
            raise errors.EndOfInput(getattr(value, "value", value))

        elif pressed == key.CTRL_C:
            raise KeyboardInterrupt()

        elif pressed == key.BACKSPACE:
            self.filter = self.filter[:-1]
        elif pressed in [key.LEFT, key.RIGHT]:
            pass
        else:
            if pressed in string.printable:
                self.filter += pressed

        if old_filter != self.filter:
            self.current = 0
            self.question.filter_choices(self.filter)

        if self.filter:
            raise errors.ValidationError(self.filter)

    def _current_index(self):
        try:
            return self.question.choices.index(self.question.default) if self.question.default is not None else 0
        except ValueError:
            return 0


class ListWithFilter(List):
    kind = "list_with_filter"

    def __init__(
            self,
            name,
            message="",
            choices=None,
            default=None,
            ignore=False,
            validate=True,
            carousel=False,
            other=False,
            autocomplete=None,
    ):
        super().__init__(name, message, choices, default, ignore, validate, carousel, other, autocomplete)

        self._start_choices = choices

    def filter_choices(self, filter_str: t.Optional[str]):
        if filter_str:
            self._choices = [choice for (choice, parsed_choice) in self.start_choices_generator()
                             if filter_str.lower() in getattr(parsed_choice, "label", parsed_choice).lower()]

        else:
            self._choices = self._start_choices

    def start_choices_generator(self) -> t.Tuple[str, t.Union[str, TaggedValue]]:
        for choice in self._solve(self._start_choices):
            yield choice, TaggedValue(*choice) if isinstance(choice, tuple) and len(choice) == 2 else choice

    @staticmethod
    def zip_choices_and_values(choices: t.Union[t.List, t.Tuple], values: t.Union[t.List, t.Tuple]):
        if not len(choices) == len(values):
            raise ValueError("values must have the same length as choices")

        return [(choice, value) for choice, value in zip(choices, values)]
