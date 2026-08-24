import logging

from dotenv import load_dotenv

from controller import Controller
from database import Database

logger = logging.getLogger(__name__)

_ = load_dotenv()


def overwrite_logs(path: str):
    try:
        with open(path, "w") as f:
            _ = f.write("")
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
    purity = input("Выберете возрастную категорию: sfw/sketchy/nsfw\n")
    try:
        if purity == "sfw" or purity == "sketchy" or purity == "nsfw":
            pass
        else:
            raise TypeError
    except TypeError:
        print("Вы ввели недопустимое значение")
        purity = input("Выберете возрастную категорию: sfw/sketchy/nsfw\n")
        logger.error("Вы ввели недопустимое значение")
    controller = Controller(logger)
    controller.choose_type(purity)
