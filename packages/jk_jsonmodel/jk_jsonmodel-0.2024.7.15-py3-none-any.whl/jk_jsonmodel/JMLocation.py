

import typing




class JMLocation(typing.NamedTuple):
	sourceID: typing.Union[str,None]
	lineNo: int
	charPos: int
	jsonPath: str

	@classmethod
	def instantiate(cls, sourceID:typing.Union[str,None], lineNo:int, charPos:int, jsonPath:str):
		if jsonPath.startswith("."):
			jsonPath = jsonPath[1:]
		return cls(sourceID, lineNo, charPos, jsonPath)
	#

	def __str__(self) -> str:
		if self.sourceID:
			return "{}:{}:{}".format(self.sourceID, self.lineNo + 1, self.charPos + 1)
		else:
			return "{}:{}".format(self.lineNo + 1, self.charPos + 1)
	#

#

