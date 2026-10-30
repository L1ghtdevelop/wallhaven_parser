import logging
from pathlib import Path

from dotenv import load_dotenv

from wallhaven_parser.controller import Controller
from wallhaven_parser.database import Database

logger = logging.getLogger(__name__)

_ = load_dotenv()


def overwrite_logs(path: Path) -> None:
    """Overwrite logs."""
    try:
        with path.open("w") as f:
            _ = f.write("")
    except FileExistsError:
        logger.exception("FileExistsError")

    except FileNotFoundError:
        logger.exception("FileNotFoundError")

def main() -> None:
    """Entry function."""
    log_path = Path("wallhaven_parser.log")
    overwrite_logs(log_path)
    logging.basicConfig(filename=log_path, level=logging.INFO)
    db = Database("database/database.db", logger)
    db.create_table()
    purity = input("Выберете возрастную категорию: sfw/sketchy/nsfw\n")
    try:
        if purity in ["sfw", "sketchy", "nsfw"]:
            controller = Controller(logger)
            controller.choose_type(purity)
    except TypeError:
        purity = input("Выберете возрастную категорию: sfw/sketchy/nsfw\n")
        logger.exception("Вы ввели недопустимое значение")
