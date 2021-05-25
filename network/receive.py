# -*- coding: utf-8 -*-
"""
Created on Sat May 15 09:40:22 2021

@author: lor
"""

import pika
import sys
import os



def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        print("[x] received %r" % body)

    
    channel.queue_declare(queue = 'hello')
    channel.basic_consume(queue = 'hello',  on_message_callback = callback , auto_ack = True)
    
    print(' [*] Waiting for messages. Prestt Ctrl+C to exit.')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

