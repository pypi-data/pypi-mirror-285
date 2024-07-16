

__all__ = (
	"minValue", "maxValue", "valueIn", "minLength", "maxLength",
	"minSize", "maxSize",
	"matchRegEx", "tcpPort", "absPOSIXPath", "absWindowsPath",
	"ipAddress", "ip4Address", "ip6Address", "hostNameOrIP4Address", "hostNameOrIP6Address", "hostNameOrIPAddress", "hostName",
)



import typing
import re

from .AbstractConstraint import AbstractConstraint





################################################################################################################################

#
# apply to: int, float
#
class _MinValue(AbstractConstraint):

	def __init__(self, value) -> None:
		self.__value = value
	#

	def __call__(self, value) -> typing.Union[str,None]:
		if value >= self.__value:
			return None
		return ">= {}".format(repr(self.__value))
	#

#

# --------------------------------------------------------------------------------------------------------------------------------

#
# apply to: int, float
#
class _MaxValue(AbstractConstraint):

	def __init__(self, value) -> None:
		self.__value = value
	#

	def __call__(self, value) -> typing.Union[str,None]:
		if value <= self.__value:
			return None
		return "<= {}".format(repr(self.__value))
	#

#

################################################################################################################################

#
# apply to: str, int, float, bool
#
class _ValueIn(AbstractConstraint):

	def __init__(self, values) -> None:
		self.__values = values
	#

	def __call__(self, value) -> typing.Union[str,None]:
		if value in self.__values:
			return None
		return "in {}".format(repr(self.__values))
	#

#

################################################################################################################################

#
# apply to: str
#
class _MinLength(AbstractConstraint):

	def __init__(self, value) -> None:
		self.__value = value
	#

	def __call__(self, value) -> typing.Union[str,None]:
		if len(value) >= self.__value:
			return None
		return "length >= {}".format(repr(self.__value))
	#

#

# --------------------------------------------------------------------------------------------------------------------------------

#
# apply to: str
#
class _MaxLength(AbstractConstraint):

	def __init__(self, value) -> None:
		self.__value = value
	#

	def __call__(self, value) -> typing.Union[str,None]:
		if len(value) <= self.__value:
			return None
		return "length <= {}".format(repr(self.__value))
	#

#

# --------------------------------------------------------------------------------------------------------------------------------

#
# apply to: str
#
class _MatchesRegEx(AbstractConstraint):

	def __init__(self, regExPatternStr:str) -> None:
		self.__regExPatternStr = regExPatternStr
		self.__regExPattern = re.compile(regExPatternStr)
	#

	def __call__(self, value) -> typing.Union[str,None]:
		m = self.__regExPattern.match(value)
		if m:
			return None
		return "/{}/".format(repr(self.__regExPatternStr)[1:-1])
	#

#

################################################################################################################################

#
# apply to: JMDict, JMList
#
class _MinSize(AbstractConstraint):

	def __init__(self, value) -> None:
		self.__value = value
	#

	def __call__(self, value) -> typing.Union[str,None]:
		if len(value) >= self.__value:
			return None
		return "size >= {}".format(repr(self.__value))
	#

#

# --------------------------------------------------------------------------------------------------------------------------------

#
# apply to: JMDict, JMList
#
class _MaxSize(AbstractConstraint):

	def __init__(self, value) -> None:
		self.__value = value
	#

	def __call__(self, value) -> typing.Union[str,None]:
		if len(value) <= self.__value:
			return None
		return "size <= {}".format(repr(self.__value))
	#

#

################################################################################################################################

class _ValidTCPPort(AbstractConstraint):

	def __call__(self, value) -> typing.Union[str,None]:
		assert isinstance(value, int)
		if 0 < len(value) <= 65535:
			return None
		return "TCP port"
	#

#

################################################################################################################################

class _AbsolutePOSIXPath(AbstractConstraint):

	def __call__(self, value) -> typing.Union[str,None]:
		assert isinstance(value, str)
		if not value.startswith("/"):
			return "absolute POSIX path"

		if "//" in value:
			return "absolute POSIX path"
		value = value.replace("\\\\", "x")
		for c in value:
			if c in "|\0*?\\<>:":
				return "absolute POSIX path"
		return None
	#

#

# --------------------------------------------------------------------------------------------------------------------------------

