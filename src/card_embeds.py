import discord
from discord import Embed
from src.utils import getStatusInBanlist

def cardToEmbed(card, banlistFile, formatName, bot):
	
	banlist = open(banlistFile).read()

	cardId = card.get('id')
	name = card.get('name')
	cType = card.get('type')
	race = card.get('race')
	attribute = card.get('attribute')
	imageUrl = card.get('card_images')[0].get('image_url')
	level =card.get('level')
	attack = card.get('atk')
	defense = card.get('def')
	scale = card.get('scale')
	linkval = card.get('linkval')

	color = discord.Color.from_str("0x000000")

	cardType = ""
	if ("Monster" in cType):
		cardType = "Monster"
		if "XYZ" in cType:
			color = discord.Color.from_str("0x0c1216")
		elif "Synchro" in cType:
			color = discord.Color.from_str("0xcbcbcb")
		elif "Fusion" in cType:
			color = discord.Color.from_str("0x8968b9")
		elif "Normal" in cType:
			color = discord.Color.from_str("0xdccdc4")
		elif "Link" in cType:
			color = discord.Color.from_str("0x1e6895")
		elif "Ritual" in cType:
			color = discord.Color.from_str("0x3575a1")
		else:
			color = discord.Color.from_str("0xa4633b")
	elif ("Spell" in cType):
		cardType = "Spell"
		color = discord.Color.from_str("0x94c0af")
	elif ("Trap" in cType):
		cardType = "Trap"
		color = discord.Color.from_str("0xdeb0cd")


	embed = Embed(title=name, color=color)
	embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
	embed.set_thumbnail(url=imageUrl)

	status = getStatusInBanlist(cardId, banlist)
	statusAsString = getStatusAsString(status)
	embed.add_field(name="Status (%s):"%formatName, value=statusAsString)
	if (cardType == "Monster"):
		if not "Normal" in cType:
			formattedType = cType.replace(" Monster", "")
			if " " in formattedType:
				formattedType = formattedType.replace(" Effect", "")
				formattedType = formattedType.replace(" ", "/")
			formattedCardType = "%s / %s / %s"%(attribute, race, formattedType)
		else:
			formattedCardType = "%s / %s"%(attribute, race)
		if "XYZ" in cType:
			embed.add_field(name="Rank", value=level)
		elif not "Link" in cType:
			embed.add_field(name="Level", value=level)
		embed.add_field(name="Card type", value=formattedCardType, inline=True)
	else:
		formattedType = cType.replace(" Card", "")
		formattedCardType = "%s %s"%(race, formattedType)
		embed.add_field(name="Type", value=formattedCardType, inline=True)

	embed.add_field(name="Card effect", value=formatDesc(card),inline=False)
	if (cardType == "Monster"):
		if "Link" in cType:
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
		
		if "Pendulum" in cType:
			embed.add_field(name="Scale", value=scale)

	return embed

def formatDesc(card):
	cardDesc = card.get('desc')

	cardName = "\"%s\""%card.get('name')
	pluralCardName = "\"%s(s)\""%card.get('name')
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

	replaceList = [
		"Summon", "Set", "Destroy", "destroy", "Discard", "discard", "Send", 
		"send", "Sent", "sent", "Banish", "banish","Normal", "Tribute", "Special",
		"Fusion", "Ritual", "Synchro", "XYZ", "Pendulum", "Monster", "monster",
		"Spell", "Trap", "Card", "(Quick Effect)", "Target", "target", "Material",
		"material", "Level", "Detach", "detach", "Draw Phase", "Standby Phase",
		"Battle Phase", "Main Phase", "End Phase", "Once per turn", 
		"once per turn","Twice per turn", "twice per turn", "Thrice per turn", 
		"thrice per turn","Once per Chain", "once per Chain", "during either player's turn",
		"You can only activate this effect", "You can only activate each effect",
		"You can only use this effect", "You can only use each effect", "This effect",
		"The effect of", "can only be activated", "can only be used", "Attack Position",
		"Defense Position", "face-down", "Face-down", "FLIP", "Graveyard", "GY", "Deck",
		"Continuous", "Quick-Play", "Equip " "Equipped", "face-up", "Counter", "Xyz", "activated",
		"Aqua", "Beast", "Warrior", "Cyberse", "Dinosaur", "Divine-Beast", "Dragon",
		"Fairy", "Fiend", "Fish", "Insect", "Machine", "Plant", "Psychic", "Pyro", "Reptile",
		"Rock", "Sea-Serpent", "Thunder" , "Winged Beast", "Wyrm", "Zombie",
		"DARK", "LIGHT", "WATER", "FIRE", "EARTH", "WIND", "DIVINE","ATK","DEF","controller", "owner", 
		"Remove from play", "Removed from play"]

	for termToReplace in replaceList:
		replacement = "**%s**"%termToReplace
		cardDesc = cardDesc.replace(termToReplace, replacement)


	suffixList = ["s", "/s", "(s)", "ed", "d", "ing"]
	punctuationList = [";", " ", ".", ":", ",", "\n"]

	for suffix in suffixList:
		for punctuation in punctuationList:
			before = "**%s%s"%(suffix, punctuation)
			after = "%s%s**"%(suffix, punctuation)
			cardDesc = cardDesc.replace(before, after)

	cardDesc = cardDesc.replace("**Main Phase** 1", "**Main Phase 1**")
	cardDesc = cardDesc.replace("**Main Phase** 2", "**Main Phase 2**")

	cardDesc = cardDesc.replace(";", "**;**")
	cardDesc = cardDesc.replace(":", "**:**")

	cardDesc = cardDesc.replace("**Spell**caster", "**Spellcaster**")
	cardDesc = cardDesc.replace("**Beast**-**Warrior**", "**Beast-Warrior**")
	cardDesc = cardDesc.replace("Divine-**Beast**", "**Divine-Beast**")
	cardDesc = cardDesc.replace("Winged **Beast**", "**Winged Beast**")
	

	boldCardName = "**%s**"%cardName
	boldCardNamePlural = "**%s(s)**"%cardName

	cardDesc = cardDesc.replace("$cardname$", boldCardName)
	cardDesc = cardDesc.replace("$cardnameplural", boldCardNamePlural)

	while "** **" in cardDesc:
		cardDesc = cardDesc.replace("** **", " ")
	while "****" in cardDesc:
		cardDesc = cardDesc.replace("****", "")
	while "**/**" in cardDesc:
		cardDesc = cardDesc.replace("**/**", "/")
	return cardDesc

def getArrows(card):
	linkmarkers = card.get('linkmarkers')
	emoji = ""
	for arrow in linkmarkers:
		if (arrow == "Top-Left"):
			emoji = "%s%s"%(emoji, "↖")
		if (arrow == "Top"):
			emoji = "%s%s"%(emoji, "⬆")
		if (arrow == "Top-Right"):
			emoji = "%s%s"%(emoji, "↗")
		if (arrow == "Left"):
			emoji = "%s%s"%(emoji, "⬅")
		if (arrow == "Right"):
			emoji = "%s%s"%(emoji, "➡")
		if (arrow == "Bottom-Left"):
			emoji = "%s%s"%(emoji, "↙")
		if (arrow == "Bottom"):
			emoji = "%s%s"%(emoji, "⬇")
		if (arrow == "Bottom-Right"):
			emoji = "%s%s"%(emoji, "↘")
	return emoji

def getStatusAsString(status):
	if (status == -1):
		return "Illegal"
	if (status == 0):
		return "Forbidden"
	if (status == 1):
		return "Limited"
	if (status == 2):
		return "Semi-Limited"
	return "Unlimited"