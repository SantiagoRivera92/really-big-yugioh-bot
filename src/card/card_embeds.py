import json
import math
import discord
from discord import Embed

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
COLOR_RITUAL = discord.Color.from_str("0x3575a1")
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

def get_status_in_banlist(card_id, banlist):
	banlist_as_lines = banlist.split("\n")
	id_as_string = str(card_id)
	for line in banlist_as_lines:
		id_in_line = line.split(' ')[0]
		if id_as_string == id_in_line:
			id_count = int(math.log10(card_id))+1
			line = line[id_count+1:id_count+2]
			if line == "-":
				line = "-1"
			return int(line)
	return -1

def card_to_embed(card, banlist_file, format_name, bot):
	
	with open(banlist_file, encoding="utf-8") as file:
		banlist = file.read()

	card_id = card.get(CARD_ID_KEY)
	name = card.get(CARD_NAME_KEY)
	c_type = card.get(CARD_TYPE_KEY)
	race = card.get(CARD_RACE_KEY)
	attribute = card.get(CARD_ATTRIBUTE_KEY)
	image_url = card.get(CARD_IMAGES_KEY)[0].get(CARD_IMAGE_URL_KEY)
	level = card.get(CARD_LEVEL_KEY)
	attack = card.get(CARD_ATK_KEY)
	defense = card.get(CARD_DEF_KEY)
	scale = card.get(CARD_SCALE_KEY)
	linkval = card.get(CARD_LINK_RATING_KEY)
	emoji = ""
	attr_emoji = ""
	type_emoji = ""

	bg_color = COLOR_DEFAULT

	if attribute == "FIRE":
		attr_emoji = EMOJI_ATTR_FIRE
	elif attribute == "WATER":
		attr_emoji = EMOJI_ATTR_WATER
	elif attribute == "DARK":
		attr_emoji = EMOJI_ATTR_DARK
	elif attribute == "LIGHT":
		attr_emoji = EMOJI_ATTR_LIGHT
	elif attribute == "EARTH":
		attr_emoji = EMOJI_ATTR_EARTH
	elif attribute == "WIND":
		attr_emoji = EMOJI_ATTR_WIND
	elif attribute == "DIVINE":
		attr_emoji = EMOJI_ATTR_DIVINE

	if race == "Aqua":
		type_emoji = EMOJI_TYPE_AQUA
	elif race == "Beast":
		type_emoji = EMOJI_TYPE_BEAST
	elif race == "Beast-Warrior":
		type_emoji = EMOJI_TYPE_BEAST_WARRIOR
	elif race == "Creator-God":
		type_emoji = EMOJI_TYPE_CREATOR_GOD
	elif race == "Cyberse":
		type_emoji = EMOJI_TYPE_CYBERSE
	elif race == "Dinosaur":
		type_emoji = EMOJI_TYPE_DINOSAUR
	elif race == "Divine-Beast":
		type_emoji = EMOJI_TYPE_DIVINE_BEAST
	elif race == "Dragon":
		type_emoji = EMOJI_TYPE_DRAGON
	elif race == "Fairy":
		type_emoji = EMOJI_TYPE_FAIRY
	elif race == "Fiend":
		type_emoji = EMOJI_TYPE_FIEND
	elif race == "Fish":
		type_emoji = EMOJI_TYPE_FISH
	elif race == "Insect":
		type_emoji = EMOJI_TYPE_INSECT
	elif race == "Machine":
		type_emoji = EMOJI_TYPE_MACHINE
	elif race == "Plant":
		type_emoji = EMOJI_TYPE_PLANT
	elif race == "Psychic":
		type_emoji = EMOJI_TYPE_PSYCHIC
	elif race == "Pyro":
		type_emoji = EMOJI_TYPE_PYRO
	elif race == "Reptile":
		type_emoji = EMOJI_TYPE_REPTILE
	elif race == "Rock":
		type_emoji = EMOJI_TYPE_ROCK
	elif race == "Sea Serpent":
		type_emoji = EMOJI_TYPE_SEA_SERPENT
	elif race == "Spellcaster":
		type_emoji = EMOJI_TYPE_SPELLCASTER
	elif race == "Thunder":
		type_emoji = EMOJI_TYPE_THUNDER
	elif race == "Warrior":
		type_emoji = EMOJI_TYPE_WARRIOR
	elif race == "Winged Beast":
		type_emoji = EMOJI_TYPE_WINGED_BEAST
	elif race == "Wyrm":
		type_emoji = EMOJI_TYPE_WYRM
	elif race == "Zombie":
		type_emoji = EMOJI_TYPE_ZOMBIE

	card_type = ""
	if TYPE_MONSTER in c_type:
		card_type = TYPE_MONSTER
		if TYPE_XYZ in c_type:
			bg_color = COLOR_XYZ
		elif TYPE_SYNCHRO in c_type:
			bg_color = COLOR_SYNCHRO
		elif TYPE_FUSION in c_type:
			bg_color = COLOR_FUSION
		elif TYPE_NORMAL in c_type:
			bg_color = COLOR_NORMAL
		elif TYPE_LINK in c_type:
			bg_color = COLOR_LINK
		elif TYPE_RITUAL in c_type:
			bg_color = COLOR_RITUAL
		else:
			bg_color = COLOR_EFFECT
	elif TYPE_SPELL in c_type:
		card_type = TYPE_SPELL
		bg_color = COLOR_SPELL
		if race == TYPE_EQUIP:
			emoji = f"{EMOJI_ATTR_SPELL} {EMOJI_EQUIP_SPELL}"
		elif race == TYPE_CONTINUOUS:
			emoji = f"{EMOJI_ATTR_SPELL} {EMOJI_CONTINUOUS_ST}"
		elif race == TYPE_QUICKPLAY:
			emoji = f"{EMOJI_ATTR_SPELL} {EMOJI_QUICKPLAY_SPELL}"
		elif race == TYPE_RITUAL:
			emoji = f"{EMOJI_ATTR_SPELL} {EMOJI_RITUAL_SPELL}"
		elif race == TYPE_FIELD:
			emoji = f"{EMOJI_ATTR_SPELL} {EMOJI_FIELD_SPELL}"
		else:
			emoji = EMOJI_ATTR_SPELL
	elif TYPE_TRAP in c_type:
		card_type = TYPE_TRAP
		bg_color = COLOR_TRAP
		if race == TYPE_COUNTER:
			emoji = f"{EMOJI_ATTR_TRAP} {EMOJI_COUNTER_TRAP}"
		elif race == TYPE_CONTINUOUS:
			emoji = f"{EMOJI_ATTR_TRAP} {EMOJI_CONTINUOUS_ST}"
		else:
			emoji = EMOJI_ATTR_TRAP


	embed = Embed(title=name, color=bg_color)
	embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
	embed.set_thumbnail(url=image_url)

	status = get_status_in_banlist(card_id, banlist)
	status_as_string = get_status_as_string(status)
	embed.add_field(name=f"Status ({format_name})", value=status_as_string)

	if card_type == TYPE_MONSTER:
		if not TYPE_NORMAL in c_type:
			formatted_type = c_type.replace(" Monster", "")
			if " " in formatted_type:
				formatted_type = formatted_type.replace(" Effect", "")
				formatted_type = formatted_type.replace(" ", "/")
			if len(type_emoji) > 0:
				formatted_card_type = f"{attr_emoji} {type_emoji}"
			else:
				formatted_card_type = f"{attr_emoji} / {race}"
		else:
			formatted_card_type = f"{attr_emoji} / {type_emoji}"

		if TYPE_XYZ in c_type:
			text = f"{EMOJI_RANK} Rank"
			embed.add_field(name=text, value=level)
		elif not TYPE_LINK in c_type:
			text = f"{EMOJI_LEVEL} Level"
			embed.add_field(name=text, value=level)
		embed.add_field(name="Card type", value=formatted_card_type, inline=False)
	else:
		formatted_type = c_type.replace(" Card", "")
		if len(emoji)>0:
			formatted_card_type = emoji
		else:
			formatted_card_type = f"{race} {formatted_type}"
		embed.add_field(name="Type", value=formatted_card_type, inline=True)
	desc = format_desc(card)
	if isinstance(desc, list):
		embed.add_field(name="Monster Effect", value=desc[0], inline=False)
		embed.add_field(name="Pendulum Effect", value=desc[1], inline=False)
	else:
		embed.add_field(name="Card effect", value=desc,inline=False)
	if card_type == TYPE_MONSTER:
		if TYPE_LINK in c_type:
			embed.add_field(name="Stats", value=f"{EMOJI_ATK} {attack}")
			embed.add_field(name="Link Rating", value=linkval)
			embed.add_field(name="Link Arrows", value=get_arrows(card))
		else:
			if attack is None:
				if defense is None:
					stats = f"{EMOJI_ATK} ? {EMOJI_DEF} ?"
				else:
					stats = f"{EMOJI_ATK} ? {EMOJI_DEF} {defense}"
			else:
				if defense is None:
					stats = f"{EMOJI_ATK} {attack} {EMOJI_DEF} ?"
				else:
					stats = f"{EMOJI_ATK} {attack} {EMOJI_DEF} {defense}"
			embed.add_field(name="Stats", value=stats)
		
		if TYPE_PENDULUM in c_type:
			embed.add_field(name="Scale", value=scale)

	return embed

