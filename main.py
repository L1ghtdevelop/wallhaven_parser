import os
import sys
import argparse
import time
from dotenv import load_dotenv
import logging
import json
import bs4
import requests

logger = logging.getLogger(__name__)

load_dotenv()

class Parser:
    def __init__(self, rating: str, pages: int) -> None:
        self.url = "https://wallhaven.cc/"
        self.headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.rating = rating
        self.to_pages = pages
        self.page = 1
        self.num_img = 1
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_url_rating(self):
        match self.rating.lower():
            case "sfw":
                self.url = f"https://wallhaven.cc/search?categories=111&purity=100&sorting=date_added&order=desc&page={self.page}"
            case "sketchy":
                self.url = f"https://wallhaven.cc/search?categories=111&purity=010&sorting=date_added&order=desc&page={self.page}"

    def get_page_list(self):
        logger.info(self.url)
        time.sleep(0.5)
        response = self.session.get(self.url, headers=self.headers, timeout=30)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.content, "lxml")
        return soup.find_all('a')

    def get_image_page(self, images):
        img_arr = []
        for image_link in images:
            if image_link.has_attr("class") and image_link["class"][0] == "preview":
                logger.info(image_link)
                link = str(image_link["href"])
                time.sleep(1)
                image_response = self.session.get(link, headers=self.headers, timeout=30)
                if image_response.status_code == 429:
                    wait = int(image_response.headers.get('Retry-After', 5))
                    logger.warning(f"429 on {link}, waiting {wait}")
                    time.sleep(wait)
                    continue
                image_response.raise_for_status()
                soup = bs4.BeautifulSoup(image_response.content, "lxml")
                resource = soup.find_all("img")
                for img in resource:
                    if img.has_attr("id") and img["id"] == "wallpaper":
                        img_arr.append(img["src"])
        return img_arr

    def download_image(self, images):
        for img in images:
            link = self.session.get(img)
            self.open_write_file(link.content)

    def open_write_file(self, content):
        with open(f'src/{self.rating.lower()}/img{self.num_img}.jpg', 'wb') as o:
            self.num_img += 1
            o.write(content)

    def parse_pages(self):
        self.get_url_rating()

        while self.page <= self.to_pages:
            os.makedirs(f"src/{self.rating}", exist_ok=True)
            resource = self.get_page_list()
            images = self.get_image_page(resource)
            self.download_image(images)
            logger.info("Image downloaded")
            self.page += 1
            self.get_url_rating()

class Parser_JSON:
    def __init__(self, rating, to_page) -> None:
        self.TOKEN = os.getenv("API_TOKEN")
        self.headers = {
                    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
        self.page = 1
        self.num_img = 1
        self.to_page = to_page
        self.rating = rating.lower()
        self.path = f"https://wallhaven.cc/api/v1/search?page={self.page}?apikey={self.TOKEN}"
        self.session = requests.Session()
        self.session.headers.update(self.headers)

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


    def download_images(self):
        while self.page <= self.to_page:
            self.get_purity()
            logger.info(self.path)
            response = self.session.get(self.path)
            json_data = json.loads(response.content)
            data = json_data["data"]
            for image in data:
                path = image["path"]
                logger.info(image["purity"])
                logger.info(image["url"])
                logger.info(image["category"])
                logger.info(f"Page: {self.page}")
                image = self.session.get(path).content
                with open(f'src/{self.rating.lower()}/img{self.num_img}.jpg', 'wb') as o:
                    self.num_img += 1
                    o.write(image)
            self.page += 1

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("Wallhaven parser")
    arg_parser.add_argument("rating", type=str, help="Возрастное ограничение: sfw или sketchy")
    arg_parser.add_argument("pages", type=int, help="Количество страниц для обработки")
    args = arg_parser.parse_args()
    logging.basicConfig(filename='wallhaven_parser.log', level=logging.INFO)
    if len(sys.argv) < 3:
        raise Exception("Количество аргументов недостаточное для выполнения программы", sys.argv)
    parser = Parser_JSON(args.rating, args.pages)
    parser.download_images()

