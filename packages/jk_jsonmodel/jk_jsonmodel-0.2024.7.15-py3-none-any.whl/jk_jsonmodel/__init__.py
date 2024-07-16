


__author__ = "Jürgen Knauth"
__version__ = "0.2024.7.15"



import bz2
import gzip
import chardet
import typing

import jk_json



from .JMLocation import JMLocation
from .JsonParserRelaxedModel import JsonParserRelaxedModel as _JsonParserRelaxedModel
from .AbstractConstraint import AbstractConstraint
from .jclasses import AbstractJMElement, JMDict, JMValue, JMList, _JMProperty
from . import constraints
from .JMRetriever import JMRetriever
from .JMMerger import JMMerger





__tokenizerRelaxed = jk_json.TokenizerRelaxed()

__parserRelaxedModel = _JsonParserRelaxedModel()





#
# Deserialize a JSON string: Reconstruct a python data structure from the specified JSON string.
#
# @param	str textToParse		The JSON to parse in binary or string representation. If binary data is specified a simple UTF-8 decoding is performed
#								to get to a string which is then parsed.
# @param	bool bStrict		If ```True``` this parser sticks strictly to the JSON standard. If ```False``` C-style comments
#								are allowed and strings can be specified with single quotes and double quotes.
#								Furthermore NaN, positive and negative infinitiy is supported.
#
def loadModelFromStr(
		textToParse:str,
		bDebugging:bool = False,
		errPrintFunc = None,
		allowDuplicatePropertyNames:bool = False,
		sourceID:str = None,
	) -> typing.Union[JMDict,JMList]:

	assert isinstance(textToParse, str)
	assert isinstance(bDebugging, bool)
	assert isinstance(allowDuplicatePropertyNames, bool)
	if sourceID is not None:
		assert isinstance(sourceID, str)

	# ----

	if isinstance(textToParse, (bytes, bytearray)):
		textToParse = textToParse.decode("utf-8")
	elif not isinstance(textToParse, str):
		raise Exception("Can't decode JSON data from a non-string or non-binary value!")

	tokenizer = __tokenizerRelaxed
	parser = __parserRelaxedModel

	if errPrintFunc and callable(errPrintFunc):
		try:
			ret = parser.parse(tokenizer.tokenize(textToParse, sourceID), bDebugging, allowDuplicatePropertyNames)
		except jk_json.ParserErrorException as ee:
			if sourceID:
				s = sourceID if len(sourceID) < 40 else ("..." + sourceID[-40:])
				prefix = "{}:{} ".format(s, ee.location.lineNo + 1)
			else:
				prefix = "<unknown-source> "
			prefix = "{}:{} ".format(s, ee.location.lineNo + 1)
			errPrintFunc(prefix + ee.textLine.replace("\t", " "))
			errPrintFunc(" " * (len(prefix) + ee.location.charPos + 1) + "ᐃ")
			errPrintFunc(" " * (len(prefix) + ee.location.charPos + 1 - 6) + "╌╌╍╍━━┛")
			raise
	else:
		ret = parser.parse(tokenizer.tokenize(textToParse, sourceID), bDebugging, allowDuplicatePropertyNames)

	assert isinstance(ret, (JMDict,JMList))
	return ret
#

def loadListModelFromStr(
		textToParse:str,
		bDebugging:bool = False,
		errPrintFunc = None,
		allowDuplicatePropertyNames:bool = False,
		sourceID:str = None,
	) -> JMList:

	ret = loadModelFromStr(textToParse, bDebugging, errPrintFunc, allowDuplicatePropertyNames, sourceID)
	assert isinstance(ret, JMList)
	return ret
#

def loadDictModelFromStr(
		textToParse:str,
		bDebugging:bool = False,
		errPrintFunc = None,
		allowDuplicatePropertyNames:bool = False,
		sourceID:str = None,
	) -> JMDict:

	ret = loadModelFromStr(textToParse, bDebugging, errPrintFunc, allowDuplicatePropertyNames, sourceID)
	assert isinstance(ret, JMDict)
	return ret
#