class _AbsoluteWindowsPath(AbstractConstraint):

	def __call__(self, value) -> typing.Union[str,None]:
		assert isinstance(value, str)
		m = re.match("[a-zA-Z]:\\", value)
		if m is None:
			return "absolute Windows path"
		if "\\\\" in value:
			return "absolute Windows path"
		value = value.replace("\\\\", "x")
		for c in value:
			if c in "|\0*?/<>:":
				return "absolute Windows path"
		return None
	#

#

################################################################################################################################

class _ValidIP4Address(AbstractConstraint):

	def __call__(self, value) -> typing.Union[str,None]:
		assert isinstance(value, str)
		# https://stackoverflow.com/questions/106179/regular-expression-to-match-dns-hostname-or-ip-address
		m = re.match(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", value)
		if m:
			return None
		return "TCPv4 address"
	#

#

# --------------------------------------------------------------------------------------------------------------------------------

class _ValidIP6Address(AbstractConstraint):

	def __call__(self, value) -> typing.Union[str,None]:
		assert isinstance(value, str)
		# https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch08s17.html
		m = re.match(r"^(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}$", value)
		if m:
			return None
		return "TCPv6 address"
	#

#

################################################################################################################################

class _ValidHostName(AbstractConstraint):

	def __call__(self, value) -> typing.Union[str,None]:
		assert isinstance(value, str)
		# https://stackoverflow.com/questions/106179/regular-expression-to-match-dns-hostname-or-ip-address
		m = re.match(r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$", value)
		if m:
			return None
		return "hostname"
	#

#

################################################################################################################################

class _Or(AbstractConstraint):

	def __init__(self, errMsg:str, *constraints:typing.Tuple[AbstractConstraint]) -> None:
		assert isinstance(errMsg, str)
		self.__errMsg = errMsg
		self.__constraints = constraints
	#

	def __call__(self, value) -> typing.Union[str,None]:
		for c in self.__constraints:
			errMsg = c(value)
			if errMsg is None:
				return None
		return self.__errMsg
	#

#

################################################################################################################################







def minSize(value:int) -> AbstractConstraint:
	assert isinstance(value, int)
	return _MinSize(value)
#

def maxSize(value:int) -> AbstractConstraint:
	assert isinstance(value, int)
	return _MaxSize(value)
#

def minValue(value:typing.Union[int,float]) -> AbstractConstraint:
	assert isinstance(value, (int,float))
	return _MinValue(value)
#

def maxValue(value:typing.Union[int,float]) -> AbstractConstraint:
	assert isinstance(value, (int,float))
	return _MaxValue(value)
#

def valueIn(value:typing.Union[set,list,tuple,typing.Any], *args) -> AbstractConstraint:
	if len(args) == 0:
		if str(type(value)) == "<class 'dict_keys'>":
			return _ValueIn(value)
		assert isinstance(value, (set,list,tuple))
		return _ValueIn(value)
	else:
		_values = [ value, *args ]
		return _ValueIn(_values)
#

def minLength(value:int) -> AbstractConstraint:
	assert isinstance(value, int)
	return _MinLength(value)
#

def maxLength(value:int) -> AbstractConstraint:
	assert isinstance(value, int)
	return _MaxLength(value)
#

def matchRegEx(regExPattern:str) -> AbstractConstraint:
	assert isinstance(regExPattern, str)
	return _MatchesRegEx(regExPattern)
#

def tcpPort() -> AbstractConstraint:
	return _ValidTCPPort()
#

def absPOSIXPath() -> AbstractConstraint:
	return _AbsolutePOSIXPath()
#

def absWindowsPath() -> AbstractConstraint:
	return _AbsoluteWindowsPath()
#

def ipAddress() -> AbstractConstraint:
	return _Or("IP address", _ValidIP4Address(), _ValidIP6Address())
#

def ip4Address() -> AbstractConstraint:
	return _ValidIP4Address()
#

def ip6Address() -> AbstractConstraint:
	return _ValidIP6Address()
#

def hostNameOrIP4Address() -> AbstractConstraint:
	return _Or("hostname or IPv4 address", _ValidIP4Address(), _ValidHostName())
#

def hostNameOrIP6Address() -> AbstractConstraint:
	return _Or("hostname or IPv6 address", _ValidIP6Address(), _ValidHostName())
#

def hostNameOrIPAddress() -> AbstractConstraint:
	return _Or("hostname or IP address", _ValidIP4Address(), _ValidIP6Address(), _ValidHostName())
#

def hostName() -> AbstractConstraint:
	return _ValidHostName()
#


