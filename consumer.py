import json

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


class ContentTypeEnum:
    product_created = 'product_created'
    product_updated = 'product_updated'
    product_deleted = 'product_deleted'


def callback(ch, method, properties, body):
    print(f'received in {queue_name}')
    data = json.loads(body)
    print(data)

    content_type: str = properties.content_type

    match content_type:
        case ContentTypeEnum.product_created:
            product = Product(id=data['id'], title=data['title'], image=data['image'])
            db.session.add(product)
            db.session.commit()
            print(ContentTypeEnum.product_created)
        case ContentTypeEnum.product_updated:
            product = Product.query.get(data['id'])
            product.title = data['title']
            product.image = data['image']
            db.session.commit()
            print(ContentTypeEnum.product_updated)
        case ContentTypeEnum.product_deleted:
            product = Product.query.get(data)
            db.session.delete(product)
            db.session.commit()
            print(ContentTypeEnum.product_deleted)


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print('Started consuming')

channel.start_consuming()

channel.close()
