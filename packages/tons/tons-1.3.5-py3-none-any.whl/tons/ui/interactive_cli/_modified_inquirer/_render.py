import functools

from blessed import Terminal
from inquirer import events, errors
from inquirer.render.console import ConsoleRender
from inquirer.render.console.base import BaseConsoleRender

from ._render_mixin import ConsoleRenderMixin

from ._confirm_render import ModifiedConfirmRender, RemovePrevAfterEnterRender
from ._list_with_filter_render import ListWithFilterRender
from ._menu_with_hotkeys import MenuWithHotkeysRender
from ._text_render import ModifiedTextRender, TempTextRender
from ._utils import text_to_not_formatted_displayed_lines, evaluate_cursor_movement
from .._exceptions import EscButtonPressed

ESC_BUTTONS = {"\x1b", "\x1b\x1b"}

_print = functools.partial(print, flush=True, end="")


class LineMemory:
    """
    A context manager for managing the text output on a terminal line.

    It is used to calculate the number of lines printed, including line wraps, when printing text.
    The cursor should be in the leftmost column (at the beginning of the line) upon initialization.
    """
    def __init__(self, terminal: Terminal):
        self._terminal = terminal
        self._text = ""

    def __enter__(self) -> 'LineMemory':
        self._text = ""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def lines_printed(self) -> int:
        """ Returns the number of lines printed, including line wraps, from the accumulated text. """
        return len(text_to_not_formatted_displayed_lines(self._text, self._terminal.width))

    @property
    def text(self) -> str:
        return self._text

    def print_string(self, string: str):
        for movement in ('\x1b[A',  # up
                         '\x1b[B',  # down
                         '\x1b[C',  # right
                         '\x1b[D',  # left
                         '\x08'     # backspace
                         ):
            if movement in string:
                raise ValueError(f'Cursor movement inside {self.__class__.__name__}.print_string is not allowed')
        self._text += string
        _print(string)


class ModifiedConsoleRender(ConsoleRender, ConsoleRenderMixin):
    def render(self, question, answers=None):
        """ Render the question and return the answer. """
        question.answers = answers or {}
        if question.ignore:
            return question.default
        cls = self.render_factory(question.kind)
        render = cls(question, terminal=self.terminal, theme=self._theme, show_default=question.show_default)
        self.clear_eos()
        is_success = True
        try:
            answer = self._event_loop(render)
            return answer
        except (EscButtonPressed, KeyboardInterrupt):
            is_success = False
            raise
        except Exception as exception:  # TODO too general exception
            is_success = False
            raise exception
        finally:
            self._erase_additional_lines(render)
            self._leave_trace(render, is_success)

    @property
    def theme(self):
        return self._theme

    def _event_loop(self, render):
        """
        The event loop for rendering a dialogue and capturing user input.
        """
        while True:
            # Display the dialogue
            self._force_initial_column()
            self._print_status_bar(render)

            # Calculate how many lines have been printed (including line wraps)
            with LineMemory(self.terminal) as line_memory:
                line_memory.print_string(self.compose(render))
                lines_to_move_back = line_memory.lines_printed

            # Offset the cursor (if present)
            try:
                cursor_offset = render.cursor_offset
            except AttributeError:
                pass
            else:
                dx, dy = evaluate_cursor_movement(text=line_memory.text,
                                                  offset=cursor_offset,
                                                  terminal_width=self.terminal.width)
                self.move_cursor(dx, dy)
                lines_to_move_back += dy

            # Wait for the user input
            try:
                self._process_input(render)
            except errors.EndOfInput as e:
                # The user has made a selection
                return e.selection
            except (EscButtonPressed, KeyboardInterrupt):
                # Abort
                raise
            finally:
                # Erase
                self._force_initial_column()
                self.move_cursor(0, -lines_to_move_back + 1)
                self.clear_eos()

    def _force_initial_column(self):
        _print('\r')

    def _leave_trace(self, render: BaseConsoleRender, is_success: bool):
        _print(self.compose_trace(render, is_success))

    def _erase_additional_lines(self, render):
        try:
            extra_lines_to_erase = render.get_lines_count_to_erase()
        except AttributeError:
            pass
        else:
            self._force_initial_column()
            self.move_cursor(0, -extra_lines_to_erase)
            self.clear_eos()

    def move_cursor(self, delta_x, delta_y):
        txt = ''
        if delta_x > 0:
            txt += self.terminal.move_right * delta_x
        else:
            txt += self.terminal.move_left * (-delta_x)

        if delta_y > 0:
            txt += self.terminal.move_down * delta_y
        else:
            txt += self.terminal.move_up * (-delta_y)

        _print(txt)

    """ ========================================================================================================
    These methods were present in the vanilla inquirer and are deleted to avoid an accidental call
    (using these functions now can break the render logic) """
    def _print_header(self, render, specific_msg_mark=None):
        raise NotImplementedError

    def _print_options(self, render):
        raise NotImplementedError

    def print_str(self, base, lf=False, fit_width=False, **kwargs):
        raise NotImplementedError
    """ ========================================================================================================= """

    def _process_input(self, render):
        try:
            ev = self._event_gen.next()
            if isinstance(ev, events.KeyPressed):
                if ev.value in ESC_BUTTONS:
                    raise EscButtonPressed()

                render.process_input(ev.value)
        except errors.ValidationError as e:
            self._previous_error = e.value
        except errors.EndOfInput as e:
            try:
                render.question.validate(e.selection)
                raise
            except errors.ValidationError as e:
                self._previous_error = render.handle_validation_error(e)

    def render_factory(self, question_type):
        matrix = {
                    'text': ModifiedTextRender,
                    'path': ModifiedTextRender,
                    'temp_text': TempTextRender,
                    'modified_confirm': ModifiedConfirmRender,
                    'remove_prev_after_enter': RemovePrevAfterEnterRender,
                    'list_with_filter': ListWithFilterRender,
                    'menu_with_hotkeys': MenuWithHotkeysRender
                }
        try:
            return matrix[question_type]
        except KeyError:
            return super().render_factory(question_type)

    def render_in_bottombar(self, message):
        with self.terminal.location(0, self.height - 2):
            self.clear_eos()
            _print(message)
