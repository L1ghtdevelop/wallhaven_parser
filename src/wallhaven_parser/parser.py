import json
import os
from logging import Logger
from pathlib import Path
from typing import cast

import requests
from fake_useragent import UserAgent
from PIL import Image

from wallhaven_parser.database import Database


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

    def get_purity(self) -> None:
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
            Category: %s
            Page: %s""", {image["purity"]}, {image["url"]},
            {image["category"]}, {self.page})

    def compress_image(self, input_path: Path, target_quality: int =75) -> None:
        try:
            with Image.open(input_path) as img:
                processed = img.convert("RGB") if img.mode in ("RGBA", "B") else img
                self.logger.info(img.size)
                processed.save(input_path, "JPEG",optimize=True, quality=target_quality)
        except Image.DecompressionBombWarning:
            self.logger.info(input_path)

    def download_images(self, data: dict[dict[str, str], str]) -> None:
        # Получает список, который можно получить в функции get_images
        if self.db.get_last_id(self.purity) > 1:
            self.num_img = self.db.get_last_id(self.purity) + 1
        else:
            self.num_img = 1
        for image in data:
            save_path = Path(f"images/{self.purity.lower()}/img{self.num_img}.jpg")
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
            self.get_purity()
            self.logger.info(self.path)
            response = self.session.get(self.path)
            data: dict[dict[str, str], str] = (
                cast("dict[dict[str, str], str]", json.loads(response.content)["data"])
            )
            self.download_images(data)
            self.page += 1
