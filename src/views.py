import discord

class Dropdown(discord.ui.Select):

	def __init__(self):
		super().__init__(placeholder='Choose a format', min_values=1, max_values=1)

	def setup(self, list, interaction, callbackFunc, params):
		for item in list:
			self.add_option(label=item)
		self.callbackFunc = callbackFunc
		self.params = params
		self.interaction = interaction


	async def callback(self, interaction: discord.Interaction):
		if self.callbackFunc != None:
			await self.callbackFunc.executeCallback(self.values[0], self.params)

class PaginationView(discord.ui.View):

	def setup(self, optionList, interaction, callback, params):
		self.dropdown = Dropdown()
		self.dropdown.setup(optionList, interaction, callback, params)
		self.add_item(self.dropdown)
