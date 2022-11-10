import json
import os
from src.banlist_generation import BanlistGenerator
from src.utils import OperationResult
from typing import List

discordApiKey = 'discord_key'
maxResultsKey = 'max_results'
supportedFormatsKey = 'supported_formats'
sanitizedNamesKey = 'sanitized_format_names'
banlistFilesKey = 'banlist_files'
channelConfigKey = 'channel_config'

disabledChannelsKey = 'disabled_channels'

originalKey = 'original'
nameKey = 'name'
filenameKey = 'filename'
channelNameKey = 'channel_name'
useDefaultFormatKey = 'use_default_format'
defaultFormatKey = 'default_format'

dmChannelKey = 'dm'
groupChannelKey = 'group'
threadChannelKey = 'thread'

fileName = "./json/servers/%d.json"
banlistFolder = "./lflist/%d"
defaultConfigFileName = "./json/default.json"

class Config:
	def __init__(self, cardCollection):
		self.banlistGenerator = BanlistGenerator(cardCollection)

	def getConfigForServer(self, serverId):
		serverFilename = fileName % serverId
		banlistFoldername = banlistFolder % serverId
		if not os.path.exists(banlistFoldername):
			with open(defaultConfigFileName) as defaultConfigFile:
				defaultConfig = json.load(defaultConfigFile)
				with open(serverFilename, 'w') as conf:
					json.dump(defaultConfig, conf, indent=4)
		if not os.path.exists(banlistFoldername):
			os.makedirs(banlistFoldername)
		with open(serverFilename) as conf:
			return json.load(conf)

	def saveConfigForServer(self, config, serverId):
		with open(fileName%serverId, 'w') as conf:
			json.dump(config, conf, indent=4)

	def addSupportedFormat(self, formatName, lflistFile, serverId):
		config = self.getConfigForServer(serverId)
		supportedFormats = config.get(supportedFormatsKey)
		
		for format in supportedFormats:
			if format.lower() == formatName.lower():
				return OperationResult(False, "Format %s already exists. You can edit the format using /edit_format." % formatName)

		
		result = self.banlistGenerator.writeBanlist(formatName, lflistFile, serverId)
		if result.wasSuccessful():
			supportedFormats.append(formatName)
			banlistFiles = config.get(banlistFilesKey)
			newBanlistFile = {}
			newBanlistFile[nameKey] = formatName
			newBanlistFile[filenameKey] = "./lflist/%d/%s.lflist.conf"%(serverId,formatName)
			banlistFiles.append(newBanlistFile)

			config[banlistFilesKey] = banlistFiles
			config[supportedFormatsKey] = supportedFormats
			self.saveConfigForServer(config, serverId)
		return result


	def editSupportedFormat(self, formatName, lflistFile, serverId):
		config = self.getConfigForServer(serverId)
		supportedFormats = config.get(supportedFormatsKey)
		
		found = False
		forcedFormat = ""
		for format in supportedFormats:
			if format.lower() == formatName.lower():
				found=True
				forcedFormat = format
		
		if not found:
			return OperationResult(False, "Format %s doesn't exist yet. You can add a new format using /add_format"%formatName)
		
		result = self.banlistGenerator.writeBanlist(forcedFormat, lflistFile, serverId)
		return result

	def renameFormat(self, oldName, newName, serverId):
		config = self.getConfigForServer(serverId)
		supportedFormats: List[str] = config.get(supportedFormatsKey)

		found = False
		forcedFormat = ""
		for format in supportedFormats:
			if format.lower() == oldName.lower():
				found = True
				forcedFormat = format
		
		if not found:
			return OperationResult(False, "Format %s doesn't exist yet. You can check which formats already exist with /format_list."%oldName)
		
		supportedFormats.remove(forcedFormat)
		supportedFormats.add(newName)

		banlistFiles: List[dict] = config.get(banlistFilesKey)
		for banlist in banlistFiles:
			if banlist.get(nameKey).lower() == oldName.lower():
				banlist[nameKey] = newName
		
		channelConfig :List[dict] = config.get(channelConfigKey)
		for config in channelConfig:
			if config.get(nameKey).lower() == oldName.lower():
				config[nameKey] = newName

		config[banlistFilesKey] = banlistFiles
		config[supportedFormatsKey] = supportedFormats
		config[channelConfigKey] = channelConfig
		self.saveConfigForServer(config, serverId)
		return OperationResult(True, "")

	def removeFormat(self, formatName, serverId):
		config = self.getConfigForServer(serverId)
		supportedFormats :List[str] = config.get(supportedFormatsKey)

		found = False
		forcedFormat = ""
		for format in supportedFormats:
			if format.lower() == formatName.lower():
				found = True
				forcedFormat = format
		
		if not found:
			return OperationResult(False, "Format %s doesn't exist yet. You can check which formats already exist with /format_list"%forcedFormat)

		newBanlistFiles = []

		banlistFiles: List[dict] = config.get(banlistFilesKey)
		for banlist in banlistFiles:
			if banlist.get(nameKey) != forcedFormat:
				newBanlistFiles.append(banlist)
		
		newChannelConfig = []
		channelConfig = config.get(channelConfigKey)
		for individualChannelConfig in channelConfig:
			if individualChannelConfig.get(nameKey) != forcedFormat:
				newChannelConfig.append(individualChannelConfig)

		supportedFormats.remove(forcedFormat)

		config[banlistFilesKey] = newBanlistFiles
		config[supportedFormatsKey] = supportedFormats
		config[channelConfigKey] = newChannelConfig
		self.banlistGenerator.deleteBanlist(forcedFormat, serverId)
		self.saveConfigForServer(config, serverId)
		return OperationResult(True, "")

	def setDefaultFormatForChannel(self, formatName, channelName, serverId):

		config = self.getConfigForServer(serverId)
		supportedFormats = config.get(supportedFormatsKey)

		if formatName in supportedFormats:
			channelConfig = config.get(channelConfigKey)
			found = False
			for channel in channelConfig:
				if channel.get(channelNameKey) == channelName:
					found = True
					channel[nameKey] = formatName
			if not found:
				newConfig = {}
				newConfig[channelNameKey] = channelName
				newConfig[nameKey] = formatName
				newConfig[useDefaultFormatKey] = False
				channelConfig.append(newConfig)
			self.saveConfigForServer(config, serverId)
			return OperationResult(True, "")
		else:
			return OperationResult(False, "Format %s is not supported. You can add it manually with /add_format."%formatName)

	def getBanlistForFormat(self, formatName, serverId):
		config = self.getConfigForServer(serverId)
		for lflist in config.get(banlistFilesKey):
			if lflist.get(nameKey) == formatName:
				return lflist.get(filenameKey)

	def isChannelEnabled(self, channelName, serverId):
		if channelName == groupChannelKey or channelName == threadChannelKey:
			return OperationResult(False, "This bot doesn't support groups or threads")
		for disabledChannel in self.getDisabledChannels(serverId):
			if disabledChannel == channelName:
				return OperationResult(False, "This channel is disabled")
		return OperationResult(True, "")

	def getForcedFormat(self, channelName, serverId):

		config = self.getConfigForServer(serverId)

		defaultFormat = config.get(defaultFormatKey)
		
		for channelConfig in config.get(channelConfigKey):
			if channelConfig.get(channelNameKey) == channelName:
				if channelConfig.get(nameKey) != None:
					return channelConfig.get(nameKey)
				elif channelConfig.get(useDefaultFormatKey):
					return defaultFormat
				else:
					return None
		return defaultFormat



	def isFormatSupported(self, formatName, serverId):
		config = self.getConfigForServer(serverId)
		return formatName in config.get(supportedFormatsKey)

	def getDisabledChannels(self, serverId):
		config = self.getConfigForServer(serverId)
		return config.get(disabledChannelsKey)

	def getSupportedFormats(self, serverId):
		config = self.getConfigForServer(serverId)
		return config.get(supportedFormatsKey)