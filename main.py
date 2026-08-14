import logging
import httplib2
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
        self.pages = pages

    def get_url_rating(self):
        match self.rating.lower():
            case "sfw":
                self.url += "latest?categories=111&purity=100&sorting=date_added&order=desc&page=2"
            case "sketchy":
                self.url += "latest?categories=111&purity=010&sorting=date_added&order=desc&page=2"
            case "nsfw":
                self.url += "latest?categories=111&purity=001&sorting=date_added&order=desc&page=2"
    
    def get_link_images(self):
        self.get_url_rating()
        self.number = 1
        response = requests.get(self.url, headers=self.headers, timeout=10)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.content, "lxml")
        image_tag = soup.find_all('a')
        resource = self.get_image_page(image_tag)
        logger.info(resource)
        for image in resource:
            logger.info("enter")
            self.download_image(image)
            logger.info("exit")
        
    def get_image_page(self, images):
        img_arr = []
        for image_link in images:
            if image_link.has_attr("class") and image_link["class"][0] == "preview":
                link = str(image_link["href"])
                image_request = requests.get(link, headers=self.headers, timeout=10)
                soup = bs4.BeautifulSoup(image_request.content, "lxml")
                resource = soup.find_all("img")
                for img in resource:
                    if img.has_attr("id") and img["id"] == "wallpaper":
                        img_arr.append(img["src"])
        return img_arr

    def download_image(self, img):
        h = httplib2.Http('.cache')
        response, content = h.request(img)
        logger.info(img)
        logger.info(self.number)
        with open(f'src/img{self.number}.jpg', 'wb') as o:
            self.number += 1
            o.write(content)

if __name__ == "__main__":
    logging.basicConfig(filename='wallhaven_parser.log', level=logging.INFO)
    parser = Parser("sfw", 10)
    parser.get_link_images()


