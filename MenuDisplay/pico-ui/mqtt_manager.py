import constants
import json
from adafruit_minimqtt.adafruit_minimqtt import MQTT

def connected(client, userdata, flags, rc):
  print("Connected to MQTT Broker!")
  client.subscribe(constants.WEATHER_TOPIC)    

def message(client, topic, message):
    try:
        payload = json.loads(message)
        print(payload)
    except ValueError as e:
        print(f"Failed to parse payload: ({e})")
        return
        
class MqttManager:
    def __init__(self, pool, ssl_connect):
        self.pool = pool
        self.ssl_context = ssl_connect
    
    def create_mqtt_client(self):
        mqtt_client = MQTT(
            broker=constants.MQTT_BROKER,
            port=constants.MQTT_PORT,
            socket_pool=self.pool,
            ssl_context=self.ssl_context,
            username=constants.MQTT_USERNAME,
            password=constants.MQTT_PASSWORD
        )
        
        mqtt_client.on_message = message
        mqtt_client.on_connect = connected
        mqtt_client.connect()

        mqtt_client.loop()
        
        return mqtt_client

