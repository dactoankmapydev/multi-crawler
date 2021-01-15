import pika


def setup(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5673,
                                                                   credentials=pika.PlainCredentials(username='test',
                                                                                                     password='test')))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True, arguments={'x-max-priority': 5})
    return connection, channel
