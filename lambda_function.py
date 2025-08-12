# This is the code for the AWS Lambda function
import requests
from bs4 import BeautifulSoup, Tag
import boto3
import asyncio
import logging
from telegram import Bot
from telegram.constants import ParseMode

BASE_URL = "https://www.imoova.com/"
USA_URI = "/en/relocations?region=US"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


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
        'id': int(offer['href'].split('/')[-1]),
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


def generate_image_caption(offer: dict[str, str]) -> str:
    caption = (
        f"<b>{offer['title']}</b>\n\n"
        f"📍  From: {offer['origin']} -> To: {offer['destination']}\n"
        f"📅  Dates: {offer['dates']}\n"
        f"💺  Seats: {offer['seats']}\n"
        f"⏱️  Duration: {offer['duration']}\n"
        f"🔗  <a href=\"{BASE_URL + offer['link']}\">View Offer</a>"
    )
    return caption


async def send_offers_to_telegram(token: str, channel_id: str, offers: list[dict[str, str]]) -> None:
    async with Bot(token) as bot:
        for offer in offers:
            await bot.send_photo(chat_id=channel_id,
                                 photo=offer["img_url"],
                                 caption=generate_image_caption(offer),
                                 parse_mode=ParseMode.HTML
                                 )


async def report_exception_to_telegram(token: str, channel_id: str, exc: Exception) -> None:
    async with Bot(token) as bot:
        await bot.send_message(channel_id, f"Error raised: {exc}")


def lambda_handler(event, context):
    ssm = boto3.client('ssm', 'us-east-2')
    bot_token = ssm.get_parameter(Name='telegramBotToken', WithDecryption=True)['Parameter']['Value']
    channel_id = ssm.get_parameter(Name='telegramImoovaUSChannelID', WithDecryption=True)['Parameter']['Value']

    try:
        page = requests.get(BASE_URL + USA_URI)
        soup = BeautifulSoup(page.content, 'html.parser')
        offer_class_type = ("focus:outline-hidden flex flex-col rounded-2xl focus:ring-2 "
                            "focus:ring-amber-400/50 focus:ring-offset-2 md:flex-row")
        offers = [parse_offer(offer) for offer in soup.find_all("a", class_=offer_class_type)]
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('imoova-US-offers')

        new_offers = []
        for offer in offers:
            query = table.get_item(Key={
                'id': offer['id'],
            })
            if 'Item' not in query:
                new_offers.append(offer)
                table.put_item(Item=offer)
        asyncio.run(send_offers_to_telegram(bot_token, channel_id, new_offers))
    except Exception as e:
        logger.error(e)
        asyncio.run(report_exception_to_telegram(bot_token, channel_id, e))
