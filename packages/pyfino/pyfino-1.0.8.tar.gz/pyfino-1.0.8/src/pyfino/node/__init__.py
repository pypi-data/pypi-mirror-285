# coding : utf-8

from abc import ABC, abstractmethod
from pyfino.messages import MessageChannel, MessageChannelOption
from json import loads

def _get_value(kwargs:dict, key:str, default:any=None):
  return kwargs[key] if key in kwargs else default


class Node(ABC):
  
  def _load_launch_json(self, file='launch.json'):
    
    with open(file, 'r') as f:
      self.config = loads(f.read())
      
 
  def _on_channel_message(self, ch, method, properties, body):
    self.on_node_message(method.routing_key, body)
  
    
  def __init__(self, **kwargs):
    
    # 尝试加载本地配置
    self._load_launch_json()
    if self.config == None:
      raise 'Failed to load launch.json'

    self.node_options = kwargs
    self.node_id = _get_value(self.node_options,'nodeId')
    if self.node_id is None or len(self.node_id) == 0:
      raise 'Must be setting a nodeid for inner message channel.'
    
    if 'rabbitmq' in self.config:
      _channel = self.config['rabbitmq']
      _option = MessageChannelOption(**_channel)
      self.node_channel = MessageChannel(_option )
      self.node_channel.subscribe(f'$nodes.{self.node_id}', self._on_channel_message)
      
    
    self.on_node_initialized(**kwargs)
    
    
  def halt(self):
    """ 停止节点 ，并会触发 on_node_halting
    """
    try:
      
      self.node_channel.stop_loop()
      self.node_channel.remove_queue(f'$nodes.{self.node_id}')
    finally:
      self.on_node_halting()
  
  
  def launch(self, **kwargs):
    """运行节点，并会触发 on_node_launching 
    
    """
    self.on_node_launching(**kwargs)
    self.node_channel.start_loop_async()
    
    
  def send_to_node(self, nodeId, body):
    queueName = f'$nodes.{nodeId}'
    self.node_channel.publish(queueName, body)
  
  
  def on_node_initialized(self, **kwargs):
    pass
  
  
  def on_node_message(self, route, payload):
    pass
  
  def on_node_halting(self):
    pass
  
  def on_node_launching(self, **kwargs):
    pass
  
