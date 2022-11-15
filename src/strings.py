# Banlist Generation

ERROR_BANLIST_FILE_MISSING = "Banlist file doesn't exist."

BOT_MESSAGE_CARD_ADDED_TO_BANLIST = "Card added to banlist."

# Banlist validation

ERROR_BANLIST_BLACKLIST_NOT_SUPPORTED = "Blacklist banlists aren't supported yet."
ERROR_BANLIST_LINE_INVALID = "Line \"%s\" is invalid."
ERROR_BANLIST_MAX_COPIES_IS_THREE = "Line \"%s\" is invalid, maximum amount of copies per card is 3."
ERROR_BANLIST_NO_NAME = "Banlist file doesn't contain a name. A .lflist.conf file is supposed to have a name with the syntax !name at the top of the file."
ERROR_BANLIST_NO_TYPE = "Banlist file doesn't contain a type. A .lflist.conf file is supposed to have either $whitelist or $blacklist just below the name."

# Config

ERROR_CONFIG_FORMAT_ALREADY_EXISTS = "Format %s already exists. You can edit the format using /edit_format."
ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET = "Format %s doesn't exist yet. You can add a new format using /add_format."

ERROR_CONFIG_GROUPS_AND_THREADS = "This bot doesn't support groups or threads."
ERROR_CONFIG_DISABLED_CHANNEL = "This channel is disabled."

MESSAGE_CONFIG_DEFAULT_FORMAT_SET = "%s is now the default format for the server."

# Deck Collection

ERROR_DECK_COLLECTION_SUBMISSION_DISABLED = "Deck submission is not enabled at this point."
ERROR_DECK_COLLECTION_ALREADY_ENABLED = "Deck submission was already enabled."
ERROR_DECK_COLLECTION_ALREADY_DISABLED = "Deck submission was already disabled."

MESSAGE_DECK_COLLECTION_SUBMISSION_SUCCESSFUL = "Deck has been successfully submitted."
MESSAGE_DECK_COLLECTION_CLEAR_SUCCESSFUL = "All decks cleared successfully."
MESSAGE_DECK_COLLECTION_ENABLED = "Deck submission enabled."
MESSAGE_DECK_COLLECTION_DISABLED = "Deck submission disabled."

# Deck Validation

ERROR_YDK_INVALID_LINE = "Invalid line in ydk: %s"

ERROR_YDK_SMALL_MAIN_DECK = "Main Deck has %d cards, minimum is 40."
ERROR_YDK_BIG_MAIN_DECK = "Main Deck has %d cards, maximum is 60."
ERROR_YDK_BIG_EXTRA_DECK = "Extra Deck has %d cards, maximum is 15."
ERROR_YDK_BIG_SIDE_DECK = "Side Deck has %d cards, maximum is 15."

ERROR_YDK_NON_EXISTING_ID = "Card with id %s is not legal or doesn't exist."
ERROR_YDK_ILLEGAL_CARD = "%s is illegal in the format."
ERROR_YDK_FORBIDDEN_CARD = "%s is Forbidden."
ERROR_YDK_EXTRA_COPIES = "You are running %d copies of %s, maximum is %d."

# Matchmaking

ERROR_MATCHMAKING_USER_ALREADY_REGISTERED = "User <@%d> was already registered for %s!"
ERROR_MATCHMAKING_ALREADY_IN_QUEUE = "You are already in queue!"
ERROR_MATCHMAKING_REGISTER_FIRST = "You aren't registered to the league. Please register using /register before joining the queue!"
ERROR_MATCHMAKING_NO_ACTIVE_MATCHES = "You have no active matches."
ERROR_MATCHMAKING_ACTIVE_MATCH_IN_PROGRESS = "<@%d> has an active match already" 

MESSAGE_MATCHMAKING_USER_REGISTERED = "User <@%d> was registered for %s with a rating of 1000!"
MESSAGE_MATCHMAKING_JOINED_QUEUE = "You have joined the queue! If someone else joins the queue in 10 minutes, a ranked match will start."
MESSAGE_MATCHMAKING_MATCH_STARTED = "A %s ranked match has started between <@%d> and <@%d>."
MESSAGE_MATCHMAKING_MATCH_CANCELLED = "The match between <@%d> and <@%d> has been cancelled by <@%d>'s request."
MESSAGE_MATCHMAKING_WON_ELO_UPDATED = "<@%d> (%.2f => %.2f) won their match against <@%d> (%.2f => %.2f)!"

# Server Config

ERROR_PAY_ME_MONEY = "This server is not enabled.\n\nTo enable this server you have to be a member in https://patreon.com/DiamondDudeYGO \n\nOnce you've done that, contact @DiamondDudeYGO#5198 with this server ID: %d."

# Utils

ERROR_FORMAT_NAME_EMPTY = "Format name can't be empty."
ERROR_FORMAT_NAME_INVALID_CHARACTER = "You can't have \"%s\" in a format name."

# RBYB

