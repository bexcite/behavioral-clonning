'''
Runs server and infere model for testing.
'''

import argparse
import base64
import json

import numpy as np
import socketio
import eventlet
import eventlet.wsgi
import time
from PIL import Image
from PIL import ImageOps
from flask import Flask, render_template
from io import BytesIO

from sdc_utils import normalize, resize_image

from keras.models import model_from_json
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array

from scipy.misc import imresize


sio = socketio.Server()
app = Flask(__name__)
model = None
resize_factor = 1.0
crop_bottom = 25
prev_image_array = None

@sio.on('telemetry')
def telemetry(sid, data):
    # The current steering angle of the car
    steering_angle = data["steering_angle"]
    # The current throttle of the car
    throttle = data["throttle"]
    # The current speed of the car
    speed = data["speed"]
    # The current image from the center camera of the car
    imgString = data["image"]
    image = Image.open(BytesIO(base64.b64decode(imgString)))
    image_array = np.asarray(image)

    # Crop bottom (remove car image)
    if crop_bottom:
      image_array = image_array[:-crop_bottom,:]

    # print('rf = ', resize_factor)
    # Resize image acc to resize_factor

    # Resize image
    image_array = resize_image(image_array, resize_factor)

    transformed_image_array = image_array[None, :, :, :]

    # Normalize
    norm_image_array = normalize(transformed_image_array)

    # print('image_array =', norm_image_array)

    # This model currently assumes that the features of the model are just the images. Feel free to change this.
    steering_angle = float(model.predict(norm_image_array, batch_size=1))

    # steering_angle = 0

    # The driving model currently just outputs a constant throttle. Feel free to edit this.
    throttle = 0.2 #
    print(steering_angle, throttle)
    send_control(steering_angle, throttle)


@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)
    send_control(0, 0)


def send_control(steering_angle, throttle):
    sio.emit("steer", data={
    'steering_angle': steering_angle.__str__(),
    'throttle': throttle.__str__()
    }, skip_sid=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Remote Driving')
    parser.add_argument('model', type=str,
        help='Path to model definition json. Model weights should be on the same path or specify --restore_weights.')
    parser.add_argument('--restore_weights', type=str, help='Restore weights from checkpoint')
    parser.add_argument('--resize_factor', type=float, default=8, help='Resize image factor - default 1.0')
    parser.add_argument('--crop_bottom', type=int, default=0, help='Crop bottom. to remove car image')
    args = parser.parse_args()

    resize_factor = args.resize_factor
    crop_bottom = args.crop_bottom

    with open(args.model, 'r') as jfile:
        model = model_from_json(jfile.read())
        # model = model_from_json(json.load(jfile))

    model.compile("adam", "mse")

    if args.restore_weights:
      # eventlet
      print('Restoring weights from', args.restore_weights)
      model.load_weights(args.restore_weights)
    else:
      weights_file = args.model.replace('json', 'h5')
      print('Restoring weights from', weights_file)
      model.load_weights(weights_file)


    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
