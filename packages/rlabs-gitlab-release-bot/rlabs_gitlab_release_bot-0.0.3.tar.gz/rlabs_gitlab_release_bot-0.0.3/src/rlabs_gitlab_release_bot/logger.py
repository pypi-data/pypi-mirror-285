#
# Copyright (C) 2024 RomanLabs, Rafael Roman Otero
# This file is part of RLabs Gitlab Release Bot.
#
# RLabs Gitlab Release Bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RLabs Gitlab Release Bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with RLabs Gitlab Release Bot. If not, see <http://www.gnu.org/licenses/>.
#
'''
    logger.py
'''
import logging
import json
import rich
from rich.logging import RichHandler
from rich.traceback import install

from rlabs_gitlab_release_bot import config

def enable_pretty_tracebacks() -> None:
    '''
        Enable Pretty Traceback

        Uses rich to print pretty tracebacks
    '''
    install()

def stdout(name: str, log_level: int) -> logging.Logger:
    '''
        Sets up a logger that logs to stdout

        Uses RichHandler to pretty print logs
    '''
    words_to_highlight = config.log_words_to_highlight

    handler = RichHandler(
        show_time=config.log_show_time,
        keywords=[w.lower() for w in words_to_highlight] + \
                 [w.upper() for w in words_to_highlight] + \
                 [w.capitalize() for w in words_to_highlight]
    )

    logger = CustomLogger(name)
    logger.setLevel(log_level)
    formatter = logging.Formatter(config.log_formatter)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

class CustomLogger(logging.Logger):
    '''
        Extends the logging.Logger class
        with  custom methods
    '''
    def flush(self) -> None:
        '''
            Flush

            Flushes the logger
        '''
        for handler in self.handlers:
            handler.flush()

    def write_json_to_file(self, file_name: str, obj: object, indent: int) -> None:
        '''
            Writes JSON to a File
        '''
        file_path = f"{config.log_dir / file_name}.json"

        self.debug(f"Writing JSON object to {file_path}")

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(
                json.dumps(obj, indent=indent)
            )

    def debug_json(self, obj: object, indent: int) -> None:
        '''
            Debug JSON

            Logs a JSON object at DEBUG level
        '''
        self.debug(
            json.dumps(obj, indent=indent)
        )

    def info_json(self, obj: object, indent: int) -> None:
        '''
            Warning INFO

            Logs a JSON object at INFO level
        '''
        self.info(
            json.dumps(obj, indent=indent)
        )

    def warning_json(self, obj: object, indent: int) -> None:
        '''
            Warning JSON

            Logs a JSON object at WARNING level
        '''
        self.warning(
            json.dumps(obj, indent=indent)
        )

    def inspect(obj: object, title: str) -> None:
        '''
            Inspect

            Wrapper for rich's inspect
        '''
        rich.inspect(
            obj,
            title=title,
            docs=False
        )
