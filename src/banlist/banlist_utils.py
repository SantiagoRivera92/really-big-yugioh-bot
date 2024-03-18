import os

from src.utils.utils import OperationResult
import src.strings as Strings

WHITELIST = "$whitelist"
BLACKLIST = "$blacklist"

def create_folder_for_server(server_id):
        folder_name = f"./lflist/{server_id}"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

def write_banlist(format_name, lflist_file, server_id):
    create_folder_for_server(server_id)
    filename = f"./lflist/{server_id}/{format_name}.lflist.conf"
    with open(filename, 'w', encoding="utf-8") as banlist:
        banlist_as_lines = lflist_file.split("\n")
        for line in banlist_as_lines:
            line = line.replace("\n", "").replace("\r", "")
            if len(line) > 0:
                banlist.write(f"{line}\n")
    return OperationResult(True, Strings.BOT_MESSAGE_FORMAT_ADDED)

def fix_banlist(format_name, server_id, card_id, card_name, new_status):
    filename = f"./lflist/{server_id}/{format_name}.lflist.conf"
    lines = []
    with open(filename, encoding="utf-8") as banlist:
        banlist_as_lines = banlist.read().split("\n")
        for line in banlist_as_lines:
            if not str(card_id) in line:
                if len(line) > 0:
                    lines.append(line)
        lines.append(f"{card_id} {new_status} -- {card_name}")
    with open(filename, 'w', encoding="utf-8") as banlist:
        for line in lines:
            banlist.write(line)
            banlist.write("\n")
    if new_status == -1:
        status = "illegal"
    elif new_status == 0:
        status = "forbidden"
    elif new_status == 1:
        status = "limited"
    elif new_status == 2:
        status = "semi-limited"
    else:
        status = "unlimited"
    return OperationResult(True, Strings.BOT_MESSAGE_CARD_ADDED_TO_BANLIST % (card_name, status, format_name))

def delete_banlist(format_name, server_id):
    filename = f"./lflist/{server_id}/{format_name}.lflist.conf"
    if os.path.exists(filename):
        os.remove(filename)
        return OperationResult(True, "")
    return OperationResult(False, Strings.ERROR_BANLIST_FILE_MISSING)


def validate_banlist( decoded_banlist: str):
	decoded_banlist = decoded_banlist.replace("\r", "")
	while "\n\n" in decoded_banlist:
		decoded_banlist = decoded_banlist.replace("\n\n", "\n")

	banlist_as_lines = decoded_banlist.split('\n')
	contains_name = False
	contains_type = False
	for line in banlist_as_lines:
		if line.startswith('!') or line.startswith('['):
			contains_name = True
		elif line == WHITELIST:
			contains_type = True
		elif line == BLACKLIST:
			return OperationResult(False, Strings.ERROR_BANLIST_BLACKLIST_NOT_SUPPORTED)
		elif len(line) > 0 and not (line.startswith("#") or line.startswith("!") or line.startswith("[")):
			first_char = line[0]

			if not first_char.isdigit():
				return OperationResult(False, Strings.ERROR_BANLIST_LINE_INVALID % line)

			split_line = line.split("--")
			true_line = split_line[0].lstrip()
			split = true_line.split(" ")

			if len(split) < 2:
				return OperationResult(False, Strings.ERROR_BANLIST_LINE_INVALID % line)

			card_id = split[0]
			status = split[1]
			a = card_id.isdigit()
			b = status.isdigit()
			c = status == "-1"

			if b:
				if int(b) > 3:
					return OperationResult(False, Strings.ERROR_BANLIST_MAX_COPIES_IS_THREE % line)
			d = a and (b or c)
			if not d:
				return OperationResult(False, Strings.ERROR_BANLIST_LINE_INVALID % line)

	if not contains_name:
		return OperationResult(False, Strings.ERROR_BANLIST_NO_NAME)
	if not contains_type:
		return OperationResult(False, Strings.ERROR_BANLIST_NO_TYPE)
	return OperationResult(True, "")