

import os
import typing

import jk_prettyprintobj



from .JMLocation import JMLocation
from .AbstractConstraint import AbstractConstraint, _packConstraints







AbstractJMElement = typing.NewType("AbstractJElement", object)
JMDict = typing.NewType("JMDict", AbstractJMElement)
JMList = typing.NewType("JMList", AbstractJMElement)
JMValue = typing.NewType("JMValue", AbstractJMElement)







class AbstractJMElement(jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, location:JMLocation) -> None:
		assert isinstance(location, JMLocation)

		self._location = location
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def location(self) -> JMLocation:
		return self._location
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dumpVarNames(self) -> typing.List[str]:
		raise NotImplementedError()
	#

	def _buildErrorTypeMismatch(self, typeStr:str) -> Exception:
		assert isinstance(typeStr, str)

		if typeStr[0] in "aeiou":
			typeStr = "an " + typeStr
		else:
			typeStr = "a " + typeStr

		return Exception("Expecting value at {} to be {} ({})".format(
			repr(self._location.jsonPath),
			typeStr,
			str(self._location),
		))
	#

	def _buildConstraintViolation(self, constraintText:str) -> Exception:
		assert isinstance(constraintText, str)

		return Exception("Expecting value at {} to match: {} ({})".format(
			repr(self._location.jsonPath),
			constraintText,
			str(self._location),
		))
	#

	def _buildConstraintViolationIndexed(self, i:int, constraintText:str) -> Exception:
		assert isinstance(i, int)
		assert isinstance(constraintText, str)

		return Exception("Expecting value at {}[{}] to match: {} ({})".format(
			repr(self._location.jsonPath),
			i,
			constraintText,
			str(self._location),
		))
	#

	def _buildErrorTypeMismatchIndexed(self, i:int, typeStr:str) -> Exception:
		assert isinstance(i, int)
		assert isinstance(typeStr, str)

		if typeStr[0] in "aeiou":
			typeStr = "an " + typeStr
		else:
			typeStr = "a " + typeStr

		return Exception("Expecting value at {}[{}] to be {} ({})".format(
			repr(self._location.jsonPath),
			i,
			typeStr,
			str(self._location),
		))
	#

	def _buildErrorMissingKey(self, key:str) -> Exception:
		assert isinstance(key, str)

		return Exception("Expecting key {} at {} ({})".format(
			repr(key),
			self._location.jsonPath,
			str(self._location),
		))
	#

	def fail(self):
		raise Exception("Can't process data at {} ({})".format(
			self._location.jsonPath,
			str(self._location),
		))
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def toJSON(self):
		raise NotImplementedError()
	#

	def ensureIsDictE(self) -> JMDict:
		raise NotImplementedError()
	#

	def ensureIsListE(self) -> JMList:
		raise NotImplementedError()
	#

	def ensureIsValueE(self) -> JMValue:
		raise NotImplementedError()
	#

#





