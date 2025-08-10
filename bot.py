# This is the code for the AWS Lambda function
import boto3
import asyncio
import logging
from telegram import Bot

ssm = boto3.client('ssm', 'us-east-2')


def lambda_handler(event, context):
    bot_token = ssm.get_parameter(Name='telegramBotToken', WithDecryption=True)['Parameter']['Value']
    channel_id = ssm.get_parameter(Name='telegramImoovaUSChannelID', WithDecryption=True)['Parameter']['Value']

    asyncio.run(main(bot_token, channel_id))


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def main(token: str, channel_id: str) -> None:
    async with Bot(token) as bot:
        await bot.send_message(channel_id, "Hello World!")

