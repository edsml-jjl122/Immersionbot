import discord
from discord.ext import commands
from datetime import datetime
from datetime import date as new_date, datetime, timedelta
from datetime import timedelta
import json
from collections import defaultdict
from typing import Optional
from discord import app_commands
from discord.app_commands import Choice

from vndb_thigh_highs import VNDB
from vndb_thigh_highs.models import VN
import re
from AnilistPython import Anilist
from discord.ui import Select
from sql import Set_Goal, Store

import time
from discord.utils import get

import helpers
import pytz
import os
# from dotenv import load_dotenv

import aiohttp
from typing import List
import asyncio
import logging

#############################################################

log = logging.getLogger(__name__)

#############################################################

class Set_Goal_Points(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(617136488840429598)
    
    @app_commands.command(name='set_goal_points', description=f'Set daily immersion log goals')
    @app_commands.describe(amount='''Points to log.''')
    @app_commands.choices(media_type = [Choice(name="Anything", value="Anything"), Choice(name="Visual Novel", value="VN"), Choice(name="Manga", value="Manga"), Choice(name="Anime", value="Anime"), Choice(name="Book", value="Book"), Choice(name="Readtime", value="Readtime"), Choice(name="Listening", value="Listening"), Choice(name="Reading", value="Reading")])
    @app_commands.describe(span='''Day, Daily, Weekly, Monthly, [Date = Till a certain date ([year-month-day] Example: '2022-12-29')]''')
    @app_commands.checks.has_role("QA Tester")
    async def set_goal_points(self, interaction: discord.Interaction, media_type: Optional[str], amount: int, span: str):

        if not media_type: 
            media_type = "ANYTHING"

        store = Set_Goal("goals.db")
        goal_type = "POINTS"
        
        if not amount > 0:
            return await interaction.response.send_message(ephemeral=True, content='Only positive numers allowed.')

        if amount > 30000:
            return await interaction.edit_original_response(content='Only numbers under 30 thousand allowed.')
        
        if amount in [float('inf'), float('-inf')]:
            return await interaction.response.send_message(ephemeral=True, content='No infinities allowed.')
        
        if span.upper() == "DAY":
            span = "DAY"
            created_at = interaction.created_at
            end = interaction.created_at.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        elif span.upper() == "DAILY":
            span = "DAILY"
            created_at = interaction.created_at
            end = interaction.created_at + timedelta(days=1)
        elif span.upper() == "WEEKLY":
            span = "WEEKLY"
            created_at = interaction.created_at - timedelta(days=interaction.created_at.weekday())
            end = created_at + timedelta(days=6)
        elif span.upper() == "MONTHLY":
            span = "MONTHLY"
            created_at = interaction.created.replace(day=1)
            next_month = interaction.created.replace(day=28) + timedelta(days=4)
            end = next_month - timedelta(days=next_month.day)
        else:
            created_at = interaction.created_at
            try:
                end = interaction.created_at.replace(year=int((span.split("-"))[0]), month=int((span.split("-"))[1]), day=int((span.split("-"))[2]), hour=0, minute=0, second=0)
                if end > interaction.created_at + timedelta(days=366):
                    return await interaction.response.send_message(content='''A goal span can't be longer than a year.''', ephemeral=True)
                if end < interaction.created_at:
                    return await interaction.response.send_message(content='''You can't set a goal in the past.''', ephemeral=True)
            except Exception:
                return await interaction.response.send_message(ephemeral=True, content='Please enter the date in the correct format.')
            else:
                span = "DATE"
                if end < created_at:
                    return await interaction.response.send_message(ephemeral=True, content='''You can't set goals for the past.''')

        bool = store.check_goal_exists(interaction.user.id, goal_type, span, media_type.upper(), f"of {media_type.upper()}")
        if bool:
            return await interaction.response.send_message(ephemeral=True, content='You already set this goal.')
    
        if len(store.get_goals(interaction.user.id)) > 10:
            return await interaction.response.send_message(ephemeral=True, content='''You can't set more than 10 goals. To delete a goal do ```/delete_goal``''')

        store.new_point_goal(interaction.user.id, "POINTS", media_type.upper(), amount, f"of {media_type.upper()}", span, created_at, end)
        await interaction.response.send_message(ephemeral=True, content=f'''## Set {goal_type} goal as {span} goal\n- {amount} {helpers.media_type_format(media_type.upper())} {" of " + media_type.upper()}\n\nUse ``/goals`` to view your goals for <t:{int(time.mktime((interaction.created_at.replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()))}:D>''')

    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Set_Goal_Points(bot))