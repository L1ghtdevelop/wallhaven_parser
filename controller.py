from parser import Parser
from sender import Sender

import asyncio

class Controller:
    def __init__(self, logger) -> None:
        self.logger = logger

    def parse(self, rating):
        try:
            self.pages = 1
            parser = Parser(rating, self.pages, self.logger)
            parser.create_dirs()
            parser.get_images()
            print("Success")
            self.logger.info(f"Success, parsed pages: {self.pages}")
        except TypeError:
            print("Вы ввели недопустимые значения")
            self.logger.error(f"Значения недопустимы:\nrating={rating}\npages={self.pages}")

    def send(self, rating):
        try:
            self.num = 20
            sender = Sender(self.logger)
            asyncio.run(sender.main(self.num, rating))
        except TypeError:
            print("Вы ввели недопустимые значения")
            self.logger.error(f"Значения недопустимы:\nnums={self.num}")

    def choose_type(self, type, rating):
        try:
            if type == "parse":
                self.parse(rating)

            elif type == "send":
                self.send(rating)
            else:
                raise TypeError
        except TypeError:
            print("Вы ввели недопустимые значения")
            self.logger.error(f"Значения недопустимы: {rating}")
            return []