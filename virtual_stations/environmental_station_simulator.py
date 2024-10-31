from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from random import randint
import math
import sys
import logging
import time
import json
import datetime
import argparse
import boto3
import parser

import csv

csv_file_path = '../../Ana_accessKeys.csv'

with open(csv_file_path, 'r') as csvfile:
    csv_reader = csv.reader(csvfile)

    # Skip the first line (header)
    header = next(csv_reader, None)

    # Read the second line
    second_line = next(csv_reader, None)

    if second_line:
        aws_access_key_id = second_line[0]
        aws_secret_access_key = second_line[1]

boto3.setup_default_session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='eu-north-1'  # Replace with your actual AWS region
)

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')                    # connection to DynamoDB and access
dynamoTable = dynamodb.Table('EnvironmentalStationData')                                     # to the table EnvironmentalStation that will store the data provided
jsonP = '';                                                                         # by the two simulated stations

def data_store(client, userdata, msg):                                              # the function stores the recieved data in the DynamoDB table
    payload = str(msg.payload)[2:-1]
    jsonP = json.loads(payload)
    dynamoTable.put_item(Item=jsonP)


def send_data(myClient, data, topic):                                               # the function publishes the recieved data
    messageJson = json.dumps(data)
    myClient.publish(topic, messageJson, 1)
    print("########## DATA RECEIVED ##########")
    print("Published on topic: %s\nData provided by: %s\nReceived data:\n%s\n" % (topic, clientId, messageJson))
    print("I'm sending the data to DynamoDB... \n \n")

def random_values():                                                                 # the function provides in a simple way random environmental values...
    temperature = str(randint(-50,50))
    humidity = str(randint(0, 100))
    wind_direction = str(randint(0, 360))
    wind_intensity = str(randint(0, 100))
    rain_height = str(randint(0, 50))
    datatime = str(datetime.datetime.now())[:19]                                     #... and take notice about the time of the detection, that is important for data storing in the table

    return temperature, humidity, wind_direction, wind_intensity, rain_height, datatime

def awsconnection(useWebsocket = False,                                          # the function sets the connection to AWS
    clientId = "",                                                               # client id
    thingName = "EnvironmentData",                                               # thing name (on AWS)
    host = "aa1tbm5ptngoj-ats.iot.eu-north-1.amazonaws.com",                                                      # your AWS endpoint
    caPath = "../EnvironmentDataThingCertificatesAndKeys/AmazonRootCA1.pem",                                             # rootCA certificate (folder's path)
    certPath = "../EnvironmentDataThingCertificatesAndKeys/b416e148c61ebe8d203fb2ee55bc4f3ae541f5c60fdc007e8b02db211a922149-certificate.pem.crt",                       # client certificate (folder's path)
    keyPath = "../EnvironmentDataThingCertificatesAndKeys/b416e148c61ebe8d203fb2ee55bc4f3ae541f5c60fdc007e8b02db211a922149-private.pem.key"                             # private key (folder's path)
    ):

    port = 8883 if not useWebsocket else 443
    useWebsocket = useWebsocket
    clientId = clientId
    host = host
    port = port
    rootCaPath = caPath
    privateKeyPath = keyPath
    certificatePath = certPath

    # Logger settings
    # more information at https://docs.python.org/3/library/logging.html
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.NOTSET)                                                      # NOTSET causes all messages to be processed when the logger is the root logger
    streamHandler = logging.StreamHandler()                                              # sends logging output to streams
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    # AWSIoTMQTTClient initialization
    myClient = None
    if useWebsocket:
        myClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
        myClient.configureEndpoint(host, port)
        myClient.configureCredentials(rootCaPath)
    else:
        myClient = AWSIoTMQTTClient(clientId)
        myClient.configureEndpoint(host, port)
        myClient.configureCredentials(rootCaPath, privateKeyPath, certificatePath)

    # AWSIoTMQTTClient connection configuration
    myClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myClient.configureOfflinePublishQueueing(-1)      # param: if set to 0, the queue is disabled. If set to -1, the queue size is set to be infinite.
    myClient.configureDrainingFrequency(2)            # Draining: 2 Hz
    myClient.configureConnectDisconnectTimeout(10)    # 10 sec
    myClient.configureMQTTOperationTimeout(5)         # 5 sec

    return myClient


# Arguments passing: in this case the only argument that we need is the clientId, that is supposed to be station1 or station2
parser = argparse.ArgumentParser()
parser.add_argument('--clientid', type=str)
args = parser.parse_args()
clientId = args.clientid
topic = "EnvironmentData"


myClient =  awsconnection(clientId=clientId)
myClient.connect()
myClient.subscribe(topic, 1, data_store)

# Every 5 seconds, random data are generated, sent and published
while True:

    temperature, humidity, wind_direction, wind_intensity, rain_height, datatime = random_values()

    data = {"ID":clientId, "timestamp":datatime, "Temperature":temperature, "Humidity":humidity,
           "WindDirection":wind_direction, "WindIntensity":wind_intensity, "RainHeight":rain_height}

    send_data(myClient, data, topic)

    time.sleep(5)

myClient.disconnect()
