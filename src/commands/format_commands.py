from typing import List

from discord import Interaction, app_commands, Attachment, File

from src.commands.generic_command_manager import GenericCommandManager

import src.banlist.banlist_utils as Banlist

import src.strings as Strings

def banlist_to_discord_file(banlist_file: str, format_name: str):
	file_name = f"{format_name}.lflist.conf"
	return File(filename=file_name, fp=banlist_file)

class FormatCommandManager(GenericCommandManager):
	
	def add_commands(self):		

		@self.bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_ADD, description="Adds a format to the bot.")
		async def add_format(interaction: Interaction, format_name: str, lflist: Attachment):
			server_id = interaction.guild_id
			result = self.can_command_execute(interaction, True)
			if not result.was_successful():
				await interaction.response.send_message(result.get_message(), ephemeral=True)
				return

			result = self.is_valid_filename(format_name)
			if not result.was_successful():
				await interaction.response.send_message(result.get_message(), ephemeral=True)
				return

			await interaction.response.defer(ephemeral=True)
			if lflist.filename.endswith(".lflist.conf"):
				file_content = await lflist.read()
				decoded_file_content = file_content.decode("utf-8")
				result = Banlist.validate_banlist(decoded_file_content)
				if not result.was_successful():
					await interaction.followup.send(result.get_message())
					return

				result = self.config.add_supported_format(format_name, decoded_file_content, server_id)
				await interaction.followup.send(result.get_message())
			else:
				await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_BANLIST_FORMAT)

		@self.bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_TIE, description="Sets the default format for this channel.")
		async def tie_format_to_channel(interaction: Interaction, format_name: str):
			server_id = interaction.guild_id
			result = self.can_command_execute(interaction, True)
			if not result.was_successful():
				await interaction.response.send_message(result.get_message(), ephemeral=True)
				return

			supported_formats = self.config.get_supported_formats(server_id)
			if len(supported_formats) == 0:
				await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED, ephemeral=True)
				return

			channel_name = self.get_channel_name(interaction.channel)
			result = self.config.set_default_format_for_channel(format_name, channel_name, server_id)
			await interaction.response.send_message(result.get_message(), ephemeral=True)

		@self.bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_DEFAULT, description="Sets the default format for the entire server.")
		async def set_default_format(interaction: Interaction, format_name: str):
			server_id = interaction.guild_id
			result = self.can_command_execute(interaction, True)

			if not result.was_successful():
				await interaction.response.send_message(result.get_message(), ephemeral=True)
				return

			supported_formats = self.config.get_supported_formats(server_id)
			if len(supported_formats) == 0:
				await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED, ephemeral=True)
				return

			result = self.config.set_default_format_for_server(format_name, server_id)
			await interaction.response.send_message(result.get_message(), ephemeral=True)

		@self.bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_CHECK_TIED, description="Checks if this channel has a format tied to it",)
		async def check_tied_format(interaction: Interaction):
			server_id = interaction.guild_id
			result = self.can_command_execute(interaction, False)
			if not result.was_successful():
				await interaction.response.send_message(result.get_message(), ephemeral=True)
				return
			
			supported_formats = self.config.get_supported_formats(server_id)
			if len(supported_formats) == 0:
				await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED, ephemeral=True)
				return

			await interaction.response.defer(ephemeral=True)
			channel_name = self.get_channel_name(interaction.channel)
			forced_format = self.config.get_forced_format(channel_name, server_id)
			if forced_format is None:
				await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMAT_TIED)
			else:
				await interaction.followup.send(Strings.BOT_MESSAGE_CHANNEL_IS_TIED_TO_FORMAT % (channel_name, forced_format))

		@self.bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_UPDATE, description="Updates the banlist for an already existing format",)
		async def update_format(interaction: Interaction, format_name: str, lflist: Attachment):
			server_id = interaction.guild_id

			result = self.is_valid_filename(format_name)
			if not result.was_successful():
				await interaction.response.send_message(result.get_message())
				return

			result = self.can_command_execute(interaction, True)

			supported_formats = self.config.get_supported_formats(server_id)
			found = False
			for _format in supported_formats:
				if _format.lower() == format_name.lower():
					found = True
					break

			if not found:
				await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMAT_FOR_NAME % format_name)
				return

			if result.was_successful():
				await interaction.response.defer(ephemeral=True)
				if lflist.filename.endswith(".lflist.conf"):
					file_content = await lflist.read()
					decodedfile_content = file_content.decode("utf-8")
					result = Banlist.validate_banlist(decodedfile_content)
					if result.was_successful():
						result = self.config.edit_supported_format(format_name, decodedfile_content, server_id)
						if result.was_successful():
							await interaction.followup.send(Strings.BOT_MESSAGE_FORMAT_UPDATED)
						else:
							await interaction.followup.send(result.get_message())
					else:
						await interaction.followup.send(result.get_message())
				else:
					await interaction.followup.send(Strings.ERROR_MESSAGE_WRONG_BANLIST_FORMAT)
			else:
				await interaction.response.send_message(result.get_message())

		@self.bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_REMOVE, description="Removes a format")
		async def remove_format(interaction: Interaction, format_name: str):
			server_id = interaction.guild_id

			result = self.is_valid_filename(format_name)
			if not result.was_successful():
				await interaction.response.send_message(result.get_message())
				return

			result = self.can_command_execute(interaction, True)

			supported_formats = self.config.get_supported_formats(server_id)
			found = False
			for _format in supported_formats:
				if _format.lower() == format_name.lower():
					found = True
					break

			if not found:
				await interaction.response.send_message(Strings.ERROR_MESSAGE_NO_FORMAT_FOR_NAME % format_name)
				return

			if result.was_successful():
				await interaction.response.defer(ephemeral=True)
				result = self.config.remove_format(format_name, server_id)
				if result.was_successful():
					await interaction.followup.send(Strings.BOT_MESSAGE_FORMAT_REMOVED % format_name)
				else:
					await interaction.followup.send(result.get_message())
			else:
				await interaction.response.send_message(result.get_message())
    

		@self.bot.tree.command(name=Strings.COMMAND_NAME_FORMAT_BANLIST, description="Get an EDOPRO banlist")
		async def get_banlist(interaction: Interaction):
			server_id = interaction.guild_id
			result = self.can_command_execute(interaction, False)
			if result.was_successful():
				await interaction.response.defer(ephemeral=True)
				channel_name = self.get_channel_name(interaction.channel)
				forced_format = self.config.get_forced_format(channel_name, server_id)
				banlist_file = self.config.get_banlist_for_format(forced_format, server_id)
				if forced_format is None:
					supported_formats = self.config.get_supported_formats(server_id)
					if len(supported_formats) > 0:
						await interaction.followup.send(Strings.ERROR_MESSAGE_NO_DEFAULT_FORMAT)
					else:
						await interaction.followup.send(Strings.ERROR_MESSAGE_NO_FORMATS_ENABLED)
				else:
					await interaction.followup.send(file=banlist_to_discord_file(banlist_file, forced_format))
			else:
				await interaction.response.send_message(result.get_message(), ephemeral=True)

		@tie_format_to_channel.autocomplete("format_name")
		@update_format.autocomplete("format_name")
		@remove_format.autocomplete("format_name")
		@set_default_format.autocomplete("format_name")
		async def format_autocomplete(
			interaction: Interaction, current: str
		) -> List[app_commands.Choice[str]]:
			choices: List[app_commands.Choice[str]] = []
			formats = self.config.get_supported_formats(interaction.guild_id)
			for _format in formats:
				if current.lower() in _format.lower():
					if len(choices) < 25:
						choice = app_commands.Choice(name=_format, value=format)
						choices.append(choice)
			return choices
