import re
from typing import List


def evaluate_cursor_movement(text: str, offset: int, terminal_width: int) -> [int, int]:
    """
    Evaluate the cursor movement based on the given text, cursor offset, and terminal width.

    This function calculates the cursor's movement (delta) on the screen based on the provided text, cursor offset,
    and terminal width. It determines the new cursor position after applying the given offset to the original cursor
    position.

    Args:
        text (str): The input text containing the content displayed on the screen.
        offset (int): The cursor offset, indicating the number of characters to move the cursor backward from its
                      original position.
        terminal_width (int): The width of the terminal, used to format the text and calculate line breaks.

    Returns:
        Tuple[int, int]: A tuple containing the cursor's horizontal (x) and vertical (y) movement (delta) on the screen.
            - The first value represents the horizontal movement (delta_x) where a positive value means moving right
              and a negative value means moving left.
            - The second value represents the vertical movement (delta_y) where a positive value means moving down and
              a negative value means moving up.

    Note:
        - The function uses the `text_to_not_formatted_displayed_lines` function to process the input text and calculate
          the line breaks within the specified terminal width.
        - The cursor's original position is determined by counting the number of lines (cursor_y) and characters
          in the last line (cursor_x).
        - The function applies the offset to the original cursor position, moving the cursor backward in the text,
          and calculates the new cursor position (cursor_x, cursor_y) after the movement.
    """
    message_lines = text_to_not_formatted_displayed_lines(text, terminal_width)
    cursor_x0 = cursor_x = len(message_lines[-1])
    cursor_y0 = cursor_y = len(message_lines) - 1
    while offset > 0:
        cursor_x -= 1
        if cursor_x < 0:
            cursor_y -= 1
            cursor_x = len(message_lines[cursor_y]) - 1
        offset -= 1

    cursor_delta_x = cursor_x - cursor_x0
    cursor_delta_y = cursor_y - cursor_y0

    return cursor_delta_x, cursor_delta_y


def text_to_not_formatted_displayed_lines(text: str, terminal_width: int) -> List[str]:
    """
    Convert the input text into a list of lines, how it will be displayed within the specified terminal width.

    This function processes the input text and wraps it into multiple lines, ensuring that each line does not exceed
    the specified terminal width. It removes ANSI escape codes from the text before processing to ensure accurate line
    wrapping.

    Args:
        text (str): The input text to be processed and formatted into lines.
        terminal_width (int): The maximum width of the terminal to display the lines without overflow.

    Returns:
        List[str]: A list of lines containing the processed text, formatted to fit within the terminal width.

    Note:
        - The function removes ANSI escape codes from the input text using the `remove_ansi_escape_codes` function.
        - It wraps the text into multiple lines, ensuring that each line does not exceed the specified terminal width.
        - If the input text contains newline characters ('\n'), the function splits the text at those points to create
          separate lines.
    """
    text = remove_ansi_escape_codes(text)
    lines = []
    while len(text) > 0:
        if '\n' in text[:terminal_width+1]:
            crop_pos = text.find('\n')
            lines.append(text[:crop_pos])
            text = text[crop_pos+1:]
            if len(text) == 0:
                lines.append('')
        else:
            lines.append(text[:terminal_width])
            text = text[terminal_width:]
    return lines


def displayable_line_length(text: str) -> int:
    """
    Calculate the length of the displayable text by removing ANSI escape sequences and measuring the remaining
    characters.

    ANSI escape sequences are used to control text formatting and colors in terminal environments.
    These sequences do not contribute to the visual length of the text when displayed in modern systems.
    This function removes ANSI escape sequences from the input text and measures the length of the remaining characters
    (graphemes) to determine the length of the displayable text.

    Example:
        >> displayable_text_length("Hello, \x1B[1mworld!\x1B[0m")
        13
    """
    text = remove_ansi_escape_codes(text)
    return len(text)


def remove_ansi_escape_codes(text) -> str:
    """
    Remove ANSI escape codes from the input `text`.

    ANSI escape codes are used in terminal environments to add formatting and color to text.
    This function utilizes a regular expression to find and remove ANSI escape codes from the provided `text`.

    Example:
        >> remove_ansi_escape_codes("Hello, \x1B[1mworld!\x1B[0m")
        'Hello, world!'

    References:
        - ANSI Escape Sequences: https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
        - Regex reference: https://stackoverflow.com/questions/38982637/regex-to-match-any-character-or-none
    """
    ansi_escape = \
        re.compile(r'''
            \x1B  # ESC
            (?:   # 7-bit C1 Fe (except CSI)
                [@-Z\\-_]
            |     # or [ for CSI, followed by a control sequence
                \[
                [0-?]*  # Parameter bytes
                [ -/]*  # Intermediate bytes
                [@-~]   # Final byte
            |
                \(  # G0 character set
                [A-Za-z0-9]
            )   
        ''', re.VERBOSE)
    return ansi_escape.sub('', text)
