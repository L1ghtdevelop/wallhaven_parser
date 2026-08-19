import asyncio
from parser import Parser

class Manager:
    def __init__(self, type: str, logger) -> None:
        self.type = type.lower()
        self.logger = logger

    def choose_type(self, main):
        if self.type == "parse":
            try:
                self.rating = input("Введите возрастное ограничение: sfw/sketchy/nsfw\n").lower()
                self.pages = int(input("Введите количество страниц для парсинга: "))
                parser = Parser(self.rating, self.pages, self.logger)
                parser.create_dirs()
                parser.get_images()
                print("Success")
                self.logger.info(f"Success, parsed pages: {self.pages}")
            except TypeError:
                print("Вы ввели недопустимые значения")
                self.logger.error(f"Значения недопустимы:\nrating={self.rating}\npages={self.pages}")

        elif self.type == "send":
            try:
                self.num = int(input("Сколько картинок, хотите, отправить?\n"))
                self.rating = input("Какие картинки вы хотите отправить? sfw/sketchy/nsfw\n").lower()
                asyncio.run(main(self.num, self.rating))
            except TypeError:
                print("Вы ввели недопустимые значения")
                self.logger.error(f"Значения недопустимы:\nnums={self.num}")