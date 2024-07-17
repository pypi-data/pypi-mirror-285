"""Utils."""

import colorama


def warning(msg):
    """Print warning message."""
    print(colorama.Fore.YELLOW + "WARN\t" + colorama.Style.RESET_ALL + msg)


def critical(msg):
    """Print critical message."""
    print(colorama.Fore.RED + "CRIT\t" + colorama.Style.RESET_ALL + msg)


def success(msg):
    """Print critical message."""
    print(colorama.Fore.BLUE + "SUCC\t" + colorama.Style.RESET_ALL + msg)
