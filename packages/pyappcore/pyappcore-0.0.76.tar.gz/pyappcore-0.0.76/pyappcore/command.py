#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
import argparse
import os
import re
import sys
import shutil


#------------------------------------------------------------------------
# 전역 상수 목록.
#------------------------------------------------------------------------
EMPTY : str = str()
GITKEEPFILENAME : str = ".gitkeep"
SLASH : str = "/"
BACKSLASH : str = "\\"
CURRENTFILEPATH : str = os.path.abspath(__file__)
SRCPATH : str = os.path.dirname(CURRENTFILEPATH).replace(BACKSLASH, SLASH)
ROOTPATH : str = os.path.dirname(SRCPATH).replace(BACKSLASH, SLASH)
RESPATH : str = f"{ROOTPATH}/res"
NOT_DIRECTORYNAME_PATTERN : str =  "[<>:\"/\\|?*\x00-\x1F]"
TEMPLATEFILES : list = {
	("launch.json", ".vscode"),
	("settiings.json",".vscode"),
	("task.json", ".vscode"),

	("configuration.json", "res"),

	("__init__.py", "src"),
	("__launcher__.py", "src"),
	("__prebuilder__.py", "src"),
	("main.py", "src"),

	("__init__.py", "tests"),
	("__main__.py", "tests"),
	("main.py", "tests"),

	(".env", ""),

	("requirements.txt", ""),

	("venv-create.bat", ""),
	("venv-destroy.bat", ""),
	("venv-enable.bat", ""),
	("venv-disable.bat", ""),
	("venv-pip.bat", ""),

	("pyappcore-path.bat", ""),
	("pyappcore-build.bat", ""),
	("pyappcore-prebuild.bat", ""),
	("pyappcore-source.bat", ""),
	("pyappcore-tests.bat", ""),

	("project-path.bat", ""),
	("project-pip.bat", ""),

	("run-source.bat", ""),
	("run-source.sh", ""),
	("run-exec.bat", ""),
	# ("run-uitool.bat", ""),

	# ("run-service-dev.bat", ""),
	# ("run-service-test.bat", ""),
	# ("run-service-live.bat", ""),

	# {"run-service.sh", ""}
	# ("run-service-dev.sh", ""),
	# ("run-service-test.sh", ""),
	# ("run-service-live.sh", ""),
}


#------------------------------------------------------------------------
# 파일 불러오기.
#------------------------------------------------------------------------
def LoadContentFromFile(filePath : str) -> str:
	if not filePath:
		return EMPTY
	if not os.path.isfile(filePath):
		return EMPTY
	try:
		with builtins.open(filePath, "r", encoding = "utf-8") as file:
			content = file.read()
			return content
	except Exception as exception:
		builtins.print(exception)
		return EMPTY		
		

#------------------------------------------------------------------------
# 파일 저장하기.
# - 파일 생성시 경로 내에 폴더가 존재하지 않으면 폴더 생성.
#------------------------------------------------------------------------
def SaveContentToFile(filePath : str, content : str = EMPTY, isOverwrite = False) -> bool:
	if not filePath:
		return False

	if not isOverwrite and os.path.isfile(filePath):
		return False

	try:
		path = os.path.dirname(filePath)
		if not os.path.isdir(path):
			os.makedirs(path)

		with builtins.open(filePath, "w", encoding = "utf-8") as file:
			file.write(content)
		return True
	except Exception as exception:
		builtins.print(exception)
		return False


#------------------------------------------------------------------------
# .gitkeep 파일 생성.
#------------------------------------------------------------------------
def MakeDirectoryAndGitKeepFile(keepPath) -> None:
	gitKeepFilePath = f"{keepPath}/{GITKEEPFILENAME}"
	SaveContentToFile(gitKeepFilePath)


#------------------------------------------------------------------------
# 디렉토리 이름으로 유효한지 체크.
#------------------------------------------------------------------------
def IsValidateDirectoryName(directoryName : str) -> bool:
    # 공통 규칙 적용
    if re.search(NOT_DIRECTORYNAME_PATTERN, directoryName):
        return False  
    return True


