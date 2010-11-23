import json

from base_msg import BaseMsg, encode_msg_field, decode_msg_field

class StateMsg(BaseMsg):
  def __init__(self, status, missing_refs=[]):
    BaseMsg.__init__(self, 'state')
    if (status != 'running' and status != 'blocked'):
      raise ValueError, 'unknown value for status parameter'

    if (status == 'blocked'):
      if (len(missing_refs) == 0):
        raise ValueError, '''len(missing_refs) should be non-zero
                             if status is 'blocked' '''

    elif (status == 'running' and len(missing_refs) != 0):
      raise ValueError, '''len(missing_refs) should be zero
                           if status is not 'blocked' '''

    self.__status = status
    self.__missing_refs = missing_refs

  def status(self):
    return self.__status

  def missing_refs(self):
    return self.__mising_refs

  def json_str(self):
    msg = {'type': self.type(), 'status': self.__status}
    if (len(self.__missing_refs) != 0):
      msg['missing_refs'] = self.__mising_refs

    return json.dumps(msg)


def StateMsgFromDict(dict):
  if (dict['type'] != 'state'):
    raise TypeError

  status = dict['status']
  if ('missing_refs' in dict):
    missing_refs = dict['missing_refs']
  else:
    missing_refs = []
  
  return StateMsg(status, missing_refs)
