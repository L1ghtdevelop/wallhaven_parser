import json
import os
import logging
import requests
from PIL import Image

class Parser:

    def __init__(self, rating: str, to_page: int, logger) -> None:
        self.TOKEN = os.getenv("API_TOKEN")
        self.headers = {
                    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
        self.logger = logger
        self.page = 1
        self.num_img = 1
        self.to_page = to_page
        self.rating = rating.lower()
        self.path_db = "data/database.json"
        self.path = f"https://wallhaven.cc/api/v1/search?page={self.page}?apikey={self.TOKEN}"
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def create_dirs(self):
        os.makedirs("src/sfw", exist_ok=True)
        os.makedirs("src/sketchy", exist_ok=True)
        os.makedirs("src/nsfw", exist_ok=True)
        os.makedirs("data", exist_ok=True)

    def add_to_database(self, id, url):
        try:
            with open(self.path_db, "r") as f:
                data = json.load(f)
        except (FileExistsError, json.JSONDecodeError):
            data = {}

        if id in data:
            self.logger.warning("Такой элемент уже существует")
            return False

        data[id] = url
        with open(self.path_db, "w") as f:
            json.dump(data, f, indent=4)
            return True

    def get_purity(self):
        match self.rating:
            case "sfw":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=100&categories=111?apikey={self.TOKEN}&page={self.page}"

            case "sketchy":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=010&categories=111?apikey={self.TOKEN}&page={self.page}"

            case "nsfw":
                self.path = f"https://wallhaven.cc/api/v1/search?purity=001&categories=111&apikey={self.TOKEN}&page={self.page}"

            case _:
                self.path = f"https://wallhaven.cc/api/v1/search?page={self.page}?apikey={self.TOKEN}"

    def log_image(self, image):
        self.logger.info(image["purity"])
        self.logger.info(image["url"])
        self.logger.info(image["category"])
        self.logger.info(f"Page: {self.page}")

    def validate_image(self, path) -> bool:
        try:
            with Image.open(path) as img:
                w, h = img.size

                if w < 32 or h < 32:
                    self.logger.warning(f"Изображение слишком маленькое: {w}x{h}")
                    os.remove(path)
                    return False
                
                elif w > 10000 or h > 10000:
                    self.logger.warning(f"Изображение слишком большое: {w}x{h}")
                    img.thumbnail((2560, 2560))
                    img.save(path, quality=85)
                    return True
                
                elif img.mode == "RGBA":
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                    img.save(path)
                    return True
                
        except Exception as ex:
            self.logger.warning(f"Невалидное изображение: {ex}")
            os.remove(path)
            return False
        
        return True

    def compress_image(self, input_path, target_quality=75):
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            self.logger.info(img.size)
            img.save(input_path, "JPEG",optimize=True, quality=target_quality)


    def download_images(self, data):
        for image in data:
            save_path = f'src/{self.rating.lower()}/img{self.num_img}.jpg'
            if self.add_to_database(image["id"], image["url"]):
                path = image["path"]
                self.log_image(image)
                image = self.session.get(path).content
                with open(save_path, 'wb') as o:
                    o.write(image)
                self.compress_image(save_path, 80)
                self.num_img += 1

    def get_images(self):
        while self.page <= self.to_page:
            self.get_purity()
            self.logger.info(self.path)
            response = self.session.get(self.path)
            json_data = json.loads(response.content)
            data = json_data["data"]
            self.download_images(data)
            self.page += 1