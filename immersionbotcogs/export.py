import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
from typing import Optional
from discord import app_commands
from discord.app_commands import Choice
from sql import Store
import xlsxwriter
import os
import asyncio
import helpers
# from dotenv import load_dotenv

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

class Export(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(617136488840429598)
                
    @app_commands.command(name='export', description=f'Export your immersion logs.')
    @app_commands.describe(timeframe='''Span of logs used.''')
    @app_commands.choices(timeframe = [Choice(name="Monthly", value="Monthly"), Choice(name="All Time", value="All Time"), Choice(name="Weekly", value="Weekly"), Choice(name="Yearly", value="Yearly")])
    @app_commands.choices(media_type = [Choice(name="Visual Novels", value="VN"), Choice(name="Manga", value="MANGA"), Choice(name="Anime", value="ANIME"), Choice(name="Book", value="BOOK"), Choice(name="Readtime", value="READTIME"), Choice(name="Listening", value="LISTENING"), Choice(name="Reading", value="READING")])
    @app_commands.describe(date='''[year-month-day] Example: '2022-12-29'.''')
    @app_commands.checks.has_role("Moderator")
    async def export(self, interaction: discord.Interaction, timeframe: str, media_type: Optional[str], date: Optional[str]):

        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private:
            return await interaction.response.send_message(content='You can only log in #immersion-log or DMs.',ephemeral=True)

        await interaction.response.defer()

        if not date:
            now = interaction.created_at
        else:
            now = interaction.created_at.replace(year=int(date.split("-")[0]), month=int(date.split("-")[1]), day=int(date.split("-")[2]), hour=0, minute=0, second=0, microsecond=0)
        
        now, start, end, title = helpers.start_end_tf(now, timeframe)
        store = Store("prod.db")
        logs = store.get_logs_by_user(interaction.user.id, media_type, (start, now, end), None)
        print(logs)

        workbook = xlsxwriter.Workbook(f'''{interaction.user.name}'s {timeframe}{' ' + media_type if media_type else ''}{' (' + date + ')' if date else ''}.xlsx''')
        worksheet = workbook.add_worksheet('Logs')

        row = 0
        col = 0

        for log in logs:
            worksheet.write_number(row, col, log.discord_guild_id)
            worksheet.write_number(row, col + 1, log.discord_user_id)
            worksheet.write_string(row, col + 2, log.media_type.value)
            worksheet.write_number(row, col + 3, log.amount)
            worksheet.write_number(row, col + 4, helpers._to_amount(log.media_type.value, log.amount))
            worksheet.write_string(row, col + 5, log.note)
            worksheet.write_datetime(row, col + 6, log.created_at)
            row += 1
                
        workbook.close()
        await interaction.delete_original_response()
        await interaction.channel.send(file=discord.File(fr'''{[file for file in os.listdir() if file == f"{interaction.user.name}'s {timeframe}{' ' + media_type if media_type else ''}{' (' + date + ')' if date else ''}.xlsx"][0]}'''))
        
        await asyncio.sleep(1)

        for file in os.listdir():
            if file == f'''{interaction.user.name}'s {timeframe}{' ' + media_type if media_type else ''}{' (' + date + ')' if date else ''}.xlsx''':
                os.remove(f'''{interaction.user.name}'s {timeframe}{' ' + media_type if media_type else ''}{' (' + date + ')' if date else ''}.xlsx''')

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Export(bot))