def format_desc(card):
	card_desc: str = card.get(CARD_DESC_KEY)

	card_name = f'"{card.get(CARD_NAME_KEY)}"'
	plural_card_name = f'"{card.get(CARD_NAME_KEY)}(s)"'
	card_desc = card_desc.replace(card_name, "$cardname$")
	card_desc = card_desc.replace(plural_card_name, "$cardnameplural$")

	quotations = card_desc.split('\"')[1::2]
	new_quotations = []
	quote_index = 0
	for quotation in quotations:
		cool_quotation = f'"{quotation}"'
		if not cool_quotation in new_quotations:
			new_quotations.append(cool_quotation)
			card_desc = card_desc.replace(cool_quotation, f"${quote_index}$")
			quote_index+=1
	

	card_desc = card_desc.replace("\r", "")
	card_desc = card_desc.replace("[ Pendulum Effect ]\n", "[ Pendulum Effect ]")
	card_desc = card_desc.replace("[ Monster Effect ]\n", "[ Monster Effect ]")
	card_desc = card_desc.replace("[ Pendulum Effect ]", "**Pendulum Effect**\n")
	card_desc = card_desc.replace("[ Monster Effect ]", "**Monster Effect**\n")
	card_desc = card_desc.replace("----------------------------------------", "")
	while "\n\n**Monster Effect**" in card_desc:
		card_desc = card_desc.replace("\n\n**Monster Effect**", "\n**Monster Effect**")
	card_desc = card_desc.replace("\n**Monster Effect**", "\n\n**Monster Effect**")
	replace_list = []
	suffix_list = []
	punctuation_list = []
	alias_list = []
	cleanup_list = []
	with open(REPLACE_LIST_FILENAME, encoding="utf-8") as file:
		replace_list = json.load(file)
	with open(PUNCTUATION_LIST_FILENAME, encoding="utf-8") as file:
		punctuation_list = json.load(file)
	with open(SUFFIX_LIST_FILENAME, encoding="utf-8") as file:
		suffix_list = json.load(file)
	with open(ALIAS_LIST_FILENAME, encoding="utf-8") as file:
		alias_list = json.load(file)
	with open(ALIAS_CLEANUP_LIST_FILENAME, encoding="utf-8") as file:
		cleanup_list = json.load(file)

	for term in replace_list:
		replacement = f"**{term}**"
		card_desc = card_desc.replace(term, replacement)

	for suffix in suffix_list:
		for punctuation in punctuation_list:
			before = f"**{suffix}{punctuation}"
			after = f"{suffix}{punctuation}**"
			card_desc = card_desc.replace(before, after)

	for alias in alias_list:
		card_desc = card_desc.replace(alias[ALIAS_BEFORE_KEY], alias[ALIAS_AFTER_KEY])

	bold_card_name = f"**{card_name}**"
	bold_card_name_plural = f"**{card_name}(s)"

	card_desc = card_desc.replace("$cardname$", bold_card_name)
	card_desc = card_desc.replace("$cardnameplural$", bold_card_name_plural)

	quote_index = 0
	for quotation in new_quotations:
		card_desc = card_desc.replace(f"${quote_index}$", f"**{quotation}**")
		quote_index+=1

	for cleanup_item in cleanup_list:
		while cleanup_item.get(ALIAS_BEFORE_KEY) in card_desc:
			card_desc = card_desc.replace(cleanup_item.get(ALIAS_BEFORE_KEY), cleanup_item.get(ALIAS_AFTER_KEY))

	if len(card_desc) > 1024:
		if "monster_desc" in card and len(card["monster_desc"]) < 1024:
			if "Monster Effect" in card["monster_desc"]:
				card[CARD_DESC_KEY] = card["monster_desc"]
				numbers = "1234567890"
				monster_desc = ""
				for i in range(200):
					monster_desc += numbers
				card["monster_desc"] = monster_desc
				return format_desc(card)

		if "Monster Effect" in card_desc:
			## This is a Pendulum Monster whose entire effect is longer than 1024 characters.
			desc = card_desc.split("Monster Effect")
			for i, item in enumerate(desc):
				item = item.replace("Pendulum Effect\n", "")
				item = item.replace("Monster Effect\n", "")
				desc[i] = item
			return desc
		new_card_desc = card_desc.replace("**", "")
		if len(new_card_desc) > 1024:
			print("Card is too fucking long man")
		else:
			return new_card_desc
 
	return card_desc

def get_arrows(card):
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

def get_status_as_string(status):
	if status == -1:
		return CARD_STATUS_ILLEGAL
	if status == 0:
		return CARD_STATUS_FORBIDDEN
	if status == 1:
		return CARD_STATUS_LIMITED
	if status == 2:
		return CARD_STATUS_SEMI_LIMITED
	return CARD_STATUS_UNLIMITED