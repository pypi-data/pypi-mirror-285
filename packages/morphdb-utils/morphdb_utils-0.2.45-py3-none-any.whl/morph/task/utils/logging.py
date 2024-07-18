import logging
from typing import TextIO

import colorlog


class PrefixedStream(object):
    """メッセージにプレフィックスを付与するためのストリーム"""

    def __init__(self, original_stream: TextIO, prefix: str) -> None:
        self.original_stream = original_stream
        self.prefix = prefix

    def write(self, message: str) -> None:
        # 空のメッセージ（例えば改行のみ）をフィルタリング
        if message.strip() != "":
            message = f"{self.prefix}{message}"
        self.original_stream.write(message)

    def flush(self) -> None:
        self.original_stream.flush()


def get_morph_logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger(log_file)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(file_handler)

        # Console handler with colorlog
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "cyan",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


class LogPrefix:
    SQL = "[SQL]"
