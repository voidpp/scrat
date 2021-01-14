from datetime import datetime
from urllib.parse import urlencode

from discord import Member, Embed, Client, Message
from discord.abc import Messageable
from wows_api_async import Wows
from wows_api_async.cache.redis import RedisCache

from scrat.components.config import load
from scrat.components.database import Database
from scrat.components.link_cache import LinkCache
from scrat.constants import Route, REDIRECT_TOKEN_KEY
from scrat.models import Link

config = load()

db = Database(str(config.database))

discord_client = Client()
wows_cache = RedisCache(config.redis)
wows_client = Wows(config.wows_token, wows_cache)

link_cache = LinkCache(config.redis)


@discord_client.event
async def on_connect():
    print("Client connected")
    await wows_cache.connect()


@discord_client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(discord_client))


def get_wows_user_id(discord_user_id: int) -> int:
    with db.session_scope() as conn:
        link = conn.query(Link.wows_user_id).filter(Link.discord_user_id == discord_user_id).first()
        return link.wows_user_id if link else None


async def start_link(author: Member):
    token = await link_cache.store_discord_user_id(author.id)

    redirect_uri = config.web_base_url + Route.LINK_REDIRECT + "?" + urlencode({REDIRECT_TOKEN_KEY: token})

    url_params = {
        "application_id": config.wows_token,
        "redirect_uri": redirect_uri,
    }

    url = "https://api.worldoftanks.eu/wot/auth/login/?" + urlencode(url_params)

    await author.send(f"To link your account follow this url: {url} (the link is valid for 60 minutes)")


async def send_get_last_battle_times(wows_user_id: int, channel: Messageable):
    # TODO: cache account.info (cache expiry!!!!!)
    wows_user = (await wows_client.account.info([wows_user_id]))[wows_user_id]

    user_ships = await wows_client.ships.stats(wows_user_id)
    user_ships.sort(key = lambda s: s.last_battle_time)
    user_ship_id_list = [s.ship_id for s in user_ships]
    ships_data = await wows_client.encyclopedia.ships(user_ship_id_list)

    ship_names = []
    tiers = []
    dates = []

    for ship in user_ships:
        ship_details = ships_data.get(ship.ship_id)
        if not ship_details:
            continue

        if ship_details.tier != 10:
            continue

        ship_names.append(ship_details.name)
        tiers.append(str(ship_details.tier))
        dates.append(datetime.utcfromtimestamp(ship.last_battle_time).strftime('%Y-%m-%d %H:%M:%S'))

    msg = Embed(title = f"Last battle times for {wows_user.nickname}", color = 0x00CC00)
    msg.add_field(name = "Ship name", value = "\n".join(ship_names))
    msg.add_field(name = "Tier", value = "\n".join(tiers))
    msg.add_field(name = "Date", value = "\n".join(dates))

    await channel.send(embed = msg)


@discord_client.event
async def on_message(message: Message):
    if message.author == discord_client.user:
        return

    author: Member = message.author

    # print(message.guild.id, message.guild.name)

    if message.content.startswith('!last-battle-times'):
        wows_user_id = get_wows_user_id(author.id)
        if wows_user_id:
            await send_get_last_battle_times(wows_user_id, message.channel)
        else:
            await message.channel.send("No wargaming account linked. If you want, use the !link command and follow the instructions.")

    if message.content.startswith('!link'):
        # TODO: check if it is already linked
        await message.channel.send("Check your private messages to continue.")
        await start_link(author)

    if message.content.startswith('!unlink'):
        # TODO: check if it is linked yet
        pass


def run():
    discord_client.run(config.discord_token)
