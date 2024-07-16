

import os
import typing

import jk_typing
import jk_utils
import jk_logging
import jk_json
import jk_prettyprintobj

from .JMLocation import JMLocation
from .AbstractConstraint import AbstractConstraint
from .jclasses import AbstractJMElement, JMDict, JMValue, JMList
from . import constraints








class JMRetriever(object):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	################################################################################################################################
	## Public Static Methods
	################################################################################################################################

	@staticmethod
	def getValueE(jmData:JMDict, *keySequence:str, refPath:str = None) -> JMValue:
		assert isinstance(jmData, JMDict)

		if refPath is not None:
			assert isinstance(refPath, str)
			if keySequence:
				raise Exception("Either specify a key sequence or a reference path!")
			keySequence = refPath.split(".")

		for i in range(0, len(keySequence) - 1):
			key = keySequence[i]
			assert isinstance(key, str)
			if not key or (" " in key):
				if refPath is not None:
					raise Exception("Invalid reference path specified: " + repr(refPath))
				else:
					raise Exception("Invalid key specified: " + repr(key))
			jmData = jmData.getDictE(key)

		key = keySequence[-1]
		if not key or (" " in key):
			if refPath is not None:
				raise Exception("Invalid reference path specified: " + repr(refPath))
			else:
				raise Exception("Invalid key specified: " + repr(key))
		return jmData.getValueE(key)
	#

	@staticmethod
	def getValueN(jmData:JMDict, *keySequence:str, refPath:str = None) -> typing.Union[JMValue,None]:
		assert isinstance(jmData, JMDict)

		if refPath is not None:
			assert isinstance(refPath, str)
			if keySequence:
				raise Exception("Either specify a key sequence or a reference path!")
			keySequence = refPath.split(".")

		for i in range(0, len(keySequence) - 1):
			key = keySequence[i]
			assert isinstance(key, str)
			if not key or (" " in key):
				if refPath is not None:
					raise Exception("Invalid reference path specified: " + repr(refPath))
				else:
					raise Exception("Invalid key specified: " + repr(key))
			jmData = jmData.getDictN(key)
			if jmData is None:
				return None

		key = keySequence[-1]
		if not key or (" " in key):
			if refPath is not None:
				raise Exception("Invalid reference path specified: " + repr(refPath))
			else:
				raise Exception("Invalid key specified: " + repr(key))
		return jmData.getValueN(key)
	#

	# --------------------------------------------------------------------------------------------------------------------------------

	@staticmethod
	def getStrE(jmData:JMDict, *keySequence:str, refPath:str = None) -> str:
		v = JMRetriever.getValueE(jmData, *keySequence, refPath=refPath)
		return v.vStrE()
	#

	@staticmethod
	def getStrN(jmData:JMDict, *keySequence:str, refPath:str = None) -> typing.Union[str,None]:
		v = JMRetriever.getValueN(jmData, *keySequence, refPath=refPath)
		if v is None:
			return None
		return v.vStrN()
	#

	@staticmethod
	def getIntE(jmData:JMDict, *keySequence:str, refPath:str = None) -> int:
		v = JMRetriever.getValueE(jmData, *keySequence, refPath=refPath)
		return v.vIntE()
	#

	@staticmethod
	def getIntN(jmData:JMDict, *keySequence:str, refPath:str = None) -> typing.Union[int,None]:
		v = JMRetriever.getValueN(jmData, *keySequence, refPath=refPath)
		if v is None:
			return None
		return v.vIntN()
	#

	@staticmethod
	def getFloatE(jmData:JMDict, *keySequence:str, refPath:str = None) -> float:
		v = JMRetriever.getValueE(jmData, *keySequence, refPath=refPath)
		return v.vFloatE()
	#

	@staticmethod
	def getFloatN(jmData:JMDict, *keySequence:str, refPath:str = None) -> typing.Union[float,None]:
		v = JMRetriever.getValueN(jmData, *keySequence, refPath=refPath)
		if v is None:
			return None
		return v.vFloatN()
	#

	@staticmethod
	def getBoolE(jmData:JMDict, *keySequence:str, refPath:str = None) -> bool:
		v = JMRetriever.getValueE(jmData, *keySequence, refPath=refPath)
		return v.vBoolE()
	#

	@staticmethod
	def getBoolN(jmData:JMDict, *keySequence:str, refPath:str = None) -> typing.Union[bool,None]:
		v = JMRetriever.getValueN(jmData, *keySequence, refPath=refPath)
		if v is None:
			return None
		return v.vBoolN()
	#

#




