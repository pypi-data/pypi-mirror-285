#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
import sys
import types


#------------------------------------------------------------------------
# 상수.
#------------------------------------------------------------------------
class Constants:
    #------------------------------------------------------------------------
    # 상수 설정.
    #------------------------------------------------------------------------
    def SetConstant(self, constName : str, constValue : Any) -> None:
        builtins.setattr(self, constName, constValue)

    #------------------------------------------------------------------------
    # 상수 반환.
    #------------------------------------------------------------------------
    def GetConstant(self, constName : str) -> Any:
        return builtins.getattr(self, constName)

    #------------------------------------------------------------------------
    # 인스턴스의 멤버 설정.
    #------------------------------------------------------------------------
    def __setattr__(self, name : str, value : Any):
        if name in self.__dict__:
            raise Exception("Cannot overwrite value.")
        self.__dict__[name] = value

    #------------------------------------------------------------------------
    # 인스턴스의 멤버 반환.
    #------------------------------------------------------------------------
    def __delattr__(self, name : str):
        if name in self.__dict__:
            raise Exception("Cannot delete value.")


#------------------------------------------------------------------------
# 클래스 대신 모듈 자체를 클래스로 사용.
#------------------------------------------------------------------------
def Use():
    moduleName : str = __name__
    newConstants : Constants = Constants()
    # sys.modules[moduleName] = newConstants