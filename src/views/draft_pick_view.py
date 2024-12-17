import discord
from src.drafting.draft_manager import DraftManager

class DraftDropdown(discord.ui.Select):
    def __init__(self, player_id, pack, server_id, on_new_pick, on_card_picked):

        self.player_id = player_id
        self.pack = pack
        self.server_id = server_id
        self.on_new_pick = on_new_pick
        self.on_card_picked = on_card_picked
        options = [discord.SelectOption(label=card["name"], value=str(i)) for i, card in enumerate(pack)]
        super().__init__(placeholder="Choose a card", min_values=1, max_values=1, options=options)

    async def on_error(self, interaction, exception, item, /) -> None:
        raise exception

    async def callback(self, interaction: discord.Interaction):
        card_index = int(self.values[0])
        draft_manager = DraftManager(self.server_id)
        result = draft_manager.pick(self.player_id, self.pack[card_index]["id"])
        await interaction.response.defer()
        await interaction.followup.edit_message(message_id=self.message.id, view=None)
        if self.on_card_picked:
            await self.on_card_picked()
        if result.success:
            if self.on_new_pick:
                await self.on_new_pick()
        
class DraftPickView(discord.ui.View):
    def __init__(self, player_id, pack, server_id, on_new_pick, on_card_picked):
        super().__init__()
        self.add_item(DraftDropdown(player_id, pack, server_id, on_new_pick, on_card_picked))