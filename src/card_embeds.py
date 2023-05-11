import discord
import json
from discord import Embed
from src.utils import getStatusInBanlist

CARD_ID_KEY = 'id'
CARD_NAME_KEY = 'name'
CARD_TYPE_KEY = 'type'
CARD_RACE_KEY = 'race'
CARD_ATTRIBUTE_KEY = 'attribute'
CARD_IMAGES_KEY = 'card_images'
CARD_IMAGE_URL_KEY = 'image_url'
CARD_LEVEL_KEY = 'level'
CARD_ATK_KEY = 'atk'
CARD_DEF_KEY = 'def'
CARD_SCALE_KEY = 'scale'
CARD_LINK_RATING_KEY = 'linkval'
CARD_LINK_MARKERS_KEY = 'linkmarkers'
CARD_DESC_KEY = 'desc'

LINK_MARKER_TOP_LEFT = 'Top-Left'
LINK_MARKER_TOP = 'Top'
LINK_MARKER_TOP_RIGHT = 'Top-Right'
LINK_MARKER_LEFT = 'Left'
LINK_MARKER_RIGHT = 'Right'
LINK_MARKER_BOTTOM_LEFT = 'Bottom-Left'
LINK_MARKER_BOTTOM = 'Bottom'
LINK_MARKER_BOTTOM_RIGHT = 'Bottom-Right'

COLOR_DEFAULT = discord.Color.from_str("0x000000")
COLOR_XYZ = discord.Color.from_str("0x0c1216")
COLOR_SYNCHRO = discord.Color.from_str("0xcbcbcb")
COLOR_FUSION = discord.Color.from_str("0x8968b9")
COLOR_NORMAL = discord.Color.from_str("0xdccdc4")
COLOR_RITUAL = color = discord.Color.from_str("0x3575a1")
COLOR_LINK = discord.Color.from_str("0x1e6895")
COLOR_EFFECT = discord.Color.from_str("0xa4633b")
COLOR_SPELL = discord.Color.from_str("0x94c0af")
COLOR_TRAP = discord.Color.from_str("0xdeb0cd")


EMOJI_RITUAL_SPELL = "<:st_ritual:1099554313086443570>"
EMOJI_QUICKPLAY_SPELL = "<:st_quickplay:1099554310343364608>"
EMOJI_CONTINUOUS_ST = "<:st_continuous:1099554301824733295>"
EMOJI_EQUIP_SPELL = "<:st_equip:1099554306430087329>"
EMOJI_COUNTER_TRAP = "<:st_counter:1099554304597180446>"
EMOJI_FIELD_SPELL = "<:st_field:1099554308544020552>"

EMOJI_LEVEL = "<:stat_level:1099554354370986084>"
EMOJI_RANK = "<:stat_rank:1099554357395071039>"
EMOJI_ATK = "<:stat_atk:1099554349891473408>"
EMOJI_DEF = "<:stat_def:1099554353028792451>"

EMOJI_ATTR_DARK = "<:att_dark:1099554254651412510>"
EMOJI_ATTR_LIGHT = "<:att_light:1099554262243086396>"
EMOJI_ATTR_EARTH = "<:att_earth:1099554258485006396>"
EMOJI_ATTR_WIND = "<:att_wind:1099554271474745414>"
EMOJI_ATTR_FIRE = "<:att_fire:1099554260141740093>"
EMOJI_ATTR_WATER = "<:att_water:1099554268828151818>"
EMOJI_ATTR_DIVINE = "<:att_divine:1099554256257814629>"
EMOJI_ATTR_SPELL = "<:att_spell:1099554264948428850>"
EMOJI_ATTR_TRAP = "<:att_trap:1099554267448229999>"

