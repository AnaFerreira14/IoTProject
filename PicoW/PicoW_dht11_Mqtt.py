import machine
import network
import ssl
import ubinascii
from simple import MQTTClient
from machine import Pin
import dht
import time
import json



SSID = ""
WIFI_PASSWORD = ""
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_CLIENT_KEY = ""
MQTT_CLIENT_CERT = ""
MQTT_BROKER = ""
MQTT_BROKER_CA = "AmazonRootCA1.pem"

dht_pin = machine.Pin(2)
dht_sesnor = dht.DHT11(dht_pin)

def get_timestamp():
    # Get the current time in seconds since epoch
    t = time.localtime()  # Get local time tuple
    # Get microseconds since an arbitrary point
    microseconds = time.ticks_us() % 1000000  
    nanoseconds = microseconds * 1000  # Approximate nanoseconds
    
    # Format the timestamp: YYYY-MM-DD HH:MM:SS.NNNNNNNNN
    timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:09d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5], nanoseconds
    )
    return timestamp

def read_pem(file):
    with open(file, "r") as input:
        text = input.read().strip()
        split_text = text.split("\n")
        base64_text = "".join(split_text[1:-1])
        return ubinascii.a2b_base64(base64_text)

def connect_internet():
    try:
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(SSID, WIFI_PASSWORD)

        for i in range(0, 10):
            if not sta_if.isconnected():
                time.sleep(1)
        print("Connected to Wi-Fi")
    except Exception as e:
        print('There was an issue connecting to WIFI')
        print(e)


def publish_dht11_values():  
    
    try:
        dht_sesnor.measure()
        time_stamp = get_timestamp()
        payload = {
        "time_stamp": time_stamp,
        "temperature": dht_sesnor.temperature(),
        "humidity": dht_sesnor.humidity(),
        "topic": "DHT11"
        }
        
        mqtt_client.publish('DHT11', json.dumps(payload))
        print("PUBLISHED: ", str(payload))
          
    except Exception as e:
        print("Error reading DHT11", str(e))
           

connect_internet()

key = read_pem(MQTT_CLIENT_KEY)
cert = read_pem(MQTT_CLIENT_CERT)
ca = read_pem(MQTT_BROKER_CA)

mqtt_client = MQTTClient(
    MQTT_CLIENT_ID,
    MQTT_BROKER,
    keepalive=60,
    ssl=True,
    ssl_params={
        "key": key,
        "cert": cert,
        "server_hostname": MQTT_BROKER,
        "cert_reqs": ssl.CERT_REQUIRED,
        "cadata": ca,
    },
)


print(f"Connecting to MQTT broker")
mqtt_client.connect()
print("Done Connecting, sending Values")

while True:
    publish_dht11_values()
    time.sleep(0.1)


