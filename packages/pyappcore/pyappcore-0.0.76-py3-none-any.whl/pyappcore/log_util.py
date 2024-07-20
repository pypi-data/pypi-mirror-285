#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
from logging import Logger, handlers, Handler, StreamHandler, FileHandler, Formatter, LogRecord, getLevelName, NOTSET, DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL, FATAL
import os
import queue
import threading
from .ansicode import *
from .str_util import GetTimestampString


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
# 화면 출력 핸들러.
#------------------------------------------------------------------------
class PrintHandler(Handler):
	def emit(self, record : LogRecord):
		message = self.format(record)
		# if record.levelno == FATAL or record.levelno == CRITICAL: Print(f"<bg_red><white><b>{message}</b></white></bg_red>")
		# elif record.levelno == ERROR: Print(f"<red>{message}</red>")
		# elif record.levelno == WARN or record.levelno == WARNING: Print(f"<yellow>{message}</yellow>")
		# elif record.levelno == INFO: Print(f"{message}")
		# elif record.levelno == DEBUG: Print(f"<magenta>{message}</magenta>")
		PrintLog(message, record.levelno)


#------------------------------------------------------------------------
# 화면 출력.
#------------------------------------------------------------------------
def InitializeLogSystem():
	# 순환참조 무서워서 로컬 임포트.
	from .application import Application, SYMBOL_SERVICE
	timestamp = GetTimestampString(EMPTY, EMPTY, EMPTY, True, EMPTY)
	useLogFile : bool = False
	logLevel : int = NOTSET
	logFilePath : str = str()

	# EXE 파일 실행.
	if Application.IsBuild():
		useLogFile = False
		logLevel = WARNING
	# VSCode에서 디버깅 실행.
	elif Application.IsDebug():
		useLogFile = True
		logLevel = DEBUG
		logFilePath = Application.GetRootPathWithRelativePath(f"logs/pyappcore-debug-{timestamp}.log")
	# Blender.exe로 소스코드 실행.
	elif Application.HasSymbol(SYMBOL_SERVICE):
		useLogFile = True
		logLevel = INFO
		logFilePath = Application.GetRootPathWithRelativePath(f"logs/pyappcore-service-{timestamp}.log")
	# VSCode에서 디버깅 없이 실행.
	else:
		useLogFile = True
		logLevel = INFO
		logFilePath = Application.GetRootPathWithRelativePath(f"logs/pyappcore-nodebug-{timestamp}.log")


	# 설정.
	applicationLogger : Logger = Application.GetLogger()
	applicationLogger.setLevel(logLevel)

	# 로깅 큐.
	# 로그가 자꾸 씹히는 이슈 있음.
	logQueue = queue.Queue()
	ququeHandler = handlers.QueueHandler(logQueue)
	applicationLogger.addHandler(ququeHandler)

	# formatter : Formatter = Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s")
	formatter : Formatter = Formatter("[%(asctime)s][%(levelname)s] %(message)s")

	# 프린트 핸들러.
	# printHandler : PrintHandler = PrintHandler()
	# printHandler.setLevel(logLevel)
	# printHandler.setFormatter(formatter)
	# applicationLogger.addHandler(printHandler)

	# 로그파일 설정.
	if useLogFile:
		logDirPath = Application.GetRootPathWithRelativePath("logs")
		if not os.path.exists(logDirPath):
			os.makedirs(logDirPath)
		fileHandler : StreamHandler = FileHandler(logFilePath, encoding = "utf-8")
		fileHandler.setLevel(logLevel)
		fileHandler.setFormatter(formatter)
		# applicationLogger.addHandler(fileHandler)
		# queueListener = handlers.QueueListener(logQueue, printHandler, fileHandler)
		queueListener = handlers.QueueListener(logQueue, fileHandler)
		queueListener.start()


#------------------------------------------------------------------------
# 로그 출력.
#------------------------------------------------------------------------
def PrintLog(text : str, logLevel : int) -> None:
	if logLevel == FATAL or logLevel == CRITICAL: Print(f"<bg_red><white><b>{text}</b></white></bg_red>")
	elif logLevel == ERROR: Print(f"<red>{text}</red>")
	elif logLevel == WARN or logLevel == WARNING: Print(f"<yellow>{text}</yellow>")
	elif logLevel == INFO: Print(f"{text}")
	elif logLevel == DEBUG: Print(f"<magenta>{text}</magenta>")


#------------------------------------------------------------------------
# 로그레벨에 대한 문자열 출력.
#------------------------------------------------------------------------
def GetStringFromLogLevel(logLevel : int) -> str:
	return getLevelName(logLevel)