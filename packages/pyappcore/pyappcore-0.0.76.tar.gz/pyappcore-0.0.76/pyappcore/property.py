#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
import inspect
from .application import Application


#------------------------------------------------------------------------
# 기본 클래스.
#------------------------------------------------------------------------
class BaseClass:
	#------------------------------------------------------------------------
	# 상속된 클래스의 인스턴스로 형변환하여 반환.
	#------------------------------------------------------------------------
	@property
	def Base(self) -> None:
		class InternalBaseWrapper:
			__targetInstance : object
			__targetInstance : object
			def __init__(self, targetInstance, targetClass):
				self.__targetInstance = targetInstance
				self.__targetClass = targetClass
			def __getattr__(self, name):
				return builtins.getattr(super(self.__targetClass, self.__targetInstance), name)
		return InternalBaseWrapper(self, type(self))


#------------------------------------------------------------------------
# 값 클래스.
#------------------------------------------------------------------------
TValueType = TypeVar("TValueType")
class Value(BaseClass):
	__valueType : Type[TValueType]
	__value : Optional[TValueType]
	def __init__(self, valueType : Type[TValueType], defaultValue : Optional[TValueType] = None):
		self.__valueType = valueType
		if defaultValue and builtins.isinstance(defaultValue, self.__valueType):
			self.value = defaultValue
		else:
			self.__value = self.__valueType()
	@property
	def Value(self) -> TValueType:
		return self.__value
	@Value.setter
	def Value(self, value : TValueType):
		if not builtins.isinstance(value, self.__valueType):
			raise TypeError(f"Value must be of type '{self.__valueType.__name__}'")
		self.__value = value
	@property
	def ValueType(self) -> Type[TValueType]:
		return self.__valueType


#------------------------------------------------------------------------
# 읽기전용 값 클래스.
#------------------------------------------------------------------------
class ConstValue(Value):
	def __init__(self, valueType : Type[TValueType], defaultValue : Optional[TValueType] = None):
		base = super()
		base.__init__(valueType, defaultValue)
	@property
	def Value(self) -> TValueType:
		base = super()
		return base.Value
	@Value.setter
	def Value(self, value : TValueType):
		raise AttributeError("Cannot modify read-only value")


#------------------------------------------------------------------------
# 프로퍼티 클래스 (현재 프로퍼티를 소유한 클래스에서만 Set이 가능함).
#	- 즉, 프로퍼티 자신을 소유한 클래스 안에서는 값 반환 가능 / 값 수정 가능, 외부에서는 값 반환 가능 / 값 수정 불가능.
#------------------------------------------------------------------------
class PropertyValue(Value):
	__ownerClassType : Type[Any]
	def __init__(self, valueType : Type[TValueType], defaultValue : Optional[TValueType] = None, ownerClassTypeOrInstance : Any = None):
		base = super()
		base.__init__(valueType, defaultValue)
		self.__ownerClassType = None
		if ownerClassTypeOrInstance:
			if isinstance(ownerClassTypeOrInstance, type):
				self.__ownerClassType = ownerClassTypeOrInstance
			else:
				self.__ownerClassType = type(ownerClassTypeOrInstance)
	@property
	def Value(self) -> TValueType:
		base = super()
		return base.Value
	@Value.setter
	def Value(self, value : TValueType):
		base = super()
		Application.Log(f"property value setter : {base.Value}")
  
		if not builtins.isinstance(value, base.ValueType):
			raise TypeError(f"Value must be of type '{self.ValueType.__name__}'")
		elif self.__ownerClassType is not None:
			# 스택의 2번째 요소 (현재 함수를 지닌 객체를 호출한 쪽)가 지정 클래스였는지 확인.
			if len(stack := inspect.stack()) > 1 and "self" in (current := stack[1]).frame.f_locals and isinstance(current.frame.f_locals["self"], self.__ownerClassType):
				self.__class__.__base__.__class__(self).Value = value # 부모의 프로퍼티에 셋팅 (형변환 안되서 우회).
			else:
				raise Exception(f"property called class is not property owner.")
		else:
			self.__class__.__base__.__class__(self).Value = value # 부모의 프로퍼티에 셋팅 (형변환 안되서 우회).