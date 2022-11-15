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

TYPE_MONSTER = "Monster"
TYPE_SYNCHRO = "Synchro"
TYPE_XYZ = "XYZ"
TYPE_FUSION = "Fusion"
TYPE_NORMAL = "Normal"
TYPE_LINK = "Link"
TYPE_RITUAL = "Ritual"
TYPE_EFFECT = "Effect"
TYPE_SPELL = "Spell"
TYPE_TRAP = "Trap"
TYPE_PENDULUM = "Pendulum"

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

	color = COLOR_DEFAULT

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
	elif (TYPE_TRAP in cType):
		cardType = TYPE_TRAP
		color = COLOR_TRAP


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
			formattedCardType = "%s / %s / %s"%(attribute, race, formattedType)
		else:
			formattedCardType = "%s / %s"%(attribute, race)
		if TYPE_XYZ in cType:
			embed.add_field(name="Rank", value=level)
		elif not TYPE_LINK in cType:
			embed.add_field(name="Level", value=level)
		embed.add_field(name="Card type", value=formattedCardType, inline=True)
	else:
		formattedType = cType.replace(" Card", "")
		formattedCardType = "%s %s"%(race, formattedType)
		embed.add_field(name="Type", value=formattedCardType, inline=True)

	embed.add_field(name="Card effect", value=formatDesc(card),inline=False)
	if (cardType == TYPE_MONSTER):
		if TYPE_LINK in cType:
			embed.add_field(name="ATK", value=attack)
			embed.add_field(name="Link Rating", value=linkval)
			embed.add_field(name="Link Arrows", value=getArrows(card))
		else:
			if attack is None:
				if defense is None:
					stats = "? / ?"
				else:
					stats = "? / %d"%defense
			else:
				if defense is None:
					stats = "%d / ?"%attack
				else:
					stats = "%d / %d"%(attack, defense)
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
	cardDesc = cardDesc.replace("$cardnameplural", boldCardNamePlural)

	for cleanupItem in cleanupList:
		while cleanupItem.get(ALIAS_BEFORE_KEY) in cardDesc:
			cardDesc = cardDesc.replace(cleanupItem.get(ALIAS_BEFORE_KEY), cleanupItem.get(ALIAS_AFTER_KEY))

	return cardDesc

def getArrows(card):
	linkmarkers = card.get(CARD_LINK_MARKERS_KEY)
	emoji = ""
	for arrow in linkmarkers:
		if (arrow == LINK_MARKER_TOP_LEFT):
			emoji = "%s%s"%(emoji, "↖")
		if (arrow == LINK_MARKER_TOP):
			emoji = "%s%s"%(emoji, "⬆")
		if (arrow == LINK_MARKER_TOP_RIGHT):
			emoji = "%s%s"%(emoji, "↗")
		if (arrow == LINK_MARKER_LEFT):
			emoji = "%s%s"%(emoji, "⬅")
		if (arrow == LINK_MARKER_RIGHT):
			emoji = "%s%s"%(emoji, "➡")
		if (arrow == LINK_MARKER_BOTTOM_LEFT):
			emoji = "%s%s"%(emoji, "↙")
		if (arrow == LINK_MARKER_BOTTOM):
			emoji = "%s%s"%(emoji, "⬇")
		if (arrow == LINK_MARKER_BOTTOM_RIGHT):
			emoji = "%s%s"%(emoji, "↘")
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