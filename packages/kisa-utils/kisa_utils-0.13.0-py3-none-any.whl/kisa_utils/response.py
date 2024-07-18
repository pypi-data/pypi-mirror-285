from kisa_utils.storage import encodeJSON
from typing import Any

class Response:
    def __init__(self, status:bool, /, *, log:str='', data:Any=None):
        
        if not isinstance(status,bool):
            raise TypeError(f'`status` expected to be a bool')

        if not isinstance(log,str):
            raise TypeError(f'`log` expected to be a string')

        log = log.strip()

        if (not status) and (not log):
            raise ValueError(f'not effective `log` provided for `status` of False')

        if (not status) and data:
            raise ValueError(f'`data` provided for `status` of False')

        self.__status = status
        self.__log = log
        self.__data = data

    def __bool__(self): return self.__status

    @property
    def status(self): return self.__status

    @property
    def log(self): return self.__log

    @property
    def data(self): return self.__data

    @property
    def asDict(self): 
        return {'status':self.__status, 'log':self.__log, 'data':self.__data}

    @property
    def asJSON(self): 
        return encodeJSON(self.asDict)
    
    def __repr__(self):
        return f'Reponse(status={self.__status}, log="{self.__log}", data={self.__data})'

def Ok(data:Any=None) -> Response:
    return Response(True, data=data)

def Error(log:str) -> Response:
    return Response(False, log=log)