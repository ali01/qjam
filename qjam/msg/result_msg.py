import base64
import cPickle as pickle
import json

from base_msg import BaseMsg, encode_msg_field, decode_msg_field

class ResultMsg(BaseMsg):
  def __init__(self, result_object):
    BaseMsg.__init__(self, 'result')
    self.__result = result_object

  def result(self):
    return self.__result

  def json_str(self):
    msg = {'type': self.type(),
           'result': encode_msg_field(self.__result)}
    return json.dumps(msg)


def ResultMsgFromDict(dict):
  if (dict['type'] != 'result'):
    raise TypeError

  result_object = decode_msg_field(dict['result'])
  return ResultMsg(result_object)
