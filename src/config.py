import json
import os
from src.banlist_generation import BanlistConverter
from src.utils import OperationResult
from typing import List
import src.strings as Strings

SUPPORTED_FORMATS_KEY = 'supported_formats'
SANITIZED_NAMES_KEY = 'sanitized_format_names'
BANLIST_FILES_KEY = 'banlist_files'
CHANNEL_CONFIG_KEY = 'channel_config'

DISABLED_CHANNELS_KEY = 'disabled_channels'

NAME_KEY = 'name'
FILENAME_KEY = 'filename'
CHANNEL_NAME_KEY = 'channel_name'
DEFAULT_FORMAT_KEY = 'default_format'

DM_CHANNEL_KEY = 'dm'
GROUP_CHANNEL_KEY = 'group'
THREAD_CHANNEL_KEY = 'thread'

FILE_NAME = "./json/servers/%d.json"
BANLIST_FOLDER = "./lflist/%d"
DEFAULT_CONFIG_FILE_NAME = "./json/default.json"


class Config:
    def __init__(self, cardCollection):
        self.banlistGenerator = BanlistConverter(cardCollection)

    def changeStatus(self, formatName, serverId, cardId, cardName, status):
        return self.banlistGenerator.fixBanlist(formatName, serverId, cardId, cardName, status)

    def getConfigForServer(self, serverId):
        serverFilename = FILE_NAME % serverId
        banlistFoldername = BANLIST_FOLDER % serverId
        if not os.path.exists(banlistFoldername):
            with open(DEFAULT_CONFIG_FILE_NAME) as defaultConfigFile:
                defaultConfig = json.load(defaultConfigFile)
                with open(serverFilename, 'w') as conf:
                    json.dump(defaultConfig, conf, indent=4)
        if not os.path.exists(banlistFoldername):
            os.makedirs(banlistFoldername)
        with open(serverFilename) as conf:
            return json.load(conf)

    def saveConfigForServer(self, config, serverId):
        with open(FILE_NAME % serverId, 'w') as conf:
            json.dump(config, conf, indent=4)

    def setDefaultFormatForServer(self, formatName, serverId):
        config = self.getConfigForServer(serverId)
        supportedFormats = config.get(SUPPORTED_FORMATS_KEY)
        found = False
        forcedFormat = ""
        for format in supportedFormats:
            if format.lower() == formatName.lower():
                found = True
                forcedFormat = format
        if not found:
            return OperationResult(False, Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET % formatName)
        config[DEFAULT_FORMAT_KEY] = forcedFormat
        self.saveConfigForServer(config, serverId)
        return OperationResult(True, Strings.MESSAGE_CONFIG_DEFAULT_FORMAT_SET % formatName)

    def addSupportedFormat(self, formatName: str, lflistFile: str, serverId: int):
        config = self.getConfigForServer(serverId)
        supportedFormats = config.get(SUPPORTED_FORMATS_KEY)

        for format in supportedFormats:
            if format.lower() == formatName.lower():
                return OperationResult(False, Strings.ERROR_CONFIG_FORMAT_ALREADY_EXISTS % formatName)

        result = self.banlistGenerator.writeBanlist(
            formatName, lflistFile, serverId)
        if result.wasSuccessful():
            supportedFormats.append(formatName)
            banlistFiles = config.get(BANLIST_FILES_KEY)
            newBanlistFile = {}
            newBanlistFile[NAME_KEY] = formatName
            newBanlistFile[FILENAME_KEY] = "./lflist/%d/%s.lflist.conf" % (
                serverId, formatName)
            banlistFiles.append(newBanlistFile)

            config[BANLIST_FILES_KEY] = banlistFiles
            config[SUPPORTED_FORMATS_KEY] = supportedFormats
            self.saveConfigForServer(config, serverId)
        return result

    def editSupportedFormat(self, formatName, lflistFile, serverId):
        config = self.getConfigForServer(serverId)
        supportedFormats = config.get(SUPPORTED_FORMATS_KEY)

        found = False
        forcedFormat = ""
        for format in supportedFormats:
            if format.lower() == formatName.lower():
                found = True
                forcedFormat = format

        if not found:
            return OperationResult(False, Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET % formatName)

        result = self.banlistGenerator.writeBanlist(
            forcedFormat, lflistFile, serverId)
        return result

    def renameFormat(self, oldName, newName, serverId):
        config = self.getConfigForServer(serverId)
        supportedFormats: List[str] = config.get(SUPPORTED_FORMATS_KEY)

        found = False
        forcedFormat = ""
        for format in supportedFormats:
            if format.lower() == oldName.lower():
                found = True
                forcedFormat = format

        if not found:
            return OperationResult(False, Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET % oldName)

        supportedFormats.remove(forcedFormat)
        supportedFormats.add(newName)

        banlistFiles: List[dict] = config.get(BANLIST_FILES_KEY)
        for banlist in banlistFiles:
            if banlist.get(NAME_KEY).lower() == oldName.lower():
                banlist[NAME_KEY] = newName

        channelConfig: List[dict] = config.get(CHANNEL_CONFIG_KEY)
        for config in channelConfig:
            if config.get(NAME_KEY).lower() == oldName.lower():
                config[NAME_KEY] = newName

        config[BANLIST_FILES_KEY] = banlistFiles
        config[SUPPORTED_FORMATS_KEY] = supportedFormats
        config[CHANNEL_CONFIG_KEY] = channelConfig
        self.saveConfigForServer(config, serverId)
        return OperationResult(True, "")

    def removeFormat(self, formatName, serverId):
        config = self.getConfigForServer(serverId)
        supportedFormats: List[str] = config.get(SUPPORTED_FORMATS_KEY)

        found = False
        forcedFormat = ""
        for format in supportedFormats:
            if format.lower() == formatName.lower():
                found = True
                forcedFormat = format

        if not found:
            return OperationResult(False, Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET % forcedFormat)

        newBanlistFiles = []

        banlistFiles: List[dict] = config.get(BANLIST_FILES_KEY)
        for banlist in banlistFiles:
            if banlist.get(NAME_KEY) != forcedFormat:
                newBanlistFiles.append(banlist)

        newChannelConfig = []
        channelConfig = config.get(CHANNEL_CONFIG_KEY)
        for individualChannelConfig in channelConfig:
            if individualChannelConfig.get(NAME_KEY) != forcedFormat:
                newChannelConfig.append(individualChannelConfig)

        supportedFormats.remove(forcedFormat)

        config[BANLIST_FILES_KEY] = newBanlistFiles
        config[SUPPORTED_FORMATS_KEY] = supportedFormats
        config[CHANNEL_CONFIG_KEY] = newChannelConfig
        self.banlistGenerator.deleteBanlist(forcedFormat, serverId)
        self.saveConfigForServer(config, serverId)
        return OperationResult(True, "")

    def setDefaultFormatForChannel(self, formatName, channelName, serverId):

        config = self.getConfigForServer(serverId)
        supportedFormats = config.get(SUPPORTED_FORMATS_KEY)

        if formatName in supportedFormats:
            channelConfig = config.get(CHANNEL_CONFIG_KEY)
            found = False
            for channel in channelConfig:
                if channel.get(CHANNEL_NAME_KEY) == channelName:
                    found = True
                    channel[NAME_KEY] = formatName
            if not found:
                newConfig = {}
                newConfig[CHANNEL_NAME_KEY] = channelName
                newConfig[NAME_KEY] = formatName
                channelConfig.append(newConfig)
            self.saveConfigForServer(config, serverId)
            return OperationResult(True, Strings.BOT_MESSAGE_FORMAT_TIED % (formatName, channelName))
        else:
            return OperationResult(False, Strings.ERROR_CONFIG_FORMAT_DOESNT_EXIST_YET % formatName)

    def getBanlistForFormat(self, formatName, serverId) -> str:
        config = self.getConfigForServer(serverId)
        for lflist in config.get(BANLIST_FILES_KEY):
            if lflist.get(NAME_KEY) == formatName:
                return lflist.get(FILENAME_KEY)

    def isChannelEnabled(self, channelName, serverId):
        if channelName == GROUP_CHANNEL_KEY or channelName == THREAD_CHANNEL_KEY:
            return OperationResult(False, Strings.ERROR_CONFIG_GROUPS_AND_THREADS)
        for disabledChannel in self.getDisabledChannels(serverId):
            if disabledChannel == channelName:
                return OperationResult(False, Strings.ERROR_CONFIG_DISABLED_CHANNEL)
        return OperationResult(True, "")

    def getForcedFormat(self, channelName, serverId):

        config = self.getConfigForServer(serverId)

        defaultFormat = config.get(DEFAULT_FORMAT_KEY)

        for channelConfig in config.get(CHANNEL_CONFIG_KEY):
            if channelConfig.get(CHANNEL_NAME_KEY) == channelName:
                if channelConfig.get(NAME_KEY) != None:
                    return channelConfig.get(NAME_KEY)
                else:
                    return None

        if defaultFormat == None:
            supportedFormats = self.getSupportedFormats(serverId)
            if len(supportedFormats) == 1:
                return supportedFormats[0]

        return defaultFormat

    def isFormatSupported(self, formatName, serverId):
        config = self.getConfigForServer(serverId)
        return formatName in config.get(SUPPORTED_FORMATS_KEY)

    def getDisabledChannels(self, serverId):
        config = self.getConfigForServer(serverId)
        return config.get(DISABLED_CHANNELS_KEY)

    def getSupportedFormats(self, serverId) -> List[str]:
        config = self.getConfigForServer(serverId)
        return config.get(SUPPORTED_FORMATS_KEY)
