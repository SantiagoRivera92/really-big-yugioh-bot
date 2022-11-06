from src.utils import OperationResult

whitelist = "$whitelist"
blacklist = "$whitelist"

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

			elif line == whitelist:
		
				containsType = True
				
			elif line == blacklist:

				return OperationResult(False, "Blacklist banlists aren't supported yet")

			elif len(line) > 0 and not line.startswith("#"):

				firstChar = line[0]
				if not firstChar.isdigit():
					return OperationResult(False, "Line \"%s\" is invalid."%line)

				splitLine = line.split("--")
				trueLine = splitLine[0].lstrip()
				
				split = trueLine.split(" ")
				if len(split) < 2:
					return OperationResult(False, "Line \"%s\" is invalid" % line)
					
				cardId = split[0]
				status = split[1]

				a = cardId.isdigit()

				b = status.isdigit()
				c = status == "-1"

				if b:
					if int(b) > 3:
						return OperationResult(False, "Line \"%s\" is invalid, maximum amount of copies per card is 3." % line)

				d = a and (b or c)

				if not d:
					return OperationResult(False, "Line \"%d\" is invalid." % line)

		if not containsName:
			return OperationResult(False, "Banlist file doesn't contain a name. A .lflist.conf file is supposed to have a name with the syntax !name at the top of the file.")
		if not containsType:
			return OperationResult(False, "Banlist file doesn't contain a type. A .lflist.conf file is supposed to have either $whitelist or $blacklist just below the name.")
		return OperationResult(True, "")