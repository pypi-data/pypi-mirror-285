# coding: utf-8
""" 消息队列
@comment 基于pika实现的rabbitmq消息队列模块
"""

import pika
from pika.exceptions import StreamLostError
import threading


class MessageChannelOption:
  
  def __init__(self, host, port=5672, virtualHost='/', userName:str=None, password:str=None):
    self.host = host
    self.port = port
    self.virtual_host = virtualHost
    self.username = userName
    self.password = password


class MessageChannel:
  
  def __init__(self,  options:MessageChannelOption):
    self._consume_thread = None
    self.options = options
    auth_credentials = pika.PlainCredentials(self.options.username, self.options.password)
    self.connection = pika.BlockingConnection(
      pika.ConnectionParameters(
        self.options.host, 
        self.options.port, 
        virtual_host=self.options.virtual_host, 
        credentials=auth_credentials))
    
    self.channel = self.connection.channel()
    
    
  def create_queue(self, queueName) :
    self.channel.queue_declare(queue=queueName)
    
    
  def remove_queue(self, queueName):
    try:
      self.channel.queue_delete(queue=queueName)
    except Exception:
      return
    finally:
      pass
    
    
  def publish(self, queueName:str, body: str|bytes):
    self.channel.basic_publish(exchange='', routing_key=queueName, body=body)
    
    
  def subscribe(self, queueName, onMessaged):
    self.channel.queue_declare(queue=queueName)
    return self.channel.basic_consume(queue=queueName,
                  auto_ack=True,
                  on_message_callback=onMessaged)
    
    
  def start_loop(self):
    try:
      self.channel.start_consuming()
    except:
      print('Force thread to exit\n')
      return
    
    
  def stop_loop(self):
    self._consume_thread.join(2)
      
    
      
    
  def start_loop_async(self):
    self._consume_thread = threading.Thread(target=self.start_loop, daemon=True)
    self._consume_thread.start()