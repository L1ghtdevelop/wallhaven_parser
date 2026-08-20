import aiogram.exceptions as ex
import os

from aiogram import Bot
from time import sleep
from aiogram.types import InputMediaPhoto, FSInputFile
from aiogram.client.session.aiohttp import AiohttpSession


class Sender:
    def __init__(self, logger) -> None:
        self.logger = logger
        self.rating = {"nsfw": 239, "sketchy": 243, "sfw": 241}
        
    def get_path_image(self, num, rate):
        path = f"src/{rate}/img{num}.jpg"
        return path

    def set_arr_images(self, rate, start, step):
        arr = []
        for j in range(start, start + step):
            self.logger.info(f"{start}, {start + step}")
            path = self.get_path_image(j, rate)
            self.logger.info(path)
            arr.append(InputMediaPhoto(media=FSInputFile(path)))
        return arr

    async def main(self, num, rate):# type: ignore
        try:
            self.logger.info("Enter to main")
            session = AiohttpSession() # type: ignore
            self.logger.info("Connected to session")
            async with Bot(os.getenv("BOT_TOKEN"), session=session) as bot: # type: ignore
                self.logger.info("Enter to Bot manager")
                start = 1
                step = 2
                max_num = (num // step) + 1
                for i in range(1, max_num):
                    path = self.get_path_image(num, rate)
                    try:
                        sleep(1)
                        arr = self.set_arr_images(rate, start, step)
                        self.logger.info(len(arr))
                        await bot.send_media_group(os.getenv("GROUP_ID"), arr, message_thread_id=self.rating[rate]) # type: ignore
                        start += step
                        self.logger.info(f"Images group #{i} sended")
                    except ex.TelegramBadRequest as e:
                        self.logger.error(f"{e}\n{path}\n") # type: ignore
                        print("Error")
                        continue
                    except ex.TelegramNetworkError as e:
                        logger.error(f"{e}\n{path}")# type: ignore
                        print("Error")
                        continue

        except ex.TelegramBadRequest:
            self.logger.error(ex.TelegramBadRequest.url)
            print("Error")
