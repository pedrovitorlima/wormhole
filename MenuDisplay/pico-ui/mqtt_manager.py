import constants
import json
from adafruit_minimqtt.adafruit_minimqtt import MQTT

weather = {}
dishwasher = {}

def connected(client, userdata, flags, rc):
  print("Connected to MQTT Broker!")
  client.subscribe(constants.WEATHER_TOPIC)    
  client.subscribe(constants.DISHWASHER_TOPIC)    

def message(client, topic, message):
    try:
        payload = json.loads(message)
        print(payload)
        
        if (topic == constants.WEATHER_TOPIC):
            global weather
            weather = payload
        elif (topic == constants.DISHWASHER_TOPIC):
            global dishwasher
            dishwasher = payload
    except ValueError as e:
        print(f"Failed to parse payload: ({e})")
        return
        
class MqttManager:
    def __init__(self, pool, ssl_connect):
        self.pool = pool
        self.ssl_context = ssl_connect
        self.mqtt_client = None
    
    def create_mqtt_client(self):
        mqtt_client = MQTT(
            broker=constants.MQTT_BROKER,
            port=constants.MQTT_PORT,
            socket_pool=self.pool,
            ssl_context=self.ssl_context,
            username=constants.MQTT_USERNAME,
            password=constants.MQTT_PASSWORD
        )
        
        self.mqtt_client = mqtt_client
        
        mqtt_client.on_message = message
        mqtt_client.on_connect = connected
        mqtt_client.connect()
        
        self.load_initial_data()
        return mqtt_client

    def load_initial_data(self):
        print("Sending message to load initial data")
        self.mqtt_client.publish(constants.ACTION_TOPIC, json.dumps({"command": "load_all"}))
    
    def update_dishwasher(self, data):
        print("Updating dishwasher data:", data)
        self.mqtt_client.publish(constants.DISHWASHER_TOPIC, json.dumps(data))
        global dishwasher 
        dishwasher = data
