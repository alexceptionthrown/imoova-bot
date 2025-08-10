import requests
from bs4 import BeautifulSoup, Tag
import boto3

BASE_URL = "https://www.imoova.com/"
USA_URI = "/en/relocations?region=US"


def parse_offer(offer: Tag) -> dict[str, str]:
    origin_destination = [span.text for span in offer.find_all('span', class_="text-sm font-medium sm:text-base")]
    attributes = [
        div.text
        for div in offer.find(
            'div',
            class_='mb-3 flex flex-wrap items-center gap-3 border-b border-gray-100 pb-3 sm:mb-4 sm:gap-4 sm:pb-4'
        ).find_all('div')
    ]
    duration = offer.find(
        'span',
        class_="inline-flex items-center rounded-full border "
               "border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700 sm:px-3 sm:py-1.5"
    ).text
    offer_dict = {
        'id': offer['href'].split('/')[-1],
        'link': offer['href'],
        'img_url': offer.find("img")['src'],
        'title': offer.h2.text,
        'origin': origin_destination[0],
        'destination': origin_destination[1],
        'dates': offer.find('time').text,
        'seats': attributes[0],
        'duration': duration
    }
    return offer_dict


if __name__ == "__main__":
    page = requests.get(BASE_URL + USA_URI)
    soup = BeautifulSoup(page.content, 'html.parser')
    offer_class_type = ("focus:outline-hidden flex flex-col rounded-2xl focus:ring-2 "
                        "focus:ring-amber-400/50 focus:ring-offset-2 md:flex-row")
    offers = [parse_offer(offer) for offer in soup.find_all("a", class_=offer_class_type)]

    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:8000',
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy',
        region_name='local',
    )
    table = dynamodb.Table('imoova-US-offers')

    for offer in offers:
        query = table.get_item(Key={
            'id': offer['id'],
        })
        if 'Item' not in query:
            print(f"send offer {offer['title']}")
            table.put_item(Item=offer)


