import os
from asyncio import sleep
from logging import Logger

import aiogram.exceptions as ex
from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.types.media_union import MediaUnion
from dotenv import load_dotenv

from database import Database

_ = load_dotenv()

class Sender:
    def __init__(self, logger: Logger) -> None:
        self.logger: Logger = logger
        self.purity: dict[str, int] = {"nsfw": int(os.getenv("NSFW_TOPIC", "1")),
                                        "sketchy": int(os.getenv("SKETCHY_TOPIC", "2")),
                                        "sfw": int(os.getenv("SFW_TOPIC", "3"))}
        self.group_id: int = int(os.getenv("GROUP_ID", "-100"))
        self.bot_token: str = os.getenv("BOT_TOKEN", "")
        self.db: Database = Database("database/database.db", logger)

    def get_path_image(self, num: int, purity: str) -> str:
        path = f"src/{purity}/img{num}.jpg"
        return path

    def set_arr_images(self, purity: str, start: int, step: int) -> list[MediaUnion]:
        arr: list[MediaUnion] = []
        for j in range(start, start + step):
            self.logger.info(f"{start}, {start + step}")
            path = self.get_path_image(j, purity)
            self.logger.info(not self.db.is_sended(path))
            if not self.db.is_sended(path):
                photo = FSInputFile(path)
                arr.append(InputMediaPhoto(media=photo))
                self.db.mark_sended(path)
            else:
                self.logger.info("Это изображение отправлено")
                continue
        return arr

    async def main(self, num: int, purity: str) -> None:
        try:
            self.logger.info("Enter to main")
            self.logger.info("Connected to session")
            async with Bot(self.bot_token) as bot:
                self.logger.info("Enter to Bot manager")
                start: int = 1
                step: int = 2
                max_num: int = (num // step) + 1
                for i in range(1, max_num):
                    try:
                        await sleep(1)
                        arr = self.set_arr_images(purity, start, step)
                        _ = await bot.send_media_group(self.group_id, media=arr, message_thread_id=self.purity[purity])
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
