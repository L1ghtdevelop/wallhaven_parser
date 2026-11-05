import asyncio
import json
import os
from logging import Logger
from pathlib import Path

import aiofiles
import aiohttp
import requests
from fake_useragent import UserAgent
from PIL import Image

from wallhaven_parser.database import Database

SUCCESS_RESPONSE = 200

class Parser:

    def __init__(self, purity: str, to_page: int, logger: Logger) -> None:
        """Initialize parser settings."""
        self.TOKEN: str = str(os.environ.get("API_TOKEN", ""))
        self.user_agent = UserAgent().random
        self.headers: dict[str, str] = {
            "User-Agent": self.user_agent,
                }

        self.logger: Logger = logger

        self.page: int = 1
        self.to_page: int = to_page

        self.purity: str = purity.lower()

        self.path_db: str = "database/database.json"
        self.header_api = "https://wallhaven.cc/api/v1/search?"
        self.path: str = f"{self.header_api}page={self.page}&apikey={self.TOKEN}"

        self.db: Database = Database("database/database.db", logger)

        self.num_img: int = 1

        self.session: requests.Session = requests.Session()
        self.session.headers.update(self.headers)

    def get_link_response(self) -> str:
        return self.path

    def get_format_data(self) -> list:
        response = self.session.get(self.path)
        data = json.loads(response.content)["data"]
        result = []
        for element in data:
            res = {"id": element["id"],
                "path": element["path"],
                "purity": element["purity"],
                "url": element["url"],
            }
            result.append(res)
        return result

    def get_save_path(self) -> Path:
        return Path(f"images/{self.purity.lower()}/img{self.num_img}.jpg")

    def update_path(self) -> None:
        """Set a purity for a parse images."""
        match self.purity:
            case "sfw":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=100&categories=111&apikey={self.TOKEN}&page={self.page}"

            case "sketchy":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=010&categories=111&apikey={self.TOKEN}&page={self.page}"

            case "nsfw":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=001&categories=111&apikey={self.TOKEN}&page={self.page}"

            case _:
                self.path = f"https://wallhaven.cc/api/v1/search?page={self.page}&apikey={self.TOKEN}"

    def log_image(self, image: dict[str, str]) -> None:
        self.logger.info("""Purity: %s
            URL: %s
            Page: %s""", image["purity"], image["url"], self.page)

    def compress_image(self, input_path: Path, target_quality: int =75) -> None:
        try:
            with Image.open(input_path) as img:
                processed = img.convert("RGB") if img.mode in ("RGBA", "B") else img
                self.logger.info(img.size)
                processed.save(input_path, "JPEG",optimize=True, quality=target_quality)
        except Image.DecompressionBombWarning:
            self.logger.info(input_path)

    def set_num_img(self) -> None:
        if self.db.get_last_id(self.purity) > 1:
            self.num_img = self.db.get_last_id(self.purity) + 1
        else:
            self.num_img = 1

    def download_images(self, data: list) -> None:
        # Получает список, который можно получить в функции get_images
        self.set_num_img()
        for image in data:
            save_path = self.get_save_path()
            if not self.db.has_item(image["id"]):
                path: str = str(image["path"])
                image_id = image["id"]
                self.log_image(image)
                web_image = self.session.get(path).content
                with save_path.open("wb") as o:
                    _ = o.write(web_image)
                self.compress_image(save_path, 80)
                self.db.add_to_database(self.num_img, image_id,
                    save_path.anchor, self.purity)
                self.num_img += 1

    def get_images(self) -> None:
    # Парсит запрос и выдает список, который можно отдать функции скачивания картинок
        while self.page <= self.to_page:
            self.update_path()
            self.logger.info(self.path)
            self.download_images(self.get_format_data())
            self.page += 1

    async def async_get_images(self) -> None:
        async with aiohttp.ClientSession() as session:
            while self.page <= self.to_page:
                tasks = []
                self.update_path()
                response = await session.get(self.path)
                data = await response.json()
                for element in data["data"]:
                    task = self.async_download_image(element, session)
                    tasks.append(task)
                await asyncio.gather(*tasks)
                self.page += 1

    async def async_download_image(self, image: dict,
        session: aiohttp.ClientSession) -> None:
        if not self.db.has_item(image["id"]):
            resource = await session.get(image["path"])
            content = await resource.content.read()
            async with aiofiles.open(self.get_save_path(), "wb") as file:
                self.logger.info(image)
                self.logger.info(resource)
                await file.write(content)
                self.num_img += 1
