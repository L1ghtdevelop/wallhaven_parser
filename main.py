from dotenv import load_dotenv
from manager import Manager
from sender import Sender
from database import Database

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
    manager = Manager(input("Что вы хотите сделать? Parse/Send\n"), logger)
    sender = Sender(logger)
    data = manager.choose_type()
    asyncio.run(sender.main(data[0], data[1]))

    
    
    

