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
import time
import pytz
from discord.utils import get

import seaborn as sns
import pandas as pd
import numpy as np

#############################################################

log = logging.getLogger(__name__)
#############################################################


class Streak(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(617136488840429598)

    async def create_heatmap():
        df = pd.DataFrame(np.random.random((5,5)), columns=["a","b","c","d","e"])
        p1 = sns.heatmap(df)

    # async def create_embed(self):
    #     heatmap = await create_heatmap()
    

    @app_commands.command(name='streak', description=f'View your log streak')
    @app_commands.checks.has_role("Moderator")
    async def streak(self, interaction: discord.Interaction, user: Optional[discord.User], timeframe: Optional[str], media_type: Optional[str], name: Optional[str]):
        
        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private:
            return await interaction.response.send_message(content='You can only log in #immersion-log or DMs.',ephemeral=True)
        
        # myembed = await create_embed()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Streak(bot))
