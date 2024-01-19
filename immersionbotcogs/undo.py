import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import json
from typing import Optional
from discord import app_commands
from discord.app_commands import Choice
from typing import List
import json
from sql import Store, Set_Goal
import helpers
import logging
import aiohttp
import asyncio
import os
import time
import pytz
from discord.utils import get

class Undo(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(617136488840429598)
                
    @app_commands.command(name='undo_log', description=f'Undo your latest immersion log.')
    @app_commands.checks.has_role("QA Tester")
    async def undo_log(self, interaction: discord.Interaction):
        
        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private:
            return await interaction.response.send_message(content='You can only log in #immersion-log or DMs.', ephemeral=True)

        store = Store("prod.db")
        log = store.get_that_log(interaction.user.id)
        store.delete_log(interaction.user.id, log.media_type.value, log.amount, log.note)
        return await interaction.response.send_message(content='Deleted log.', ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Undo(bot))
