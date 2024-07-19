import discord

from abc import ABCMeta, abstractmethod
from typing import Any

class AbstractPageView(discord.ui.View, metaclass=ABCMeta):
    def __init__(self, *, interaction: discord.Interaction, raw: list[Any], perPage: int=5):
        self.interaction = interaction
        self._raw = raw
        self.total_pages = (len(raw) // perPage) + 1 if (len(raw) % perPage != 0) else (len(raw) // perPage)
        self.page = 1
        self.per_page = perPage
        super().__init__(timeout=60)
    
    async def show(self):
        embed = await self.build_view()
        await self.update_buttons()
        await self.interaction.response.send_message(embed=embed, view=self)
        
    @abstractmethod
    async def build_view(self):
        pass
    
    async def update_view(self, interaction: discord.Interaction):
        embed = await self.build_view()
        await self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
        
    async def update_buttons(self):
        self.children[0].disabled = (self.total_pages == 1 or self.page <= 2)
        self.children[1].disabled = (self.total_pages == 1 or self.page == 1)
        self.children[2].disabled = (self.total_pages == 1 or self.page == self.total_pages)
        self.children[3].disabled = (self.total_pages == 1 or self.page >= self.total_pages - 1)
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.interaction.user.id
       
    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji='⏮️')
    async def first(self, interaction: discord.Interaction, button: discord.Button):
        self.page = 1
        await self.update_view(interaction)
    
    @discord.ui.button(style=discord.ButtonStyle.primary, emoji='⏪')
    async def prev(self, interaction: discord.Interaction, button: discord.Button):
        self.page -= 1
        await self.update_view(interaction)
        
    @discord.ui.button(style=discord.ButtonStyle.primary, emoji='⏩')
    async def succ(self, interaction: discord.Interaction, button: discord.Button):
        self.page += 1
        await self.update_view(interaction)
        
    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji='⏭️')
    async def last(self, interaction: discord.Interaction, button: discord.Button):
        self.page = self.total_pages
        await self.update_view(interaction)
        
    async def on_timeout(self):
        message = await self.interaction.original_response()
        await message.edit(view=None)