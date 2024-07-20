#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
import os
from datetime import datetime as DateTime
from .ansicode import *


#------------------------------------------------------------------------
# 전역 상수 목록.
#------------------------------------------------------------------------
EMPTY : str = ""
NONE : str = "NONE"
COLON : str = ":"
SPACE : str = " "
SLASH : str = "/"
HYPHEN : str = "-"
COMMA : str = ","


#------------------------------------------------------------------------
# 파일의 전체경로를 파일의 (경로, 이름, 확장자) 분리.
#------------------------------------------------------------------------
def GetSplitFilePath(filePath : str, useLowerExtension : bool = True) -> tuple[str, str, str]:
	path, name = os.path.split(filePath)
	name, extension = os.path.splitext(name)
	if useLowerExtension:
		extension = extension.lower()
	return path, name, extension


#------------------------------------------------------------------------
# 구분자로 구분된 스트링을 하나의 리스트로 변환한다. 
# - 예 : "A/B/C" ==> ["A", "B", "C"]
#------------------------------------------------------------------------
def GetStringFromSeperatedStringList(string : str, seperator : str = COMMA) -> list[str]:
	if not string:
		return list()

	if seperator in string:
		result = string.split(seperator)
	else:
		result = list()
		result.append(string)

	return result

#------------------------------------------------------------------------
# 구분자로 구분된 스트링의 리스트를 하나의 리스트로 통합한다. 
# - 예 : ["A,B,C", "A,B,C", "A,B,C", ...] ==> ["A,B,C","A,B,C","A,B,C"]
#------------------------------------------------------------------------
def CreateStringListFromSeperatedStringList(strings : list[str], seperator : str = COMMA) -> list[str]:
	if not strings:
		return list()	
	result = list()
	for string in strings:
		if seperator in string: result.extend(filter(None, string.split(seperator)))
		else: result.append(string)
	return result


#------------------------------------------------------------------------
# 현재 시간 텍스트 반환.
#------------------------------------------------------------------------
def GetTimestampString(seperateDate : str = EMPTY, seperateGap : str = SPACE, seperateTime : str = EMPTY, useMilliseconds : bool = False, seperateMillySecondsTime : str = COMMA) -> str:
	nowTime : DateTime = DateTime.now()
	if useMilliseconds:
		milliseconds = nowTime.strftime("%f")[:3]
		timestamp = nowTime.strftime(f"%Y{seperateDate}%m{seperateDate}%d{seperateGap}%H{seperateTime}%M{seperateTime}%S{seperateMillySecondsTime}{milliseconds}")
	else:
		timestamp = nowTime.strftime(f"%Y{seperateDate}%m{seperateDate}%d{seperateGap}%H{seperateTime}%M{seperateTime}%S")
	return timestamp


#------------------------------------------------------------------------
# 현재 시간 출력.
#------------------------------------------------------------------------
def PrintTimestamp(text : str = str()) -> None:
	from pyappcore import ansicode
	timestamp = GetTimestampString(HYPHEN, SPACE, COLON, True, COMMA)
	if text:
		ansicode.PrintWithBold(f"[{timestamp}] {text}")
	else:
		ansicode.PrintWithBold(timestamp)