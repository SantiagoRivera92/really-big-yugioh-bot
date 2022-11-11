from src.utils import OperationResult
import src.strings

WHITELIST = "$whitelist"
BLACKLIST = "$blacklist"

class BanlistValidator:

	def validateBanlist(self, decodedBanlist):

		decodedBanlist = decodedBanlist.replace("\r", "")

		while "\n\n" in decodedBanlist:
			decodedBanlist = decodedBanlist.replace("\n\n", "\n")

		banlistAsLines = decodedBanlist.split('\n')

		containsName = False
		containsType = False

		for line in banlistAsLines:
			if line.startswith('!'):

				containsName = True 

			elif line == WHITELIST:
		
				containsType = True
				
			elif line == BLACKLIST:

				return OperationResult(False, src.strings.ERROR_BANLIST_BLACKLIST_NOT_SUPPORTED)

			elif len(line) > 0 and not line.startswith("#"):

				firstChar = line[0]
				if not firstChar.isdigit():
					return OperationResult(False, src.strings.ERROR_BANLIST_LINE_INVALID % line)

				splitLine = line.split("--")
				trueLine = splitLine[0].lstrip()
				
				split = trueLine.split(" ")
				if len(split) < 2:
					return OperationResult(False, src.strings.ERROR_BANLIST_LINE_INVALID % line)
					
				cardId = split[0]
				status = split[1]

				a = cardId.isdigit()

				b = status.isdigit()
				c = status == "-1"

				if b:
					if int(b) > 3:
						return OperationResult(False, src.strings.ERROR_BANLIST_MAX_COPIES_IS_THREE % line)

				d = a and (b or c)

				if not d:
					return OperationResult(False, src.strings.ERROR_BANLIST_LINE_INVALID % line)

		if not containsName:
			return OperationResult(False, src.strings.ERROR_BANLIST_NO_NAME)
		if not containsType:
			return OperationResult(False, src.strings.ERROR_BANLIST_NO_TYPE)
		return OperationResult(True, "")