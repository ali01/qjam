#!/usr/bin/python

class BaseMsg(object):
  def __init__(self, type):
    self.__type = type

  def type(self):
    return self.__type

  def json_str(self):
    raise NotImplementedError




def encode_msg_field(field):
  return base64.b64encode(pickle.dumps(field))


def decode_msg_field(encoded_field):
  return pickle.loads(base64.b64decode(encoded_field))
