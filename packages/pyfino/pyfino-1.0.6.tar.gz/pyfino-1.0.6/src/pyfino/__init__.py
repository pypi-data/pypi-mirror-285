# coding: utf-8
from time import sleep
import json, threading


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
    threads = []
    for nodename in nodes:
      node = nodes[nodename]
      nodeModule = __import__(f'nodes.{nodename}', fromlist=['None'])
      moduleName = node['module']
      classInstance = eval(f'nodeModule.{moduleName}(**node)')
      # log.debug(f'Package {moduleName} loaded')
      threads.append(threading.Thread(target=classInstance.launch, name=nodename, kwargs=node, daemon=True))
    
    
    try:
      if len(threads) > 0:
        for t in threads:
          t.start()
          
      self._wait_forever()
        
    except KeyboardInterrupt:
      # log.debug('Fino 退出')
      pass
      
      
  