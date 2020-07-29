import pika
from django.conf import settings

rabbit_settings = getattr(settings, "RABBIT_MQ", None)
if rabbit_settings is None:
    raise ValueError("No settings found")

def publish(data):
    try:
        credentials = pika.PlainCredentials(rabbit_settings.get('USER_NAME'), rabbit_settings.get('PASSWORD'))
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=rabbit_settings.get('HOST'),
                port=rabbit_settings.get('PORT'),
                credentials=credentials,
#                heartbeat_interval=rabbit_settings.get("HEARTBEAT")
            ))
        
        if (connection):
            print ("connection to RabbitmQ at {} successful".format(rabbit_settings.get('HOST')))
        else:
            print ("connection to RabbitmQ at {} FAILED".format(rabbit_settings.get('HOST')))
            print("e: ",e)
                
        channel = connection.channel()
        channel.queue_declare(queue="ocr_queue",  durable=True)
        channel.basic_publish(exchange='', routing_key="ocr_queue", body=data)
        print("Published to RabbitMQ - id:", data)

        connection.close()
    except Exception as e:
        print("Published to RabbitMQ might have failed for id:", data)
        print("e: ",e)