from dotenv import load_dotenv
from aiogram import Bot
from aiogram.types import InputMediaPhoto, FSInputFile
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import encode_basic_auth
from time import sleep
from PIL import Image
import os
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
        self.path_db = "data/database.json"
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

    def log_image(self, image):
        logger.info(image["purity"])
        logger.info(image["url"])
        logger.info(image["category"])
        logger.info(f"Page: {self.page}")

    def validate_image(self, path) -> bool:
        try:
            with Image.open(path) as img:
                w, h = img.size

                if w < 32 or h < 32:
                    logger.warning(f"Изображение слишком маленькое: {w}x{h}")
                    os.remove(path)
                    return False
                
                elif w > 10000 or h > 10000:
                    logger.warning(f"Изображение слишком большое: {w}x{h}")
                    img.thumbnail((2560, 2560))
                    img.save(path, quality=85)
                    return True
                
                elif img.mode == "RGBA":
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                    img.save(path)
                    return True
                
        except Exception as ex:
            logger.warning(f"Невалидное изображение: {ex}")
            os.remove(path)
            return False
        
        return True

    def download_images(self, data):
        for image in data:
            save_path = f'src/{self.rating.lower()}/img{self.num_img}.jpg'
            if self.add_to_database(image["id"], image["url"]):
                path = image["path"]
                self.log_image(image)
                image = self.session.get(path).content
                with open(save_path, 'wb') as o:
                    o.write(image)
            self.validate_image(save_path)
            self.num_img += 1

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
            self.rating = input("Введите возрастное ограничение: sfw/sketchy/nsfw\n").lower()
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

def set_arr_images(rate, start, stop):
    arr = []
    for j in range(start, stop):
        logger.info(f"{start}, {stop}")
        path = get_path_image(j, rate)
        logger.info(path)
        arr.append(InputMediaPhoto(media=FSInputFile(path)))
    return arr

async def main(num, rate):# type: ignore
    try:
        logger.info("Enter to main")
        session = AiohttpSession(os.getenv("PROXY")) # type: ignore
        logger.info("Connected to session")
        async with Bot(os.getenv("BOT_TOKEN"), session=session) as bot: # type: ignore
            logger.info("Enter to Bot manager")
            max_num = (num // 5) + 1
            start = 1
            stop = 6
            for i in range(1, max_num):
                path = get_path_image(num, rate)
                try:
                    sleep(1)
                    arr = set_arr_images(rate, start, stop)
                    await bot.send_media_group(os.getenv("GROUP_ID"), arr) # type: ignore
                    start = stop
                    stop += 5
                    logger.info(f"Images group #{i} sended")
                except ex.TelegramBadRequest as e:
                    logger.error(f"{e}\n{path}\n") # type: ignore
                    print("Error")
                    continue
                except ex.TelegramNetworkError as e:
                    logger.error(f"{e}\n{path}")# type: ignore
                    print("Error")
                    continue

    except ex.TelegramBadRequest:
        logger.error(ex.TelegramBadRequest.url)
        print("Error")

def overwrite_logs(path):
    try:
        with open(log_path, "w") as f:
            f.write("")
    except FileExistsError as e:
        logger.error(e)

    except FileNotFoundError as e:
        logger.error(e)

if __name__ == "__main__":
    log_path = "wallhaven_parser.log"
    overwrite_logs(log_path)
    logging.basicConfig(filename=log_path, level=logging.INFO)
    manager = Manager(input("Что вы хотите сделать? Parse/Send\n"))
    manager.choose_type()
    
    

