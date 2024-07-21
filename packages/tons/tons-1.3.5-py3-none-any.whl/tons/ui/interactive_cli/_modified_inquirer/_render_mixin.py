from blessed import Terminal
from inquirer.render.console.base import BaseConsoleRender
from inquirer.themes import Theme

from ._utils import displayable_line_length


class ConsoleRenderMixin:
    """
    Rendering utilities that can be utilized by individual question render classes.

    TODO: use this mixin to display the options in ListWithFilter and MenuWithHotkeys
          without exceeding the terminal height.
    """
    terminal: Terminal
    theme: Theme

    def compose(self, render: BaseConsoleRender):
        return self.compose_header(render) + self.compose_options(render)

    def compose_header(self, render: BaseConsoleRender, message_mark='?') -> str:
        header = render.get_header()
        default_value = " ({color}{default}{normal})".format(
            default=render.question.default, color=self.theme.Question.default_color,
            normal=self.terminal.normal
        )
        show_default = render.question.default and render.show_default
        header += default_value if show_default else ""
        tq = self.theme.Question
        t = self.terminal
        text = f"{tq.brackets_color}[{tq.mark_color}{message_mark}{tq.brackets_color}]{t.normal} {header}: "
        # ensure any user input with { or } will not cause a formatting error
        escaped_current_value = str(render.get_current_value()).replace("{", "{{").replace("}", "}}")
        text += escaped_current_value
        if not render.title_inline:
            text += '\n'
        return text

    def compose_options(self, render: BaseConsoleRender, truncate: bool = True) -> str:
        text = ""
        for message, symbol, color in render.get_options():
            formatted_option = f" {color}{symbol} {message}{self.terminal.normal}"
            if truncate:
                formatted_option = self.fit_line_within_terminal_width(formatted_option)
            text += formatted_option + '\n'

        return text

    def compose_trace(self, render: BaseConsoleRender, is_success: bool) -> str:
        """
        Compose a trace for displaying after the question is answered.

        The trace looks like a header with a custom message mark (that signifies success or failure).
        Displaying it can be avoided by defining a `dont_leave_trace` attribute in the concrete question render class.
        """
        try:
            render.dont_leave_trace
        except AttributeError:
            trace = self.compose_header(render, self.get_msg_mark(is_success))
            if render.title_inline:  # Force the linefeed and clear_eol at the end of the trace
                trace += '\n' + self.terminal.clear_eol
            return trace
        else:
            return ''

    def fit_line_within_terminal_width(self, line: str) -> str:
        """
        Make the `line` fit within the terminal width by truncating and adding an ellipsis (...).
        """
        def with_ellipsis_at_end(_text: str) -> str:
            return _text[:-3] + self.terminal.normal + '...'

        if displayable_line_length(line) >= self.terminal.width:
            while displayable_line_length(with_ellipsis_at_end(line)) >= self.terminal.width and len(line) > 0:
                line = line[:-1]
            line = with_ellipsis_at_end(line)

        return line

    @staticmethod
    def get_msg_mark(is_success) -> str:
        return "✓" if is_success else "✕"
