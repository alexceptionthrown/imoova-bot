import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://www.imoova.com/en/relocations?region=US"


def parse_offer(offer: Tag) -> dict[str, str]:
    offer_dict = {}
    offer_dict['link'] = offer['href']
    offer_dict['id'] = offer['href'].split('/')[-1]



if __name__ == "__main__":
    page = requests.get(BASE_URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    offer_class_type = ("focus:outline-hidden flex flex-col rounded-2xl focus:ring-2 "
                        "focus:ring-amber-400/50 focus:ring-offset-2 md:flex-row")
    offers = soup.find_all("a", class_=offer_class_type)
    for offer in offers:
        print(offer.text)
