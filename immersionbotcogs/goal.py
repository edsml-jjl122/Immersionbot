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

# class MyView(discord.ui.View):
#     def __init__(self, *, timeout: Optional[float] = 900, data, beginning_index: int, end_index: int):
#         super().__init__(timeout=timeout)
#         self.data: list = data
#         self.beginning_index: int = beginning_index
#         self.ending_index: int = end_index
    
    
#     async def edit_embed(self, data, beginning_index, ending_index):
#         myembed = discord.Embed(title=f'{len(data)} Goals found.')
#         for result in data[beginning_index:ending_index]:
#             myembed.add_field(name=f'{result[0]}: {result[1]}',value=f'{result[2]}', inline=False)
#         if len(data) >= 2:
#             myembed.set_footer(text="... not all results displayed but you can pick any index.\n"
#                                     "Pick an index to retrieve a scene next.")
#         else:
#             myembed.set_footer(text="Pick an index to retrieve a scene next.")
#         return myembed
        
        
#     @discord.ui.button(label='≪', style=discord.ButtonStyle.grey, row=1)
#     async def go_to_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.beginning_index -= 10
#         self.ending_index -= 10
#         if self.beginning_index >= len(self.data):
#             self.beginning_index = 0
#             self.ending_index = 10
#         myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
#         await interaction.response.edit_message(embed=myembed)
        
        
#     @discord.ui.button(label='Back', style=discord.ButtonStyle.blurple, row=1)
#     async def go_to_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.beginning_index -= 5
#         self.ending_index -= 5
#         myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
#         await interaction.response.edit_message(embed=myembed)
    
    
#     @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple, row=1)
#     async def go_to_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.beginning_index += 5
#         self.ending_index += 5
#         myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
#         await interaction.response.edit_message(embed=myembed)
        
        
#     @discord.ui.button(label='≫', style=discord.ButtonStyle.grey, row=1)
#     async def go_to_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.beginning_index += 10
#         self.ending_index += 10
#         if self.beginning_index >= len(self.data):
#             self.beginning_index -= 10
#             self.ending_index -= 10
#         myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
#         await interaction.response.edit_message(embed=myembed)
        
        
#     @discord.ui.button(label='Quit', style=discord.ButtonStyle.red, row=1)
#     async def stop_pages(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.message.delete()

class Goal(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(617136488840429598)

    @app_commands.command(name='goals', description=f'See your immersion log goal overview.')
    @app_commands.checks.has_role("QA Tester")
    async def goals(self, interaction: discord.Interaction):
        
        store_goal = Set_Goal("goals.db")
        goals = store_goal.get_goals(interaction.user.id)
                
        if not goals:
            return await interaction.response.send_message(ephemeral=True, content='No goals found. Set goals with ``/set_goal``.')
        
        store_prod = Store("prod.db")
        beginn = goals[0].created_at
        end = interaction.created_at + timedelta(hours=26)

        relevant_logs = store_prod.get_logs_by_user(interaction.user.id, None, (beginn, end), None)

        if not relevant_logs:
            goals_description = []
            for goal_row in goals:
                goals_description.append(f"""- 0/{goal_row.amount} {helpers.media_type_format(goal_row.media_type.value) if goal_row.goal_type != "POINTS" else "points"} {goal_row.text} ({goal_row.span}{"=" + str(goal_row.end) if goal_row.span == "DATE" else ""})""")
            goals_description = '\n'.join(goals_description)
            
            return await interaction.response.send_message(ephemeral=True, content=f'''## {interaction.user.display_name}'s Goal Overview\n{goals_description if goals_description else "No goals found."}\n\nUse ``/set_goal`` to set your goals for <t:{int(time.mktime((interaction.created_at.replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()))}:D> and more!''')
            
        dicts = helpers.get_time_relevant_logs(goals, relevant_logs)
        goals_description, goal_message = helpers.get_goal_description(dicts=dicts, log_bool=False, store=store_goal, interaction=interaction, media_type=None)

        await interaction.response.send_message(ephemeral=True, content=f'''## {interaction.user.display_name}'s Goal Overview\n{goals_description if goals_description else "No goals found."}\n\nUse ``/set_goal`` to set your goals for <t:{int(time.mktime((interaction.created_at.replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()))}:D> and more!''')
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Goal(bot))
