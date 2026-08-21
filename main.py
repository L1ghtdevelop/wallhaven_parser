from dotenv import load_dotenv
from controller import Controller
from sender import Sender
from database import Database

import datetime as dt
from scheduler import Scheduler
from time import sleep

import asyncio
import logging

logger = logging.getLogger(__name__)

load_dotenv()


def overwrite_logs(path):
    try:
        with open(path, "w") as f:
            f.write("")
    except FileExistsError as e:
        logger.error(e)

    except FileNotFoundError as e:
        logger.error(e)

if __name__ == "__main__":
    log_path = "wallhaven_parser.log"
    overwrite_logs(log_path)
    logging.basicConfig(filename=log_path, level=logging.INFO)
    db = Database("database/database.db", logger)
    db.create_table()
    scheduler = Scheduler()
    rating = input("Выберете возрастную категорию: sfw/sketchy/nsfw\n")
    controller = Controller(logger)
    scheduler.daily(dt.time(hour=9), controller.choose_type, kwargs={"type": "parse", "rating": rating})
    scheduler.daily(dt.time(hour=10), controller.choose_type, kwargs={"type": "send", "rating": rating})
    scheduler.daily(dt.time(hour=20), controller.choose_type, kwargs={"type": "parse", "rating": rating})
    scheduler.daily(dt.time(hour=21), controller.choose_type, kwargs={"type": "send", "rating": rating})
    logger.info(scheduler)
    while True:
        scheduler.exec_jobs()
        sleep(1)

    
    
    

