import json
import os
from typing import List, Union
from src.banlist_generation import BanlistConverter
from src.utils import OperationResult
import src.strings as Strings

SUPPORTED_FORMATS_KEY = "supported_formats"
SANITIZED_NAMES_KEY = "sanitized_format_names"
BANLIST_FILES_KEY = "banlist_files"
CHANNEL_CONFIG_KEY = "channel_config"

DISABLED_CHANNELS_KEY = "disabled_channels"

NAME_KEY = "name"
FILENAME_KEY = "filename"
CHANNEL_NAME_KEY = "channel_name"
DEFAULT_FORMAT_KEY = "default_format"

DEFAULT_LEAGUE_CHANNEL_KEY = "default_league_channel"

DM_CHANNEL_KEY = "dm"
GROUP_CHANNEL_KEY = "group"
THREAD_CHANNEL_KEY = "thread"

FILE_NAME = "./json/servers/%d.json"
BANLIST_FOLDER = "./lflist/%d"
DEFAULT_CONFIG_FILE_NAME = "./json/default.json"


class Config:

    def __init__(self, card_collection):
        self.banlist_generator = BanlistConverter(card_collection)

    def change_status(self, format_name, server_id, card_id, card_name, status):
        return self.banlist_generator.fixBanlist(format_name, server_id, card_id, card_name, status)

    def get_config_for_server(self, server_id):
        server_filename = FILE_NAME % server_id
        banlist_foldername = BANLIST_FOLDER % server_id
        if not os.path.exists(banlist_foldername):
            with open(DEFAULT_CONFIG_FILE_NAME, encoding="utf-8") as default_config_file:
                default_config = json.load(default_config_file)
                with open(server_filename, "w", encoding="utf-8") as conf:
                    json.dump(default_config, conf, indent=4)
        if not os.path.exists(banlist_foldername):
            os.makedirs(banlist_foldername)
        with open(server_filename, encoding="utf-8") as conf:
            return json.load(conf)

    def save_config_for_server(self, config, server_id):
        with open(FILE_NAME % server_id, "w", encoding="utf-8") as conf:
            json.dump(config, conf, indent=4)

    def set_default_format_for_server(self, format_name, server_id):
        config = self.get_config_for_server(server_id)
        supported_formats = config.get(SUPPORTED_FORMATS_KEY)
        found = False
        forced_format = ""
        for _format in supported_formats:
            if _format.lower() == format_name.lower():
                found = True
                forced_format = _format
        if not found:
            return OperationResult(False, Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET % format_name)
        config[DEFAULT_FORMAT_KEY] = forced_format
        self.save_config_for_server(config, server_id)
        return OperationResult(True, Strings.MESSAGE_CONFIG_DEFAULT_FORMAT_SET % format_name)

    def add_supported_format(self, format_name: str, lflist_file: str, server_id: int):
        config = self.get_config_for_server(server_id)
        supported_formats = config.get(SUPPORTED_FORMATS_KEY)

        for _format in supported_formats:
            if _format.lower() == format_name.lower():
                return OperationResult( False, Strings.ERROR_CONFIG_FORMAT_ALREADY_EXISTS % format_name)

        result = self.banlist_generator.writeBanlist(
            format_name, lflist_file, server_id
        )
        if result.was_successful():
            supported_formats.append(format_name)
            banlist_files = config.get(BANLIST_FILES_KEY)
            new_banlist_file = {}
            new_banlist_file[NAME_KEY] = format_name
            new_banlist_file[FILENAME_KEY] = f"./lflist/{server_id}/{format_name}.lflist.conf"
            banlist_files.append(new_banlist_file)

            config[BANLIST_FILES_KEY] = banlist_files
            config[SUPPORTED_FORMATS_KEY] = supported_formats
            self.save_config_for_server(config, server_id)
        return result

    def edit_supported_format(self, format_name: str, lflist_file: str, server_id):
        config = self.get_config_for_server(server_id)
        supported_formats = config.get(SUPPORTED_FORMATS_KEY)

        found = False
        forced_format = ""
        for _format in supported_formats:
            if _format.lower() == format_name.lower():
                found = True
                forced_format = _format

        if not found:
            return OperationResult(False, Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET % format_name)

        result = self.banlist_generator.writeBanlist(
            forced_format, lflist_file, server_id
        )
        return result

    def remove_format(self, format_name, server_id):
        config = self.get_config_for_server(server_id)
        supported_formats: List[str] = config.get(SUPPORTED_FORMATS_KEY)

        found = False
        forced_format = ""
        for _format in supported_formats:
            if _format.lower() == format_name.lower():
                found = True
                forced_format = _format

        if not found:
            return OperationResult(False, Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET % forced_format)

        new_banlist_files = []

        banlist_files: List[dict] = config.get(BANLIST_FILES_KEY)
        for banlist in banlist_files:
            if banlist.get(NAME_KEY) != forced_format:
                new_banlist_files.append(banlist)

        new_channel_config = []
        channel_config = config.get(CHANNEL_CONFIG_KEY)
        for individual_channel_config in channel_config:
            if individual_channel_config.get(NAME_KEY) != forced_format:
                new_channel_config.append(individual_channel_config)

        supported_formats.remove(forced_format)

        config[BANLIST_FILES_KEY] = new_banlist_files
        config[SUPPORTED_FORMATS_KEY] = supported_formats
        config[CHANNEL_CONFIG_KEY] = new_channel_config
        self.banlist_generator.deleteBanlist(forced_format, server_id)
        self.save_config_for_server(config, server_id)
        return OperationResult(True, "")

    def set_default_format_for_channel(self, format_name, channel_name, server_id):
        config = self.get_config_for_server(server_id)
        supported_formats = config.get(SUPPORTED_FORMATS_KEY)

        if format_name in supported_formats:
            channel_config = config.get(CHANNEL_CONFIG_KEY)
            found = False
            for channel in channel_config:
                if channel.get(CHANNEL_NAME_KEY) == channel_name:
                    found = True
                    channel[NAME_KEY] = format_name
            if not found:
                new_config = {}
                new_config[CHANNEL_NAME_KEY] = channel_name
                new_config[NAME_KEY] = format_name
                channel_config.append(new_config)
            self.save_config_for_server(config, server_id)
            return OperationResult(True, Strings.BOT_MESSAGE_FORMAT_TIED % (format_name, channel_name))

        return OperationResult(False, Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET % format_name)

    def get_banlist_for_format(self, format_name, server_id) -> Union[str | None]:
        config = self.get_config_for_server(server_id)
        for lflist in config.get(BANLIST_FILES_KEY):
            if lflist.get(NAME_KEY) == format_name:
                return lflist.get(FILENAME_KEY)
        return None

    def is_channel_enabled(self, channel_name, server_id):
        if channel_name == GROUP_CHANNEL_KEY or channel_name == THREAD_CHANNEL_KEY:
            return OperationResult(False, Strings.ERROR_CONFIG_GROUPS_AND_THREADS)
        for disabled_channel in self.get_disabled_channels(server_id):
            if disabled_channel == channel_name:
                return OperationResult(False, Strings.ERROR_CONFIG_DISABLED_CHANNEL)
        return OperationResult(True, "")

    def get_forced_format(self, channel_name, server_id):
        config = self.get_config_for_server(server_id)

        default_format = config.get(DEFAULT_FORMAT_KEY)

        for channel_config in config.get(CHANNEL_CONFIG_KEY):
            if channel_config.get(CHANNEL_NAME_KEY) == channel_name:
                if channel_config.get(NAME_KEY) is not None:
                    return channel_config.get(NAME_KEY)
                return None

        if default_format is None:
            supported_formats = self.get_supported_formats(server_id)
            if len(supported_formats) == 1:
                return supported_formats[0]

        return default_format

    def is_format_supported(self, format_name, server_id):
        config = self.get_config_for_server(server_id)
        return format_name in config.get(SUPPORTED_FORMATS_KEY)

    def get_disabled_channels(self, server_id):
        config = self.get_config_for_server(server_id)
        return config.get(DISABLED_CHANNELS_KEY)

    def get_supported_formats(self, server_id) -> List[str]:
        config = self.get_config_for_server(server_id)
        return config.get(SUPPORTED_FORMATS_KEY)

    def set_default_league_channel(self, channel_id: int, server_id: int):
        config = self.get_config_for_server(server_id)
        config[DEFAULT_LEAGUE_CHANNEL_KEY] = channel_id
        self.save_config_for_server(config, server_id)
        return OperationResult(True, Strings.MESSAGE_DEFAULT_LEAGUE_CHANNEL_SET)

    def get_default_league_channel(self, current_channel_id: int, server_id: int):
        config = self.get_config_for_server(server_id)
        if DEFAULT_LEAGUE_CHANNEL_KEY in config:
            return config[DEFAULT_LEAGUE_CHANNEL_KEY]
        return current_channel_id
