from nextcord.ui import Select
from nextcord import Interaction
from utils.functions.embeds import create_settings_embed


class LocationDropdown(Select):
    def __init__(self, locations):
        super().__init__(placeholder="location")
        for location in locations:
            self.add_option(value=location[0],
                            label=location[0], default=False)

    async def callback(self, interaction=Interaction):
        self.view.set_location_and_server_id(self.values[0])
        self.view.update_lobby()
        self.disabled = True
        overtime, team_damage, map, location = self.view.get_settings()
        settings_embed = create_settings_embed(
            overtime, team_damage, map, location)
        await interaction.response.edit_message(view=self.view, embed=settings_embed)


class MapDropdown(Select):
    def __init__(self, map_pool):
        super().__init__(placeholder="Map")
        for map in map_pool:
            self.add_option(label=map, value=map, default=False)

    async def callback(self, interaction=Interaction):
        self.view.set_map(self.values[0])
        overtime, team_damage, map, location = self.view.get_settings()
        settings_embed = create_settings_embed(
            overtime, team_damage, map, location)
        await interaction.response.edit_message(view=self.view, embed=settings_embed)
