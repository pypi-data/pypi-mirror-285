

import os
import typing

import jk_typing
import jk_utils
import jk_logging
import jk_json
import jk_prettyprintobj





from .jclasses import JMDict, JMList, JMValue, _JMProperty







class JMMerger(object):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self,
		):
		
		pass
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	@staticmethod
	def _mergeIntoList(currentList:JMList, otherList:JMList):
		assert isinstance(currentList, JMList)
		assert isinstance(otherList, JMList)
		currentList._data.extend(otherList._data)
	#

	@staticmethod
	def _mergeIntoDict(currentDict:JMDict, otherDict:JMDict):
		assert isinstance(currentDict, JMDict)
		assert isinstance(otherDict, JMDict)
		JMMerger.mergeInfo(currentDict, otherDict)
	#

	@staticmethod
	def _mergeIntoValue(currentProperty:_JMProperty, otherProperty:_JMProperty):
		assert isinstance(currentProperty, _JMProperty)
		assert isinstance(otherProperty, _JMProperty)
		currentProperty._location = otherProperty._location
		currentProperty._data = otherProperty._data
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	################################################################################################################################
	## Public Static Methods
	################################################################################################################################

	@staticmethod
	def mergeInfo(current:JMDict, other:JMDict) -> None:
		for key in other._data.keys():
			currentProperty = current._data.get(key)
			otherProperty = other._data.get(key)
			# print("--", key)
			# print("----", currentProperty)
			# print("----", otherProperty)

			if otherProperty is None:
				continue

			if currentProperty is None:
				# does not exist at current
				current._data[key] = _JMProperty(otherProperty._location, key, otherProperty._data)

			elif isinstance(currentProperty._data, JMList):
				if isinstance(otherProperty._data, JMValue) and (otherProperty._data._data is None):
					currentProperty._location = otherProperty._location
					currentProperty._data = otherProperty._data
				else:
					otherProperty._data.ensureIsListE()
					JMMerger._mergeIntoList(currentProperty._data, otherProperty._data)

			elif isinstance(currentProperty._data, JMDict):
				if isinstance(otherProperty._data, JMValue) and (otherProperty._data._data is None):
					currentProperty._location = otherProperty._location
					currentProperty._data = otherProperty._data
				else:
					otherProperty._data.ensureIsDictE()
					JMMerger._mergeIntoDict(currentProperty._data, otherProperty._data)

			elif isinstance(currentProperty._data, JMValue):
				otherProperty._data.ensureIsValueE()
				JMMerger._mergeIntoValue(currentProperty, otherProperty)
	#

#







