import pika

def publish(data):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host="3.7.61.186",
                    port=5672,
                    credentials=pika.PlainCredentials("indifi","test123"),
#                    heartbeat_interval=60
                ))
        if (connection):
            print ("connection to RabbitmQ at 3.7.61.186 successful" )
        else:
             print ("connection to RabbitmQ at 3.7.61.186 FAILED" )
#        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue="ocr_queue",  durable=True)
        channel.basic_publish(exchange='', routing_key="ocr_queue", body=data)
        print("Published to RabbitMQ - id:", data)

        connection.close()
    except:
        print("Published to RabbitMQ might have failed for id:", data)
