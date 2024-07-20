#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
import json
import logging
from logging import Logger
import re
import subprocess
import sys
import traceback
from .ansicode import *
from .json_util import *
from .str_util import *
from .log_util import PrintLog, GetStringFromLogLevel


#------------------------------------------------------------------------
# 전역 상수 목록.
#------------------------------------------------------------------------
EMPTY : str = ""
NONE : str = "NONE"
COMMA : str = ","
SLASH : str = "/"
BACKSLASH : str = "\\"
COLON : str = ":"
SPACE : str = " "
DEBUG : str = "DEBUG"

SYMBOL_SERVICE : str = "SERVICE" # "PYAPPCORE_SYMBOL_SERVICE"
SYMBOL_SUBPROCESS : str = "SUBPROCESS" # "PYAPPCORE_SYMBOL_SUBPROCESS"
SYMBOL_LOG : str = "LOG" # "PYAPPCORE_SYMBOL_LOG"
SYMBOL_DEBUG : str = "DEBUG" # "PYAPPCORE_SYMBOL_DEBUG"
NODEBUG : str = "NODEBUG" # "PYAPPCORE_SYMBOL_NODEBUG"

SYMBOL_NAMING_PATTERN : str = "^[A-Z_][A-Z0-9_]*$"
CONFIGURATION_FILENAME : str = "configuration.json"
PYAPPCORE_LOG_LOGGERNAME : str = "pyappcore"
LOG_CRITICAL : int  = 50
LOG_ERROR : int = 40
LOG_EXCEPTION : int  = 40
LOG_WARNING : int  = 30
LOG_INFO : int = 20
LOG_DEBUG : int  = 10
LOG_NOTSET : int = 0


