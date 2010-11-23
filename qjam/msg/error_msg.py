import base64
import cPickle as pickle
import json

from base_msg import BaseMsg, encode_msg_field, decode_msg_field

class ErrorMsg(BaseMsg):
  def __init__(self, error_str):
    BaseMsg.__init__(self, 'error')
    self.__error = error_str

  def json_str(self):
    msg = {'type': self.type(),
           'error': self.__error}
    return json.dumps(msg)

  def __str__(self):
    return self.__error


def ErrorMsgFromDict(dict):
  if (dict['type'] != 'error'):
    raise TypeError

  error_str = dict['error']
  return ErrorMsg(error_str)
