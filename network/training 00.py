# -*- coding: utf-8 -*-
"""
Created on Sat May 15 09:30:52 2021

@author: lor
"""

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue = 'hello')


channel.basic_publish(exchange = '', routing_key = 'hello', body = 'Hello World!')

print("[x] sent 'Hello World!'")

connection.close()