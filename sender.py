import aiogram.exceptions as ex
import os

from database import Database

from aiogram import Bot
from dotenv import load_dotenv
from time import sleep
from aiogram.types import InputMediaPhoto, FSInputFile
load_dotenv()

class Sender:
    def __init__(self, logger) -> None:
        self.logger = logger
        self.rating = {"nsfw": 239, "sketchy": 243, "sfw": 241}

        self.group_id: int = os.getenv("GROUP_ID") # type: ignore
        self.bot_token: str = os.getenv("BOT_TOKEN") # type: ignore
        self.db = Database("database/database.db", logger)
        
    def get_path_image(self, num, rate):
        path = f"src/{rate}/img{num}.jpg"
        return path

    def set_arr_images(self, rate, start, step):
        arr = []
        for j in range(start, start + step):
            self.logger.info(f"{start}, {start + step}")
            path = self.get_path_image(j, rate)
            self.logger.info(not self.db.is_sended(path))
            if not self.db.is_sended(path):
                photo = FSInputFile(path)
                arr.append(InputMediaPhoto(media=photo))
                self.db.mark_sended(path)
            else:
                self.logger.info("Это изображение отправлено")
                continue
        return arr

    async def main(self, num, rate):
        try:
            self.logger.info("Enter to main")
            self.logger.info("Connected to session")
            async with Bot(self.bot_token) as bot: 
                self.logger.info("Enter to Bot manager")
                start = 1
                step = 2
                max_num = (num // step) + 1
                for i in range(1, max_num):
                    try:
                        sleep(1)
                        arr = self.set_arr_images(rate, start, step)
                        await bot.send_media_group(self.group_id, media=arr, message_thread_id=self.rating[rate])
                        start += step
                        self.logger.info(f"Images group #{i} sended")
                    except ex.TelegramBadRequest as e:
                        self.logger.error(f"{e}")
                        print("Bad Request")
                        start += step
                    except ex.TelegramNetworkError as e:
                        self.logger.error(f"{e}")
                        print("Network Error")
                        continue

        except ex.TelegramBadRequest:
            self.logger.error(ex.TelegramBadRequest.url)
            print("Error")
