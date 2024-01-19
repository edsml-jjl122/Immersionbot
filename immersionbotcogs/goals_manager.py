import discord
from discord.ext import commands
from discord.ext import tasks
import json
from datetime import datetime
from discord.app_commands import Choice
from typing import Optional
import asyncpg
import os
from datetime import timedelta
import pytz
from discord.ui import Select
from discord import app_commands
from sql import Store, Set_Goal
# from dotenv import load_dotenv
import helpers
#############################################################

  
#############################################################

class MyView(discord.ui.View):
    def __init__(self, *, timeout: Optional[float] = 900, data, beginning_index: int, end_index: int):
        super().__init__(timeout=timeout)
        self.data: list = data
        self.beginning_index: int = beginning_index
        self.ending_index: int = end_index
    
    
    async def edit_embed(self, data, beginning_index, ending_index):
        myembed = discord.Embed(title=f'Select a goal to delete:')
        for result in data[beginning_index:ending_index]:
            myembed.add_field(name=f'{result[0]}. goal',value=f'{result[1]}', inline=False)
        if len(data) >= 5:
            myembed.set_footer(text="... not all results displayed but you can pick any index.\n" 
                                    "Pick an index to retrieve a scene next.")
        else:
            myembed.set_footer(text="Pick an index to retrieve a scene next.")
        return myembed
        
        
    @discord.ui.button(label='≪', style=discord.ButtonStyle.grey, row=1)
    async def go_to_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.beginning_index -=5
        self.ending_index -=5
        if self.beginning_index >= len(self.data):
            self.beginning_index = 0
            self.ending_index =5
        myembed = await self.edit_embed(self.data, self.beginning_index, self.ending_index)
        await interaction.response.edit_message(embed=myembed)
        
        
    @discord.ui.button(label='Back', style=discord.ButtonStyle.blurple, row=1)
    async def go_to_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.beginning_index -= 5
        self.ending_index -= 5
        myembed = await self.edit_embed(self.data, self.beginning_index, self.ending_index)
        await interaction.response.edit_message(embed=myembed)
    
    
    @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple, row=1)
    async def go_to_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.beginning_index += 5
        self.ending_index += 5
        myembed = await self.edit_embed(self.data, self.beginning_index, self.ending_index)
        await interaction.response.edit_message(embed=myembed)        
        
        
    @discord.ui.button(label='≫', style=discord.ButtonStyle.grey, row=1)
    async def go_to_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.beginning_index +=5
        self.ending_index +=5
        if self.beginning_index >= len(self.data):
            self.beginning_index -=5
            self.ending_index -=5
        myembed = await self.edit_embed(self.data, self.beginning_index, self.ending_index)
        await interaction.response.edit_message(embed=myembed)
        
    @discord.ui.button(label='Quit', style=discord.ButtonStyle.red, row=1)
    async def stop_pages(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

class Goals_manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.batch_update.start()
        
    def cog_unload(self):
        self.batch_update.cancel()
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.batch_update.start()
        
    @app_commands.command(name='delete_goal', description=f'Delete an immersion goal.')
    @app_commands.checks.has_role("QA Tester")
    async def delete_goal(self, interaction: discord.Interaction):
        
        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private:
            return await interaction.response.send_message(content='You can only log in #immersion-log or DMs.',ephemeral=True)

        store_goal = Set_Goal("goals.db")
        goals = store_goal.get_goals(interaction.user.id)
        if not goals:
            return await interaction.response.send_message(ephemeral=True, content='No goals found. Set goals with ``/set_goal``.')

        store_prod = Store("prod.db")
        beginn = goals[0].created_at
        end = interaction.created_at + timedelta(hours=26)

        relevant_logs = store_prod.get_goal_relevant_logs(interaction.user.id, beginn, end)

        day_dict, date_dict, weekly_dict, monthly_dict = helpers.get_time_relevant_logs(interaction, goals, relevant_logs)
        print(day_dict, date_dict, weekly_dict, monthly_dict)
        goals, goal_message = helpers.get_goal_description(day_dict=day_dict, date_dict=date_dict, weekly_dict=weekly_dict, monthly_dict=monthly_dict, goals=goals, log=False, store=store_goal, interaction=interaction, media_type=None)

        goals_description = []
        raw_goals = store_goal.get_goals(interaction.user.id)

        results = []
        for i, goal in enumerate(zip(goals, raw_goals)):
            results.append((i + 1, goal[0], goal[1]))

        print(results)
        myembed = discord.Embed(title=f'Select a goal to delete:')
        for result in results[0:5]:
            myembed.add_field(name=f'{result[0]}. goal',value=f'{result[1]}', inline=False)
        if len(results) >= 5:
            myembed.set_footer(text="... not all results displayed but you can pick any index.\n"
                               "Pick an index to retrieve a scene next.")
        else:
            myembed.set_footer(text="Pick an index to retrieve a scene next.")
        beginning_index = 0
        end_index = 5
        
        options = []
        for result in results[0:5]:
            item = discord.SelectOption(label=f'{result[0]}')
            options.append(item)
            
        select = Select(min_values = 1, max_values = 1, options=options)   
        async def my_callback(interaction):
            relevant_result = select.view.data[(int(select.values[0])-1) + int(select.view.beginning_index)]
            store_goal.delete_goal(interaction.user.id, relevant_result[2].media_type.value, relevant_result[2].amount, relevant_result[2].span)        
            await interaction.response.edit_message(content='## **Deleted goal.**')

        select.callback = my_callback
        view = MyView(data=results, beginning_index=beginning_index, end_index=end_index)
        
        view.add_item(select)
        await interaction.response.send_message(embed=myembed, view=view, ephemeral=True)

    @tasks.loop(hours=25)
    async def batch_update(self):
        store = Set_Goal("goals.db")
        goals = store.get_all_goals()
        for goal in goals:
            if goal.span == "DAY" or goal.span == "DATE":
                if pytz.utc.localize(datetime.now()) > datetime.strptime(goal.end, "%Y-%m-%d %H:%M:%S.%f%z").replace(tzinfo=pytz.UTC):
                    store.delete_goal(goal.discord_user_id, goal.media_type.value, goal.amount, goal.span)
                    store.delete_completed(goal.discord_user_id, goal.span, goal.amount, goal.media_type.value, goal.text)
                    continue
                else:
                    continue

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Goals_manager(bot))