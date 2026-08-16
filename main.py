import os
import sys
import argparse
import time
import random
import logging
import bs4
import requests

logger = logging.getLogger(__name__)

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
                time.sleep(random.uniform(0.2, 0.8))
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

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("Wallhaven parser")
    arg_parser.add_argument("rating", type=str, help="Возрастное ограничение: sfw или sketchy")
    arg_parser.add_argument("pages", type=int, help="Количество страниц для обработки")
    args = arg_parser.parse_args()
    logging.basicConfig(filename='wallhaven_parser.log', level=logging.INFO)
    try:
        if len(sys.argv) < 3:
            raise Exception("Количество аргументов недостаточное для выполнения программы", sys.argv)
        parser = Parser(args.rating, args.pages)
        parser.parse_pages()
    except Exception as ex:
        print(ex)

