import pika
from bson.objectid import ObjectId
from db import *
from pan_ocr import url_to_image, pan_ocr, load_retinanet_model
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
        objId = body.decode()
        print("RabbitMQ Received %r" % objId)
        db = connect_db()
        rec = getById(db,objId)
        
        if rec != None and ('type' in rec) and rec['type'] == 'pan':
            pan_empty = not bool(rec['pan_data'])
            if(pan_empty):
                image = url_to_image(rec['fileUrl'])
                pan_data = pan_ocr(image, model)
                
                print(pan_data)
                
                stored_data = save_pan_data(db,objId,pan_data)
                
                if 'callbackUrl' in rec:
                    callbackUrl = rec['callbackUrl']
#                    print(callbackUrl)
                post_data = {'transactionId': str(rec['_id'])}
                
                json_str = json.dumps(post_data, indent=4)

                response = requests.post(callbackUrl, data=json_str)
                content = response.content
                
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except:
        print('error in RebbitMQ subscriber')
#    getData(db)

channel.basic_consume('ocr_queue', callback)
print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()