#------------------------------------------------------------------------
# 새로운 프로젝트 생성.
#------------------------------------------------------------------------
def Create(projectPath : str) -> bool:
	# 스크립트를 실행한 터미널의 현재 경로.
	executedPath = os.getcwd()
	builtins.print(f"[pyappcore] executedPath: {executedPath}")

	# 루트경로 생성.
	rootPath = EMPTY
	# 경로가 비어있거나 점이라면.
	if projectPath == EMPTY or projectPath == ".":
		rootPath = executedPath
	# 경로가 존재하는 파일일 경우 파일이 존재하는 디렉토리를 선택.
	elif os.path.isfile(projectPath):
		rootPath = os.path.dirname(projectPath)
	# 파일이 아닌데 실존하는 디렉토리 일 경우.
	elif os.path.isdir(projectPath):
		rootPath = projectPath
	# 그 외.
	# 현재 위치에서 해당 이름으로 하위 디렉토리 추가.
	elif IsValidateDirectoryName(projectPath):
		rootPath = f"{executedPath}/{projectPath}"
	# 도저히 폴더를 만들 수 없다면 해볼 수 있는게 없음.
	else:
		return False


	# 해당 경로를 기준으로 프로젝트 생성.
	builtins.print(f"[pyappcore] create project path: {rootPath}")
	if not os.path.isdir(rootPath): os.makedirs(rootPath)

	# 프로젝트 디렉토리 하위 디렉토리 목록.
	vscodePath = f"{rootPath}/.vscode"
	buildPath = f"{rootPath}/build"
	hintsPath = f"{rootPath}/hints"
	libsPath = f"{rootPath}/libs"
	logsPath = f"{rootPath}/logs"
	resPath = f"{rootPath}/res"
	srcPath = f"{rootPath}/src"
	testsPath = f"{rootPath}/tests"
	workspace = f"{rootPath}/workspace"
	
	# 디렉토리 및 .gitkeep 파일 생성.
	MakeDirectoryAndGitKeepFile(vscodePath)
	MakeDirectoryAndGitKeepFile(buildPath)
	MakeDirectoryAndGitKeepFile(hintsPath)
	MakeDirectoryAndGitKeepFile(libsPath)
	MakeDirectoryAndGitKeepFile(logsPath)
	MakeDirectoryAndGitKeepFile(resPath)
	MakeDirectoryAndGitKeepFile(srcPath)
	MakeDirectoryAndGitKeepFile(testsPath)
	MakeDirectoryAndGitKeepFile(workspace)

	# 복사할 파일 순회.
	templateRootPath = f"{RESPATH}/template"
	for templateFile in TEMPLATEFILES:
		templateFileName = templateFile[0]
		templateDirectoryName = templateFile[1]

		if templateDirectoryName:
			loadFilePath = f"{templateRootPath}/{templateDirectoryName}/{templateFileName}"
			saveFilePath = f"{rootPath}/{templateDirectoryName}/{templateFileName}"
		else:
			loadFilePath = f"{templateRootPath}/{templateFileName}"
			saveFilePath = f"{rootPath}/{templateFileName}"

		# 파일 읽기.
		content = LoadContentFromFile(loadFilePath)

		# 파일 저장.
		SaveContentToFile(saveFilePath, content)


#------------------------------------------------------------------------
# 외부 호출.
#------------------------------------------------------------------------
def Run():
	# 실행 인자 획득.
	argumentParser = argparse.ArgumentParser(description = "pyappcore commands.")
	argumentParser.add_argument("name", type = str, help = "")
	argumentParser.add_argument('--type', type = str, default = "none", help = "")
	argumentParser.add_argument('--path', type = str, default = ".", help = "")
	argumentObject = argumentParser.parse_args()
	commandName = argumentObject.name.upper()

	builtins.print(f"[pyappcore] Command: {commandName}")

	# 프로젝트 생성.
	if commandName == "CREATE":
		projectPath = argumentObject.path
		Create(projectPath)
	else:
		builtins.print("[pyappcore] not found input command.")