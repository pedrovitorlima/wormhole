import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import asyncio
from gmqtt import Client as MQTTClient
import json
import logging

load_dotenv()

MQTT_BROKER = os.getenv("BROKER_NAME")
MQTT_PORT = 1883
MQTT_TOPIC = "prod/sensor_wormhole"
MQTT_USER = os.getenv("BROKER_USER")
MQTT_PASSWORD = os.getenv("BROKER_PASSWORD")
MQTT_CONSUMER_NAME = os.getenv("CONSUMER_NAME")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Receiver:
    def __init__(self, handle_message=None):
        self.client = MQTTClient("sensor_consumer")  # Replace with actual consumer name variable
        self.client.set_auth_credentials(MQTT_USER, MQTT_PASSWORD)  # Replace with secure retrieval of credentials
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.handle_message = handle_message

    async def connect(self):
        try:
            logger.info("Attempting to connect to MQTT broker...")
            await self.client.connect(MQTT_BROKER, MQTT_PORT)  # Replace with actual broker and port
            logger.info("Successfully connected to MQTT broker.")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    async def subscribe(self, topic):
        try:
            self.client.subscribe(topic)
            logger.info(f"Subscribed to topic: {topic}")
        except Exception as e:
            logger.error(f"Failed to subscribe to topic {topic}: {e}")
            raise

    def on_connect(self, client, flags, rc, properties):
        logger.info(f"Connected with result code {rc}")

    def on_message(self, client, topic, payload, qos, properties):
        logger.info(f"Received message on topic {topic}")
        try:
            message = json.loads(payload.decode())
            if self.handle_message:
                self.handle_message(message)
            else:
                logger.info(json.dumps(message, indent=2))
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload: {payload.decode()}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def on_disconnect(self, client, packet, exc=None):
        logger.warning("Disconnected from MQTT broker.")

    def on_subscribe(self, client, mid, qos, properties):
        logger.info(f"Successfully subscribed with message ID: {mid}")

    async def start(self):
        try:
            await self.connect()
            await self.subscribe(MQTT_TOPIC)  # Replace with actual topic variable
            logger.info("Receiver is running. Waiting for messages...")
            await asyncio.Event().wait()
        except Exception as e:
            logger.error(f"An error occurred in the Receiver: {e}")
        finally:
            await self.shutdown()

    async def shutdown(self):
        try:
            await self.client.disconnect()
            logger.info("Disconnected from MQTT broker.")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

