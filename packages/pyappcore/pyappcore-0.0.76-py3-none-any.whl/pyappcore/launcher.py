#------------------------------------------------------------------------
# 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
import debugpy # type: ignore
import importlib
import os
import sys
import unittest
from .application import Application
from .log_util import InitializeLogSystem
from .str_util import *


#------------------------------------------------------------------------
# 전역 상수 목록.
#------------------------------------------------------------------------
EMPTY : str = ""
FROZEN : str = "frozen"
MAIN : str = "__main__"
SLASH : str = "/"
SYMBOL_SUBPROCESS : str = "SUBPROCESS"
SYMBOL_LOG : str = "LOG"
SYMBOL_DEBUG : str = "DEBUG"
SYMBOL_NODEBUG : str = "NODEBUG"
DEPENDENCIESINBUILDMODULENAME : str = "__pyappcore_dependencies_in_build__"
SYMBOLSINBUILDMODULENAME : str = "__pyappcore_symbols_in_build__"


#------------------------------------------------------------------------
# 빌드.
#------------------------------------------------------------------------
def IsBuild() -> bool:
	# 실행 환경 체크.
	try:
		return builtins.getattr(sys, FROZEN, False)
	except Exception as exception:
		return False


#------------------------------------------------------------------------
# 유닛테스트용 시작.
#------------------------------------------------------------------------
def TestsLaunching(rootPath : str) -> int:
    # 파이썬 모듈 추가.
	# 테스트 하위 패키지.
	# testsPath : str = f"{rootPath}/tests"
	# if testsPath and testsPath not in sys.path: sys.path.append(testsPath)

	# 소스 하위 패키지.
	srcPath : str = f"{rootPath}/src"
	if srcPath and srcPath not in sys.path: sys.path.append(srcPath)

	# 소스, 테스트 패키지.
	if rootPath and rootPath not in sys.path: sys.path.append(rootPath)

	Application.Log("__tests__")
	Application._Application__SetBuild(False)
	Application._Application__SetDebug(False)
	Application._Application__SetSymbols("NODEBUG/LOG")
	Application._Application__SetRootPath(rootPath)
	Application._Application__SetResPath(f"{rootPath}/res")
	Application._Application__SetExecuteFileName("__main__.py")

	# 현재 폴더 전체 테스트. 
	testLoader = unittest.TestLoader()
	testResult = testLoader.discover(f"{rootPath}/tests", pattern = "test*.py")
	testRunner = unittest.TextTestRunner()
	testRunner.run(testResult)


