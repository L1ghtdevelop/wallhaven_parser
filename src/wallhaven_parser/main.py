import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from wallhaven_parser.controller import Controller
from wallhaven_parser.database import Database
from wallhaven_parser.parser import Parser

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

async def main() -> None:
    """Entry function."""
    log_path = Path("wallhaven_parser.log")
    overwrite_logs(log_path)
    logging.basicConfig(filename=log_path, level=logging.INFO)
    db = Database("database/database.db", logger)
    db.delete_table()
    db.create_table()
    parser = Parser("sketchy", 5, logger)
    task = asyncio.create_task(parser.async_get_images())
    await task

def run() -> None:
    asyncio.run(main())

    # purity = input("Выберете возрастную категорию: sfw/sketchy/nsfw\n")
    # try:
    #     if purity in ["sfw", "sketchy", "nsfw"]:
    #         controller = Controller(logger)
    #         controller.choose_type(purity)
    # except TypeError:
    #     purity = input("Выберете возрастную категорию: sfw/sketchy/nsfw\n")
    #     logger.exception("Вы ввели недопустимое значение")
