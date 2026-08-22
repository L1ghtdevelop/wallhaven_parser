from dotenv import load_dotenv
from controller import Controller
from database import Database

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
    rating = input("Выберете возрастную категорию: sfw/sketchy/nsfw\n")
    controller = Controller(logger)

    
    
    

