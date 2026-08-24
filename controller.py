import asyncio
from logging import Logger

from parser import Parser
from sender import Sender


class Controller:
    def __init__(self, logger: Logger) -> None:
        self.logger: Logger = logger
        self.pages: int = 1
        self.num: int = 20

    def parse(self, purity: str):
        try:
            self.pages = int(input("Сколько страниц вы хотите спарсить?\n"))
            parser = Parser(purity, self.pages, self.logger)
            parser.create_dirs()
            parser.get_images()
            print("Success")
            self.logger.info(f"Success, parsed pages: {self.pages}")
        except TypeError:
            print("Вы ввели недопустимые значения")
            self.logger.error(f"Значения недопустимы:\npurity={purity}\npages={self.pages}")

    def send(self, purity: str):
        try:
            sender = Sender(self.logger)
            asyncio.run(sender.main(self.num, purity))
        except TypeError:
            print("Вы ввели недопустимые значения")
            self.logger.error(f"Значения недопустимы:\nnums={self.num}")

    def choose_type(self, purity: str):
            job = input("Что вы хотите сделать? parse/send\n").lower()
            self.choose_job(job, purity)

    def choose_job(self, job: str, purity: str) -> None:
        try:
            if job == "parse":
                self.parse(purity)

            elif job == "send":
                self.send(purity)
            else:
                raise TypeError
        except TypeError:
            print("Вы ввели недопустимые значения")
            self.logger.error(f"Значения недопустимы: {purity}")
