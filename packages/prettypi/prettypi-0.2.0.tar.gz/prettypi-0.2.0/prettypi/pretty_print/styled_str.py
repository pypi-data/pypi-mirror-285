""" This module contains the StyledStr class."""

from .utils.ansi_codes import Color, Style, BackgroundColor, Align


class StyledStr:
    """This class represents a string with ANSI color and style codes.
    You can use this class to create a string with ANSI color and style codes.

    **Features:**

    - Set the color of the string.
    - Set the background color of the string.
    - Set the style of the string.

    :param string: The string to style
    :type string: str
    :param color: The color of the string, defaults to Color.RESET
    :type color: Color
    :param style: The style of the string, defaults to Style.RESET
    :type style: Style
    :param background_color: The background color of the string, defaults to BackgroundColor.RESET
    :type background_color: BackgroundColor

    :raises ValueError: If the input is invalid

    **Example:**

    .. code-block:: python

            from prettypi.pretty_print import StyledStr
            from prettypi.pretty_print.utils import Color, Style, Emoji, BackgroundColor

            print(StyledStr("This is a styled string", color=Color.RED, style=Style.BOLD))

    .. code-block:: python

            styled_str = StyledStr(
                "My name",
                background_color=BackgroundColor.MAGENTA,
                style=Style.UNDERLINE
            )
            styled_str2 = StyledStr("Toto", color=Color.RED, style=Style.BOLD)

            print(f"{styled_str} is {styled_str2} {Emoji.SMILE}")

    """

    def __init__(
        self,
        string: str = "",
        color: Color = Color.RESET,
        style: Style = Style.RESET,
        background_color: BackgroundColor = BackgroundColor.RESET,
    ):
        self.string = string
        self.color = color
        self.background_color = background_color
        self.style = style
        self.align = (Align.LEFT, None)
        self._check_input()

    def _check_input(self):
        """Check if the input is valid"""
        if not isinstance(self.string, str):
            raise ValueError(f"Invalid string: {self.string}")
        if not isinstance(self.color, Color):
            raise ValueError(f"Invalid color: {self.color}")
        if not isinstance(self.style, Style):
            raise ValueError(f"Invalid style: {self.style}")
        if not isinstance(self.background_color, BackgroundColor):
            raise ValueError(f"Invalid background color: {self.background_color}")
        if len(self.align) != 2 or not isinstance(self.align[0], Align):
            raise ValueError(f"Invalid align: {self.align}")
        if not isinstance(self.align[1], int) and self.align[1] is not None:
            raise ValueError(f"Invalid align: {self.align}")

    def set_color(self, color: Color):
        """Set the color of the string.

        :param color: The color of the string
        :type color: Color

        :raises ValueError: If the input is invalid

        **Example:**

        .. code-block:: python

                styled_str = StyledStr("This is a styled string")
                styled_str.set_color(Color.RED)
                print(styled_str)

        """
        self.color = color
        self._check_input()

    def set_background_color(self, background_color: Color):
        """Set the background color of the string.

        :param background_color: The background color of the string
        :type background_color: Color

        :raises ValueError: If the input is invalid

        **Example:**

        .. code-block:: python

                styled_str = StyledStr("This is a styled string")
                styled_str.set_background_color(BackgroundColor.RED)
                print(styled_str)

        """
        self.background_color = background_color
        self._check_input()

    def set_style(self, style: Style):
        """Set the style of the string.

        :param style: The style of the string
        :type style: Style

        :raises ValueError: If the input is invalid

        **Example:**

        .. code-block:: python

                styled_str = StyledStr("This is a styled string")
                styled_str.set_style(Style.BOLD)
                print(styled_str)

        """
        self.style = style
        self._check_input()

    def set_align(self, align: Align, width: int = None):
        """Set the alignment of the string.

        :param align: The alignment of the string
        :type align: Align
        :param width: The width of the max string, defaults to None
        :type width: int

        :raises ValueError: If the input is invalid

        **Example:**

        .. code-block:: python

                styled_str = StyledStr("This is a styled string")
                styled_str.set_align(Align.CENTER, 20)
                print(styled_str)

        """
        self.align = (align, width)
        self._check_input()

    def _len_without_ansi(self):
        """Return the length of the string without ANSI codes

        :return: The length of the string without ANSI codes
        :rtype: int
        """
        return len(self.string)

    def _align_string(self):
        """Align the string

        :return: The aligned string
        :rtype: str
        """
        if self.align[1] is None:
            return self.string

        direction, width = self.align
        if direction == Align.LEFT:
            return self.string.ljust(width)
        if direction == Align.CENTER:
            return self.string.center(width)
        return self.string.rjust(width)

    def __len__(self):
        return self._len_without_ansi()

    def __str__(self):
        parts = []

        string = self._align_string()

        if self.color != Color.RESET:
            parts.append(str(self.color))
        if self.style != Style.RESET:
            parts.append(str(self.style))
        if self.background_color != BackgroundColor.RESET:
            parts.append(str(self.background_color))

        if parts:
            return f"{''.join(parts)}{string}{Style.RESET}"
        return string
