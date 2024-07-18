import discord
import discord.ext.commands as commands

from discord import app_commands

from astra.connections import AstraHandler
from astra.generation import AstraMarkovModel

@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
class QuoteGroup(commands.GroupCog, name='quote', group_name='quote'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        menus = [
            app_commands.ContextMenu(
                name='Quote Message',
                callback=self.quote_msg),
            app_commands.ContextMenu(
                name='List Quotes',
                callback=self.quote_list)]
        for menu in menus:
            self.bot.tree.add_command(menu)
    
    async def quote_msg(self, interaction: discord.Interaction, msg: discord.Message):
        await AstraHandler.add_quote(interaction, msg.author, msg)
        
    @app_commands.command(name='add', description='Add a quote')
    @app_commands.describe(user='The user to quote', msg='The quote')
    async def quote_msg_cmd(self, interaction: discord.Interaction, user: discord.User | discord.Member, msg: str):
        await AstraHandler.add_quote(interaction, user, msg)
        
    async def quote_list(self, interaction: discord.Interaction, user: discord.Member):
        await AstraHandler.read_quotes(interaction, user)
        
    @app_commands.command(name='list', description='List quotes')
    @app_commands.describe(user='Target user')
    async def quote_list_cmd(self, interaction: discord.Interaction, user: discord.User | discord.Member):
        await AstraHandler.read_quotes(interaction, user)
        
    @app_commands.command(name='gen', description='Generate a quote')
    async def quote_gen(self, interaction: discord.Interaction):
        sentence = AstraMarkovModel().make_sentence()
        await interaction.response.send_message(sentence)