import pika

RABBITMQ_HOST = "localhost"

def get_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    return connection, channel

def send_message(queue_name: str, message: str):
    connection, channel = get_connection()
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,
        ),
    )
    connection.close()

