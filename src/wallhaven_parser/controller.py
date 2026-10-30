import asyncio
from logging import Logger
from pathlib import Path

from wallhaven_parser.parser import Parser
from wallhaven_parser.sender import Sender


class Controller:
    def __init__(self, logger: Logger) -> None:
        """Initialize class controller."""
        self.logger: Logger = logger
        self.pages: int = 1
        self.num: int = 20
        self.create_dirs()

    def create_dirs(self) -> None:
        Path("images/").mkdir(exist_ok=True)
        Path("images/sfw/").mkdir(exist_ok=True)
        Path("images/sketchy/").mkdir(exist_ok=True)
        Path("images/nsfw/").mkdir(exist_ok=True)
        Path("database").mkdir(exist_ok=True)

    def parse(self, purity: str) -> None:
        try:
            self.pages = int(input("Сколько страниц вы хотите спарсить?\n"))
            parser = Parser(purity, self.pages, self.logger)
            parser.get_images()
            self.logger.info("Success")
            self.logger.info("Success, parsed pages: %d", self.pages)
        except TypeError:
            self.logger.exception("Значения недопустимы:\npurity=%s\npages=%d",
                purity, self.pages)

    def send(self, purity: str) -> None:
        try:
            sender = Sender(self.logger)
            asyncio.run(sender.main(self.num, purity))
        except TypeError:
            self.logger.exception("Значения недопустимы:\nnums=%d", self.num)

    def choose_type(self, purity: str) -> None:
            job = input("Что вы хотите сделать? parse/send\n").lower()
            self.choose_job(job, purity)

    def choose_job(self, job: str, purity: str) -> None:
        try:
            if job == "parse":
                self.parse(purity)
            elif job == "send":
                self.send(purity)
        except TypeError:
            self.logger.exception("Значения недопустимы: %s", purity)
