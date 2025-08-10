# imoova-bot
Telegram Bot hosted on AWS which sends new Imoova posts to Telgram channel 

## AWS install Steps
Reproduce these steps to install the bot on AWS

### SSM Secure String Parameter store
We are using this storage instead of AWS's proper secret manager because it is much cheaper and we do not need
the added benefits of Secret Manager such as key rotation, etc. since we are only using it to store API keys
- add bot token as a secure string
- add channel id as a secure string

### AWS IAM 
- Configure Policy for access to SSM secrets
- Configure Role for Lambda Function
  - DynamoDB
  - Secrets Policy

### AWS Lambda
- Create Lambda Function with Python 3.13
- Add layers for SSM (AWS provided), Telegram and scraping (Custom Layers to upload to AWS)
