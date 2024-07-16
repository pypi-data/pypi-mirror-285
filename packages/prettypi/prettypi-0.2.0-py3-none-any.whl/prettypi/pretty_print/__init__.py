""" prettypi.pretty_print module helps you to print easily styled messages.

- Use the StyledStr class to print styled messages.
    - Color the text.
    - Set the background color of the text.
    - Set the style of the text.
    - Align the text.
- Use the Alert class to print alerts.
    - Information alert.
    - Warning alert.
    - Error alert.
    - Success alert.
    - Custom alert.

"""

from prettypi.pretty_print.styled_str import StyledStr
from prettypi.pretty_print.alert import Alert

__all__ = ["StyledStr", "Alert"]
