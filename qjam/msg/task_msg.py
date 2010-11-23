import base64
import cPickle as pickle
import json

from base_msg import BaseMsg, encode_msg_field, decode_msg_field

class TaskMsg(BaseMsg):
  def __init__(self, module_object, params, dataset):
    BaseMsg.__init__(self, 'task')
    self.__module  = module_object
    self.__params  = params
    self.__dataset = dataset

  def json_str(self):
    msg = {'type': self.type(),
           'module':  encode_msg_field(self.__module_src(self.__module)),
           'dataset': self.__dataset,
           'params':  encode_msg_field(self.__params)}
    return json.dumps(msg)

  def __module_src(self, module):
    '''Return the source code for a given module object.'''
    filename = module.__file__
    filename = filename.replace('.pyc', '.py')
    with open(filename, 'r') as fh:
      return fh.read()