ERROR_MESSAGE_NO_FORMAT_TIED = "There is no format tied to this channel."
ERROR_MESSAGE_NO_PLAYERS_JOINED_LEAGUE = "There are no players registered for the %s league."
ERROR_MESSAGE_JOIN_LEAGUE_FIRST = "You are not registered in the %s league."
ERROR_MESSAGE_PLAYER_HASNT_JOINED_LEAGUE = "Player %s is not registered to the league"
ERROR_MESSAGE_NO_FORMATS_ENABLED = "No formats have been enabled in this server. To add a format, use /add_format"
ERROR_MESSAGE_PARTIAL_SEARCH_FAILED = "There are no cards with %s in their name."
ERROR_MESSAGE_NO_ACTIVE_MATCHES_IN_LEAGUE = "There are no active matches in the %s league."
ERROR_MESSAGE_PLAYER_HAS_NO_MATCHES_PENDING = "Player %s has no pending active matches."
ERROR_MESSAGE_BOT_DISABLED_IN_CHANNEL = "The bot is disabled in this channel!"
ERROR_MESSAGE_NOT_AN_ADMIN = "This command requires admin privileges."
ERROR_MESSAGE_TOO_MANY_RESULTS = "More than 20 cards contain %s. Please be more specific."
ERROR_MESSAGE_WRONG_BANLIST_FORMAT = "The only supported banlist format is a .lflist.conf file."
ERROR_MESSAGE_WRONG_DECK_FORMAT = "Only .ydk files can be validated."
ERROR_MESSAGE_NO_FORMAT_FOR_NAME = "There's no format named %s. You can get a list of all installed formats with /formats."
ERROR_MESSAGE_NO_SUBMITTED_DECKLIST = "Player %s doesn't have a submitted decklist."
ERROR_MESSAGE_DECK_INVALID = "Your deck is not valid in %s.\n%s"
ERROR_MESSAGE_FORMAT_UNSUPPORTED = "%s is not supported as a format as of right now."
ERROR_MESSAGE_WRONG_STATUS = "The valid status values are -1, 0, 1, 2 and 3."
ERROR_MESSAGE_ABSOLUTE_SEARCH_FAILED = "%s is not a card."

BOT_MESSAGE_SOMEONE_JOINED_THE_QUEUE = "Someone entered the ranked queue."
BOT_MESSAGE_YOUR_RATING_IS = "Your current rating in the %s league is %.2f"
BOT_MESSAGE_FORMAT_LIST = "These are all the supported formats in this server:\n%s"
BOT_MESSAGE_CHOOSE_A_FORMAT = "Select a format."
BOT_MESSAGE_CHOOSE_A_CARD = "Select a card."
BOT_MESSAGE_ACTIVE_MATCH_LIST = "This is a list of all active matches in the %s league:\n%s"
BOT_MESSAGE_CHOOSE_A_FORMAT_TO_DISPLAY_BANLIST_STATUS = "Please choose a format to display banlist status."
BOT_MESSAGE_MULTIPLE_RESULTS_AVAILABLE = "Multiple results available. Please pick one."
BOT_MESSAGE_FORMAT_ADDED = "Your format was added to the bot."
BOT_MESSAGE_FORMAT_UPDATED = "Your format was updated."
BOT_MESSAGE_FORMAT_REMOVED = "Format %s has been removed from the bot."
BOT_MESSAGE_FORMAT_TIED = "%s is now the default format for channel %s."
BOT_MESSAGE_CHOOSE_A_FORMAT_TO_DOWNLOAD_BANLIST = "Please choose a format to download its banlist."
BOT_MESSAGE_CHOOSE_FORMAT_TO_VALIDATE_DECK = "Please choose a format to validate your deck."
BOT_MESSAGE_CHANNEL_IS_TIED_TO_FORMAT = "Channel %s is tied to a format: %s"
BOT_MESSAGE_DECK_VALID = "Your deck is valid in %s."

BOT_MESSAGE_ACTIVE_MATCH_FORMAT = "%s (%.2f) vs %s (%.2f)"


# Command names


COMMAND_NAME_CARD = "card"
COMMAND_NAME_ADD_FORMAT = "add_format"
COMMAND_NAME_TIE = "tie"
COMMAND_NAME_DEFAULT_FORMAT = "default_format"
COMMAND_NAME_CHECK_TIED = "check_tied"
COMMAND_NAME_VALIDATE = "validate"
COMMAND_NAME_BANLIST = "banlist"
COMMAND_NAME_FORMATS = "formats"
COMMAND_NAME_REGISTER = "register"
COMMAND_NAME_RATING = "rating"
COMMAND_NAME_ACTIVE_MATCHES = "active_matches"
COMMAND_NAME_GET_MATCH = "get_match"
COMMAND_NAME_LEADERBOARD = "leaderboard"
COMMAND_NAME_JOIN = "join"
COMMAND_NAME_CANCEL = "cancel"
COMMAND_NAME_LOST = "lost"
COMMAND_NAME_UPDATE_FORMAT = "update_format"
COMMAND_NAME_REMOVE_FORMAT = "remove_format"
COMMAND_NAME_COLLECT_LISTS = "collect"
COMMAND_NAME_END_COLLECTION = "end_collection"
COMMAND_NAME_SUBMIT_LIST = "submit"
COMMAND_NAME_TXT_DECK = "txt_deck"
COMMAND_NAME_YDK_DECK = "ydk_deck"
COMMAND_NAME_IMG_DECK = "img_deck"
COMMAND_NAME_HELP = "help"
COMMAND_NAME_FORCE_LOSS = "force_loss"
COMMAND_NAME_CHANGE_CARD_STATUS = "change_card_status"
