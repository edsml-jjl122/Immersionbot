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

class Set_Goal_Media(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(617136488840429598)
    
    @app_commands.command(name='set_goal_media', description=f'Set daily immersion log goals')
    @app_commands.describe(amount='''Episode to watch, characters or pages to read. Time to read/listen in [hr:min] or [min] for example '1.30' or '25'.''')
    @app_commands.choices(media_type = [Choice(name="Visual Novel", value="VN"), Choice(name="Manga", value="Manga"), Choice(name="Anime", value="Anime"), Choice(name="Book", value="Book"), Choice(name="Readtime", value="Readtime"), Choice(name="Listening", value="Listening"), Choice(name="Reading", value="Reading")])
    @app_commands.describe(name='''You can use vndb IDs for VN and Anilist codes for Anime, Manga and Light Novels''')
    @app_commands.describe(span='''[Day = Till the end of today], [Daily = Everyday], [Date = Till a certain date ([year-month-day] Example: '2022-12-29')]''')
    @app_commands.checks.has_role("QA Tester")
    async def set_goal_media(self, interaction: discord.Interaction, media_type: str, amount: str, name: Optional[str], span: str):
        store = Set_Goal("goals.db")
        goal_type = "MEDIA" if not name else "SPECIFIC"
        
        amount = helpers.amount_time_conversion(media_type=media_type, amount=amount)

        if not amount > 0:
            await interaction.response.defer()
            return await interaction.response.send_message(ephemeral=True, content='Only positive numers allowed.')

        if media_type == "VN" and amount > 2000000:
            return await interaction.response.send_message(ephemeral=True, content='Only numbers under 2 million allowed.')
        
        if media_type == "Manga" and amount > 1000:
            return await interaction.response.send_message(ephemeral=True, content='Only numbers under 1000 allowed.')
        
        if media_type == "Anime" and amount > 200:
            return await interaction.response.send_message(ephemeral=True, content='Only numbers under 200 allowed.')
        
        if media_type == "Book" and amount > 500:
            return await interaction.response.send_message(ephemeral=True, content='Only numbers under 500 allowed.')

        if media_type == "READTIME" and amount > 400:
            return await interaction.response.send_message(ephemeral=True, content='Only numbers under 400 allowed.')

        if media_type == "LISTENING" and amount > 400:
            return await interaction.response.send_message(ephemeral=True, content='Only numbers under 400 allowed.')

        if media_type == "READING" and amount > 2000000:
            return await interaction.response.send_message(ephemeral=True, content='Only numbers under 2 million allowed.')
        
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
            created_at = interaction.created_at.replace(day=1)
            next_month = interaction.created_at.replace(day=28) + timedelta(days=4)
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

        bool = store.check_goal_exists(interaction.user.id, goal_type, span, media_type.upper(), amount, (helpers.point_message_converter(media_type.upper(), int(amount), name if name else ""))[3])
        if bool:
            return await interaction.response.send_message(ephemeral=True, content='You already set this goal.')

        if len(store.get_goals(interaction.user.id)) > 10:
            return await interaction.response.send_message(ephemeral=True, content='''You can't set more than 10 goals. To delete a goal do ```/delete_goal``''')

        store.new_goal(interaction.user.id, "MEDIA", media_type.upper(), amount, (helpers.point_message_converter(media_type.upper(), amount, name if name else ""))[3], span, created_at, end)

        await interaction.response.send_message(ephemeral=True, content=f'''## Set {goal_type} goal as {span} goal\n- {amount} {helpers.media_type_format(media_type.upper())} {(helpers.point_message_converter(media_type.upper(), amount, name))[3]}\n\nUse ``/goals`` to view your goals for <t:{int(time.mktime((interaction.created_at.replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()))}:D>''')

    @set_goal_media.autocomplete('name')
    async def log_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:

        await interaction.response.defer()
        media_type = interaction.namespace['media_type']
        suggestions = []
        url = ''

        if media_type == 'VN':
            url = 'https://api.vndb.org/kana/vn'
            data = {'filters': ['search', '=', f'{current}'], 'fields': 'title, alttitle'} # default no. of results is 10
        
        elif media_type == 'Anime' or media_type == 'Manga':
            url = 'https://graphql.anilist.co'
            query = f'''
            query ($page: Int, $perPage: Int, $title: String) {{
                Page(page: $page, perPage: $perPage) {{
                    pageInfo {{
                        total
                        perPage
                    }}
                    media (search: $title, type: {media_type.upper()}) {{
                        id
                        title {{
                            romaji
                            native
                        }}
                    }}
                }}
            }}
            '''

            variables = {
                'title': current,
                'page': 1,
                'perPage': 10
            }

            data = {'query': query, 'variables': variables}

        if not url:
            return []

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                log.info(resp.status)
                json_data = await resp.json()

                if media_type == 'VN':
                    suggestions = [(result['title'], result['id']) for result in json_data['results']]

                elif media_type == 'Anime' or media_type == 'Manga':
                    suggestions = [(f"{result['title']['romaji']} ({result['title']['native']})", result['id']) for result in json_data['data']['Page']['media']]

                await asyncio.sleep(0)

                return [
                    app_commands.Choice(name=title, value=str(id))
                    for title, id in suggestions if current.lower() in title.lower()
                ]
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Set_Goal_Media(bot))