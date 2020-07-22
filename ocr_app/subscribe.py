import pika
from bson.objectid import ObjectId
from db import *
from pan_ocr import url_to_image, pan_ocr, load_retinanet_model
from datetime import date 
from time import process_time 
import requests
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(
            host="3.7.61.186",
            port=5672,
            credentials=pika.PlainCredentials("indifi","test123"),
#            heartbeat_interval='60'
        ))
if (connection):
    print ("connection to RabbitmQ at 3.7.61.186 successful" )
else:
     print ("connection to RabbitmQ at 3.7.61.186 FAILED" )
#connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='ocr_queue',  durable=True)
model = load_retinanet_model()


def callback(ch, method, properties, body):
    try:
        t1_start = process_time() 
        objId = body.decode()
        print("RabbitMQ Received %r" % objId)
        db = connect_db()
        status = updateStatus(db,objId,'in_process')
        rec = getById(db,objId)
        
        if rec is not None and ('type' in rec) and rec['type'] == 'pan':
        
            pan_empty = not bool(rec['pan_data'])
            if(pan_empty):
                print(rec['fileUrl'])
                image = url_to_image(rec['fileUrl'])
                if image is not None:
                    print("image is not empty")
                    pan_data = pan_ocr(image, model)

                    print(pan_data)
                    stored_data = save_pan_data(db,objId,pan_data)

                    try:
                        if 'callbackUrl' in rec:
                            callbackUrl = rec['callbackUrl']
                            print(callbackUrl)
                            post_data = {'transactionId': str(rec['_id'])}
                            print(post_data)
                            json_str = json.dumps(post_data, indent=4)
                            print(json_str)

                            #response = requests.post(callbackUrl, data=json_str)
                            response = requests.get(callbackUrl, params=post_data)
                            print("responsei from callback URL: ",response)
                            content = response.content
                            #print(content)
                    except:
                        print("callback URL failed") 

        print("reached here") 
        status = updateStatus(db,objId,'success')
        pan_data = json.loads(pan_data)
        save_pan_data(db,objId,pan_data)
        t1_stop = process_time() 
        processTime = str(t1_stop-t1_start)
        print(processTime)
        today = str(date.today())

#        print(today)
        updateProcessTime(db, objId, processTime, str(t1_start), today) 
        data = getById(db, str(rec['_id']))
        print(data)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except:
        status = updateStatus(db,objId,'error')
        channel.basic_ack(delivery_tag=method.delivery_tag)
        print('error in RabbitMQ subscriber')
#    getData(db)

channel.basic_consume('ocr_queue', callback)
print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()
