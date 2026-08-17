import os
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.types import InputMediaPhoto, FSInputFile
from aiogram.client.session.aiohttp import AiohttpSession
import aiogram.exceptions as ex
import asyncio
import logging
import json
import requests

logger = logging.getLogger(__name__)

load_dotenv()

class Parser_JSON:
    def __init__(self, rating: str, to_page: int) -> None:
        self.TOKEN = os.getenv("API_TOKEN")
        self.headers = {
                    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
        self.page = 1
        self.num_img = 1
        self.to_page = to_page
        self.rating = rating.lower()
        self.path_db = "database.json"
        self.path = f"https://wallhaven.cc/api/v1/search?page={self.page}?apikey={self.TOKEN}"
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def add_to_database(self, id, url):
        try:
            with open(self.path_db, "r") as f:
                data = json.load(f)
        except (FileExistsError, json.JSONDecodeError):
            data = {}

        if id in data:
            logger.warning("Такой элемент уже существует")
            return False

        data[id] = url
        with open(self.path_db, "w") as f:
            json.dump(data, f, indent=4)
            return True

    def get_purity(self):
        match self.rating:
            case "sfw":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=100&categories=111?apikey={self.TOKEN}&page={self.page}"

            case "sketchy":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=010&categories=111?apikey={self.TOKEN}&page={self.page}"

            case "nsfw":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=001&categories=111&apikey={self.TOKEN}&page={self.page}"

            case _:
                self.path = f"https://wallhaven.cc/api/v1/search?page={self.page}?apikey={self.TOKEN}"

    def download_images(self, data):
        for image in data:
            if self.add_to_database(image["id"], image["url"]):
                path = image["path"]
                logger.info(image["purity"])
                logger.info(image["url"])
                logger.info(image["category"])
                logger.info(f"Page: {self.page}")
                image = self.session.get(path).content
                with open(f'src/{self.rating.lower()}/img{self.num_img}.jpg', 'wb') as o:
                    self.num_img += 1
                    o.write(image)

    def get_images(self):
        while self.page <= self.to_page:
            self.get_purity()
            logger.info(self.path)
            response = self.session.get(self.path)
            json_data = json.loads(response.content)
            data = json_data["data"]
            self.download_images(data)
            self.page += 1

class Manager:
    def __init__(self, type: str) -> None:
        self.type = type.lower()

    def do_parse(self):
        try:
            self.rating = input("Введите возрастное ограничение: sfw/sketchy/nsfw").lower()
            self.pages = int(input("Введите количество страниц для парсинга: "))
            parser = Parser_JSON(self.rating, self.pages)
            parser.get_images()
            print("Success")
            logger.info(f"Success, parsed pages: {self.pages}")
        except TypeError:
            print("Вы ввели недопустимые значения")
            logger.error(f"Значения недопустимы:\nrating={self.rating}\npages={self.pages}")

    def send_images(self):
            try:
                self.num = int(input("Сколько картинок, хотите, отправить?\n"))
                self.rating = input("Какие картинки вы хотите отправить? sfw/sketchy/nsfw\n").lower()
                asyncio.run(main(self.num, self.rating))
            except TypeError:
                print("Вы ввели недопустимые значения")
                logger.error(f"Значения недопустимы:\nnums={self.num}")
    
    def choose_type(self):
        if self.type == "parse":
            self.do_parse()

        elif self.type == "send":
            self.send_images()

def get_path_image(num, rate):
    path = f"src/{rate}/img{num}.jpg"
    return path

async def main(num, rate):
    try:
        session = AiohttpSession("socks5://gqVMrB:poFSJJ@45.147.180.18:8000")
        async with Bot(os.getenv("BOT_TOKEN"), session=session) as bot: # type: ignore
            for i in range(1, num+1):
                try:
                    path = get_path_image(i, rate)
                    await bot.send_photo(os.getenv("GROUP_ID"), FSInputFile(path)) # type: ignore
                except ex.TelegramBadRequest:
                    logger.error(f"PHOTO_INVALID_DIMENSIONS\n{path}") # type: ignore
                    print("Error")
                    continue
                except ex.TelegramNetworkError:
                    logger.error(f"Can`t send image\n{path}")# type: ignore
                    print("Error")
                    continue

    except ex.TelegramBadRequest:
        logger.error(ex.TelegramBadRequest.url)
        print("Error")


if __name__ == "__main__":
    logging.basicConfig(filename='wallhaven_parser.log', level=logging.INFO)
    manager = Manager(input("Что вы хотите сделать? Parse/Send\n"))
    manager.choose_type()
    
    

