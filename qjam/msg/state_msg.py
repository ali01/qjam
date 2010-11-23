#!/usr/bin/python

import base64
import cPickle as pickle
import json

from base_msg import BaseMsg, encode_msg_field, decode_msg_field

class StateMsg(BaseMsg):
  def __init__(self, status):
    BaseMsg.__init__(self, 'state')
    if (status != 'running' and status != 'blocked')
      raise ValueError
    
    self.__status = status

  def status(self):
    return self.__status

  def json_str(self):
    msg = {'type': self.type(),
           'status': self.__status}
    return json.dumps(msg)


def StateMsgFromDict(dict):
  if (dict['type'] != 'state'):
    raise TypeError

  status = dict['status']
  return StateMsg(status)
