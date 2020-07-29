import pika
from bson.objectid import ObjectId
from db import *
from pan_ocr import url_to_image, pan_ocr, load_retinanet_model
from datetime import date 
from time import process_time 
import requests
import json
import os
import argparse


import sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

sys.path.insert(0,parentdir) 
from config.settings.stage import *

rabbit_settings = RABBIT_MQ
db_settings = MONGO
model_path = MODEL_PATH
model_name = MODEL_NAME

if rabbit_settings is None:
    raise ValueError("No settings found")


credentials = pika.PlainCredentials(rabbit_settings.get('USER_NAME'), rabbit_settings.get('PASSWORD'))
connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rabbit_settings.get('HOST'),
        port=rabbit_settings.get('PORT'),
        credentials=credentials,
#        heartbeat_interval=rabbit_settings.get("HEARTBEAT")
    ))

if (connection):
    print ("connection to RabbitmQ at {} successful".format(rabbit_settings.get('HOST')))
else:
     print ("connection to RabbitmQ at {} FAILED".format(rabbit_settings.get('HOST')))
    
channel = connection.channel()
channel.queue_declare(queue='ocr_queue',  durable=True)


model = load_retinanet_model(model_name, model_path)


def callback_rabbitMQ(ch, method, properties, body):
    try:
        t1_start = process_time() 
        objId = body.decode()
        print("RabbitMQ Received %r" % objId)
        
        db = connect_db_conf(db_settings.get('USER'), db_settings.get('HOST'), db_settings.get('PASSWORD'), db_settings.get('DBNAME'))
    
        if (db):
            print ("connection to DB at {} successful".format(db_settings.get('HOST')))
        else:
             print ("connection to DB at {} FAILED".format(db_settings.get('HOST')))
    
        status = updateStatus(db,objId,'in_process')
        rec = getById(db,objId)
        
        if rec is not None and ('type' in rec) and rec['type'] == 'pan':
            pan_data = ''
            pan_empty = not bool(rec['pan_data'])
            if(pan_empty):
                image, isPDF, pdfFile, jpgFile = url_to_image(rec['file_url'],rec['_id'])
                if image is not None:
                    pan_data, empty = pan_ocr(image, model)

                    print(pan_data)
                    stored_data = save_pan_data(db,objId,pan_data)
                    
                    if empty == 1:
                        status = updateStatus(db,objId,'error')
                        error = updateError(db,objId,'image quality not apt for parsing')
                    
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
                            error = updateError(db,objId,'callback URL failed')

                        pan_data = json.loads(pan_data)
                        
                        save_pan_data(db,objId,pan_data)
                        status = updateStatus(db,objId,'success')
                    try:
                        if(isPDF):
                            print("deleting downloded pdf and it's converted jpg file")
                            if(pdfFile != ''):
                                os.remove(pdfFile)
                            if(jpgFile != ''):
                                os.remove(jpgFile)
                    except Exception as e:
                        print("failed to delete downloded pdf and it's converted jpg file: ", e)
                else:
                    print("ERROR: Failed to load image")
                    status = updateStatus(db,objId,'error')
                    error = updateError(db,objId,'failed to load image')
        
        t1_stop = process_time() 
        processTime = str(t1_stop-t1_start)
        today = str(date.today())

        updateProcessTime(db, objId, processTime, str(t1_start), today) 
        data = getById(db, str(rec['_id']))
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print('error in RabbitMQ subscriber: ',e)
        status = updateStatus(db,objId,'error')
        error = updateError(db,objId,'error in RabbitMQ subscriber')
        channel.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume('ocr_queue', callback_rabbitMQ)
print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()
