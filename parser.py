import json
import os
from logging import Logger
from typing import cast

import requests
from PIL import Image

from database import Database


class Parser:

    def __init__(self, purity: str, to_page: int, logger: Logger) -> None:
        self.TOKEN: str = str(os.getenv("API_TOKEN", ""))

        self.headers: dict[str, str] = {
                    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }

        self.logger: Logger = logger

        self.page: int = 1
        self.to_page: int = to_page

        self.purity: str = purity.lower()

        self.path_db: str = "database/database.json"
        self.path: str = f"https://wallhaven.cc/api/v1/search?page={self.page}?apikey={self.TOKEN}"

        self.db: Database = Database("database/database.db", logger)

        self.num_img: int = 1

        self.session: requests.Session = requests.Session()
        self.session.headers.update(self.headers)

    def create_dirs(self):
        os.makedirs("src/sfw", exist_ok=True)
        os.makedirs("src/sketchy", exist_ok=True)
        os.makedirs("src/nsfw", exist_ok=True)
        os.makedirs("database", exist_ok=True)

    def get_purity(self):
        match self.purity:
            case "sfw":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=100&categories=111?apikey={self.TOKEN}&page={self.page}"

            case "sketchy":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=010&categories=111?apikey={self.TOKEN}&page={self.page}"

            case "nsfw":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=001&categories=111&apikey={self.TOKEN}&page={self.page}"

            case _:
                self.path = f"https://wallhaven.cc/api/v1/search?page={self.page}?apikey={self.TOKEN}"

    def log_image(self, image: dict[str, str]):
        self.logger.info(image["purity"])
        self.logger.info(image["url"])
        self.logger.info(image["category"])
        self.logger.info(f"Page: {self.page}")

    def compress_image(self, input_path: str, target_quality: int =75):
        try:
            with Image.open(input_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                self.logger.info(img.size)
                img.save(input_path, "JPEG",optimize=True, quality=target_quality)
        except Image.DecompressionBombWarning:
            self.logger.info(input_path)

    def download_images(self, data: dict[dict[str, str], str]) -> None:
        self.num_img = self.db.get_last_id(self.purity) + 1 if self.db.get_last_id(self.purity) > 1 else 1
        for image in data:
            save_path = f'src/{self.purity.lower()}/img{self.num_img}.jpg'
            if not self.db.has_item(image["id"]):
                path: str = str(image["path"])
                image_id = image["id"]
                self.log_image(image)
                image = self.session.get(path).content
                with open(save_path, 'wb') as o:
                    _ = o.write(image)
                self.compress_image(save_path, 80)
                self.db.add_to_database(self.num_img, image_id, save_path, self.purity)
                self.num_img += 1

    def get_images(self):
        while self.page <= self.to_page:
            self.get_purity()
            self.logger.info(self.path)
            response = self.session.get(self.path)
            data: dict[dict[str, str], str] = cast(dict[dict[str, str], str], json.loads(response.content)["data"])
            self.download_images(data)
            self.page += 1