#
# Deserialize a JSON string: Reconstruct a python data structure reading data from the specified JSON file.
#
# @param	str filePath		The path of the file to load.
# @param	bool bStrict		If ```True``` this parser sticks strictly to the JSON standard. If ```False``` C-style comments
#								are allowed and strings can be specified with single quotes and double quotes.
#								Furthermore NaN, positive and negative infinitiy is supported.
#
def loadModelFromFile(
		filePath:str,
		bDebugging:bool = False,
		encoding:str = None,
		autoDetectEncoding:bool = True,
		errPrintFunc = None,
		allowDuplicatePropertyNames:bool = False
	) -> typing.Union[JMDict,JMList]:

	assert isinstance(filePath, str)
	assert isinstance(bDebugging, bool)

	# ----

	if filePath.endswith(".bz2"):
		with bz2.open(filePath, "rb") as f:
			rawData = f.read()
	elif filePath.endswith(".gz"):
		with gzip.open(filePath, "rb") as f:
			rawData = f.read()
	else:
		with open(filePath, "rb") as f:
			rawData = f.read()

	textData = None

	if encoding is None:
		if autoDetectEncoding:
			try:
				if rawData.startswith(b"\xef\xbb\xbf"):		# utf-8 byte order mark
					rawData = rawData[3:]

				textData = rawData.decode("utf-8")

			except:
				encoding = chardet.detect(rawData)["encoding"]
				if encoding is None:
					encoding = "utf-8"

		else:
			encoding = "utf-8"

	if textData is None:
		textData = rawData.decode(encoding)

	return loadDictModelFromStr(textData, bDebugging, errPrintFunc, allowDuplicatePropertyNames, filePath)
#

def loadListModelFromFile(
		filePath:str,
		bDebugging:bool = False,
		encoding:str = None,
		autoDetectEncoding:bool = True,
		errPrintFunc = None,
		allowDuplicatePropertyNames:bool = False
	) -> JMList:

	ret = loadModelFromFile(filePath, bDebugging, encoding, autoDetectEncoding, errPrintFunc, allowDuplicatePropertyNames)
	assert isinstance(ret, JMList)
	return ret
#

def loadDictModelFromFile(
		filePath:str,
		bDebugging:bool = False,
		encoding:str = None,
		autoDetectEncoding:bool = True,
		errPrintFunc = None,
		allowDuplicatePropertyNames:bool = False
	) -> JMDict:

	ret = loadModelFromFile(filePath, bDebugging, encoding, autoDetectEncoding, errPrintFunc, allowDuplicatePropertyNames)
	assert isinstance(ret, JMDict)
	return ret
#



#
# Deserialize a JSON string: Reconstruct a python data structure reading data from the specified BLOB.
#
# @param	bool bStrict		If ```True``` this parser sticks strictly to the JSON standard. If ```False``` C-style comments
#								are allowed and strings can be specified with single quotes and double quotes.
#								Furthermore NaN, positive and negative infinitiy is supported.
#
def loadModelFromBytes(
		rawData:typing.Union[bytearray,bytes],
		bDebugging:bool = False,
		encoding:str = None,
		autoDetectEncoding:bool = True,
		errPrintFunc = None,
		allowDuplicatePropertyNames:bool = False,
		sourceID:str = None,
	) -> typing.Union[JMDict,JMList]:

	assert isinstance(rawData, (bytes,bytearray))
	assert isinstance(bDebugging, bool)

	# ----

	textData = None

	if encoding is None:
		if autoDetectEncoding:
			try:
				if rawData.startswith(b"\xef\xbb\xbf"):		# utf-8 byte order mark
					rawData = rawData[3:]

				textData = rawData.decode("utf-8")

			except:
				encoding = chardet.detect(rawData)["encoding"]
				if encoding is None:
					encoding = "utf-8"

		else:
			encoding = "utf-8"

	if textData is None:
		textData = rawData.decode(encoding)

	return loadDictModelFromStr(textData, bDebugging, errPrintFunc, allowDuplicatePropertyNames, sourceID)
#

def loadListModelFromBytes(
		rawData:typing.Union[bytearray,bytes],
		bDebugging:bool = False,
		encoding:str = None,
		autoDetectEncoding:bool = True,
		errPrintFunc = None,
		allowDuplicatePropertyNames:bool = False,
		sourceID:str = None,
	) -> JMList:

	ret = loadModelFromBytes(rawData, bDebugging, encoding, autoDetectEncoding, errPrintFunc, allowDuplicatePropertyNames, sourceID)
	assert isinstance(ret, JMList)
	return ret
#

def loadDictModelFromBytes(
		rawData:typing.Union[bytearray,bytes],
		bDebugging:bool = False,
		encoding:str = None,
		autoDetectEncoding:bool = True,
		errPrintFunc = None,
		allowDuplicatePropertyNames:bool = False,
		sourceID:str = None,
	) -> JMDict:

	ret = loadModelFromBytes(rawData, bDebugging, encoding, autoDetectEncoding, errPrintFunc, allowDuplicatePropertyNames, sourceID)
	assert isinstance(ret, JMDict)
	return ret
#


