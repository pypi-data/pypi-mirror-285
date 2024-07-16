

import typing
import math

import jk_json



from .JMLocation import JMLocation
from .jclasses import JMDict, JMValue, JMList, _JMProperty







class JsonParserRelaxedModel(jk_json.ParserBase):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self):
		pass
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	# @jk_json.debugDecorator
	def _tryEat_S(self, ctx:jk_json.ParsingContext, ts:jk_json.TokenStream) -> typing.Tuple[bool,typing.Union[JMDict,JMList,None]]:
		# loc = ts.location

		n = ts.skipAll("eol", None)
		hrPath:typing.List[str] = [ "" ]

		bSuccess, parsedData = self._tryEat_JOBJECT(ctx, hrPath, ts)
		if not bSuccess:
			bSuccess, parsedData = self._tryEat_JARRAY(ctx, hrPath, ts)
			if not bSuccess:
				raise jk_json.ParserErrorException(ts.location, "Syntax error: Expecting valid JSON value element")

		n = ts.skipAll("eol", None)

		#if not ts.isEOS:
		#	raise ParserErrorException(ts.location, "Syntax error")

		return (True, parsedData)
	#

	# @jk_json.debugDecorator
	def _tryEat_JANYVALUE(self, ctx:jk_json.ParsingContext, hrPath:typing.List[str], ts:jk_json.TokenStream)  -> typing.Tuple[bool,typing.Union[JMDict,JMList,JMValue,None]]:
		# loc = ts.location

		t1 = ts.peek()
		_loc = JMLocation.instantiate(t1.sourceID, t1.lineNo, t1.charPos, "".join(hrPath))

		if t1.type == "w":
			if t1.text == "null":
				ts.skip()
				return (True, JMValue(_loc, None))
			if t1.text == "true":
				ts.skip()
				return (True, JMValue(_loc, True))
			if t1.text == "false":
				ts.skip()
				return (True, JMValue(_loc, False))
			if t1.text == "Infinity":
				ts.skip()
				return (True, JMValue(_loc, math.inf))
			if t1.text == "NaN":
				ts.skip()
				return (True, JMValue(_loc, math.nan))
			raise jk_json.ParserErrorException(ts.location, "Syntax error: Expecting valid JSON value element")
		if t1.type == "s":
			ts.skip()
			return (True, JMValue(_loc, t1.text))
		if t1.type == "i":
			ts.skip()
			return (True, JMValue(_loc, int(t1.text)))
		if t1.type == "f":
			ts.skip()
			return (True, JMValue(_loc, float(t1.text)))

		bSuccess, parsedData = self._tryEat_JARRAY(ctx, hrPath, ts)
		if bSuccess:
			return (True, parsedData)

		bSuccess, parsedData = self._tryEat_JOBJECT(ctx, hrPath, ts)
		if bSuccess:
			return (True, parsedData)

		if (t1.type == "d") and (t1.text == "-"):
			m = ts.mark()
			ts.skip()
			t2 = ts.peek()
			if (t2.type == "w") and (t2.text == "Infinity"):
				ts.skip()
				return (True, float("-inf"))
			m.resetToMark()

		return (False, None)
	#

	# @jk_json.debugDecorator
	def _tryEat_JARRAY(self, ctx:jk_json.ParsingContext, hrPath:typing.List[str], ts:jk_json.TokenStream) -> typing.Tuple[bool,typing.Union[JMList,None]]:
		# loc = ts.location

		t1 = ts.peek()
		if (t1.type != "d") or (t1.text != "["):
			return (False, None)
		ts.skip()

		bSuccess, _parsedData = self._tryEat_JVALUE_LIST(ctx, hrPath, ts)
		_loc = JMLocation.instantiate(t1.sourceID, t1.lineNo, t1.charPos, "".join(hrPath))
		if bSuccess:
			parsedData = JMList(_loc, _parsedData)
		else:
			parsedData = JMList(_loc, [])

		t1 = ts.peek()
		if (t1.type != "d") or (t1.text != "]"):
			raise jk_json.ParserErrorException(ts.location, "Syntax error: Expecting JSON array elements or ']'")
		ts.skip()

		return (True, parsedData)
	#

	# @jk_json.debugDecorator
	def _tryEat_JVALUE_LIST(self, ctx:jk_json.ParsingContext, hrPath:typing.List[str], ts:jk_json.TokenStream) -> typing.Tuple[bool,typing.Union[list,None]]:
		# loc = ts.location

		retData = []
	
		_index = 0
		hrPath.append("[{}]".format(_index))
		bSuccess, parsedData = self._tryEat_JANYVALUE(ctx, hrPath, ts)
		hrPath.pop()
		if not bSuccess:
			return (False, None)
		retData.append(parsedData)
		_index += 1

		while True:
			t1 = ts.peek()
			if (t1.type != "d") or (t1.text != ","):
				return (True, retData)
			ts.skip()

			hrPath.append("[{}]".format(_index))
			bSuccess, parsedData = self._tryEat_JANYVALUE(ctx, hrPath, ts)
			hrPath.pop()
			if not bSuccess:
				return (True, retData)
			retData.append(parsedData)
			_index += 1
	#

	# @jk_json.debugDecorator
	def _tryEat_JOBJECT(self, ctx:jk_json.ParsingContext, hrPath:typing.List[str], ts:jk_json.TokenStream) -> typing.Tuple[bool,typing.Union[JMDict,None]]:
		# loc = ts.location

		t1 = ts.peek()
		if (t1.type != "d") or (t1.text != "{"):
			return (False, None)
		ts.skip()

		hrPath.append(".")
		bSuccess, _parsedData = self._tryEat_JPROPERTY_LIST(ctx, hrPath, ts)
		hrPath.pop()
		_loc = JMLocation.instantiate(t1.sourceID, t1.lineNo, t1.charPos, "".join(hrPath))
		if bSuccess:
			parsedData = JMDict(_loc, _parsedData)
		else:
			parsedData = JMDict(_loc, {})

		t1 = ts.peek()
		if (t1.type != "d") or (t1.text != "}"):
			raise jk_json.ParserErrorException(ts.location, "Syntax error: Expecting JSON property or '}'")
		ts.skip()

		return (True, parsedData)
	#

	# @jk_json.debugDecorator
	def _tryEat_JPROPERTY_LIST(self, ctx:jk_json.ParsingContext, hrPath:typing.List[str], ts:jk_json.TokenStream) -> typing.Tuple[bool,typing.Union[dict,None]]:
		# loc = ts.location

		retData = {}
		bSuccess, parsedData = self._tryEat_JPROPERTY(ctx, hrPath, ts)
		if not bSuccess:
			return (False, None)

		assert isinstance(parsedData, _JMProperty)
		retData[parsedData._key] = parsedData

		while True:
			t1 = ts.peek()
			if (t1.type != "d") or (t1.text != ","):
				return (True, retData)
			ts.skip()

			bSuccess, parsedData = self._tryEat_JPROPERTY(ctx, hrPath, ts)
			if not bSuccess:
				return (True, retData)

			assert isinstance(parsedData, _JMProperty)
			if parsedData._key in retData:
				if not ctx.allowDuplicatePropertyNames:
					raise jk_json.ParserErrorException(ts.location, "Syntax error: Duplicate property key detected: " + repr(parsedData._key))
			retData[parsedData._key] = parsedData
	#

	# @jk_json.debugDecorator
	def _tryEat_JPROPERTY(self, ctx:jk_json.ParsingContext, hrPath:typing.List[str], ts:jk_json.TokenStream) -> typing.Tuple[bool,typing.Union[_JMProperty,None]]:
		# loc = ts.location

		t1 = ts.peek()
		if t1.type != "s":
			return (False, None)
		ts.skip()

		t2 = ts.peek()
		if (t2.type != "d") or (t2.text != ":"):
			raise jk_json.ParserErrorException(ts.location, "Syntax error: Expecting ':' followed by a property value!")
		ts.skip()

		hrPath.append(t1.text)
		bSuccess, parsedData = self._tryEat_JANYVALUE(ctx, hrPath, ts)
		if bSuccess:
			_loc = JMLocation.instantiate(t1.sourceID, t1.lineNo, t1.charPos, "".join(hrPath))
			hrPath.pop()
			return (True, _JMProperty(_loc, t1.text, parsedData))
		else:
			hrPath.pop()

		raise jk_json.ParserErrorException(ts.location, "Syntax error: Expecting a valid JSON value!")
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# Parse the tokens. Construct an abstract syntax tree from the tokens provided by the tokenizer.
	#
	# @param	Tokenizer tokenizer		The tokenizer that provides the tokens.
	#
	def parse(self, tokenizer, bDebugging:bool = False, allowDuplicatePropertyNames:bool = False) -> typing.Union[JMDict,JMList,None]:
		if isinstance(tokenizer, jk_json.TokenStream):
			ts = tokenizer
		else:
			ts = jk_json.TokenStream(tokenizer)

		ctx = jk_json.ParsingContext(bDebugging, allowDuplicatePropertyNames)
		bSuccess, data = self._tryEat_S(ctx, ts)
		if bSuccess:
			return data
		else:
			raise Exception()
	#

#






