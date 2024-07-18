import discord
import discord.ext.commands as commands

from astra.connections import AstraHandler
from discord import app_commands
from typing import Optional

class JarGroup(commands.GroupCog, name='jar', group_name='jar'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name='check', description="Check a user's swear jar")
    @app_commands.describe(target='The user to query. If empty, defaults to sender.')   
    async def jar(self, interaction: discord.Interaction, target: Optional[discord.Member]=None):
        if target is None:
            target = interaction.user
        await AstraHandler.jar_check(interaction, target)
    
    @app_commands.command(name='leaderboard', description='Get the server swear jar leaderboard.')
    async def lb(self, interaction: discord.Interaction):
        await AstraHandler.show_leaderboard(interaction)
        