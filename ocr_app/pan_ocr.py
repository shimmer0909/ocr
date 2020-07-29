import os
import argparse
import numpy as np
import pandas
import json
import urllib.request
import cv2
import re
import imutils
import ghostscript
import locale
import wget
import requests


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
    print("error in loading model: ",e)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("keras_retinanet package NOT found.")
    print("Automatically switching to preprocessing will be disabled")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    kerasNotFound = True


from image_processing import img_inference
from text_processing import lines, check_date_pan, text_clean

def pdf2jpeg(pdf_input_path, jpeg_output_path):
    try:
        print("converting pdf to jpeg file")
        args = ["pdf2jpeg", 
                "-dNOPAUSE",
                "-sDEVICE=jpeg",
                "-r144",
                "-sOutputFile=" + jpeg_output_path,
                pdf_input_path]
        encoding = locale.getpreferredencoding()
        args = [a.encode(encoding) for a in args]
        ghostscript.Ghostscript(*args)
    except Exception as e:
        print ("Failed in pfd2jpeg: ",e)
        
def checkPDF(url):
    r = requests.get(url)
    content_type = r.headers.get('content-type')
    if 'application/pdf' in content_type:
        return True
    else:
        return False

def downloadFile(url,folder,uuid):
    print('Beginning file download with wget module')
    fileLoc = folder
    try:
        if not os.path.exists(fileLoc):
            print("Inside if")
            os.makedirs(fileLoc)
    except Exception as e:
        print("could not make new directory: ", e)
        
    fileLoc = os.path.abspath(fileLoc) + '/' + str(uuid)
    try:
        wget.download(str(url), fileLoc)
    except Exception as e:
        print('unable to download file correctly: ', e)
    print("File downloaded successfully")
    return fileLoc

def url_to_image(url,uuid):
    isPDF = False
    pdfFile = ''
    jpgPath = ''
    try:
        if checkPDF(url):
            print("URL is for a PDF")
            folder='downloads/'
            pdfFile = downloadFile(url, folder,str(uuid)+'.pdf')
            jpgPath = os.path.abspath(folder)+str(uuid)+'.jpg'
            pdf2jpeg(pdfFile, jpgPath)
            image = cv2.imread(jpgPath)
            isPDF = True
        else:
            print("converting url to image")
            resp = urllib.request.urlopen(url)
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
        return image, isPDF, pdfFile, jpgPath
    except:
        print("Error in loading/converting url to image, try with a valid url")
        return None, isPDF, pdfFile, jpgPath


def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)
    
def load_retinanet_model(model_name, model_path=None):
    if kerasNotFound == True:
        return None
    if model_path is None:
        MODEL_PATH = 'model/resnet50_csv_14.h5'
        print('Downloaded pretrained model to ' + MODEL_PATH)

        keras.backend.tensorflow_backend.set_session(get_session())

        CLASSES_FILE = 'model/classes.csv'
        model_path = os.path.join('model', sorted(os.listdir('model'), reverse=True)[0])

    # load retinanet model
    model = models.load_model(model_path+model_name, backbone_name='resnet50')
    
    if (model):
        print ('MODEL LOADED SUCCESSFULLY: ', model_path+model_name)
        model = models.convert_model(model)
    return model

def pan_ocr(img, model=None):
    text_line_words = []
    text_lines = []
    name = ''
    fname = ''
    dob = ''
    pan = ''
    text_lines, text_lines_words = lines(img, False)

    Pan_type, idx_date, dob, idx_pan, pan = check_date_pan(text_lines_words)

    if (kerasNotFound == False and idx_date == -1 and idx_pan == -1):
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("NOT found date or PAN. Automatically switching to preprocessing")
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        if (model == None):
            print("loading model")
            model = load_retinanet_model()
       
        b, img = img_inference(img, model)
        img = img[b[1]:b[3], b[0]:b[2]]
        (H1, W1) = img.shape[:2]

        text_lines, text_lines_words = lines(img, False)
        Pan_type, idx_date, dob, idx_pan, pan = check_date_pan(text_lines_words)
        
    c = 0
    names = []
    for i in range(idx_date - 1, -1, -1):
        capital_str = re.search('^[A-Z]+[A-Z\s]+[A-Z]', text_lines[i])
   
        if capital_str is not None:
            if (c < 2):
                text_lines[i] = capital_str.group()
                names.append(text_lines[i])
                c += 1
                
    dd = dob[:2]
    mm = dob[3:5]
    yy = dob[6:]
    dob = yy +'-'+ mm +'-'+ dd
    
    fname = ''
    name = ''
    if len(names) > 0:
        fname = names[0]

    if len(names) > 1:
        name = names[1]
        
    output_dict = {}
    print("name: ",name)
    
    empty = 0
    if name == '' and fname == '' and dob == '' and pan == '':
        empty = 1
        
    elif name == 'INCOMETAXDEPARTMENT' or name == 'INCOME TAX DEPARTMENT' or name == 'INCOMETAX DEPARTMENT' or name == 'INCOME TAXDEPARTMENT':
        name = fname
        output_dict['name_on_card'] = text_clean(name)
        output_dict['date_on_card'] = text_clean(dob)
        output_dict['pan_number'] = text_clean(pan)
    else: 
        print("inside else")
        output_dict['name_on_card'] = text_clean(name)
        output_dict['fathers_name'] = text_clean(fname)
        output_dict['date_on_card'] = text_clean(dob)
        output_dict['pan_number'] = text_clean(pan)
    json_object = json.dumps(output_dict, indent=4)
    return json_object, empty