#------------------------------------------------------------------------
# 애플리케이션.
#------------------------------------------------------------------------
class Application:
	__ExecuteFileName : str = str()
	__IsBuild : bool = False
	__IsDebug : bool = False
	__RootPath : str = str()
	__ResPath : str = str()
	__WorkspacePath : str = str()
	__Symbols : set[str] = set()

	#------------------------------------------------------------------------
	# 실제 로그 출력.
	#------------------------------------------------------------------------
	@staticmethod
	def __Log(message : str, logLevel : int) -> None:

		# 일단 콘솔에 출력.
		timestamp = GetTimestampString(HYPHEN, SPACE, COLON, True, COMMA)
		logName = GetStringFromLogLevel(logLevel)
		# builtins.print(f"[{timestamp}][{logName}] {message}")
		PrintLog(f"[{timestamp}][{logName}] {message}", logLevel)

		# 로그파일 기록시.
		if Application.HasSymbol(SYMBOL_LOG):
			applicationLogger = Application.GetLogger()
			if logLevel == LOG_NOTSET: # logging.NOTSET:
				return
			elif logLevel == LOG_DEBUG: # logging.DEBUG:
				applicationLogger.debug(message)
			elif logLevel == LOG_INFO: # logging.INFO:
				applicationLogger.info(message)
			elif logLevel == LOG_WARNING: # logging.WARN or logging.WARNING:
				applicationLogger.warning(message)
			elif logLevel == LOG_ERROR: # logging.ERROR:
				applicationLogger.error(message)
			elif logLevel == LOG_CRITICAL: # logging.FATAL or logging.CRITICAL:
				applicationLogger.critical(message)

	#------------------------------------------------------------------------
	# 로그 디버그 출력.
	#------------------------------------------------------------------------
	@staticmethod
	def LogDebug(message : str) -> None:
		Application._Application__Log(message, LOG_DEBUG)

	#------------------------------------------------------------------------
	# 로그 인포 출력.
	#------------------------------------------------------------------------
	@staticmethod
	def Log(message : str) -> None:
		Application._Application__Log(message, LOG_INFO)

	#------------------------------------------------------------------------
	# 로그 인포 출력.
	#------------------------------------------------------------------------
	@staticmethod
	def LogInfo(message : str) -> None:
		Application._Application__Log(message, LOG_INFO)

	#------------------------------------------------------------------------
	# 로그 워닝 출력.
	#------------------------------------------------------------------------
	@staticmethod
	def LogWarning(message : str) -> None:
		Application._Application__Log(message, LOG_WARNING)

	#------------------------------------------------------------------------
	# 로그 에러 출력.
	#------------------------------------------------------------------------
	@staticmethod
	def LogError(message : str) -> None:
		Application._Application__Log(message, LOG_ERROR)

	#------------------------------------------------------------------------
	# 로그 익셉션 출력.
	#------------------------------------------------------------------------
	@staticmethod
	def LogException(exception : Exception, useTraceback : bool = True, useExit : bool = True) -> None:
		if useTraceback:
			traceback.print_exc()
			tb = exception.__traceback__
			while tb:
				filename = tb.tb_frame.f_code.co_filename
				lineno = tb.tb_lineno
				funcname = tb.tb_frame.f_code.co_name
				result = traceback.format_exc()
				result = result.strip()
				line = result.splitlines()[-1]
				Application._Application__Log(f"Exception in {filename}, line {lineno}, in {funcname}", LOG_EXCEPTION)
				Application._Application__Log(f"\t{line}", LOG_EXCEPTION)
				tb = tb.tb_next
		else:
			Application._Application__Log(exception, LOG_EXCEPTION)

		if useExit:
			sys.exit(1)
	
	#------------------------------------------------------------------------
	# 로그 크리티컬 출력.
	#------------------------------------------------------------------------
	@staticmethod
	def LogCritical(message : str) -> None:
		Application._Application__Log(message, LOG_CRITICAL)
	
	# ----------------------------------------------------------------------------------
	# 메인 프로세스에서 서브 프로세스 실행.
	# - 예를 들어 블렌더 : {pythonInterpreterPath} "--background" "--python" launcher.py {symbols} {argument1} {argument2} ...
	# - 블렌더 기준의 options : "--background" "--python" ...
	# - 블렌더 기준의 arguments : {argument1} {argument2} ...
	# ----------------------------------------------------------------------------------
	@staticmethod
	def RunSubprocess(pythonInterpreterPath : str, options : set[str], symbols : set[str], arguments : list[str]) -> subprocess.CompletedProcess:
		commands = set()
		commands.append(pythonInterpreterPath)
		
		if Application.IsBuild():
			pass
		else:
			pass

		# 옵션 설정.
		if options:
			for option in options:
				commands.add(option)

		# 시작 파일 설정.
		commands.add(Application.GetRootPathWithRelativePath("/src/__launcher__.py"))

		# 객체 생성 및 심볼 설정.
		if symbols:
			symbols.add(SYMBOL_SUBPROCESS)
		else:
			symbols = set()
			symbols.add(SYMBOL_SUBPROCESS)
		commands.add(SLASH.join(symbols))
		
		if arguments:
			for argument in arguments:
				commands.add(argument)
		
		return subprocess.run(commands, check = True)

 	#------------------------------------------------------------------------
	# 실행 된 파일 이름.
	#------------------------------------------------------------------------
	@staticmethod
	def __SetExecuteFileName(executeFileName : str) -> None:
		Application._Application__ExecuteFileName = executeFileName

 	#------------------------------------------------------------------------
	# 빌드 여부 설정.
	#------------------------------------------------------------------------
	@staticmethod
	def __SetBuild(isBuild : bool) -> None:
		Application._Application__IsBuild = isBuild

	#------------------------------------------------------------------------
	# 디버그 모드 여부 설정.
	#------------------------------------------------------------------------
	@staticmethod
	def __SetDebug(isDebug : bool) -> None:
		Application._Application__IsDebug = isDebug

	#------------------------------------------------------------------------
	# 루트 경로 설정.
	#------------------------------------------------------------------------
	@staticmethod
	def __SetRootPath(rootPath : str) -> None:
		Application._Application__RootPath = rootPath.replace(BACKSLASH, SLASH)

	#------------------------------------------------------------------------
	# 리소스 경로 설정.
	#------------------------------------------------------------------------
	@staticmethod
	def __SetResPath(resPath : str) -> None:
		if not os.path.isdir(resPath): os.makedirs(resPath)
		Application._Application__ResPath = resPath.replace(BACKSLASH, SLASH)

	#------------------------------------------------------------------------
	# 워크스페이스 경로 설정.
	#------------------------------------------------------------------------
	@staticmethod
	def __SetWorkspacePath(workspacePath : str) -> None:
		if not os.path.isdir(workspacePath): os.makedirs(workspacePath)
		Application._Application__WorkspacePath = workspacePath.replace(BACKSLASH, SLASH)

	#------------------------------------------------------------------------
	# 기존 심볼을 모두 지우고 새로운 심볼 목록 설정 (구분자 : /).
	#------------------------------------------------------------------------
	@staticmethod
	def __SetSymbols(symbolsString : str) -> None:
		if symbolsString:
			# 입력받은 텍스트 정리.
			symbolsString = symbolsString.upper()
			symbols : list[str] = GetStringFromSeperatedStringList(symbolsString, SLASH)

			# 객체 생성 및 심볼 설정.
			Application._Application__Symbols = set()
			if symbols:
				for symbol in symbols:
					if symbol and not re.match(SYMBOL_NAMING_PATTERN, symbol):
						continue
					Application._Application__Symbols.add(symbol)

		# NONE, EMPTY, SPACE는 없는 것과 마찬가지이므로 목록에서 제거.
		Application._Application__Symbols.discard(NONE)
		Application._Application__Symbols.discard(EMPTY)
		Application._Application__Symbols.discard(SPACE)

	# #------------------------------------------------------------------------
	# # 기존 심볼에 새로운 심볼을 추가.
	# #------------------------------------------------------------------------
	# @staticmethod
	# def __AddSymbols(symbolsString : str) -> None:
	# 	additionalSymbols = GetStringFromSeperatedStringList(symbolsString, SLASH)
	# 	symbols = Application.GetSymbols()
	# 	if symbols:
	# 		symbols.extend(additionalSymbols)
	# 		symbolsString = SLASH.join(symbols)
	# 	Application._Application__SetSymbols(symbolsString)

	#------------------------------------------------------------------------
	# 빌드된 상태인지 여부.
	#------------------------------------------------------------------------
	@staticmethod
	def IsBuild() -> bool:
		return Application._Application__IsBuild

	#------------------------------------------------------------------------
	# 디버깅 상태인지 여부.
	#------------------------------------------------------------------------
	@staticmethod
	def IsDebug() -> bool:
		return Application._Application__IsDebug

	#------------------------------------------------------------------------
	# 실행된 파일 이름 반환.
	#------------------------------------------------------------------------
	def GetExecuteFileName() -> str:
		return Application._Application__ExecuteFileName

	#------------------------------------------------------------------------
	# 애플리케이션이 존재하는 경로 / 실행파일이 존재하는 경로.
	#------------------------------------------------------------------------
	@staticmethod
	def GetRootPath() -> str:
		return Application._Application__RootPath

	#------------------------------------------------------------------------
	# 리소스 경로 / 실행 파일 실행시 임시 리소스 폴더 경로.
	#------------------------------------------------------------------------
	@staticmethod
	def GetResPath() -> str:
		return Application._Application__ResPath

	#------------------------------------------------------------------------
	# 워크스페이스 폴더 경로.
	#------------------------------------------------------------------------
	@staticmethod
	def GetWorkspacePath() -> str:
		return Application._Application__WorkspacePath
	
	#------------------------------------------------------------------------
	# 현재 앱에 해당 심볼이 등록 되어있는지 여부.
	#------------------------------------------------------------------------
	@staticmethod
	def HasSymbol(symbolString : str) -> bool:
		if not Application._Application__Symbols:
			return False
		symbols = Application._Application__Symbols
		if not symbols:
			return False
		if not symbolString in symbols:
			return False
		return True

	#------------------------------------------------------------------------
	# 현재 앱에 입력되어있는 심볼 목록.
	#------------------------------------------------------------------------
	@staticmethod
	def GetSymbols() -> list[str]:
		return list(Application._Application__Symbols)

	#------------------------------------------------------------------------
	# 애플리케이션이 존재하는 경로에 상대경로를 입력하여 절대경로를 획득.
	#------------------------------------------------------------------------
	@staticmethod
	def GetRootPathWithRelativePath(relativePath : str) -> str:
		rootPath = Application.GetRootPath()
		if not relativePath:
			return rootPath
		relativePath = relativePath.replace(BACKSLASH, SLASH)
		absolutePath = f"{rootPath}/{relativePath}"
		return absolutePath

	#------------------------------------------------------------------------
	# 리소스가 존재하는 경로에 상대경로를 입력하여 절대경로를 획득.
	#------------------------------------------------------------------------
	@staticmethod
	def GetResPathWithRelativePath(relativePath : str) -> str:
		resPath = Application.GetResPath()
		if not os.path.isdir(resPath):
			os.makedirs(resPath)
		if not relativePath:
			return resPath
		relativePath = relativePath.replace(BACKSLASH, SLASH)
		absolutePath = f"{resPath}/{relativePath}"
		return absolutePath
	
	#------------------------------------------------------------------------
	# 워크스페이스 경로에 상대경로를 입력하여 절대경로를 획득.
	# - 기본적으로 워크스페이스 경로는 실행파일과 동일 계층에 워크스페이스 폴더가 만들어진다.
	#------------------------------------------------------------------------
	@staticmethod
	def GetWorkspacePathWithRelativePath(relativePath : str) -> str:
		workspacePath = Application.GetWorkspacePath()
		if not os.path.isdir(workspacePath):
			os.makedirs(workspacePath)
		if not relativePath:
			return workspacePath
		relativePath = relativePath.replace(BACKSLASH, SLASH)
		absolutePath = f"{workspacePath}/{relativePath}"

		return absolutePath

	#------------------------------------------------------------------------
	# 로거 반환.
	#------------------------------------------------------------------------
	@staticmethod
	def GetLogger() -> Logger:
		return logging.getLogger(PYAPPCORE_LOG_LOGGERNAME)

	#------------------------------------------------------------------------
	# 설정값 반환 : "{workspace}/res/configuration.json" 필요, 만약 파일이 없으면 None 반환.
	#------------------------------------------------------------------------
	@staticmethod
	def GetConfiguration(propertyName : str = EMPTY) -> Union[dict, None]:
		try:
			configFilePath = Application.GetResPathWithRelativePath(CONFIGURATION_FILENAME)
			with open(configFilePath, "r") as file:
				jsonText = RemoveAllCommentsInString(file.read())
				jsonData = json.loads(jsonText)
				if propertyName:
					return jsonData[propertyName]
				else:
					return jsonData     
		except Exception as exception:
			Application.LogException(exception, False, False)
			return None