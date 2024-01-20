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
from constants import _DB_NAME
#############################################################


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

    async def create_embed(self, interaction, weighed_points_mediums, logs, user, store):
        embed = discord.Embed(title=f'Streak Immersion Overview')
        embed.add_field(name='**User**', value=user.display_name)
        embed.add_field(name='**Longest streak:**', value=f'''{store.get_longest_streak(user.id)[0].streak} days''')
        embed.add_field(name='**Current streak:**', value=f'''{store.get_log_streak(user.id)[-1].streak} days''')
        amounts_by_media_desc = '\n'.join(f'{key}: {helpers.millify(weighed_points_mediums[key][1])} {helpers.media_type_format(key)} → {helpers.millify(weighed_points_mediums[key][0])} pts' for key in weighed_points_mediums)
        embed.add_field(name='**Breakdown**', value=amounts_by_media_desc or 'None', inline=False)
        
        await self.create_heatmap(interaction, weighed_points_mediums, logs)
        file = discord.File(fr'''{[file for file in os.listdir() if file.endswith('_overview_chart.png')][0]}''')
        embed.set_image(url=f"attachment://{interaction.user.id}_overview_chart.png")
        
        return embed, file
        heatmap = await create_heatmap()
    

    @app_commands.command(name='streak', description=f'View your log streak')
    @app_commands.checks.has_role("Moderator")
    async def streak(self, interaction: discord.Interaction, user: Optional[discord.User], timeframe: Optional[str], media_type: Optional[str], name: Optional[str]):
        
        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private:
            return await interaction.response.send_message(content='You can only log in #immersion-log or DMs.',ephemeral=True)
        
        store = Store(_DB_NAME)
        logs = store.get_logs_by_user(user.id, media_type, (beginn, end), name)
        if logs == []:
            return await interaction.edit_original_response(content='No logs were found.')
        
        weighed_points_mediums = helpers.multiplied_points(logs)
        embed, file = await self.create_embed(interaction, weighed_points_mediums, logs, user, store)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Streak(bot))
