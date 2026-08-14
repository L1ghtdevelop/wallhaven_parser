import os
import bs4
import requests

class Parser:
    def __init__(self, rating: str, nums_of_image: int) -> None:
        self.url = "https://wallhaven.cc/"
        self.headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.rating = rating
        self.nums_of_image = nums_of_image

    def get_url_rating(self):
        match self.rating.lower():
            case "sfw":
                self.url += "search?categories=111&purity=100"
            case "sketchy":
                self.url += "search?categories=111&purity=010"
            case "nsfw":
                self.url += "search?categories=111&purity=001"

    def get_images(self):
        self.get_url_rating()
        response = requests.get(self.url, headers=self.headers, timeout=10)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.content, "lxml")
        


