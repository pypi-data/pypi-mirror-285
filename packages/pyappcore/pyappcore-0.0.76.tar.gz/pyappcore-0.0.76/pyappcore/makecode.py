#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
import ast
from datetime import datetime as DateTime
import json
import os
import sys
from .application import Application
from .json_util import RemoveAllCommentsInString
from .module_util import Node, IsExistsPackageOrModule, IsExistsAttribute
from .str_util import GetSplitFilePath


#------------------------------------------------------------------------
# 전역 상수 목록.
#------------------------------------------------------------------------
DEPENDENCIESINBUILDFILENAME : str = "__pyappcore_dependencies_in_build__.py"
SYMBOLSINBUILDFILENAME : str = "__pyappcore_symbols_in_build__.py"
SLASH : str = "/"
COLON : str = "."
PYEXTENSION : str = ".py"
PACKAGE : str = "PACKAGE"
MODULE : str = "MODULE"
CLASS : str = "CLASS"
FUNCTION : str = "FUNCTION"
CARRIAGERETURN : str = "\r"
LINEFEED : str = "\n"
READMODE : str = "r"
WRITEMODE : str = "w"
UTF8 : str = "utf-8"
COMMAWITHSPACE : str = ", "
TYPEIGNORE : str = "# type: ignore"


#------------------------------------------------------------------------
# 대상 디렉토리에서 모듈을 찾아서 목록을 반환.
#------------------------------------------------------------------------
def FindModuleFilePaths(moduleDirPath : str) -> set:
	moduleFilePaths = set()
	for root, dirs, files in os.walk(moduleDirPath):
		for file in files:
			if not file.lower().endswith(PYEXTENSION):
				continue
			moduleFilePaths.add(os.path.join(root, file))
	return moduleFilePaths


#------------------------------------------------------------------------
# "#type: ignore" 를 추가할지 말지 여부.
# - fromimport의 from 혹은 import의 대상은 패키지 아니면 모듈이다.
#------------------------------------------------------------------------
def CheckTypeIgnore(fromName : str) -> bool:
	if IsExistsPackageOrModule(fromName):
		return False
	return True


#------------------------------------------------------------------------
# "# type: ignore" 를 추가할지 말지 여부.
# - fromimport의 import 혹은 import의 대상은 패키지, 모듈, 클래스, 함수이다.
#------------------------------------------------------------------------
def CheckTypeIgnores(fromName : str, importNames : list[str]) -> bool:
	if not importNames:
		return False
	for importName in importNames:
		if not IsExistsPackageOrModule(importName):
			return False
		if not IsExistsAttribute(fromName, importName):
			return False
	return True


#------------------------------------------------------------------------
# .vscode/settings.json 파일 불러오기.
#------------------------------------------------------------------------
def GetVisualStudioCodeSettings(rootDirPath : str) -> Union[dict, None]:
	try:
		settingsFilePath = f"{rootDirPath}/.vscode/settings.json"
		if os.path.exists(settingsFilePath):
			with builtins.open(settingsFilePath, READMODE, encoding = UTF8) as file:
				string = file.read()
				jsonText = RemoveAllCommentsInString(string)
				vscodeSettings = json.loads(jsonText)
				return vscodeSettings
		return None
	except Exception as exception:
		# Application.LogException(exception, False, False)
		Application.LogWarning(exception)
		return None


#------------------------------------------------------------------------
# 빌드시 심볼 파일 생성.
#------------------------------------------------------------------------
def CreateSymbolsInBuildToFile(symbols : list[str], symbolsDirPath : str) -> None:
	# 기존 파일 제거.
	symbolsFilePath : str = f"{symbolsDirPath}/{SYMBOLSINBUILDFILENAME}"
	if os.path.exists(symbolsFilePath):
		os.remove(symbolsFilePath)

	# 텍스트 작성.
	symbols = set(symbols)
	writelines = list()
	nowDateTime = DateTime.now()
	writelines.append(f"# Automatic dependency generation code used when building pyinstaller.")
	writelines.append(f"# Created time : {nowDateTime}")
	writelines.append("")
	writelines.append("")
	writelines.append(f"SYMBOLS = set()")
	for symbol in symbols:
		writelines.append(f"SYMBOLS.add(\"{symbol}\")")

	# 파일 작성.
	symbolsFilePath : str = f"{symbolsDirPath}/{SYMBOLSINBUILDFILENAME}"
	if os.path.exists(symbolsFilePath):  os.remove(symbolsFilePath)
	with open(symbolsFilePath, WRITEMODE, encoding = UTF8) as file:
		file.write(LINEFEED.join(writelines))


