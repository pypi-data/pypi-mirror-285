""" This module contains the ANSI color and style codes that can be used in the pretty_print """

from enum import Enum


class Color(Enum):
    """This class contains ANSI color codes that can be used in the pretty print module.

    **Example:**

    .. code-block:: python

        from pretty_print import Color
        print(f"{Color.RED}This is a red text{Color.RESET}")

    """

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"

    def __str__(self):
        return self.value


class BackgroundColor(Enum):
    """This class contains ANSI color codes that can be used in the pretty print module.

    **Example:**

    .. code-block:: python

            from pretty_print import BackgroundColor
            print(f"{BackgroundColor.RED}This is a red background{BackgroundColor.RESET}")

    """

    BLACK = "\033[40m"
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    WHITE = "\033[47m"
    RESET = "\033[0m"

    def __str__(self):
        return self.value


class Style(Enum):
    """This class contains ANSI style codes that can be used in the pretty print module.

    **Example:**

    .. code-block:: python

            from pretty_print import Style
            print(f"{Style.BOLD}This is a bold text{Style.RESET}")

    """

    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    INVERT = "\033[7m"
    HIDDEN = "\033[8m"
    STRIKETHROUGH = "\033[9m"
    RESET = "\033[0m"

    def __str__(self):
        return self.value


class Align(Enum):
    """This class contains the alignment options that can be used in the pretty print module."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
