# imoova-bot
Telegram Bot hosted on AWS which sends new [Imoova](https://www.imoova.com/en) posts to a Telegram channel 

## AWS install Steps
Reproduce these steps to install the bot on AWS

### SSM Secure String Parameter store
We are using this storage instead of AWS's proper secret manager because it is much cheaper and we do not need
the added benefits of Secret Manager such as key rotation, etc. since we are only using it to store API keys
- add bot token as a secure string
- add channel id as a secure string

### AWS IAM 
- Configure [Policy](aws_config/AccessTelegramSSMSecretsPolicy.json) for access to SSM secrets
- Configure Role for Lambda Function
  - DynamoDB
  - Secrets Policy

### AWS DynamoDB
- create new table with name imoova-US-offers, Key {'id': N, 'hash': S}. A composite key is required because Imoova 
reuses ids

### AWS Lambda
- Create Lambda Function with Python 3.13 using 1769 MB memory (exactly 1vCPU core) and 512 MB ephemeral storage
- Add layers for SSM (AWS provided), Telegram and scraping (Custom Layers to upload to AWS)

### AWS EventBridge
- Add scheduled event to trigger AWS Lambda every x minutes

## Testing environment
We provide a [local testing script](src/imoova-bot/local_lambda_test.py) which calls the AWS lambda function 
while mocking SSM and DynamoDB to local alternatives.

We recommend you use a local DynamoDB like the include [docker container config](dev_config/dynamodb/docker-compose.yml), 
As well as [NoSQL Workbench](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/workbench.html)
to configure your stored local table.

## Possible Future features:
- Also scrape secondary features like last possible drop off date, max mileage, fuel reimbursement, etc.
- Add alarm for when scraper has failed to find any for posts for x amount of time

## Known Issues
- If the async call to telegram api fails or partly fails, new posts will still have been written to DynamoDB,
So they will not be sent on the next lambda call.
- We have not tested if an exception during lambda call is picked up as an error by AWS cloudwatch metrics
- Vans with start date today get reposted every night at midnight
