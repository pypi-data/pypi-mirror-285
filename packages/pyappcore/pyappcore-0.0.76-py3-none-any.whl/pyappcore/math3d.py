#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins


#------------------------------------------------------------------------
# 공통 벡터.
#------------------------------------------------------------------------
class BaseVector:
	#------------------------------------------------------------------------
	# 비공개 클래스 변수 목록.
	#------------------------------------------------------------------------
	__Values : tuple[float, ...]
	__Dimension : int

	#------------------------------------------------------------------------
	# 생성됨.
	#------------------------------------------------------------------------
	def __init__(self, *values : float):
		self.__Values = values
		self.__class__.__Dimension = len(values)

	#------------------------------------------------------------------------
	# 문자열 변환 연산자.
	#------------------------------------------------------------------------
	def __repr__(self) -> str:
		return f"Vector{len(self.__Values)}{self.__Values}"

	#------------------------------------------------------------------------
	# 더하기 연산자.
	#------------------------------------------------------------------------
	def __add__(self, other : BaseVector) -> BaseVector:
		return BaseVector(*(left + right for left, right in zip(self.__Values, other.__Values)))

	#------------------------------------------------------------------------
	# 빼기 연산자.
	#------------------------------------------------------------------------
	def __sub__(self, other : BaseVector) -> BaseVector:
		return BaseVector(*(left - right for left, right in zip(self.__Values, other.__Values)))

	#------------------------------------------------------------------------
	# 곱하기 연산자.
	#------------------------------------------------------------------------
	def __mul__(self, scalar : float) -> BaseVector:
		return BaseVector(*(left * scalar for left in self.__Values))

	#------------------------------------------------------------------------
	# 나누기 연산자.
	#------------------------------------------------------------------------
	def __truediv__(self, scalar : float) -> BaseVector:
		return BaseVector(*(left / scalar for left in self.__Values))

	#------------------------------------------------------------------------
	# 반복문 이터레이션 연산자.
	#------------------------------------------------------------------------
	def __iter__(self):
		yield from self.__Values

	#------------------------------------------------------------------------
	# 비교 연산자.
	#------------------------------------------------------------------------
	def __eq__(self, other : Union[BaseVector, tuple[float, ...]]) -> bool:
		if isinstance(other, BaseVector):
			return self.__Values == other.__Values
		elif isinstance(other, tuple):
			return self.__Values == other
		else:
			return False
		
	#------------------------------------------------------------------------
	# 생성 연산자.
	#------------------------------------------------------------------------
	def __new__(classType, *arguments, **kwargs):
		if len(arguments) == 1 and isinstance(arguments[0], tuple):
			return classType.FromTuple(arguments[0])
		return super(BaseVector, classType).__new__(classType, *arguments, **kwargs)

	#------------------------------------------------------------------------
	# 튜플 변환하기.
	#------------------------------------------------------------------------
	def ToTuple(self) -> tuple[float, ...]:
		return self.__Values

	#------------------------------------------------------------------------
	# 튜플로부터 생성하기.
	#------------------------------------------------------------------------
	@classmethod
	def FromTuple(classType, values : tuple[float, ...]) -> BaseVector:
		return classType(*values)

	#------------------------------------------------------------------------
	# 최소값.
	#------------------------------------------------------------------------
	@classmethod
	def MinValue(classType : BaseVector) -> BaseVector:
		return classType(*([float("-inf")] * classType.__Dimension))

	#------------------------------------------------------------------------
	# 최대값.
	#------------------------------------------------------------------------
	@classmethod
	def MaxValue(classType : BaseVector) -> BaseVector:
		return classType(*([float("inf")] * classType.__Dimension))


#------------------------------------------------------------------------
# 2차원 벡터.
#------------------------------------------------------------------------
class Vector2(BaseVector):
	#------------------------------------------------------------------------
	# 공개 인스턴스 변수 목록.
	#------------------------------------------------------------------------
	x : float
	y : float

	def __init__(self, x : float, y : float):
		base = super()
		base.__init__(x, y)

	# def __iter__(self):
	# 	yield self.x
	# 	yield self.y

	# def ToTuple(self) -> tuple[float, float]:
	# 	return (self.x, self.y)

	# @classmethod
	# def FromTuple(classType, values : tuple[float, float]) -> Vector2:
	# 	return classType(values[0], values[1])


#------------------------------------------------------------------------
# 3차원 벡터.
#------------------------------------------------------------------------
class Vector3:
	x : float
	y : float
	z : float

	def __init__(self, x : float, y : float, z : float):
		base = super()
		base.__init__(x, y, z)

	
#------------------------------------------------------------------------
# 4차원 벡터.
#------------------------------------------------------------------------
class Vector4:
	x : float
	y : float
	z : float
	w : float

	def __init__(self, x : float, y : float, z : float, w : float):
		base = super()
		base.__init__(x, y, z, w)