#------------------------------------------------------------------------
# 시작.
#------------------------------------------------------------------------
def Launching(moduleName : str, functionName : str) -> int:
	Application.Log("pyappcore.launcher.Launch()")

	# 빌드인 경우 경로.
	isBuild : bool = IsBuild()
	if isBuild:
		# 실행파일에서 생성되는 임시 루트 경로.
		# 리소스를 위한 캐시폴더로 실제 실행파일의 위치가 아님.
		cachePath : str = sys._MEIPASS
		rootPath : str = os.path.dirname(sys.executable)
		sourceDirPath : str = os.path.join(cachePath, "src")
		resPath : str = os.path.join(cachePath, "res")
		workspacePath : str = os.path.join(rootPath, "workspace")
	# 빌드가 아닌 경우 경로.
	else:
		# 현재 프로젝트를 기준으로 한 경로.
		sourceDirPath : str = os.path.dirname(os.path.abspath(sys.modules[MAIN].__file__))
		rootPath : str = os.path.dirname(sourceDirPath)
		resPath : str = os.path.join(rootPath, "res")
		workspacePath : str = os.path.join(rootPath, "workspace")

	# 프로젝트 경로 등 설정.
	Application._Application__SetBuild(isBuild)
	Application._Application__SetRootPath(rootPath)
	Application._Application__SetResPath(resPath)
	Application._Application__SetWorkspacePath(workspacePath)
	Application._Application__SetSymbols(EMPTY)

	# 프로젝트 값 출력.
	Application.Log(f"Application.IsBuild(): {Application.IsBuild()}")  
	Application.Log(f"Application.GetRootPath(): {Application.GetRootPath()}")
	Application.Log(f"Application.GetResPath(): {Application.GetResPath()}")

	# 시도.
	try:
		# 실행파일 빌드.
		if Application.IsBuild():
			Application.Log("__build__")

			# 실행된 파일 이름 설정.
			if sys.argv:
				Application.Log("__execute__")
				executeFileName = sys.argv[0]
				Application._Application__SetExecuteFileName(executeFileName)
				sys.argv = sys.argv[1:]

			# 심볼 설정.
			if SYMBOLSINBUILDMODULENAME in sys.modules:
				Application.Log("__pycore_symbols_in_build__")
				module = sys.modules[SYMBOLSINBUILDMODULENAME]
				symbols = module.SYMBOLS
				if symbols:
					symbolsString : str = SLASH.join(symbols)
					Application._Application__SetSymbols(symbolsString)
					Application.Log(f"Application.GetSymbols(): {Application.GetSymbols()}")

			# 디버그 모드 설정.
			# 빌드 시 DEBUG 심볼이 있던 없던 무조건 False.
			Application._Application__SetDebug(False)
			Application.Log(f"Application.IsDebug(): {Application.IsDebug()}")
			Application.Log("__nodebug__")

		# 빌드 외.
		else:
			# VSCODE 기준 처리.
			# 일단 수동실행, VISUALSTUDIO, PYCHARM 기반에서 실행되는 것은 별도 이슈가 있을 것이므로 무시한다.
			Application.Log("__nobuild__")

			# pyappcore-source.bat을 통한 실행일 경우 9개 중 7개의 미사용 인수가 넘어오므로.
			# 심볼의 경우 첫글자는 영어대문자 혹은 언더바여야 하고, 이후는 영어대문자, 언더바, 숫자가 조합될 수 있음. 띄어쓰기 등은 허용하지 않음.
			sys.argv = [argument for argument in sys.argv if argument]

			# 실행된 파이썬 스크립트 파일 설정.
			if sys.argv:
				Application.Log("__execute__")
				executeFileName = sys.argv[0]
				Application._Application__SetExecuteFileName(executeFileName)
				sys.argv = sys.argv[1:]

			# 심볼 설정.
			if sys.argv:
				Application.Log("__symbols__")
				symbolsString = sys.argv[0]
				# Application.Log(f"symbolsString: {symbolsString}")
				Application._Application__SetSymbols(symbolsString)
				Application.Log(f"Application.GetSymbols(): {Application.GetSymbols()}")
				sys.argv = sys.argv[1:]

			# 디버그 모드 설정.
			useDebug : bool = Application.HasSymbol(SYMBOL_DEBUG)
			Application._Application__SetDebug(useDebug)
			Application.Log(f"Application.IsDebug(): {Application.IsDebug()}")
				
			# 디버그 모드 일 경우 원격 디버거 실행.
			# 콘솔에 출력되는 해당 문자열을 감지해서 디버그 대기와 시작을 판단하므로 수정금지.
			if Application.IsDebug():
				Application.Log("__debug__")
				Application.Log("pyappcore.launcher.debugpy.start()")
				remotePort : int = 4885 # vscodeSettings["launcher"]["debug"]["remotePort"]
				debugpy.listen(("localhost", remotePort))
				Application.Log("pyappcore.launcher.debugpy.wait()")
				debugpy.wait_for_client()
				Application.Log("pyappcore.launcher.debugpy.started()")
			else:
				Application.Log("__nodebug__")


		# 공통.
		# 인자 재조립 처리.
		# VSCODE 상황일때의 인자 목록은 문자열 리스트가 아닌 콤마로 합쳐진 형태로 넘어올 수 있음.
		# 어찌 되었건 쉼표 또한 구분자로 인정하고 공통 처리.
		if not Application.IsBuild() and sys.argv:
			sys.argv = CreateStringListFromSeperatedStringList(sys.argv)	

		# 잔여 인자 출력.
		if sys.argv:
			Application.Log("__arguments__")
			index = 0
			for arg in sys.argv:
				Application.Log(f" - [{index}] {arg}")
				index += 1

		# 로그 설정.
		# 순서 : DEBUG < INFO < WARNING < ERROR < CRITICAL.
		useLogFile : bool = Application.HasSymbol(SYMBOL_LOG)
		if useLogFile:
			Application.Log("__log__")
			InitializeLogSystem()

	# 예외.
	except Exception as exception:
		Application.LogException(exception)
		
	# 시작.
	try:
		Application.Log("__running__")
		module = importlib.import_module(moduleName)
		function = builtins.getattr(module, functionName)
		exitCode : int = function(sys.argv)
		return exitCode
	# 예외.
	except Exception as exception:
		Application.LogException(exception)


# #------------------------------------------------------------------------
# # 파일 진입점.
# #------------------------------------------------------------------------
# if __name__ == "__main__":
# 	exitCode = Launching()
# 	sys.exit(exitCode)