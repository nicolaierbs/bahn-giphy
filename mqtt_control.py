import paho.mqtt.client as mqtt
import io
import base64
from PIL import Image
import json
import numpy as np
import cv2
import gifted


broker = 'mqtt.infomotion.de'
port = 10037
user = 'admin'
# TODO Replace password
password = '1970'


def on_message(client, userdata, message):
    print('received message')
    topic = message.topic[6:]
    print(topic)

    decoded_payload = message.payload.decode('utf-8')
    image_data = decoded_payload.split(',')[1]
    image = Image.open(io.BytesIO(base64.b64decode(image_data))).convert('RGB')

    # Do whatever you like here
    open_cv_image = np.array(image)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    cv2.imwrite('test.jpg', open_cv_image)
    image = open_cv_image
    image_expanded = np.expand_dims(image, axis=0)

    # TODO Do the real cool stuff here

    gifted.create(20, '#welovedata')

    with open('output/temp.gif', mode='rb') as file:
        img = file.read()
    json_payload = json.dumps(
        {
            'imageData': base64.encodebytes(img).decode('utf-8'),
            'numZigs': 1,
            'id': topic
        }
    )
    # print(json_payload)
    # print(image_bytes)

    client.publish('response/' + topic, json_payload)


mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.username_pw_set(username=user, password=password)


print('Connect to broker ', broker)
mqtt_client.connect(broker, port, 60)
print("subscribing ")
mqtt_client.subscribe('trash/#')
mqtt_client.subscribe('welcomedays_test/#')
mqtt_client.subscribe('welcomedays/#')

mqtt_client.loop_forever()
