import os
import argparse
import numpy as np
import pandas
import json
import urllib.request
import cv2
import re


kerasNotFound = False
try:
    import tensorflow as tf
    import keras
    from keras_retinanet import *
    from keras_retinanet import models
    from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
    from keras_retinanet.utils.visualization import draw_box, draw_caption
    from keras_retinanet.utils.colors import label_color
except ImportError as e:
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("keras_retinanet package NOT found.")
    print("Automatically switching to preprocessing will be disabled")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    kerasNotFound = True


from image_processing import img_inference

#from ocr_app.text_processing import lines, check_date_pan
from text_processing import lines, check_date_pan, text_clean

# METHOD #1: OpenCV, NumPy, and urllib
def url_to_image(url):
    try:
        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        # return the image
        return image
    except:
        print("Error in loading/converting url to image, try with a valid url")
        return None


def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)
    
def load_retinanet_model():
    if kerasNotFound == True:
        return None
    MODEL_PATH = 'model/resnet50_csv_14.h5'
    print('Downloaded pretrained model to ' + MODEL_PATH)

    # keras.backend.tensorflow_backend.set_session(get_session())

    CLASSES_FILE = 'model/classes.csv'
    model_path = os.path.join('model', sorted(os.listdir('model'), reverse=True)[0])
    # print(model_path)

    # load retinanet model
    model = models.load_model(model_path, backbone_name='resnet50')
    model = models.convert_model(model)
    return model

def pan_ocr(img, model=None):
    text_line_words = []
    text_lines = []
    name = ''
    fname = ''
    dob = ''
    pan = ''
    print("inside pan_ocr")
    text_lines, text_lines_words = lines(img, False)
    print(text_lines)

    Pan_type, idx_date, dob, idx_pan, pan = check_date_pan(text_lines_words)
    print(dob,pan)

    if (kerasNotFound == False and idx_date == -1 and idx_pan == -1):
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("NOT found date or PAN. Automatically switching to preprocessing")
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

#     if args["preprocess"] == 1 or (idx_date == -1 and idx_pan == -1 and args["auto"] == 1):
        if (model == None):
            model = load_retinanet_model()

        # load label to names mapping for visualization purposes
        #         labels_to_names = pandas.read_csv(CLASSES_FILE, header=None).T.loc[0].to_dict()

        b, img = img_inference(img, model)
        img = img[b[1]:b[3], b[0]:b[2]]
        (H1, W1) = img.shape[:2]
        ratio = img.shape[0] / 420.0

        text_lines, text_lines_words = lines(img, False)
        Pan_type, idx_date, dob, idx_pan, pan = check_date_pan(text_lines_words)
    c = 0
    names = []
    for i in range(idx_date - 1, -1, -1):
        capital_str = re.search('^[A-Z]+[A-Z\s]+[A-Z]', text_lines[i])
        # if text_lines[i].isupper() and c<2:
   
        if capital_str is not None:
            print("LINES PARSING:",capital_str)

            if (c < 2):
                text_lines[i] = capital_str.group()
                # print(text_lines[i])
                names.append(text_lines[i])
                c += 1
    if len(names) > 0:
        fname = names[0]

    if len(names) > 1:
        name = names[1]

    output_dict = {}
    output_dict['name_on_card'] = text_clean(name)
    output_dict['fathers_name'] = text_clean(fname)
    output_dict['date_on_card'] = text_clean(dob)
    output_dict['pan_number'] = text_clean(pan)
    
    json_object = json.dumps(output_dict, indent=4)
    return json_object