EMOJI_TYPE_AQUA = "<:type_aqua:1099566372301852754>"
EMOJI_TYPE_BEAST = "<:type_beast:1099566375611158588>"
EMOJI_TYPE_BEAST_WARRIOR = "<:type_beast_warrior:1099566376907194469>"
EMOJI_TYPE_CREATOR_GOD = "<:type_creator_god:1099566378274537583>"
EMOJI_TYPE_CYBERSE = "<:type_cyberse:1099566380791123968>"
EMOJI_TYPE_DINOSAUR = "<:type_dinosaur:1099566382145871943>"
EMOJI_TYPE_DIVINE_BEAST = "<:type_divine_beast:1099566384268185710>"
EMOJI_TYPE_DRAGON = "<:type_dragon:1099566385882992640>"
EMOJI_TYPE_FAIRY = "<:type_fairy:1099566387275497523>"
EMOJI_TYPE_FIEND = "<:type_fiend:1099566389309751306>"
EMOJI_TYPE_FISH = "<:type_fish:1099566390605787156>"
EMOJI_TYPE_INSECT = "<:type_insect:1099566393705377952>"
EMOJI_TYPE_MACHINE = "<:type_machine:1099566619740622990>"
EMOJI_TYPE_PLANT = "<:type_plant:1099566398088425512>"
EMOJI_TYPE_PSYCHIC = "<:type_psychic:1099566400969904169>"
EMOJI_TYPE_PYRO = "<:type_pyro:1099566667362742293>"
EMOJI_TYPE_REPTILE = "<:type_reptile:1099566683686965258>"
EMOJI_TYPE_ROCK = "<:type_rock:1099566406103728158>"
EMOJI_TYPE_SEA_SERPENT = "<:type_sea_serpent:1099566408209285210>"
EMOJI_TYPE_SPELLCASTER = "<:type_spellcaster:1099566766956494848>"
EMOJI_TYPE_THUNDER = "<:type_thunder:1099566769129136238>"
EMOJI_TYPE_WARRIOR = "<:type_warrior:1099566411711520829>"
EMOJI_TYPE_WINGED_BEAST = "<:type_winged_beast:1099566770144161853>"
EMOJI_TYPE_WYRM = "<:type_wyrm:1099566771222089759>"
EMOJI_TYPE_ZOMBIE = "<:type_zombie:1099566415490580560>"

TYPE_MONSTER = "Monster"
TYPE_SYNCHRO = "Synchro"
TYPE_XYZ = "XYZ"
TYPE_FUSION = "Fusion"
TYPE_NORMAL = "Normal"
TYPE_LINK = "Link"
TYPE_RITUAL = "Ritual"
TYPE_PENDULUM = "Pendulum"
TYPE_EFFECT = "Effect"
TYPE_SPELL = "Spell"
TYPE_TRAP = "Trap"

TYPE_EQUIP = "Equip"
TYPE_FIELD = "Field"
TYPE_QUICKPLAY = "Quick-Play"
TYPE_COUNTER = "Counter"
TYPE_CONTINUOUS = "Continuous"

CARD_STATUS_ILLEGAL = 'Illegal'
CARD_STATUS_FORBIDDEN = 'Forbidden'
CARD_STATUS_LIMITED = 'Limited'
CARD_STATUS_SEMI_LIMITED = 'Semi-Limited'
CARD_STATUS_UNLIMITED = 'Unlimited'

REPLACE_LIST_FILENAME = "./json/cardembed/replace.json"
SUFFIX_LIST_FILENAME = "./json/cardembed/suffix.json"
PUNCTUATION_LIST_FILENAME = "./json/cardembed/punctuation.json"
ALIAS_LIST_FILENAME = "./json/cardembed/alias.json"
ALIAS_CLEANUP_LIST_FILENAME = "./json/cardembed/cleanup.json"

ALIAS_BEFORE_KEY = "before"
ALIAS_AFTER_KEY = "after"

