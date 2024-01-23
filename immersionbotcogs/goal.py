import discord
from discord.ext import commands
from datetime import timedelta
from datetime import timedelta
from discord import app_commands
from sql import Set_Goal, Store
import time
import helpers

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
