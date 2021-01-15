import logging

from discord import Client, Message
from wows_api_async import Wows
from wows_api_async.cache.redis import RedisCache

from scrat.bot.commands.unlink import Unlink
from scrat.components.argument_parser import GentleArgumentParserError
from scrat.components.config import load
from scrat.components.database import Database
from scrat.components.link_cache import LinkCache
from .commands.base import COMMAND_PREFIX, CommandBase
from .commands.command_list import CommandList
from .commands.last_battle_times import LastBattleTimes
from .commands.link import Link
from .context import Context

config = load()

db = Database(str(config.database))

discord_client = Client()
wows_cache = RedisCache(config.redis)
wows_client = Wows(config.wows_token, wows_cache)

link_cache = LinkCache(config.redis)

context = Context(wows_client, link_cache, db, config)

logger = logging.getLogger(__name__)


# move out the event handlers too? inherit from discord.Client


@discord_client.event
async def on_connect():
    logger.info("Client connected")
    await wows_cache.connect()


@discord_client.event
async def on_ready():
    logger.info('We have logged in as %s', discord_client.user)


commands: list[type[CommandBase]] = [
    LastBattleTimes,
    Link,
    Unlink,
    CommandList,
]

CommandList.commands = commands


@discord_client.event
async def on_message(message: Message):
    if message.author == discord_client.user:
        return

    for command in commands:
        if not message.content.startswith(COMMAND_PREFIX + command.name):
            continue

        logger.info("Command: %s, server: %s, author: %s", command.name, message.guild.name, message.author.name)

        handler = command(message, context)

        try:
            handler.parse_command()
        except GentleArgumentParserError as e:
            await message.channel.send(str(e))
        else:
            await handler.process()

        break


def run():
    discord_client.run(config.discord_token)
