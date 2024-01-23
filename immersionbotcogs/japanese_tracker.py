from discord.ext import commands
from sql import Set_jp
import helpers
import re
from constants import ALLOWED_CHANNELS

jp_REGEX = re.compile(r"[一-龠ぁ-ゔァ-ヴーａ-ｚＡ-Ｚ０-９々〆〤ヶ]+|[ぁ-ゔ]+|[ァ-ヴー]+|[々〆〤ヶ]+[]+] +/u")

class Japanese_tracker(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(617136488840429598)

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = message.channel
        if channel.id in ALLOWED_CHANNELS:
            return
        
        if message.author.bot:
            return
        
        if not message.content:
            return
        
        characters = helpers.check_japanese_contents(message.content, jp_REGEX)
        if characters:
            store = Set_jp("japanese.db")
            store.log_jp(message.author.id, message.channel.id, "JAPANESE", message.content, characters, message.created_at)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Japanese_tracker(bot))
