from espmega.espmega_r3 import ESPMega
from paho.mqtt.client import Client as MQTTClient

client = MQTTClient()
client.connect("192.168.0.26", 1883)
client.loop_start()
espmega1 = ESPMega("/espmega/ProR3",client)