class JMValue(AbstractJMElement, jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self,
			location:JMLocation,
			data:typing.Union[int,str,bool,float,None] = None,
		):

		super().__init__(location)

		self._data = data
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def data(self):
		return self._data
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dumpVarNames(self) -> typing.List[str]:
		return [
			"location",
			"data",
		]
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def toJSON(self):
		return self._data
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def __str__(self) -> str:
		s = repr(self._data)
		if s.startswith("'") or s.startswith("\""):
			s = s[1:-1]
		return self.__class__.__name__ + "<(" + s + ")>"
	#

	def __repr__(self) -> str:
		s = repr(self._data)
		if s.startswith("'") or s.startswith("\""):
			s = s[1:-1]
		return self.__class__.__name__ + "<(" + s + ")>"
	#

	# --------------------------------------------------------------------------------------------------------------------------------


	def ensureIsDictE(self):
		raise self._buildErrorTypeMismatch("object")
	#

	def ensureIsListE(self):
		raise self._buildErrorTypeMismatch("list")
	#

	def ensureIsValueE(self) -> JMValue:
		return self
	#

	# def ensureIsValueStrE(self) -> JMValue:
	# 	if not isinstance(self._data, str):
	# 		raise self._buildErrorTypeMismatch("str")
	# 	return self
	# #

	# def ensureIsValueBoolE(self) -> JMValue:
	# 	if not isinstance(self._data, bool):
	# 		raise self._buildErrorTypeMismatch("bool")
	# 	return self
	# #

	# def ensureIsValueIntE(self) -> JMValue:
	# 	if not isinstance(self._data, int):
	# 		raise self._buildErrorTypeMismatch("int")
	# 	return self
	# #

	# def ensureIsValueIntOrFloatE(self) -> JMValue:
	# 	if not isinstance(self._data, (int,float)):
	# 		raise self._buildErrorTypeMismatch("int,float")
	# 	return self
	# #

	# def ensureIsValueFloatE(self) -> JMValue:
	# 	if not isinstance(self._data, float):
	# 		raise self._buildErrorTypeMismatch("float")
	# 	return self
	# #

	# --------------------------------------------------------------------------------------------------------------------------------

	def vIntN(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[int,None]:
		if self._data is None:
			return None
		if constraints:
			constraints = _packConstraints(constraints)
		if constraints:
			if isinstance(self._data, int):
				errMsg = constraints(self._data)
				if errMsg:
					raise self._buildConstraintViolation(errMsg)
				return self._data
		else:
			if isinstance(self._data, int):
				return self._data
		raise self._buildErrorTypeMismatch("integer")
	#

	def vIntE(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> int:
		if self._data is None:
			raise self._buildErrorTypeMismatch("integer")
		if constraints:
			constraints = _packConstraints(constraints)
		if constraints:
			if isinstance(self._data, int):
				errMsg = constraints(self._data)
				if errMsg:
					raise self._buildConstraintViolation(errMsg)
				return self._data
		else:
			if isinstance(self._data, int):
				return self._data
		raise self._buildErrorTypeMismatch("integer")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vFloatN(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[float,None]:
		if self._data is None:
			return None
		if constraints:
			constraints = _packConstraints(constraints)
		if constraints:
			if isinstance(self._data, float):
				errMsg = constraints(self._data)
				if errMsg:
					raise self._buildConstraintViolation(errMsg)
				return self._data
		else:
			if isinstance(self._data, float):
				return self._data
		raise self._buildErrorTypeMismatch("float")
	#

	def vFloatE(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> float:
		if self._data is None:
			raise self._buildErrorTypeMismatch("float")
		if constraints:
			constraints = _packConstraints(constraints)
		if constraints:
			if isinstance(self._data, float):
				errMsg = constraints(self._data)
				if errMsg:
					raise self._buildConstraintViolation(errMsg)
				return self._data
		else:
			if isinstance(self._data, float):
				return self._data
		raise self._buildErrorTypeMismatch("float")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vNumericN(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[float,int,None]:
		if self._data is None:
			return None
		if constraints:
			constraints = _packConstraints(constraints)
		if constraints:
			if isinstance(self._data, (int, float)):
				errMsg = constraints(self._data)
				if errMsg:
					raise self._buildConstraintViolation(errMsg)
				return self._data
		else:
			if isinstance(self._data, (int, float)):
				return self._data
		raise self._buildErrorTypeMismatch("numeric")
	#

	def vNumericE(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[float,int]:
		if self._data is None:
			raise self._buildErrorTypeMismatch("numeric")
		if constraints:
			constraints = _packConstraints(constraints)
		if constraints:
			if isinstance(self._data, (int, float)):
				errMsg = constraints(self._data)
				if errMsg:
					raise self._buildConstraintViolation(errMsg)
			return self._data
		else:
			if isinstance(self._data, (int, float)):
				return self._data
		raise self._buildErrorTypeMismatch("numeric")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vBoolN(self) -> typing.Union[bool,None]:
		if self._data is None:
			return None
		if isinstance(self._data, bool):
			return self._data
		raise self._buildErrorTypeMismatch("boolean")
	#

	def vBoolE(self) -> bool:
		if self._data is None:
			raise self._buildErrorTypeMismatch("boolean")
		if isinstance(self._data, bool):
			return self._data
		raise self._buildErrorTypeMismatch("boolean")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vStrN(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[str,None]:
		if self._data is None:
			return None
		if constraints:
			constraints = _packConstraints(constraints)
		if constraints:
			if isinstance(self._data, str):
				errMsg = constraints(self._data)
				if errMsg:
					raise self._buildConstraintViolation(errMsg)
				return self._data
		else:
			if isinstance(self._data, str):
				return self._data
		raise self._buildErrorTypeMismatch("string")
	#

	def vStrE(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> str:
		if self._data is None:
			raise self._buildErrorTypeMismatch("string")
		if constraints:
			constraints = _packConstraints(constraints)
		if constraints:
			if isinstance(self._data, str):
				errMsg = constraints(self._data)
				if errMsg:
					raise self._buildConstraintViolation(errMsg)
				return self._data
		else:
			if isinstance(self._data, str):
				return self._data
		raise self._buildErrorTypeMismatch("string")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vPimitiveN(self,
		) -> typing.Union[str,int,float,bool,None]:
		return self._data
	#

	def vPimitiveE(self,
		) -> typing.Union[str,int,float,bool]:
		if self._data is None:
			raise self._buildErrorTypeMismatch("primitive")
		return self._data
	#

#



#
# This class is used internally only.
#
class _JMProperty(AbstractJMElement, jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self,
			location:JMLocation,
			key:str,
			value:AbstractJMElement,
		):

		super().__init__(location)
		assert isinstance(key, str)
		assert isinstance(value, AbstractJMElement)

		self._key = key
		self._data = value
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def data(self):
		return self._data
	#

	@property
	def key(self):
		return self._key
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dumpVarNames(self) -> typing.List[str]:
		return [
			"location",
			"key",
			"data",
		]
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __str__(self):
		return "_JMProperty<( {}={} @ {} )>".format(repr(self._key), repr(self._data), repr(self._location))
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vDictE(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> JMDict:
		if isinstance(self._data, JMDict):
			self._data._checkConstraints(*constraints)
			return self._data
		raise self._data._buildErrorTypeMismatch("object")
	#

	def vDictN(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[JMDict,None]:
		if isinstance(self._data, JMDict):
			self._data._checkConstraints(*constraints)
			return self._data
		if isinstance(self._data, JMValue):
			if self._data._data is None:
				return None
		raise self._data._buildErrorTypeMismatch("object")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vListE(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[JMList,None]:
		if isinstance(self._data, JMList):
			self._data._checkConstraints(*constraints)
			return self._data
		raise self._data._buildErrorTypeMismatch("list")
	#

	def vListN(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[JMList,None]:
		if isinstance(self._data, JMList):
			self._data._checkConstraints(*constraints)
			return self._data
		if isinstance(self._data, JMValue):
			if self._data._data is None:
				return None
		raise self._data._buildErrorTypeMismatch("list")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vStrE(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> str:
		if isinstance(self._data, JMValue):
			return self._data.vStrE(*constraints)
		raise self._data._buildErrorTypeMismatch("string")
	#

	def vStrN(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[str,None]:
		if isinstance(self._data, JMValue):
			return self._data.vStrN(*constraints)
		raise self._data._buildErrorTypeMismatch("string")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vIntE(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> int:
		if isinstance(self._data, JMValue):
			return self._data.vIntE(*constraints)
		raise self._data._buildErrorTypeMismatch("integer")
	#

	def vIntN(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[int,None]:
		if isinstance(self._data, JMValue):
			return self._data.vIntN(*constraints)
		raise self._data._buildErrorTypeMismatch("integer")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vFloatE(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> float:
		if isinstance(self._data, JMValue):
			return self._data.vFloatE(*constraints)
		raise self._data._buildErrorTypeMismatch("float")
	#

	def vFloatN(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[float,None]:
		if isinstance(self._data, JMValue):
			return self._data.vFloatN(*constraints)
		raise self._data._buildErrorTypeMismatch("float")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vNumericE(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[float,int]:
		if isinstance(self._data, JMValue):
			return self._data.vNumericE(*constraints)
		raise self._data._buildErrorTypeMismatch("numeric")
	#

	def vNumericN(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[float,int,None]:
		if isinstance(self._data, JMValue):
			return self._data.vNumericN(*constraints)
		raise self._data._buildErrorTypeMismatch("numeric")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vBoolE(self) -> bool:
		if isinstance(self._data, JMValue):
			if isinstance(self._data._data, bool):
				return self._data._data
		raise self._data._buildErrorTypeMismatch("boolean")
	#

	def vBoolN(self) -> typing.Union[bool,None]:
		if isinstance(self._data, JMValue):
			if self._data._data is None:
				return None
			if isinstance(self._data._data, bool):
				return self._data._data
		raise self._data._buildErrorTypeMismatch("boolean")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vPrimitiveE(self) -> typing.Union[bool,int,float,str]:
		if isinstance(self._data, JMValue):
			if isinstance(self._data._data, (int,float,str,bool)):
				return self._data._data
		raise self._data._buildErrorTypeMismatch("primitive")
	#

	def vPrimitiveN(self) -> typing.Union[bool,int,float,str,None]:
		if isinstance(self._data, JMValue):
			if self._data._data is None:
				return None
			if isinstance(self._data._data, (int,float,str,bool)):
				return self._data._data
		raise self._data._buildErrorTypeMismatch("primitive")
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def vValueE(self) -> JMValue:
		if isinstance(self._data, JMValue):
			return self._data
		raise self._data._buildErrorTypeMismatch("value")
	#

	def vValueN(self) -> typing.Union[JMValue,None]:
		if isinstance(self._data, JMValue):
			if self._data._data is None:
				return None
			return self._data
		raise self._data._buildErrorTypeMismatch("value")
	#

#




class JMList(AbstractJMElement, jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self,
			location:JMLocation,
			data:typing.List[AbstractJMElement],
		):

		super().__init__(location)

		self._data:typing.List[AbstractJMElement] = data
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def data(self):
		return self._data
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dumpVarNames(self) -> typing.List[str]:
		return [
			"location",
			"data",
		]
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def toJSON(self):
		ret = []
		for v in self._data:
			ret.append(v.toJSON())
		return ret
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def __str__(self) -> str:
		s = self._data.__str__()
		return self.__class__.__name__ + "<(" + s[1:-1] + ")>"
	#

	def __repr__(self) -> str:
		s = self._data.__str__()
		return self.__class__.__name__ + "<(" + s[1:-1] + ")>"
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def ensureIsDictE(self) -> JMDict:
		raise self._buildErrorTypeMismatch("object")
	#

	def ensureIsListE(self) -> JMList:
		return self
	#

	def ensureIsValueE(self) -> JMValue:
		raise self._buildErrorTypeMismatch("value")
	#

	def __getitem__(self, index:int) -> typing.Union[None,int,float,bool,str,JMList,JMDict]:
		if not isinstance(index, int):
			raise TypeError("A list index must be of type 'int'!")

		ret = self._data[index]
		if isinstance(ret, JMValue):
			return ret._data
		assert isinstance(ret, (JMList,JMDict))
		return ret
	#

	def __setitem__(self, index, value):
		raise Exception(self.__class__.__name__ + " classes are read only!")
	#

	def __delitem__(self, index):
		raise Exception(self.__class__.__name__ + " classes are read only!")
	#

	def __len__(self) -> int:
		return self._data.__len__()
	#

	def __contains__(self, value) -> bool:
		return value in self._data
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def _checkConstraints(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> None:
		if self._data is None:
			raise self._buildErrorTypeMismatch("list")
		if constraints:
			constraints = _packConstraints(constraints)
		if constraints:
			errMsg = constraints(self._data)
			if errMsg:
				raise self._buildConstraintViolation(errMsg)
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def toStrList(self,
			*constraints:typing.Tuple[AbstractConstraint],
			bAllowNullValues:bool = False,
		) -> typing.List[typing.Union[str,None]]:
		ret = []
		mRetrieveValue = JMValue.vStrN if bAllowNullValues else JMValue.vStrE
		if constraints:
			constraints = _packConstraints(constraints)
			for i, v in enumerate(self._data):
				if isinstance(v, JMValue):
					x = mRetrieveValue(v)
					if x is not None:
						errMsg = constraints(x)
						if errMsg:
							raise v._buildConstraintViolationIndexed(i, errMsg)
					ret.append(x)
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "string")
		else:
			for i, v in enumerate(self._data):
				if isinstance(v, JMValue):
					ret.append(mRetrieveValue(v))
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "string")
		return ret
	#

	def toIntList(self,
			*constraints:typing.Tuple[AbstractConstraint],
			bAllowNullValues:bool = False,
		) -> typing.List[typing.Union[int,None]]:
		ret = []
		mRetrieveValue = JMValue.vIntN if bAllowNullValues else JMValue.vIntE
		if constraints:
			constraints = _packConstraints(constraints)
			for i, v in enumerate(self._data):
				if isinstance(v, JMValue):
					x = mRetrieveValue(v)
					if x is not None:
						errMsg = constraints(x)
						if errMsg:
							raise v._buildConstraintViolationIndexed(i, errMsg)
					ret.append(x)
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "integer")
		else:
			for i, v in enumerate(self._data):
				if isinstance(v, JMValue):
					ret.append(mRetrieveValue(v))
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "integer")
		return ret
	#

	def toFloatList(self,
			*constraints:typing.Tuple[AbstractConstraint],
			bAllowNullValues:bool = False,
		) -> typing.List[typing.Union[float,None]]:
		ret = []
		mRetrieveValue = JMValue.vFloatN if bAllowNullValues else JMValue.vFloatE
		if constraints:
			constraints = _packConstraints(constraints)
			for i, v in enumerate(self._data):
				if isinstance(v, JMValue):
					x = mRetrieveValue(v)
					if x is not None:
						errMsg = constraints(x)
						if errMsg:
							raise v._buildConstraintViolationIndexed(i, errMsg)
					ret.append(x)
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "float")
		else:
			for i, v in enumerate(self._data):
				if isinstance(v, JMValue):
					ret.append(mRetrieveValue(v))
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "float")
		return ret
	#

	def toNumericList(self,
			*constraints:typing.Tuple[AbstractConstraint],
			bAllowNullValues:bool = False,
		) -> typing.List[typing.Union[float,int,None]]:
		ret = []
		mRetrieveValue = JMValue.vNumericN if bAllowNullValues else JMValue.vNumericE
		if constraints:
			constraints = _packConstraints(constraints)
			for i, v in enumerate(self._data):
				if isinstance(v, JMValue):
					x = mRetrieveValue(v)
					if x is not None:
						errMsg = constraints(x)
						if errMsg:
							raise v._buildConstraintViolationIndexed(i, errMsg)
					ret.append(x)
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "numeric")
		else:
			for i, v in enumerate(self._data):
				if isinstance(v, JMValue):
					ret.append(mRetrieveValue(v))
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "numeric")
		return ret
	#

	def toPrimitiveList(self,
			*constraints:typing.Tuple[AbstractConstraint],
			bAllowNullValues:bool = False,
		) -> typing.List[typing.Union[str,float,int,bool,None]]:
		ret = []
		mRetrieveValue = JMValue.vPimitiveN if bAllowNullValues else JMValue.vPimitiveE
		if constraints:
			constraints = _packConstraints(constraints)
			for i, v in enumerate(self._data):
				if isinstance(v, JMValue):
					x = mRetrieveValue(v)
					if x is not None:
						errMsg = constraints(x)
						if errMsg:
							raise v._buildConstraintViolationIndexed(i, errMsg)
					ret.append(x)
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "primitive")
		else:
			for i, v in enumerate(self._data):
				if isinstance(v, JMValue):
					ret.append(mRetrieveValue(v))
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "primitive")
		return ret
	#

	def toDictList(self,
			bAllowNullValues:bool = False,
		) -> typing.List[typing.Union[JMDict,None]]:
		ret = []
		for i, v in enumerate(self._data):
			if bAllowNullValues:
				if v is None:
					ret.append(None)
					continue
			else:
				if isinstance(v, JMDict):
					ret.append(v)
				else:
					raise v._buildErrorTypeMismatchIndexed(i, "object")
		return ret
	#

#



class JMDict(AbstractJMElement, jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self,
			location:JMLocation,
			data:typing.Dict[str,_JMProperty],
		):

		super().__init__(location)
		assert isinstance(data, dict)

		self._data:typing.Dict[str,_JMProperty] = data
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def data(self):
		return self._data
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dumpVarNames(self) -> typing.List[str]:
		return [
			"location",
			"data",
		]
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def toJSON(self):
		ret = {}
		for k, v in self._data.items():
			ret[k] = v._data.toJSON()
		return ret
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def __str__(self) -> str:
		s = {
			k:v for k,v in self.itemsv()
		}.__str__()
		return self.__class__.__name__ + "<(" + s[1:-1] + ")>"
	#

	def __repr__(self) -> str:
		s = {
			k:v for k,v in self.itemsv()
		}.__str__()
		return self.__class__.__name__ + "<(" + s[1:-1] + ")>"
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def ensureIsDictE(self) -> JMDict:
		return self
	#

	def ensureIsListE(self) -> JMList:
		raise self._buildErrorTypeMismatch("object")
	#

	def ensureIsValueE(self) -> JMValue:
		raise self._buildErrorTypeMismatch("value")
	#

	def __enter__(self) -> JMDict:
		return self
	#

	def __exit__(self, exception_type, exception_value, exception_traceback):
		pass
	#

	def __len__(self) -> int:
		return self._data.__len__()
	#

	def valuesv(self) -> typing.Iterable[typing.Union[int,float,str,bool,None,JMList,JMDict]]:
		for prop in self._data.values():
			assert isinstance(prop, _JMProperty)
			if isinstance(prop._data, JMValue):
				yield prop._data._data
			else:
				yield prop._data
	#

	def values(self) -> typing.Iterable[typing.Union[JMValue,JMList,JMDict]]:
		for prop in self._data.values():
			assert isinstance(prop, _JMProperty)
			yield prop._data
	#

	def keys(self) -> typing.Iterable[str]:
		yield from self._data.keys()
	#

	def itemsv(self) -> typing.Iterable[typing.Tuple[str,typing.Union[int,float,str,bool,None,JMList,JMDict]]]:
		for key, prop in self._data.items():
			assert isinstance(prop, _JMProperty)
			if isinstance(prop._data, JMValue):
				yield key, prop._data._data
			else:
				yield key, prop._data
	#

	def items(self) -> typing.Iterable[typing.Tuple[str,typing.Union[JMValue,JMList,JMDict]]]:
		for key, prop in self._data.items():
			assert isinstance(prop, _JMProperty)
			yield key, prop._data
	#

	def __getitem__(self, key:str) -> typing.Union[JMValue,JMList,JMDict]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			ret = self._data[key]
			assert isinstance(ret, _JMProperty)
			return ret._data
		raise self._buildErrorMissingKey(key)
	#

	def get(self, key:str) -> typing.Union[JMValue,JMList,JMDict]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			assert isinstance(prop, _JMProperty)
			return prop._data
		return None
	#

	def getv(self, key:str) -> typing.Union[int,float,str,bool,None,JMList,JMDict]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			assert isinstance(prop, _JMProperty)
			if isinstance(prop._data, JMValue):
				return prop._data._data
			else:
				return prop._data
		return None
	#

	def __setitem__(self, key, value):
		raise Exception(self.__class__.__name__ + " classes are read only!")
	#

	def __delitem__(self, x):
		raise Exception(self.__class__.__name__ + " classes are read only!")
	#

	def __contains__(self, key:str) -> bool:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		return key in self._data
	#

	def hasNonNull(self, key:str) -> bool:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		v = self._data.get(key)
		if v is None:
			return False

		assert isinstance(v, _JMProperty)

		if v._data is None:
			return False

		if isinstance(v._data, JMValue):
			return v._data._data is not None

		return True
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def _checkConstraints(self,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> None:
		if self._data is None:
			raise self._buildErrorTypeMismatch("object")
		if constraints:
			constraints = _packConstraints(constraints)
		if constraints:
			errMsg = constraints(self._data)
			if errMsg:
				raise self._buildConstraintViolation(errMsg)
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def getDictE(self, key:str,
			*constraints:typing.Tuple[AbstractConstraint],
			defaultValue:typing.Union[JMDict,None] = None,
		) -> JMDict:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vDictE(*constraints)
		if defaultValue is not None:
			assert isinstance(defaultValue, JMDict)
			return defaultValue
		raise self._buildErrorMissingKey(key)
	#

	def getDictN(self, key:str,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[JMDict,None]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vDictN(*constraints)
		return None
	#

	################################################################################################################################

	def getListE(self, key:str,
			defaultValue:typing.Union[JMList,None] = None,
		) -> JMList:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vListE()
		if defaultValue is not None:
			assert isinstance(defaultValue, JMList)
			return defaultValue
		raise self._buildErrorMissingKey(key)
	#

	def getListN(self, key:str) -> typing.Union[JMList,None]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vListN()
		return None
	#

	################################################################################################################################

	def getStrE(self, key:str,
			*constraints:typing.Tuple[AbstractConstraint],
			defaultValue:typing.Union[str,None] = None,
		) -> str:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vStrE(*constraints)
		if defaultValue is not None:
			assert isinstance(defaultValue, str)
			return defaultValue
		raise self._buildErrorMissingKey(key)
	#

	def getStrN(self, key:str,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[str,None]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vStrN(*constraints)			# there is a key but its value might be null
		return None						# no such key
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def getIntE(self, key:str,
			*constraints:typing.Tuple[AbstractConstraint],
			defaultValue:typing.Union[int,None] = None,
		) -> int:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vIntE(*constraints)
		if defaultValue is not None:
			assert isinstance(defaultValue, int)
			return defaultValue
		raise self._buildErrorMissingKey(key)
	#

	def getIntN(self, key:str,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[int,None]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vIntN(*constraints)			# there is a key but its value might be null
		return None						# no such key
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def getFloatE(self, key:str,
			*constraints:typing.Tuple[AbstractConstraint],
			defaultValue:typing.Union[int,float,None] = None,
		) -> float:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vFloatE(*constraints)
		if defaultValue is not None:
			assert isinstance(defaultValue, (int,float))
			return float(defaultValue)
		raise self._buildErrorMissingKey(key)
	#

	def getFloatN(self, key:str,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[float,None]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vFloatN(*constraints)		# there is a key but its value might be null
		return None						# no such key
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def getBoolE(self, key:str, defaultValue:typing.Union[bool,None] = None) -> bool:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vBoolE()
		if defaultValue is not None:
			assert isinstance(defaultValue, bool)
			return defaultValue
		raise self._buildErrorMissingKey(key)
	#

	def getBoolN(self, key:str) -> typing.Union[bool,None]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vBoolN()		# there is a key but its value might be null
		return None						# no such key
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def getPrimitiveE(self, key:str, defaultValue:typing.Union[str,int,float,bool,None] = None) -> typing.Union[str,int,float,bool]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vPrimitiveE()
		if defaultValue is not None:
			assert isinstance(defaultValue, (str,int,float,bool))
			return defaultValue
		raise self._buildErrorMissingKey(key)
	#

	def getPrimitiveN(self, key:str) -> typing.Union[str,int,float,bool,None]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vPrimitiveN()		# there is a key but its value might be null
		return None							# no such key
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def getNumericE(self, key:str,
			*constraints:typing.Tuple[AbstractConstraint],
			defaultValue:typing.Union[int,float,None] = None,
		) -> typing.Union[int,float]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vNumericE(*constraints)
		if defaultValue is not None:
			assert isinstance(defaultValue, (int,float))
			return defaultValue
		raise self._buildErrorMissingKey(key)
	#

	def getNumericN(self, key:str,
			*constraints:typing.Tuple[AbstractConstraint],
		) -> typing.Union[int,float,None]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vNumericN(*constraints)			# there is a key but its value might be null
		return None							# no such key
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	def getValueE(self, key:str) -> JMValue:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vValueE()
		raise self._buildErrorMissingKey(key)
	#

	def getValueN(self, key:str) -> typing.Union[JMValue,None]:
		if not isinstance(key, str):
			raise TypeError("A specified key is of type {} but it must be of type 'str'!".format(type(key)))

		if key in self._data:
			prop = self._data[key]
			return prop.vValueE()
		return None
	#

#


