import discord
import os
import keep_alive
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

from config import config
from musicbot.audiocontroller import AudioController
from musicbot.settings import Settings
from musicbot import utils
from musicbot.utils import guild_to_audiocontroller, guild_to_settings

from musicbot.commands.general import General


initial_extensions = ['musicbot.commands.music',
                      'musicbot.commands.general', 'musicbot.plugins.button']
bot = commands.Bot(command_prefix=config.BOT_PREFIX, pm_help=True, case_insensitive=True)
slash = SlashCommand(bot, sync_commands=False)

if __name__ == '__main__':

    config.ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    config.COOKIE_PATH = config.ABSOLUTE_PATH + config.COOKIE_PATH

    if config.BOT_TOKEN == "":
        print("Error: No bot token!")
        exit

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)


@bot.event
async def on_ready():
    print(config.STARTUP_MESSAGE)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Music, type /help"))

    for guild in bot.guilds:
        await register(guild)
        print("Joined {}".format(guild.name))

    print(config.STARTUP_COMPLETE_MESSAGE)


@bot.event
async def on_guild_join(guild):
    print(guild.name)
    await register(guild)


async def register(guild):

    guild_to_settings[guild] = Settings(guild)
    guild_to_audiocontroller[guild] = AudioController(bot, guild)

    vc_channels = guild.voice_channels
    await guild.me.edit(nick=guild_to_settings[guild].get('default_nickname'))

keep_alive.keep_alive()
bot.run(config.BOT_TOKEN, bot=True, reconnect=True)
