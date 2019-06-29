import os
import sys
from datetime import datetime
from enum import Enum


class LogType(Enum):
    LogOK = 0,
    LogSUCCESS = 1,
    LogSEND = 2,
    LogRECV = 3,
    LogFAIL = 4,
    LogEXCEPTION = 5,
    LogERROR = 6,
    LogINVALID = 7,
    LogDEBUG = 8


class TResMsg:
    __slots__ = ('Type', 'Msg')

    def __init__(self, Type=LogType.LogOK, Msg=''):
        self.Type = Type
        self.Msg = Msg

    def set(self, Type, Msg):
        self.Type = Type
        self.Msg = Msg

    def clear(self):
        self.Type = LogType.LogOK
        self.Msg = ''


def WriteLogMsg(Type, Msg):
    time = datetime.now()
    local_path = sys.path[0]
    dir_path = os.path.join(local_path, 'Log')
    file_path = os.path.join(dir_path, datetime.strftime(time, '%Y%m%d') + '.log')
    os.makedirs(dir_path, exist_ok=True)

    with open(file_path, 'a') as fs:
        try:
            msg_str = datetime.strftime(time, '%H:%M:%S.%f') + ' [' + Type.name[3:len(str(Type))] + '] ' + Msg
            print(msg_str)
            fs.write(msg_str + '\n')
        finally:
            fs.close()
