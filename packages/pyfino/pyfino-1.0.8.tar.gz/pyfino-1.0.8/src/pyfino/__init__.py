# coding: utf-8
from time import sleep
import json, threading
from pyfino.node import Node

class Fino:
  """ Fino类， 基于配置文件加载节点
  @auth       xuwh
  @comment
  @date       2024-7-15
  """
  
  def _load_config(self,configPath):
    
    with open(configPath) as f:
      return json.loads(f.read())
    
  def _wait_forever(self):
    while True:
      sleep(1)
    
  def loop_forever(self, config:str='nodes.json'):
    """ 该函数将无限循环，直到外部主动中断进程
    @param config:  包含节点配置的文件路径
    """
    
    conf = self._load_config(config)
    nodes = conf['nodes']
    nodeInstances:list[Node] = []
    for nodename in nodes:
      node = nodes[nodename]
      nodeModule = __import__(f'nodes.{nodename}', fromlist=['None'])
      moduleName = node['module']
      classInstance = eval(f'nodeModule.{moduleName}(**node)')
      # log.debug(f'Package {moduleName} loaded')
      
      nodeInstances.append(classInstance)
    
    try:
      if len(nodeInstances) > 0:
        for n in nodeInstances:
          n.launch()
          
      self._wait_forever()
        
    except KeyboardInterrupt:
      pass
    finally:
      if len(nodeInstances) > 0:
        for n in nodeInstances:
          n.halt()
      
      
  