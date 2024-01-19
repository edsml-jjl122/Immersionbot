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
import os

from discord.utils import get
#############################################################

    
MULTIPLIERS = {
    'BOOK': 1,
    'MANGA': 0.2,
    'VN': 1 / 350,
    'ANIME': 9.5,
    'READING': 1 / 350,
    'LISTENING': 0.45,
    'READTIME': 0.45
}

#############################################################

class Achievements(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(617136488840429598)
                
    @app_commands.command(name='achievements', description=f'Shows your immersion milestones.')
    @app_commands.checks.has_role("QA Tester")
    async def achievements(self, interaction: discord.Interaction):
        
        await interaction.response.defer()
        
        store = Store("prod.db")
        points = store.get_logs_by_user(interaction.user.id, None, ("2000-01-01", interaction.created_at), None)
        weighed_points_mediums = helpers.multiplied_points(points)
        abmt = helpers.calc_achievements(weighed_points_mediums)
        achievements = helpers.get_achievement_text(abmt)
        embed = discord.Embed(title='All Time Achievements')
        embed.add_field(name='Achievements', value='''
'''.join(achievements))
        await interaction.edit_original_response(embed=embed)
    
            
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Achievements(bot))