import boto3
import datetime
from decimal import Decimal
import logging

# Configure the logging module
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table_name = 'DHT11'
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    # Log information using the logging module
    logger.info("EVENT")
    topic = event['topic']
    time_stamp = event['time_stamp']
    temperature = Decimal(event['temperature'])
    humidity = Decimal(event['humidity'])
    
    logger.info(time_stamp)
    
    # Write to DynamoDB
    table.put_item(
        Item={
            'time_stamp': time_stamp,
            'temperature': temperature,
            'humidity': humidity,
            'topic': topic
        }
    )
    
    logger.info('Done Inputting')