import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.stage')

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

django.setup()

from django.conf import settings

import pika
from bson.objectid import ObjectId
from db import MongoDb
Mongo = MongoDb()

from pan_ocr import url_to_image, pan_ocr, load_retinanet_model
from datetime import datetime
import requests
import json

if settings.RABBIT_MQ is None:
    raise ValueError("No settings found")

credentials = pika.PlainCredentials(settings.RABBIT_MQ.get('USER_NAME'), settings.RABBIT_MQ.get('PASSWORD'))
connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBIT_MQ.get('HOST'),
        port=settings.RABBIT_MQ.get('PORT'),
        credentials=credentials
    ))

if (connection):
    print ("connection to RabbitmQ at {} successful".format(settings.RABBIT_MQ.get('HOST')))
else:
    print ("connection to RabbitmQ at {} FAILED".format(settings.RABBIT_MQ.get('HOST')))
    
channel = connection.channel()
channel.queue_declare(queue='ocr_queue',  durable=True)


model = load_retinanet_model(settings.MODEL_NAME, settings.MODEL_PATH)


def callback_rabbitMQ(ch, method, properties, body):
    try:
        t1_start = datetime.now()
        objId = body.decode()
        print("RabbitMQ Received %r" % objId)
            
        status = Mongo.updateStatus(objId, 'in_process')
        rec = Mongo.getById(objId)
        
        if rec is not None and ('type' in rec) and rec['type'] == 'pan':
            pan_data = ''
            pan_empty = not bool(rec['pan_data'])
            if(pan_empty):
                image, isPDF, pdfFile, jpgFile = url_to_image(rec['file_url'],rec['_id'])
                if image is not None:
                    pan_data, empty = pan_ocr(image, model)

                    stored_data = Mongo.save_pan_data(objId, pan_data)
                    
                    if empty == 1:
                        status = Mongo.updateStatus(objId, 'error')
                        error = Mongo.updateError(objId, 'image quality not apt for parsing')
                    
                    elif empty == 0:
                        try:
                            if 'callback_url' in rec:
                                callback_url = rec['callback_url']
                                post_data = {'transactionId': str(rec['_id'])}
                                json_str = json.dumps(post_data, indent=4)

                                response = requests.get(callback_url, params=post_data)
                                content = response.content
                        except Exception as e:
                            print("callback URL failed: ",e)
                            error = Mongo.updateError(objId, 'callback URL failed')

                        pan_data = json.loads(pan_data)
                        
                        Mongo.save_pan_data(objId, pan_data)
                        status = Mongo.updateStatus(objId, 'success')
                    try:
                        if(isPDF):
                            if(pdfFile != ''):
                                os.remove(pdfFile)
                            if(jpgFile != ''):
                                os.remove(jpgFile)
                    except Exception as e:
                        print("failed to delete downloded pdf and it's converted jpg file: ", e)
                else:
                    print("ERROR: Failed to load image")
                    status = Mongo.updateStatus(objId,'error')
                    error = Mongo.updateError(objId,'failed to load image')
        
        processTime = datetime.now() - t1_start

        Mongo.updateProcessTime(objId, processTime.total_seconds(), t1_start, datetime.now())
        data = Mongo.getById(str(rec['_id']))
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print('error in RabbitMQ subscriber: ',e)
        status = Mongo.updateStatus(objId, 'error')
        err = 'error in RabbitMQ subscriber'
        
        try:
            err += ':' + str(e)
        except: 
            pass
        
        error = Mongo.updateError(objId, err)
        channel.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume('ocr_queue', callback_rabbitMQ)
print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()
