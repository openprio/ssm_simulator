# This file helps to send simulated SSM messages.
import paho.mqtt.publish as publish
from datetime import datetime
import os
import logging
import certifi
import inquirer

logging.basicConfig(level=logging.DEBUG)

host = os.getenv("MQTT_HOST")
device_id = os.getenv("MQTT_DEVICE_ID")
password = os.getenv("MQTT_PASSWORD")

logger = logging.getLogger(__name__)

questions = [
  inquirer.Text('data_owner_code', message="Dataownercode"),
  inquirer.Text('vehicle_number', message="Dataownercode of bus")
]
answers = inquirer.prompt(questions)

data_owner_code = answers["data_owner_code"]
vehicle_number = answers["vehicle_number"]
topic = "/prod/pt/ssm/%s/vehicle_number/%s" % (data_owner_code, vehicle_number)

def send_ssm_message(type_msg_answer):
    publish.single(topic, payload=type_msg_answer, tls={"ca_certs":certifi.where(), "insecure": True}, 
        hostname=host, port=8883, client_id=device_id, auth={"username": device_id, "password": password})

while True:
    questions = [
    inquirer.List('type',
        message="What type of message do you want to send?",
        choices=['UNKNOWN', 'REQUESTED', 'PROCESSING', 'WATCHOTHERTRAFFIC', 'GRANTED', 'REJECTED', 'MAXPRESENCE', 'RESERVICELOCKED'],
    ),
    ]
    type_msg_answer = inquirer.prompt(questions)
    logging.info("Send ssm %s", type_msg_answer["type"])
    send_ssm_message(type_msg_answer["type"])
    logging.info("Send msg succesfully")
