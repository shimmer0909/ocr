import pika
from django.conf import settings

rabbit_settings = getattr(settings, "RABBIT_MQ", None)
if rabbit_settings is None:
    raise ValueError("No settings found")


class RabbitMQ:
    """
    This class connects to RabbitMQ
    """
    def __init__(self):
        credentials = pika.PlainCredentials(rabbit_settings.get('USER_NAME'), rabbit_settings.get('PASSWORD'))
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=rabbit_settings.get('HOST'),
                port=rabbit_settings.get('PORT'),
                credentials=credentials,
#                heartbeat_interval=rabbit_settings.get("HEARTBEAT")
            ))
        
        if (connection):
            print ("connection to RabbitMQ successful")
        else:
            print ("connection to RabbitMQ FAILED")
                
        self.channel = connection.channel()
        self.channel.queue_declare(queue="ocr_queue",  durable=True)
        
    def publish(self, data, retryCount=0):
        try:
            self.channel.basic_publish(exchange='', routing_key="ocr_queue", body=str(data))
            print("Published to RabbitMQ - id:", data)

            # connection.close()
        except Exception as e:
            if retryCount >= 10:
                # add mail
                print('max retry attempts reached')
            else:
                print("Published to RabbitMQ might have failed for id:", data)
                print("e: ",e)
                print('trying to reconnect retry count : ', retryCount)
                self.__init__()
                self.publish(data, retryCount + 1)