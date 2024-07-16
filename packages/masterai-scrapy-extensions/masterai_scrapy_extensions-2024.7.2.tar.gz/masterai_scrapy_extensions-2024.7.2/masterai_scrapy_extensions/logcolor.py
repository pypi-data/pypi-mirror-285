from __future__ import annotations

import logging

import colorlog
import scrapy.utils.log
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy.utils.log import get_scrapy_root_handler
from typing_extensions import Self

DEFAULT_FORMAT = (
    "%(light_black)s%(asctime)s%(reset)s "
    "%(light_black)s[%(name)s]%(reset)s "
    "%(log_color)s%(levelname)s%(reset)s%(light_black)s:%(reset)s "
    "%(message)s"
)

DEFAULT_DATEFORMAT = "%Y-%m-%d %H:%M:%S"

DEFAULT_COLORS = {"DEBUG": "blue", "INFO": "cyan", "WARNING": "yellow", "ERROR": "red", "CRITICAL": "purple"}


class ColoredFormatter(colorlog.ColoredFormatter):
    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls.from_settings(crawler.settings)

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:
        return cls(
            fmt=settings.get("COLORLOG_FORMAT", DEFAULT_FORMAT),
            datefmt=settings.get("COLORLOG_DATEFORMAT", DEFAULT_DATEFORMAT),
            log_colors=settings.getdict("COLORLOG_COLORS", DEFAULT_COLORS),
            secondary_log_colors=settings.getdict("COLORLOG_SECONDARY_COLORS"),
            reset=settings.getbool("COLORLOG_RESET", True),
            no_color=settings.getbool("COLORLOG_NO_COLOR", False),
            force_color=settings.getbool("COLORLOG_FORCE_COLOR", False),
        )


def configure_logging(settings: Settings | dict | None = None, install_root_handler: bool = True) -> None:
    if isinstance(settings, dict) or settings is None:
        settings = Settings(settings)
    scrapy.utils.log.configure_logging(settings, install_root_handler)
    replace_scrapy_root_handler_formatter(settings)


def install_scrapy_root_handler(settings: Settings) -> None:
    scrapy.utils.log.install_scrapy_root_handler(settings)
    replace_scrapy_root_handler_formatter(settings)


def replace_scrapy_root_handler_formatter(settings: Settings) -> None:
    handler = get_scrapy_root_handler()
    if handler and isinstance(handler, logging.StreamHandler) and not isinstance(handler.formatter, ColoredFormatter):
        formatter = ColoredFormatter.from_settings(settings)
        formatter.stream = handler.stream
        handler.setFormatter(formatter)


def log_color_init() -> None:
    from scrapy import crawler

    crawler.configure_logging = configure_logging
    crawler.install_scrapy_root_handler = install_scrapy_root_handler
