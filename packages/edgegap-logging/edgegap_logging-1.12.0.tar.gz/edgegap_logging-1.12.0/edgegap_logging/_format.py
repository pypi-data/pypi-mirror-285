import sys
from typing import Any

from colorama import Fore as Color


class Format:
    BOLD = '\033[1m'
    END = '\033[0m'
    use_colors = sys.stdout.isatty()

    @classmethod
    def color(cls, value: Any, color: Color = None, bold: bool = False) -> str:
        if not cls.use_colors:
            return value

        prefix = ''
        suffix = ''

        if bold:
            prefix += cls.BOLD
            suffix += cls.END

        if color:
            prefix += str(color)
            suffix += str(Color.RESET)

        return f'{prefix}{value}{suffix}'

    @classmethod
    def squared(cls, value: Any, color: Color = None):
        return f'[{cls.color(value, color)}]'

    @classmethod
    def curled(cls, value: Any, color: Color = None):
        return '{' + f'{cls.color(value, color)}' + '}'

    @classmethod
    def parentheses(cls, value: Any, color: Color = None):
        return f'({cls.color(value, color)})'
