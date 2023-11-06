import discord

class Dropdown(discord.ui.Select):

	def __init__(self, placeholder):
		super().__init__(placeholder=placeholder, min_values=1, max_values=1)

	def setup(self, list, interaction, callbackFunc, params):
		for item in list:
			self.add_option(label=item)
		self.callbackFunc = callbackFunc
		self.params = params
		self.interaction = interaction


	async def callback(self, interaction: discord.Interaction):
		if self.callbackFunc != None:
			await self.callbackFunc.execute_callback(self.values[0], self.params)

class PaginationView(discord.ui.View):

	def __init__(self, placeholder):
		super().__init__()
		self.placeholder = placeholder

	def setup(self,optionList, interaction, callback, params):
		self.dropdown = Dropdown(self.placeholder)
		self.dropdown.setup(optionList, interaction, callback, params)
		self.clear_items()
		self.add_item(self.dropdown)