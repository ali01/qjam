import base64
import cPickle as pickle
import json

from qjam.dataset import DataSet, BaseDataSet
from base_msg import BaseMsg, encode_msg_field, decode_msg_field

class RefsMsg(BaseMsg):
  def __init__(self, refs=[]):
    BaseMsg.__init__(self, 'refs')
    if not isinstance(refs, list):
      raise TypeError, 'refs parameter must be of type list'

    for ref in refs:
      if not isinstance(ref, list) or len(ref) != 2:
        raise TypeError, 'each element of refs must be a list of size 2'

    self.__refs = refs

  def append(self, key, object):
    ref = [key, encode_msg_field(object)]
    self.__refs.append(ref)

  def json_str(self):
    msg = {'type': self.type(),
           'refs': self.__refs}
    return json.dumps(msg)