def cardToEmbed(card, banlistFile, formatName, bot):
	
	banlist = open(banlistFile).read()

	cardId = card.get(CARD_ID_KEY)
	name = card.get(CARD_NAME_KEY)
	cType = card.get(CARD_TYPE_KEY)
	race = card.get(CARD_RACE_KEY)
	attribute = card.get(CARD_ATTRIBUTE_KEY)
	imageUrl = card.get(CARD_IMAGES_KEY)[0].get(CARD_IMAGE_URL_KEY)
	level =card.get(CARD_LEVEL_KEY)
	attack = card.get(CARD_ATK_KEY)
	defense = card.get(CARD_DEF_KEY)
	scale = card.get(CARD_SCALE_KEY)
	linkval = card.get(CARD_LINK_RATING_KEY)
	emoji = ""
	attributeEmoji = ""
	typeEmoji = ""

	color = COLOR_DEFAULT

	if attribute == "FIRE":
		attributeEmoji = EMOJI_ATTR_FIRE
	elif attribute == "WATER":
		attributeEmoji = EMOJI_ATTR_WATER
	elif attribute == "DARK":
		attributeEmoji = EMOJI_ATTR_DARK
	elif attribute == "LIGHT":
		attributeEmoji = EMOJI_ATTR_LIGHT
	elif attribute == "EARTH":
		attributeEmoji = EMOJI_ATTR_EARTH
	elif attribute == "WIND":
		attributeEmoji = EMOJI_ATTR_WIND
	elif attribute == "DIVINE":
		attributeEmoji = EMOJI_ATTR_DIVINE

	if race == "Aqua":
		typeEmoji = EMOJI_TYPE_AQUA
	elif race == "Beast":
		typeEmoji = EMOJI_TYPE_BEAST
	elif race == "Beast-Warrior":
		typeEmoji = EMOJI_TYPE_BEAST_WARRIOR
	elif race == "Creator-God":
		typeEmoji = EMOJI_TYPE_CREATOR_GOD
	elif race == "Cyberse":
		typeEmoji = EMOJI_TYPE_CYBERSE
	elif race == "Dinosaur":
		typeEmoji = EMOJI_TYPE_DINOSAUR
	elif race == "Divine-Beast":
		typeEmoji = EMOJI_TYPE_DIVINE_BEAST
	elif race == "Dragon":
		typeEmoji = EMOJI_TYPE_DRAGON
	elif race == "Fairy":
		typeEmoji = EMOJI_TYPE_FAIRY
	elif race == "Fiend":
		typeEmoji = EMOJI_TYPE_FIEND
	elif race == "Fish":
		typeEmoji = EMOJI_TYPE_FISH
	elif race == "Insect":
		typeEmoji = EMOJI_TYPE_INSECT
	elif race == "Machine":
		typeEmoji = EMOJI_TYPE_MACHINE
	elif race == "Plant":
		typeEmoji = EMOJI_TYPE_PLANT
	elif race == "Psychic":
		typeEmoji = EMOJI_TYPE_PSYCHIC
	elif race == "Pyro":
		typeEmoji = EMOJI_TYPE_PYRO
	elif race == "Reptile":
		typeEmoji = EMOJI_TYPE_REPTILE
	elif race == "Rock":
		typeEmoji = EMOJI_TYPE_ROCK
	elif race == "Sea Serpent":
		typeEmoji = EMOJI_TYPE_SEA_SERPENT
	elif race == "Spellcaster":
		typeEmoji = EMOJI_TYPE_SPELLCASTER
	elif race == "Thunder":
		typeEmoji = EMOJI_TYPE_THUNDER
	elif race == "Warrior":
		typeEmoji = EMOJI_TYPE_WARRIOR
	elif race == "Winged Beast":
		typeEmoji = EMOJI_TYPE_WINGED_BEAST
	elif race == "Wyrm":
		typeEmoji = EMOJI_TYPE_WYRM
	elif race == "Zombie":
		typeEmoji = EMOJI_TYPE_ZOMBIE

	cardType = ""
	if (TYPE_MONSTER in cType):
		cardType = TYPE_MONSTER
		if TYPE_XYZ in cType:
			color = COLOR_XYZ
		elif TYPE_SYNCHRO in cType:
			color = COLOR_SYNCHRO
		elif TYPE_FUSION in cType:
			color = COLOR_FUSION
		elif TYPE_NORMAL in cType:
			color = COLOR_NORMAL
		elif TYPE_LINK in cType:
			color = COLOR_LINK
		elif TYPE_RITUAL in cType:
			color = COLOR_RITUAL
		else:
			color = COLOR_EFFECT
	elif (TYPE_SPELL in cType):
		cardType = TYPE_SPELL
		color = COLOR_SPELL
		if race == TYPE_EQUIP:
			emoji = "%s %s" % (EMOJI_ATTR_SPELL, EMOJI_EQUIP_SPELL)
		elif race == TYPE_CONTINUOUS:
			emoji = "%s %s" % (EMOJI_ATTR_SPELL, EMOJI_CONTINUOUS_ST)
		elif race == TYPE_QUICKPLAY:
			emoji = "%s %s" % (EMOJI_ATTR_SPELL, EMOJI_QUICKPLAY_SPELL)
		elif race == TYPE_RITUAL:
			emoji = "%s %s" % (EMOJI_ATTR_SPELL, EMOJI_RITUAL_SPELL)
		elif race == TYPE_FIELD:
			emoji = "%s %s" % (EMOJI_ATTR_SPELL, EMOJI_FIELD_SPELL)
		else:
			emoji = EMOJI_ATTR_SPELL
	elif (TYPE_TRAP in cType):
		cardType = TYPE_TRAP
		color = COLOR_TRAP
		if race == TYPE_COUNTER:
			emoji = "%s %s" % (EMOJI_ATTR_TRAP, EMOJI_COUNTER_TRAP)
		elif race == TYPE_CONTINUOUS:
			emoji = "%s %s" % (EMOJI_ATTR_TRAP, EMOJI_CONTINUOUS_ST)
		else:
			emoji = EMOJI_ATTR_TRAP


	embed = Embed(title=name, color=color)
	embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
	embed.set_thumbnail(url=imageUrl)

	status = getStatusInBanlist(cardId, banlist)
	statusAsString = getStatusAsString(status)
	embed.add_field(name="Status (%s):"%formatName, value=statusAsString)
	if (cardType == TYPE_MONSTER):
		if not TYPE_NORMAL in cType:
			formattedType = cType.replace(" Monster", "")
			if " " in formattedType:
				formattedType = formattedType.replace(" Effect", "")
				formattedType = formattedType.replace(" ", "/")
			if len(typeEmoji) > 0:
				formattedCardType = "%s %s" % (attributeEmoji, typeEmoji)
			else:
				formattedCardType = "%s / %s" % (attributeEmoji, race)
		else:
			formattedCardType = "%s / %s"%(attributeEmoji, typeEmoji)
		if TYPE_XYZ in cType:
			if level > 0:
				i = 1
				lvEmoji = ""
				while i <= level:
					lvEmoji = "%s%s" % (lvEmoji, EMOJI_RANK)
					i+=1
				lvEmoji = "%s (%d)" % (lvEmoji, level)
				embed.add_field(name="Rank", value=lvEmoji, inline=False)
			else:
				embed.add_field(name="Rank", value=level, inline=False)

		elif not TYPE_LINK in cType:
			if level > 0:
				i = 1
				lvEmoji = ""
				while i <= level:
					lvEmoji = "%s%s" % (lvEmoji, EMOJI_LEVEL)
					i+=1
				lvEmoji = "%s (%d)" % (lvEmoji, level)
				embed.add_field(name="Level", value=lvEmoji, inline=False)
			else:
				embed.add_field(name="Level", value=level, inline=False)
		embed.add_field(name="Card type", value=formattedCardType, inline=False)
	else:
		formattedType = cType.replace(" Card", "")
		if len(emoji)>0:
			formattedCardType = emoji
		else:
			formattedCardType = "%s %s"%(race, formattedType)
		embed.add_field(name="Type", value=formattedCardType, inline=True)

	embed.add_field(name="Card effect", value=formatDesc(card),inline=False)
	if (cardType == TYPE_MONSTER):
		if TYPE_LINK in cType:
			embed.add_field(name="Stats", value="%s %d"%(EMOJI_ATK ,attack))
			embed.add_field(name="Link Rating", value=linkval)
			embed.add_field(name="Link Arrows", value=getArrows(card))
		else:
			if attack is None:
				if defense is None:
					stats = "%s ? %s ?"%(EMOJI_ATK, EMOJI_DEF)
				else:
					stats = "%s ? %s %d"%(EMOJI_ATK, EMOJI_DEF, defense)
			else:
				if defense is None:
					stats = "%s %d %s ?"%(EMOJI_ATK, attack, EMOJI_DEF)
				else:
					stats = "%s %d %s %d"%(EMOJI_ATK, attack, EMOJI_DEF, defense)
			embed.add_field(name="Stats", value=stats)
		
		if TYPE_PENDULUM in cType:
			embed.add_field(name="Scale", value=scale)

	return embed

