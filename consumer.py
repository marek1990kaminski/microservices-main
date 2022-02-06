import json
from enum import Enum

import pika
from pika import URLParameters, BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel

from main import Product, db

queue_name = 'main'

params: URLParameters = pika.URLParameters(
    'amqps://auxgvlie:XDN7xkGQH2kFu6QmiHYDZg5GZ-E-h3SN@rat.rmq2.cloudamqp.com/auxgvlie')

connection: BlockingConnection = pika.BlockingConnection(params)

channel: BlockingChannel = connection.channel()

channel.queue_declare(queue=queue_name)


class ContentType(Enum):
    product_created = 'product_created'
    product_updated = 'product_updated'
    product_deleted = 'product_deleted'


def callback(ch, method, properties, body):
    print(f'received in {queue_name}')
    data = json.loads(body)
    print(data)

    content_type: str = properties.content_type

    match content_type:
        case ContentType.product_created:
            product = Product(id=data['id'], title=data['title'], image=data['image'])
            db.session.add(product)
            db.session.commit()
            print(ContentType.product_created)
        case ContentType.product_updated:
            product = Product.query.get(data['id'])
            product.title = data['title']
            product.image = data['image']
            db.session.commit()
            print(ContentType.product_updated)
        case ContentType.product_deleted:
            product = Product.query.get(data['id'])
            db.session.delete(product)
            db.session.commit()
            print(ContentType.product_deleted)

    # if properties.content_type == product_created:
    #     product = Product(id=data['id'], title=data['title'], image=data['image'])
    #     db.session.add(product)
    #     db.session.commit()
    #     print(product_created)
    #
    # elif properties.content_type == product_updated:
    #     product = Product.query.get(data['id'])
    #     product.title = data['title']
    #     product.image = data['image']
    #     db.session.commit()
    #     print(product_updated)
    #
    # elif properties.content_type == product_deleted:
    #     product = Product.query.get(data['id'])
    #     db.session.delete(product)
    #     db.session.commit()
    #     print(product_deleted)


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print('Started consuming')

channel.start_consuming()

channel.close()
