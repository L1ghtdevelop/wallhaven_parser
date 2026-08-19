from dotenv import load_dotenv
from aiogram import Bot
from aiogram.types import InputMediaPhoto, FSInputFile
from aiogram.client.session.aiohttp import AiohttpSession
from time import sleep
from parser import Parser
from manager import Manager
import aiogram.exceptions as ex
import logging

logger = logging.getLogger(__name__)

load_dotenv()

def get_path_image(num, rate):
    path = f"src/{rate}/img{num}.jpg"
    return path

def set_arr_images(rate, start, step):
    arr = []
    for j in range(start, start + step):
        logger.info(f"{start}, {start + step}")
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
            start = 1
            step = 2
            max_num = (num // step) + 1
            for i in range(1, max_num):
                path = get_path_image(num, rate)
                try:
                    sleep(1)
                    arr = set_arr_images(rate, start, step)
                    logger.info(len(arr))
                    await bot.send_media_group(os.getenv("GROUP_ID"), arr) # type: ignore
                    start += step
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
    manager = Manager(input("Что вы хотите сделать? Parse/Send\n"), logger)
    manager.choose_type(main)
    
    

