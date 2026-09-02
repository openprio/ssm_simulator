# This file helps to send simulated SSM messages.
import paho.mqtt.client as mqtt
from datetime import datetime
import os
import logging
import certifi
import inquirer
import build.gen.ssm_pb2 as ssm

logging.basicConfig(level=logging.DEBUG)


host = os.getenv("MQTT_HOST")
device_id = os.getenv("MQTT_DEVICE_ID")
password = os.getenv("MQTT_PASSWORD")

logger = logging.getLogger(__name__)

missing_vars = [name for name, value in [
    ("MQTT_HOST", host),
    ("MQTT_DEVICE_ID", device_id),
    ("MQTT_PASSWORD", password),
] if not value]

if missing_vars:
    logger.error(
        "Missing required MQTT environment variables: %s. "
        "Please set them before running, e.g.:\n%s",
        ", ".join(missing_vars),
        "\n".join("  export %s=<value>" % var for var in missing_vars),
    )
    exit(1)

questions = [
  inquirer.Text('data_owner_code', message="Dataownercode"),
  inquirer.Text('vehicle_number', message="Vehicle number of bus"),
  inquirer.List('environment', message="Environment",
      choices=['test', 'prod'], default='test'),
]
answers = inquirer.prompt(questions)

data_owner_code = answers["data_owner_code"]
vehicle_number = answers["vehicle_number"]
topic = "/%s/pt/ssm/%s/vehicle_number/%s" % (answers["environment"], data_owner_code, vehicle_number)

client = mqtt.Client(client_id=device_id)
client.username_pw_set(device_id, password)
client.tls_set(ca_certs=certifi.where())
client.reconnect_delay_set(min_delay=1, max_delay=30)
client.connect(host, port=8883, keepalive=60)
client.loop_start()

def generate_ssm(priorization_response_status):
    msg = ssm.ExtendedSSM()

    ssm_msg = msg.ssm
    signal_status = ssm_msg.status.add()
    print(dir(signal_status))

    signalstatus_package = signal_status.sigStatus.add()
    signalstatus_package.status = ssm.SignalStatusPackage.PrioritizationResponseStatus.Value(priorization_response_status)
    print(signalstatus_package.status)
    print(msg)
    return msg.SerializeToString()

    

def send_ssm_message(type_msg):
    data = generate_ssm(type_msg)
    result = ssm.ExtendedSSM()
    result.ParseFromString(data)
    print(result.ssm.status[0].sigStatus[0])
    print(result)
    info = client.publish(topic, payload=data, qos=1)
    info.wait_for_publish()




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
