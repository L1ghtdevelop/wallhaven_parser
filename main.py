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

def job():
    asyncio.run(sender.main(data[0], data[1]))

if __name__ == "__main__":
    log_path = "wallhaven_parser.log"
    overwrite_logs(log_path)
    logging.basicConfig(filename=log_path, level=logging.INFO)
    db = Database("database/database.db", logger)
    db.create_table()
    manager = Controller(input("Что вы хотите сделать? Parse/Send\n"), logger)
    sender = Sender(logger)
    scheduler = Scheduler()
    data = manager.choose_type()
    if data:
        scheduler.daily(dt.time(hour=10), job)
        scheduler.daily(dt.time(hour=22), job)
        logger.info(scheduler)
    while True:
        scheduler.exec_jobs()
        sleep(1)

    
    
    

