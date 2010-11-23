import base64
import cPickle as pickle
import json

from qjam.utils import module_src
from base_msg import BaseMsg, encode_msg_field, decode_msg_field

class TaskMsg(BaseMsg):
  def __init__(self, module_object, params, dataset):
    BaseMsg.__init__(self, 'task')
    self.__module  = module_object
    self.__params  = params
    if (dataset != None):
      if not isinstance(dataset, list):
        exc_msg = 'expected list of refs or None for dataset'
        # TODO(ali01): logging
        raise ValueError, exc_msg

      self.__dataset = dataset

    else:
      self.__dataset = []

  def json_str(self):
    msg = {'type': self.type(),
           'module':  encode_msg_field(module_src(self.__module)),
           'dataset': self.__dataset,
           'params':  encode_msg_field(self.__params)}
    return json.dumps(msg)
