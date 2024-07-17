# coding: utf-8 

import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

class OssService:
  
  def __init__(self, bucketName:str, options:dict={}):
    
    accessKeyId = options['accessKeyId'] if 'accessKeyId' in options else None
    accessKeySecret = options['accessKeySecret'] if 'accessKeySecret' in options else None
    if accessKeyId is not None:
      auth = oss2.Auth(accessKeyId, accessKeySecret)
    else:
      auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
      
    self.bucket = oss2.Bucket(auth, 
                              options['region'] 
                              if 'region' in options 
                              else 'http://oss-cn-beijing.aliyuncs.com', 
                              bucketName)
  
  
  def push_object(self, objectName, file):
    response = self.bucket.put_object_from_file(objectName, file)
    return response.status == 200
  
  
  def pull_object(self, objectName):
    file = self.bucket.get_object(objectName)
    return file.read()
  
  def has_object(self, objectName):
    return self.bucket.object_exists(objectName)
  
  def pull_object_to_file(self, objectName, localfile):
    self.bucket.get_object_to_file(objectName, localfile)
    
    
  def delete_object(self, objectName):
    self.bucket.delete_object(objectName)
  
  def create_object(self, objectName):
    self.bucket.put_object()