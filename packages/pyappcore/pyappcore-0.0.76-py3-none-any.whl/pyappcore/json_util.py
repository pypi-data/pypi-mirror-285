#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
import json
import re


#------------------------------------------------------------------------
# 전역 상수 목록.
#------------------------------------------------------------------------
STRING_LITERAL_PATTERN = "\".*?\"|'.*?'" # 따옴표, 쌍따옴표.
COMMENT_PATTERN : str = "//.*?$|/\\*.*?\\*/|#.*?$" # 주석.


#------------------------------------------------------------------------
# 문자열 변환.
#------------------------------------------------------------------------
@staticmethod
def STRToJSON(jsonString : str) -> dict:
	jsonString = RemoveAllCommentsInString(jsonString)
	return json.loads(jsonString)


#------------------------------------------------------------------------
# 예쁜 JSON 텍스트로 반환.
#------------------------------------------------------------------------
def GetPrettyJSONString(jsonText : str) -> str:
	jsonDictData = json.loads(jsonText)
	newJsonText = json.dumps(jsonDictData, indent = 4, ensure_ascii = False)
	return newJsonText


#------------------------------------------------------------------------
# 문자열에서 주석(//, /**/, #)을 전부 제거.
#------------------------------------------------------------------------
def RemoveAllCommentsInString(text : str) -> str:
	stringLiterals = re.findall(STRING_LITERAL_PATTERN, text, flags=re.MULTILINE | re.DOTALL)
	placeHolders = [f"__STRING_LITERAL_{index}__" for index in range(len(stringLiterals))]
	for index, stringLiteral in enumerate(stringLiterals): text = text.replace(stringLiteral, placeHolders[index])
	text = re.sub(COMMENT_PATTERN, "", text, flags = re.MULTILINE | re.DOTALL)
	for index, placeHolder in enumerate(placeHolders): text = text.replace(placeHolder, stringLiterals[index])
	return text