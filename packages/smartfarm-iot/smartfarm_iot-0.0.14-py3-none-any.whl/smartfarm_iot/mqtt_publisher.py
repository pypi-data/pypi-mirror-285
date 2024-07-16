import json
import paho.mqtt.client as mqtt

MQTT_BROKER = "mqtt.yourbroker.com"
MQTT_PORT = 1883
MQTT_TOPIC = "smartfarm/data"

def setup_mqtt_client():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    return client

def publish_data(client, payload):
    client.publish(MQTT_TOPIC, json.dumps(payload))
    print(f"Published data: {json.dumps(payload)}")

