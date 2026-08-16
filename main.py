import os
import sys
import argparse
import time
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.types import InputMediaPhoto, FSInputFile
import asyncio
import logging
import json
import requests

logger = logging.getLogger(__name__)

load_dotenv()

class Parser_JSON:
    def __init__(self, rating, to_page) -> None:
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

    async def main(self):
        async with Bot(os.getenv("BOT_TOKEN")) as bot: # type: ignore
            await bot.send_photo(os.getenv("GROUP_ID"), FSInputFile("src/sketchy/img11.jpg")) # type: ignore


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("Wallhaven parser")
    arg_parser.add_argument("rating", type=str, help="Возрастное ограничение: sfw или sketchy")
    arg_parser.add_argument("pages", type=int, help="Количество страниц для обработки")
    args = arg_parser.parse_args()
    logging.basicConfig(filename='wallhaven_parser.log', level=logging.INFO)
    if len(sys.argv) < 3:
        raise Exception("Количество аргументов недостаточное для выполнения программы", sys.argv)
    parser = Parser_JSON(args.rating, args.pages)
    asyncio.run(parser.main())
    

