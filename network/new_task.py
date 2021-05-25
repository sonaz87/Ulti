# -*- coding: utf-8 -*-
"""
Created on Sat May 15 10:29:49 2021

@author: lor
"""

import sys
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue = 'task_queue', durable = True)

message = ' '.join(sys.argv[1:]) or 'Hello World!'
channel.basic_publish(exchange = '', routing_key = 'task_queue', body = message, properties = pika.BasicProperties(delivery_mode = 2))

print(" X sent %r" % message)
connection.close()
