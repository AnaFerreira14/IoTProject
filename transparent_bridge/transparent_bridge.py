import MQTTSNclient
from MQTTSNclient import Client
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import json
import boto3

DYNAMO_TABLE = ""
DYNAMO_REGION = ""

MQTT_CLIENT_ID  = ""
MQTT_TOPIC = ""

AWS_HOST = ""
AWS_ROOT_CA = ""
AWS_CERT = ""
AWS_PRIVATE_KEY = ""
AWS_PORT = 8883

MQTTSN_CLIENT_ID = ""
MQTTSN_PORT = 1885

class DynamoDBConnector:
    def __init__(self, region, table):
        self.region = region
        self.table = table
        self.dynamo_resource = boto3.resource('dynamodb', region_name=self.region)
        self.table = self.dynamo_resource.Table(self.table_name)

    def store_item(self, item):
        try:
            self.table.put_item(Item=item)
            print(f"Item stored in DynamoDB: {item}")
        except Exception as e:
            print(f"Error storing item in DynamoDB: {e}")

class MQTTClientHandler:
    def __init__(self, client_id, host, port, root_ca, cert, key):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.root_ca = root_ca
        self.cert = cert
        self.key = key
        self.client = AWSIoTMQTTClient(self.client_id)
        self.configure_client()
    
    def configure_client(self):
        self.client.configureEndpoint(self.host, self.port)
        self.client.configureCredentials(self.root_ca, self.key, self.cert)
        self.client.configureAutoReconnectBackoffTime(2, 30, 15)
        self.client.configureOfflinePublishQueueing(-1)
        self.client.configureDrainingFrequency(3)
        self.client.configureConnectDisconnectTimeout(15)
        self.client.configureMQTTOperationTimeout(4)
    
    def connect(self):
        self.client.connect()
    
    def publish(self, topic, payload, qos):
        self.client.publish(topic, payload, qos)

class MQTTSNClientHandler:
    def __init__(self, client_id, port):
        self.client_id = client_id
        self.port = port
        self.client = MQTTSNclient.Client(self.client_id, port=self.port)
        self.configure_client()
    
    def configure_client(self):
        self.client.registerCallback(MessageHandler())
        self.client.connect()
    
    def subscribe(self, topic):
        self.client.subscribe(topic)
    
    def disconnect(self):
        self.client.disconnect()

class MessageHandler:
    def on_message(self, topic_name, payload, qos, retained, msgid):
        payload_json = json.loads(payload)
        print(f"Message received on topic '{topic_name}': {payload}")
        mqtt_client.publish(MQTT_TOPIC, payload, qos)
        dynamo_connector.store_item(payload_json)
        return True

def setup_logging():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.NOTSET, format=log_format)

setup_logging()
mqtt_client = MQTTClientHandler(MQTT_CLIENT_ID, AWS_HOST, AWS_PORT, AWS_ROOT_CA, AWS_CERT, AWS_PRIVATE_KEY)
mqtt_client.connect()

dynamo_connector = DynamoDBConnector(region=DYNAMO_REGION, table_name=DYNAMO_TABLE)

mqtt_sn_client = MQTTSNClientHandler(client_id=MQTTSN_CLIENT_ID, port=MQTTSN_PORT)
mqtt_sn_client.subscribe(MQTT_TOPIC)

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Terminating the connection...")

mqtt_sn_client.disconnect()
mqtt_client.client.disconnect()