def formatDesc(card):
	cardDesc = card.get(CARD_DESC_KEY)

	cardName = "\"%s\""%card.get(CARD_NAME_KEY)
	pluralCardName = "\"%s(s)\""%card.get(CARD_NAME_KEY)
	cardDesc = cardDesc.replace(cardName, "$cardname$")
	cardDesc = cardDesc.replace(pluralCardName, "$cardnameplural$")

	quotations = cardDesc.split('\"')[1::2]
	newQuotations = []
	quoteIndex = 0
	for quotation in quotations:
		coolQuotation = "\"%s\""%quotation
		if not coolQuotation in newQuotations:
			newQuotations.append(coolQuotation)
			cardDesc = cardDesc.replace(coolQuotation, "$%d$"%quoteIndex)
			quoteIndex+=1
	

	cardDesc = cardDesc.replace("\r", "")
	cardDesc = cardDesc.replace("[ Pendulum Effect ]\n", "[ Pendulum Effect ]")
	cardDesc = cardDesc.replace("[ Monster Effect ]\n", "[ Monster Effect ]")
	cardDesc = cardDesc.replace("[ Pendulum Effect ]", "**Pendulum Effect**\n")
	cardDesc = cardDesc.replace("[ Monster Effect ]", "**Monster Effect**\n")
	cardDesc = cardDesc.replace("----------------------------------------", "")
	while "\n\n**Monster Effect**" in cardDesc:
		cardDesc = cardDesc.replace("\n\n**Monster Effect**", "\n**Monster Effect**")
	cardDesc = cardDesc.replace("\n**Monster Effect**", "\n\n**Monster Effect**")
	replaceList = []
	suffixList = []
	punctuationList = []
	aliasList = []
	cleanupList = []
	with open(REPLACE_LIST_FILENAME) as file:
		replaceList = json.load(file)
	with open(PUNCTUATION_LIST_FILENAME) as file:
		punctuationList = json.load(file)
	with open(SUFFIX_LIST_FILENAME) as file:
		suffixList = json.load(file)
	with open(ALIAS_LIST_FILENAME) as file:
		aliasList = json.load(file)
	with open(ALIAS_CLEANUP_LIST_FILENAME) as file:
		cleanupList = json.load(file)

	for termToReplace in replaceList:
		replacement = "**%s**"%termToReplace
		cardDesc = cardDesc.replace(termToReplace, replacement)

	for suffix in suffixList:
		for punctuation in punctuationList:
			before = "**%s%s"%(suffix, punctuation)
			after = "%s%s**"%(suffix, punctuation)
			cardDesc = cardDesc.replace(before, after)

	for alias in aliasList:
		cardDesc = cardDesc.replace(alias[ALIAS_BEFORE_KEY], alias[ALIAS_AFTER_KEY])

	boldCardName = "**%s**"%cardName
	boldCardNamePlural = "**%s(s)**"%cardName

	cardDesc = cardDesc.replace("$cardname$", boldCardName)
	cardDesc = cardDesc.replace("$cardnameplural$", boldCardNamePlural)

	quoteIndex = 0
	for quotation in newQuotations:
		cardDesc = cardDesc.replace("$%d$"%quoteIndex, "**%s**"%quotation)
		quoteIndex+=1

	for cleanupItem in cleanupList:
		while cleanupItem.get(ALIAS_BEFORE_KEY) in cardDesc:
			cardDesc = cardDesc.replace(cleanupItem.get(ALIAS_BEFORE_KEY), cleanupItem.get(ALIAS_AFTER_KEY))

	return cardDesc

