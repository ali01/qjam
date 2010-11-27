import base64
import cPickle as pickle
import json

from qjam.dataset import DataSet, BaseDataSet
from qjam.utils import module_src
from base_msg import BaseMsg, encode_msg_field, decode_msg_field


class TaskMsg(BaseMsg):
  def __init__(self, module_object, params=None, dataset=None):
    BaseMsg.__init__(self, 'task')
    self.__module  = module_object
    self.__params  = params
    if dataset != None and not issubclass(type(dataset), BaseDataSet):
      exc_msg = 'expected object of type DataSet or None for dataset param.'
      # TODO(ali01): logging
      raise ValueError, exc_msg

    self.__dataset = dataset

  def dataset(self):
    return self.__dataset

  def json_str(self):
    if self.__dataset == None:
      ref_list = []
    else:
      ref_list = self.__dataset.hash_list()

    msg = {'type': self.type(),
           'module':  encode_msg_field(module_src(self.__module)),
           'dataset': ref_list,
           'params':  encode_msg_field(self.__params)}
    return json.dumps(msg)
