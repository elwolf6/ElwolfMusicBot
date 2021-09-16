import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from discord_slash import cog_ext
from discord_slash.context import SlashContext

from config import config
from musicbot import utils
from musicbot.audiocontroller import AudioController
from musicbot.utils import guild_to_audiocontroller, guild_to_settings

guild_ids=[246861284069343234]

class General(commands.Cog):
    """ A collection of the commands for moving the bot around in you server.

            Attributes:
                bot: The instance of the bot that is executing the commands.
    """

    def __init__(self, bot):
        self.bot = bot

    # logic is split to uconnect() for wide usage
    ##@commands.command(name='connect', description=config.HELP_CONNECT_SHORT, help=config.HELP_CONNECT_SHORT, aliases=['c'])
    @cog_ext.cog_slash(name="connect", description=config.HELP_CONNECT_SHORT, guild_ids=guild_ids)
    async def _connect(self, ctx: SlashContext):  # dest_channel_name: str
        await self.uconnect(ctx)

    async def uconnect(self, ctx: SlashContext):

        vchannel = await utils.is_connected(ctx)

        if vchannel is not None:
            await ctx.send(config.ALREADY_CONNECTED_MESSAGE)
            return

        current_guild = ctx.guild

        if current_guild is None:
            await ctx.send(config.NO_GUILD_MESSAGE)
            return

        if utils.guild_to_audiocontroller[current_guild] is None:
            utils.guild_to_audiocontroller[current_guild] = AudioController(
                self.bot, current_guild)

        guild_to_audiocontroller[current_guild] = AudioController(
            self.bot, current_guild)
        await guild_to_audiocontroller[current_guild].register_voice_channel(ctx.author.voice.channel)

        await ctx.send("Connected to {} {}".format(ctx.author.voice.channel.name, ":white_check_mark:"))

    ##@commands.command(name='disconnect', description=config.HELP_DISCONNECT_SHORT, help=config.HELP_DISCONNECT_SHORT, aliases=['dc'])
    @cog_ext.cog_slash(name="disconnect", description=config.HELP_DISCONNECT_SHORT, guild_ids=guild_ids)
    async def _disconnect(self, ctx: SlashContext):
        await self.udisconnect(ctx, ctx.guild)

    async def udisconnect(self, ctx: SlashContext, current_guild):

        await utils.guild_to_audiocontroller[current_guild].stop_player()
        await current_guild.voice_client.disconnect(force=True)
        await ctx.send("Disconnected from voice channel. Use '/connect' to rejoin.".format(config.BOT_PREFIX))

    ##@commands.command(name='reset', description=config.HELP_DISCONNECT_SHORT, help=config.HELP_DISCONNECT_SHORT, aliases=['rs', 'restart'])
    @cog_ext.cog_slash(name="reset", description=config.HELP_DISCONNECT_SHORT, guild_ids=guild_ids)
    async def _reset(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if current_guild is None:
            await ctx.send(config.NO_GUILD_MESSAGE)
            return
        await utils.guild_to_audiocontroller[current_guild].stop_player()
        await current_guild.voice_client.disconnect(force=True)

        guild_to_audiocontroller[current_guild] = AudioController(
            self.bot, current_guild)
        await guild_to_audiocontroller[current_guild].register_voice_channel(ctx.author.voice.channel)
        await ctx.send("{} Connected to {}".format(":white_check_mark:", ctx.author.voice.channel.name))

    ##@commands.command(name='ping', description=config.HELP_PING_SHORT, help=config.HELP_PING_SHORT)
    @cog_ext.cog_slash(name="Ping", description="Pong", guild_ids=guild_ids)
    async def _ping(self, ctx):
        await ctx.send("Pong")

def setup(bot):
    bot.add_cog(General(bot))