def getArrows(card):
	linkmarkers = card.get(CARD_LINK_MARKERS_KEY)
	emoji = ""
	if LINK_MARKER_TOP_LEFT in linkmarkers:
		emoji = emoji + "↖️"
	else:
		emoji = emoji + "🟦"
	
	if LINK_MARKER_TOP in linkmarkers:
		emoji = emoji + "⬆️"
	else:
		emoji = emoji + "🟦"
	
	if LINK_MARKER_TOP_RIGHT in linkmarkers:
		emoji = emoji + "↗️"
	else:
		emoji = emoji + "🟦"

	emoji = emoji + "\n"
	
	if LINK_MARKER_LEFT in linkmarkers:
		emoji = emoji + "⬅️"
	else:
		emoji = emoji + "🟦"

	emoji = emoji + "🔲"

	if LINK_MARKER_RIGHT in linkmarkers:
		emoji = emoji + "➡️"
	else:
		emoji = emoji + "🟦"

	emoji = emoji + "\n"

	if LINK_MARKER_BOTTOM_LEFT in linkmarkers:
		emoji = emoji + "↙️"
	else:
		emoji = emoji + "🟦"
	
	if LINK_MARKER_BOTTOM in linkmarkers:
		emoji = emoji + "⬇️"
	else:
		emoji = emoji + "🟦"

	if LINK_MARKER_BOTTOM_RIGHT in linkmarkers:
		emoji = emoji + "↘️"
	else:
		emoji = emoji + "🟦"

	return emoji

def getStatusAsString(status):
	if (status == -1):
		return CARD_STATUS_ILLEGAL
	if (status == 0):
		return CARD_STATUS_FORBIDDEN
	if (status == 1):
		return CARD_STATUS_LIMITED
	if (status == 2):
		return CARD_STATUS_SEMI_LIMITED
	return CARD_STATUS_UNLIMITED