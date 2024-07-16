# PrettyPi

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/prettypi)
[![PyPI version](https://badge.fury.io/py/prettypy.svg)](https://badge.fury.io/py/prettypi)
![PyPI - License](https://img.shields.io/pypi/l/prettypi)
![PyPI - Downloads](https://img.shields.io/pypi/dm/prettypi)
![Doc - link](https://img.shields.io/badge/docs-pages-green?link=https%3A%2F%2Fglawnn.github.io%2FPrettyPi)



PrettyPi is a Python library for enhancing console output with colorful and style text, emojis, tables, and more.


## Features
- PrettyPrint
  - [x] **Emoji**: Add emojis to your console messages.
  - [x] **Color**: Easily print text in various colors.
  - [x] **Style**: Easily print text with style.
  - [x] **Background Color**: Print text with colored background.
  - [x] **Alignment**: Support text alignment (left, center, right).
  - [x] **Alert**: print alert messages
- PrettyTable
  - [ ] **Display**: Create and display tables in the console.
  - [ ] **Custom**: Customize table formatting and styles.
  - [ ] **Template**: Define and use templates for displaying tables.
  - [ ] **Sorting**: Implement sorting functionality for table columns.
  - [ ] **Filtering**: Add filtering capabilities to tables based on user-defined criteria.
  - [ ] **Pagination**: Enable pagination for large datasets displayed in tables.

## Installation
You can install PretiPy using pip:

```bash
pip install prettypi
```

## Usage
Here's a quick example of how to use PrettyPi:

### pretty_print
```python
from prettypi.pretty_print import StyledStr
from prettypi.pretty_print.utils import Color, Style, Emoji, BackgroundColor

styled_str = StyledStr("My name", background_color=BackgroundColor.MAGENTA, style=Style.UNDERLINE)
styled_str2 = StyledStr("Toto", color=Color.RED, style=Style.BOLD)

print(f"{styled_str} is {styled_str2} {Emoji.SMILE}")
```