#------------------------------------------------------------------------
# 빌드시 의존성 참조 파일 생성.
#------------------------------------------------------------------------
def CreateDependenciesInBuildToFile(moduleDirPaths : list[str], sourceDirPath : str, otherModuleNames : set[str] = None) -> None:
	# 기존 파일 제거.
	dependenciesFilePath : str = f"{sourceDirPath}/{DEPENDENCIESINBUILDFILENAME}"
	if os.path.exists(dependenciesFilePath):
		os.remove(dependenciesFilePath)

	# 단독 임포트 금지 모듈 이름 목록.
	excludeDontOnlyImportModuleNames = list()
	excludeDontOnlyImportModuleNames.append("__future__")
	excludeDontOnlyImportModuleNames.append("mathutils")

	# 제외 모듈 이름 목록.
	excludesModuleNames = set()
	excludesModuleNames.add("__prebuild__")
	excludesModuleNames.add("__launcher__")
	excludesModuleNames.add("__init__")
	excludesModuleNames.add("__main__")
	excludesModuleNames.add("__pyappcore_dependencies_in_build__")

	# 모든 모듈 파일 경로 가져옴.
	moduleFilePaths = set()
	for moduleDirPath in moduleDirPaths:
		for moduleFilePath in FindModuleFilePaths(moduleDirPath):
			path, name, extension = GetSplitFilePath(moduleFilePath)
			if name in excludesModuleNames:
				continue

			moduleFilePaths.add(moduleFilePath)


	# "#type: Ignore" 체크를 위한 소스 폴더 추가.
	if sourceDirPath and sourceDirPath not in sys.path:
		sys.path.append(sourceDirPath)

	# 저장 자료구조 추가.
	importData = dict()
	importData["main"] = set()
 
	# 기본적으로 그 외 사용자 추가 모듈 들은 미리 추가해둔다.
	for otherModuleName in otherModuleNames:
		if not otherModuleName in importData:
			importData[otherModuleName] = set()
	
	# 파일 목록 순회.
	for moduleFilePath in moduleFilePaths:
	 
		# 파일(모듈)의 이름 가져오기.
		path, name, extension = GetSplitFilePath(moduleFilePath)

		# # 빌드되는 소스와 동일 폴더는 종속성 여부를 따지지 않고 일단 모듈부터 집어넣는다.
		# # 아래쪽에서 실제 소스안의 모듈이나 소스안의 모듈의 참조 클래스 등을 집어 넣는 상황도
  		# # 이미 고려되어 있기 때문에 미리 넣는다고 문제가 될 일은 아예 없다.
		# if not name in importData:
		# 	importData[name] = set()

		with open(moduleFilePath, READMODE, encoding = UTF8) as file:
			# 파싱 및 구문분석.
			astNode = ast.parse(file.read(), filename = moduleFilePath)   
			for current in ast.walk(astNode):

				# import 패키지 or 하위패키지 or 모듈.
				if isinstance(current, ast.Import):
					for alias in current.names:
						importTargetName = alias.name
						# importTargetType = GetImportType(alias.name)
						if importTargetName in excludesModuleNames:
							continue
						if importTargetName in excludeDontOnlyImportModuleNames:
							continue

						# importDatas.add(f"import {importTargetName}")
						# writelines.append(f"# [ast.Import][IMPORT] current.names.name: {importTargetName}, type: {importTargetType}")

						if not importTargetName in importData:
							importData[importTargetName] = set()

				# from 패키지 or 하위패키지 or 모듈 import 패키지 and 하위패키지 and 모듈 and 클래스 and 함수.
				elif isinstance(current, ast.ImportFrom):
					fromTargetName = current.module
					# fromTargettype = GetImportType(current.module)
					if fromTargetName:
						if fromTargetName in excludesModuleNames:
							continue

						if not fromTargetName in importData:
							importData[fromTargetName] = set()

						# writelines.append(f"# [ast.ImportFrom][FROM] current.module: {fromTargetName}, type: {fromTargettype}")

						# 클래스나 함수 추가.
						for alias in current.names:
							importTargetName = alias.name
							importData[fromTargetName].add(importTargetName)
							# importTargetType = GetImportType(alias.name)
							# importAndFromDatas.add(f"from {fromTargetName} import {importTargetName}")
							# writelines.append(f"# [ast.ImportFrom][IMPORT] current.names.name: {importTargetName}, type: {importTargetType}")

	# 텍스트 작성.
	nowDateTime = DateTime.now()
	writelines = list()
	writelines.append(f"# Automatic dependency generation code used when building pyinstaller.")
	writelines.append(f"# Created time : {nowDateTime}")
	writelines.append("")
	writelines.append("")

	# 제외해야하는 모듈 제거.
	for moduleName in importData.keys():
		if moduleName not in excludesModuleNames:
			continue
		del importData[moduleName]

	# 패키지 노드 가져오기.
	node = Node.BuildTree(sourceDirPath)
	srcnames = Node.GetModuleNames(node)
	srcnames = { name : path for path, name in srcnames.items()}

	# 참조 모듈 목록 작성.
	moduleNames = sorted(importData.keys(), key = lambda value: (value[0] != "_", value))
	for fromTargetName in moduleNames:		
		importTargetNames = importData[fromTargetName]

		srcname = fromTargetName
		if srcname in srcnames:
			srcname = srcnames[srcname]
		text : str = str()
		if importTargetNames:
			importTargetsText = COMMAWITHSPACE.join(importTargetNames)
			text = f"from {srcname} import {importTargetsText}"
			if CheckTypeIgnore(fromTargetName) or CheckTypeIgnores(fromTargetName, importTargetNames):
				text += f" {TYPEIGNORE}"
		else:
			text = f"import {srcname}"
			if CheckTypeIgnore(fromTargetName):
				text += f" {TYPEIGNORE}"
			
		writelines.append(text)

	# 파일 작성.
	with open(dependenciesFilePath, WRITEMODE, encoding = UTF8) as file:
		file.write(LINEFEED.join(writelines))