from enum import IntEnum

from rich.console import Console

from netmon_proc.options import Opts
from netmon_proc.singleton import SingletonMeta


class LogLevel(IntEnum):
    INFO = 1
    WARN = 2
    ERROR = 3
    SUCCESS = 4


class Logger(metaclass=SingletonMeta):
    def __init__(self):
        self._opts = Opts()
        self._rich_console = Console()
        self._yaspin = None

    def set_yaspin(self, yaspin_controller):
        self._yaspin = yaspin_controller

    def log(self, level: LogLevel, msg: str, extra: bool = False):
        if extra and not self._opts.verbose():
            return

        style = ""
        symbol = ""
        if level == LogLevel.INFO:
            style = "bold cyan"
            symbol = "+"
        elif level == LogLevel.WARN:
            style = "bold yellow"
            symbol = "!"
        elif level == LogLevel.ERROR:
            style = "bold red"
            symbol = "!"
        elif level == LogLevel.SUCCESS:
            style = "bold green"
            symbol = "$"

        if self._yaspin is not None:
            with self._yaspin.hidden():
                self._rich_console.print(f"[{style}][{symbol}] {msg}[/{style}]")
        else:
            self._rich_console.print(f"[{style}][{symbol}] {msg}[/{style}]")
