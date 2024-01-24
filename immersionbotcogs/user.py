import discord
from discord.ext import commands
from datetime import date as new_date, timedelta
from typing import Optional
from discord import app_commands
from discord.app_commands import Choice

from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

from enum import Enum
import sqlite3
from sql import Store, Set_jp
import os

import helpers
from constants import _DB_NAME, TIMEFRAMES, _JP_DB
import asyncio

class SqliteEnum(Enum):
    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            return self.name

class MediaType(SqliteEnum):
    BOOK = 'BOOK'
    MANGA = 'MANGA'
    READTIME = 'READTIME'
    READING = 'READING'
    VN = 'VN'
    ANIME = 'ANIME'
    LISTENING = 'LISTENING'
    JAPANESE = 'JAPANESE'

class User(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(617136488840429598)
    
    async def generate_trend_graph(self, timeframe, interaction, logs):

        def daterange(start_date, end_date):
                for n in range(int((end_date - start_date).days)):
                    yield start_date + timedelta(n)
        
        def month_year_iter(start_month, start_year, end_month, end_year):
            ym_start= 12 * start_year + start_month - 1
            ym_end= 12 * end_year + end_month - 1
            for ym in range(ym_start, ym_end):
                y, m = divmod(ym, 12)
                yield y, m+1
        
        log_dict = defaultdict(lambda: defaultdict(lambda: 0))
        logs = list(reversed(logs))
        start_date, end_date = logs[0].created_at, logs[-1].created_at
        
        if timeframe == "All Time":
            for year, month in month_year_iter(start_date.month, start_date.year, end_date.month, end_date.year):
                for media_type in reversed(MediaType):
                    log_dict[media_type.value].setdefault((new_date(year, month, 1).strftime("%b/%y")), 0)
            for log in logs:
                log_dict[log.media_type.value][log.created_at.strftime("%b/%y")] += helpers._to_amount(log.media_type.value, log.amount)

        else:
            # Set empty days to 0
            for media_type in reversed(MediaType):
                for date in daterange(start_date, end_date):
                    log_dict[media_type.value].setdefault(date.date(), 0)
            for log in logs:
                log_dict[log.media_type.value][log.created_at.date()] += helpers._to_amount(log.media_type.value, log.amount)
            log_dict = dict(sorted(log_dict.items()))

        fig, ax = plt.subplots(figsize=(16, 12))
        plt.title(f'{timeframe} Immersion ', fontweight='bold', fontsize=50)
        plt.ylabel('Points', fontweight='bold', fontsize=30)
        
        # print({k: dict(v) for k, v in log_dict.items()})
        df = pd.DataFrame(log_dict)
        df = df.fillna(0)
        # print(df)
        
        color_dict = {
            "BOOK": "tab:orange",
            "MANGA": "tab:red",
            "READTIME": "tab:pink",
            "READING": "tab:green",
            "VN": "tab:cyan",
            "ANIME": "tab:purple",
            "LISTENING": "tab:blue",
            "JAPANESE": "tab:pink"
        }

        accumulator = 0
        for media_type in df.columns:
            col = df[media_type]
            ax.bar(df.index, col,
                bottom=accumulator,
                color=color_dict[media_type])

            accumulator += col

        ax.legend(df.columns)

        plt.xticks(df.index, fontsize=20, rotation=45, horizontalalignment='right')
        fig.savefig(f"{interaction.user.id}_overview_chart.png")
    
    async def create_embed(self, timeframe, interaction, weighed_points_mediums, logs, user, store):
        embed = discord.Embed(title=f'{timeframe} Immersion Overview')
        embed.add_field(name='**User**', value=user.display_name)
        embed.add_field(name='**Timeframe**', value=timeframe)
        embed.add_field(name='**Points**', value=helpers.millify(sum(i for i, j in list(weighed_points_mediums.values()))))
        embed.add_field(name='**Longest streak:**', value=f'''{store.get_log_streak(interaction.user.id)[0].longest_streak} days''')
        embed.add_field(name='**Current streak:**', value=f'''{store.get_log_streak(interaction.user.id)[0].current_streak} days''')
        amounts_by_media_desc = '\n'.join(f'{key}: {helpers.millify(weighed_points_mediums[key][1])} {helpers.media_type_format(key)} → {helpers.millify(weighed_points_mediums[key][0])} pts' for key in weighed_points_mediums)
        embed.add_field(name='**Breakdown**', value=amounts_by_media_desc or 'None', inline=False)
        
        await self.generate_trend_graph(timeframe, interaction, logs)
        file = discord.File(fr'''{[file for file in os.listdir() if file.endswith('_overview_chart.png')][0]}''')
        filename = f"{interaction.user.id}_overview_chart.png"
        embed.set_image(url=f"attachment://{filename}")
        
        return embed, file, filename

    @app_commands.command(name='user', description=f'Immersion overview of a user.')
    @app_commands.describe(timeframe='''DEFAULT=MONTH; Week, Month, Year, All, [year-month-day] or [year-month-day-year-month-day]''')
    @app_commands.choices(media_type = [Choice(name="Visual Novels", value="VN"), Choice(name="Manga", value="MANGA"), Choice(name="Anime", value="ANIME"), Choice(name="Book", value="BOOK"), Choice(name="Readtime", value="READTIME"), Choice(name="Listening", value="LISTENING"), Choice(name="Reading", value="READING")])
    @app_commands.describe(name='''You can use vndb IDs and titles for VN and Anilist codes for Anime and Manga''')
    @app_commands.checks.has_role("QA Tester")
    async def user(self, interaction: discord.Interaction, user: discord.User, timeframe: Optional[str], media_type: Optional[str], name: Optional[str]):
        
        if not media_type:
            media_type = None

        if not name:
            name = None

        if not timeframe or timeframe.upper() == "MONTH":
            #Month
            timeframe = "Monthly"
            beginn = interaction.created_at.replace(day=1, hour=0, minute=0)
            end = (beginn.replace(day=28) + timedelta(days=4)) - timedelta(days=(beginn.replace(day=28) + timedelta(days=4)).day)

        elif timeframe.upper() == "WEEK":
            beginn = (interaction.created_at - timedelta(days=interaction.created_at.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end = (beginn + timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            timeframe = f"""{beginn.strftime("{0}").format(helpers.ordinal(beginn.day))}-{end.strftime("{0} %b").format(helpers.ordinal(end.day))}"""
        
        elif timeframe.upper() == "YEAR":
            beginn = interaction.created_at.date().replace(month=1, day=1)
            end = interaction.created_at.date().replace(month=12, day=31)
            timeframe = f"""{beginn.strftime("%Y")}"""
        
        elif timeframe.upper() == "ALL":
            beginn = interaction.created_at.replace(year=2020)
            end = interaction.created_at
            timeframe = f"""All Time"""

        elif timeframe.upper() not in TIMEFRAMES:
            try:
                dates = timeframe.split('-')
                if len(timeframe.split('-')) == 6:
                    beginn = interaction.created_at.replace(year=int(dates[0]), month=int(dates[1]), day=int(dates[2]))
                    end = interaction.created_at.replace(year=int(dates[3]), month=int(dates[4]), day=int(dates[5]))
                    timeframe = f"""{beginn.strftime("{0}").format(helpers.ordinal(beginn.day))}-{end.strftime("{0} %b").format(helpers.ordinal(end.day))}"""
                    if beginn > end:
                        return await interaction.response.send_message(content='You switched up the dates.', ephemeral=True)
                elif len(timeframe.split('-')) == 3:
                    beginn = interaction.created_at.replace(year=int(dates[0]), month=int(dates[1]), day=int(dates[2]), hour=0, minute=0, second=0)
                    end = beginn + timedelta(days=1)
                    if beginn > interaction.created_at:
                        return await interaction.response.send_message(content='''You can't look into the future.''', ephemeral=True)
                else:
                    return Exception
            except Exception:
                return await interaction.response.send_message(content='Enter a valid date. [Year-Month-day] e.g 2023-12-24', ephemeral=True)

        store = Store(_DB_NAME)
        logs = store.get_logs_by_user(user.id, media_type, (beginn, end), name)
        if logs == []:
            return await interaction.edit_original_response(content='No logs were found.')

        store_jp = Set_jp(_JP_DB)
        weighed_points_mediums = helpers.multiplied_points(logs + store_jp.get_jp(interaction.user.id))
        embed, file, filename = await self.create_embed(timeframe, interaction, weighed_points_mediums, logs, user, store)
    
        await interaction.response.send_message(embed=embed, file=file)

        await asyncio.sleep(1)

        for file in os.listdir():
            if file == filename:
                os.remove(f'{filename}')

    @app_commands.command(name='me', description=f'Immersion overview of yourself.')
    @app_commands.checks.has_role("QA Tester")
    async def me(self, interaction: discord.Interaction, timeframe: Optional[str], media_type: Optional[str], name: Optional[str]):

        if not media_type:
            media_type = None

        if not name:
            name = None

        if not timeframe or timeframe.upper() == "MONTH":
            #Month
            timeframe = "Monthly"
            beginn = interaction.created_at.replace(day=1, hour=0, minute=0)
            end = (beginn.replace(day=28) + timedelta(days=4)) - timedelta(days=(beginn.replace(day=28) + timedelta(days=4)).day)

        elif timeframe.upper() == "WEEK":
            beginn = (interaction.created_at - timedelta(days=interaction.created_at.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end = (beginn + timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            timeframe = f"""{beginn.strftime("{0}").format(helpers.ordinal(beginn.day))}-{end.strftime("{0} %b").format(helpers.ordinal(end.day))}"""
        
        elif timeframe.upper() == "YEAR":
            beginn = interaction.created_at.date().replace(month=1, day=1)
            end = interaction.created_at.date().replace(month=12, day=31)
            timeframe = f"""{beginn.strftime("%Y")}"""
        
        elif timeframe.upper() == "ALL":
            beginn = interaction.created_at.replace(year=2020)
            end = interaction.created_at
            timeframe = f"""All Time"""

        elif timeframe.upper() not in TIMEFRAMES:
            try:
                dates = timeframe.split('-')
                if len(timeframe.split('-')) == 6:
                    beginn = interaction.created_at.replace(year=int(dates[0]), month=int(dates[1]), day=int(dates[2]))
                    end = interaction.created_at.replace(year=int(dates[3]), month=int(dates[4]), day=int(dates[5]))
                    timeframe = f"""{beginn.strftime("{0}").format(helpers.ordinal(beginn.day))}-{end.strftime("{0} %b").format(helpers.ordinal(end.day))}"""
                    if beginn > end:
                        return await interaction.response.send_message(content='You switched up the dates.', ephemeral=True)
                elif len(timeframe.split('-')) == 3:
                    beginn = interaction.created_at.replace(year=int(dates[0]), month=int(dates[1]), day=int(dates[2]), hour=0, minute=0, second=0)
                    end = beginn + timedelta(days=1)
                    if beginn > interaction.created_at:
                        return await interaction.response.send_message(content='''You can't look into the future.''', ephemeral=True)
                else:
                    return Exception
            except Exception:
                return await interaction.response.send_message(content='Enter a valid date. [Year-Month-day] e.g 2023-12-24', ephemeral=True)
    
        store = Store(_DB_NAME)
        logs = store.get_logs_by_user(interaction.user.id, None, (beginn, end), name)
        if logs == []:
            return await interaction.edit_original_response(content='No logs were found.')
        
        store_jp = Set_jp(_JP_DB)
        weighed_points_mediums = helpers.multiplied_points(logs + store_jp.get_jp(interaction.user.id))
        embed, file, filename = await self.create_embed(timeframe, interaction, weighed_points_mediums, logs, interaction.user, store)
        
        await interaction.response.send_message(embed=embed, file=file)

        await asyncio.sleep(1)

        for file in os.listdir():
            if file == filename:
                os.remove(f'{filename}')

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(User(bot))
