#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
import importlib.util
import os
from .application import Application
from .str_util import GetSplitFilePath


#------------------------------------------------------------------------
# 전역 상수 목록.
#------------------------------------------------------------------------
PYEXTENSION : str = "py"
INITNAME : str = "__init__"
INITFILENAME : str = f"{INITNAME}.{PYEXTENSION}"
BUILTIN : str = "built-in"
EMPTY : str = ""


#------------------------------------------------------------------------
# 노드.
#------------------------------------------------------------------------
class Node:
	#------------------------------------------------------------------------
	# 공개 멤버 변수 목록.
	#------------------------------------------------------------------------
	Name : str # 패키지, 모듈, 클래스, 함수 이름.
	Path : str # 패키지를 포함한 전체 이름.
	IsPackage : bool # 패키지 여부. 
	Parent : Node # 부모.
	Children : list # 자식들.

	#------------------------------------------------------------------------
	# 생성됨.
	#------------------------------------------------------------------------
	def __init__(self, name : str = EMPTY, path : str = EMPTY, parent : Node = None, isPackage : bool = False):
		self.Name = name
		self.Path = path
		self.IsPackage = isPackage
		self.Parent = parent		
		self.Children = list()

	#------------------------------------------------------------------------
	# 클래스 문자열 변환됨.
	#------------------------------------------------------------------------
	def __repr__(self, level : int = 0):
		ret = "\t" * level + repr(self.Name) + "\n"
		for child in self.Children:
			ret += child.__repr__(level + 1)
		return ret
	
	#------------------------------------------------------------------------
	# 자식 노드 추가.
	#------------------------------------------------------------------------
	def AddChild(self, childNode : Node):
		childNode.Parent = self
		self.Children.append(childNode)

	#------------------------------------------------------------------------
	# 패키지 여부.
	# - 폴더 경로를 넣어서 확인.
	#------------------------------------------------------------------------
	@staticmethod
	def CheckPackage(path : str) -> bool:
		if not os.path.isdir(path):
			return False
		initFilePath = os.path.join(path, INITFILENAME)
		if not os.path.isfile(initFilePath):
			return False
		return True

	#------------------------------------------------------------------------
	# 폴더 기반 트리 구조 작성.
	#------------------------------------------------------------------------
	@staticmethod
	def BuildTree(path : str, parent : Node = None) -> Node:
		name = os.path.basename(path)
		node = Node(name, path, parent, True)
		for childName in os.listdir(path):
			childPath = os.path.join(path, childName)
			if os.path.isdir(childPath):
				if Node.CheckPackage(childPath):
					child = Node.BuildTree(childPath, node)
					node.AddChild(child)
			else:
				cpath, cname, cextension = GetSplitFilePath(childPath)				
				if not cextension.endswith(PYEXTENSION):
					continue
				if cname == INITNAME:
					continue
				child = Node(cname, childPath, parent, False)
				node.AddChild(child)
		return node

	#------------------------------------------------------------------------
	# 트리 탐색.
	#------------------------------------------------------------------------
	@staticmethod
	def TraverseTree(node : Node, prefix : str = EMPTY, usePrint : bool = True, moduleFullNames : dict[str, str] = None) -> None:
		if node.IsPackage:
			path = f"{prefix}.{node.Name}" if prefix else node.Name
			if usePrint:
				Application.Log(f"package: {path}")
			for child in node.Children:
				Node.TraverseTree(child, path, usePrint, moduleFullNames)
		else:
			path = f"{prefix}.{node.Name}" if prefix else node.Name
			if usePrint:
				Application.Log(f"module: {path}")
			if not moduleFullNames is None:
				moduleFullNames[path] = node.Name

	#------------------------------------------------------------------------
	# 노드 기준 모듈 이름 반환.
	# - KEY : 패키지포함모듈명, VALUE : 모듈명
	#------------------------------------------------------------------------
	@staticmethod
	def GetModuleNames(node : Node) -> dict[str, str]:
		moduleFullNames = dict()
		Node.TraverseTree(node, EMPTY, False, moduleFullNames)
		return moduleFullNames


#------------------------------------------------------------------------
# 실제 존재하는 패키지 혹은 모듈 인지 여부.
#------------------------------------------------------------------------
def IsExistsPackageOrModule(packageOrModuleName : str) -> bool:
	try:
		# 모듈 정보 가져오기.
		moduleSpec = importlib.util.find_spec(packageOrModuleName)
		if not moduleSpec:
			return False
		else:
			# 모듈이 존재할 경우 origin은 해당 모듈의 경로 혹은 인터프리터 내장 라이브러리 식별자.
			moduleFilePath = moduleSpec.origin
			if not moduleFilePath:
				return False
			# 빌트인 인 경우는 실제 파일은 없지만 파이썬 인터프리터에 내장된 라이브러리이므로 있다고 간주.
			if not moduleFilePath == BUILTIN:
				return True
			# 경로가 실존하는 파일이나 폴더일 경우 있다고 간주.
			if os.path.isfile(moduleFilePath) or os.path.isdir(moduleFilePath):
				return True                
			return False
	except Exception as exception:
		# Application.LogException(exception, False, False)
		Application.LogWarning(exception)
		return False


#------------------------------------------------------------------------
# 실제 존재하는 어트리뷰트인지 여부.
#------------------------------------------------------------------------
def IsExistsAttribute(moduleName : str, attributeName : str) -> bool:
	if not IsExistsPackageOrModule(moduleName):
		return False
	try:
		module = importlib.import_module(moduleName)
		if not builtins.hasattr(module, attributeName):
			return False
	except Exception as exception:
		# Application.LogException(exception, False, False)
		Application.LogWarning(exception)
		return False
	return True