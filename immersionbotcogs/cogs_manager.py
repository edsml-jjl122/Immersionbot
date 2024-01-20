# from sqlite3 import Row
import discord
from discord.ui import Select, View
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import help_text
import datetime, time

start_time = time.time()

class BotManager(commands.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="uptime", description="How long the bot is working.")
    @app_commands.checks.has_role("QA Tester")
    async def uptime(self, interaction: discord.Interaction):

        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private:
            return await interaction.response.send_message(content='You can only log in #immersion-log or DMs.',ephemeral=True)

        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        await interaction.response.send_message(content=f'Current uptime is {text}', ephemeral=True)

    @app_commands.command(name="reload_cog", description="Reloads cogs.")
    @app_commands.checks.has_role("Moderator")
    async def reload_cog(self, interaction: discord.Interaction):
        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private:
            return await interaction.response.send_message(content='You can only log in #immersion-log or DMs.',ephemeral=True)

        my_view = CogSelectView(timeout=1800)
        for cog_name in [extension for extension in self.bot.extensions]:
            cog_button = ReloadButtons(self.bot, label=cog_name)
            my_view.add_item(cog_button)
        await interaction.response.send_message(f"Please select the cog you would like to reload.",
                                                view=my_view,
                                                ephemeral=True)
        
    # @app_commands.command(name="stop", description="Stops cogs.")
    # @app_commands.checks.has_role("Moderator")
    # async def stop(self, interaction: discord.Interaction):
    #     if interaction.command_failed:
    #         await interaction.response.send_message(f'I had a brain fart, try again please.', ephemeral=True)
    #     options = []
    #     for filename in os.listdir("./cogs"):
    #         if filename.endswith(".py"):
    #             item = discord.SelectOption(label=f'cogs.{filename}')
    #             options.append(item)
    #     async def my_callback(interaction):
    #         for cog in select.values:
    #             await self.bot.unload_extension(f"{cog[:-3]}")
    #         selected_values = "\n".join(select.values)
    #         await interaction.response.send_message(f'Unloaded the following cog:\n{selected_values}')

    #     select = Select(min_values = 1, max_values = int(len(options)), options=options)   
    #     select.callback = my_callback
    #     view = View()
    #     view.add_item(select)
    #     await interaction.response.send_message(f'Please select the cog you would like to reload.', view=view)
        
    @app_commands.command(name="sync", description="Syncs slash commands to the guild.")
    @app_commands.checks.has_role("Moderator")
    async def sync(self, interaction: discord.Interaction):
        await self.bot.tree.sync()
        await interaction.response.send_message(f'Synced commands to guild with id {617136488840429598}.')
    
    @app_commands.command(name='load', description='Loads cogs.')
    @app_commands.checks.has_any_role("Moderator")
    async def load(self, interaction: discord.Interaction,):
        my_view = CogSelectView(timeout=1800)
        for cog_name in [extension for extension in os.listdir('immersionbotcogs/') if extension.endswith('.py')]:
            cog_button = LoadButtons(self.bot, label=cog_name)
            my_view.add_item(cog_button)
        await interaction.response.send_message(f"Please select the cog you would like to reload.",
                                                view=my_view,
                                                ephemeral=True)
        
    @app_commands.command(name='clear_global_commands', description='Clears all global commands.')
    @app_commands.checks.has_any_role("Moderator")
    async def clear_global_commands(self, interaction: discord.Interaction):
        self.bot.tree.clear_commands(guild=interaction.guild)
        await interaction.response.send_message("Cleared global commands.")

    @app_commands.command(name='help', description='Explains commands.')
    async def help(self, interaction: discord.Interaction):
        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private:
            return await interaction.response.send_message(content='You can only log in #immersion-log or DMs.',ephemeral=True)
            
        my_view = MyView(timeout=1800)
        for cog_name in [extension for extension in self.bot.extensions] + ["immersionbotcogs.BOT"]:
            if cog_name == "immersionbotcogs.cogs_manager":
                continue
            if cog_name == "immersionbotcogs.set_goal_media":
                continue
            if cog_name == "immersionbotcogs.set_goal_points":
                cog_name = "immersionbotcogs.set_goal"
            if cog_name == "immersionbotcogs.goals_manager":
                continue
            cog_button = ExplainButtons(self.bot, label=cog_name[17:])
            my_view.add_item(cog_button)

        await interaction.response.send_message(f"Please select the command you want to be explained.",
                                                view=my_view,
                                                ephemeral=True)
        
    
    # @app_commands.command(name='load', description='Loads cogs.')
    # @app_commands.checks.has_any_role("Moderator")
    # async def load(self, interaction: discord.Interaction, *, cog: str):
    #     await interaction.response.defer()
    #     try:
    #         await self.bot.load_extension(cog)
    #     except Exception as e:
    #         await interaction.edit_original_response(content=f'**`ERROR:`** {type(e).__name__} - {e}')
    #     else:
    #         await interaction.edit_original_response(content='**`SUCCESS`**')
    
    # @app_commands.command(name='check_cogs', description='Checks the status on cogs.')
    # @app_commands.checks.has_any_role("Moderator")
    # async def check_cogs(self, interaction: discord.Interaction, *, cog_name: str):
    #     try:
    #         await self.bot.load_extension(f"cogs.{cog_name}")
    #     except commands.ExtensionAlreadyLoaded:
    #         await interaction.response.send_message(ephemeral=True, content="Cog is loaded")
    #     except commands.ExtensionNotFound:
    #         await interaction.response.send_message(ephemeral=True, content="Cog not found")
    #     else:
    #         await interaction.response.send_message(ephemeral=True, content="Cog is unloaded")
    #         await self.bot.unload_extension(ephemeral=True, content=f"cogs.{cog_name}")


class MyView(discord.ui.View):
    def __init__(self, *, timeout: float = 1800):
        super().__init__(timeout=timeout)

class ExplainButtons(discord.ui.Button):

    def __init__(self, bot: commands.Bot, label):
        super().__init__(label=label)
        self.bot = bot

    async def callback(self, interaction):
        command = self.label
        await interaction.response.send_message(f'{help_text.HELP[command]}', ephemeral=True)
        await asyncio.sleep(25)
        await interaction.delete_original_response()

class CogSelectView(discord.ui.View):

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator

class ReloadButtons(discord.ui.Button):

    def __init__(self, bot: commands.Bot, label):
        super().__init__(label=label)
        self.bot = bot

    async def callback(self, interaction):
        cog_to_reload = self.label 
        await self.bot.reload_extension(cog_to_reload)
        await interaction.response.send_message(f"Reloaded the following cog: {cog_to_reload}")
        print(f"Reloaded the following cog: {cog_to_reload}")
        await asyncio.sleep(10)
        await interaction.delete_original_response()
        
class LoadButtons(discord.ui.Button):

    def __init__(self, bot: commands.Bot, label):
        super().__init__(label=label)
        self.bot = bot

    async def callback(self, interaction):
        cog_to_reload = self.label
        print(cog_to_reload, type(cog_to_reload))
        cog_to_reload = await self.bot.get_cog(cog_to_reload)
        await self.bot.load_extension(cog_to_reload)
        await interaction.response.send_message(f"Loaded the following cog: {cog_to_reload}")
        print(f"Loaded the following cog: {cog_to_reload}")
        await asyncio.sleep(10)
        await interaction.delete_original_response()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BotManager(bot))
