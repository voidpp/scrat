import logging
from datetime import datetime

from pydantic import BaseModel
from tabulate import tabulate

from .base import CommandBase
from ...models import Link

logger = logging.getLogger(__name__)


class LastBattleTimesInput(BaseModel):
    user: str = None
    tier: int = None
    limit: int = 20
    ship: str = None


class LastBattleTimes(CommandBase[LastBattleTimesInput]):
    name = "last-battle-times"
    input_validator = LastBattleTimesInput

    async def get_user_from_wows(self) -> int:
        users = await self._context.wows_client.account.list_(self.args.user)
        logger.debug("Search users %s: matches: %s", self.args.user, users)

        if not users:
            await self._message.channel.send("User not found.")
            return 0

        exact_matches = list(filter(lambda u: u.nickname.lower() == self.args.user.lower(), users))

        if exact_matches:
            return users[0].account_id

        if len(users) > 10:
            await self._message.channel.send(f"Too many match ({len(users)})")
            return 0

        await self._message.channel.send("Too many match, pls choose from these: " + ', '.join([u.nickname for u in users]))
        return 0

    async def get_linked_user(self) -> int:
        with self._context.db.session_scope() as conn:
            link = conn.query(Link.wows_user_id).filter(Link.discord_user_id == self._message.author.id).first()
            if not link:
                await self._message.channel.send("No wargaming account linked. "
                                                 "If you want, use the !link command and follow the instructions.")
                return 0

            return link.wows_user_id

    async def get_wows_user_id(self) -> int:
        if self.args.user:
            return await self.get_user_from_wows()
        else:
            return await self.get_linked_user()

    async def process(self):
        wows_user_id = await self.get_wows_user_id()
        if wows_user_id:
            await self.send_last_battle_times(wows_user_id)

    async def send_last_battle_times(self, wows_user_id: int):
        # TODO: cache account.info (cache expiry!!!!!)
        wows_user = (await self._context.wows_client.account.info([wows_user_id]))[wows_user_id]

        user_ships = await self._context.wows_client.ships.stats(wows_user_id)
        user_ships.sort(key = lambda s: s.last_battle_time)
        user_ship_id_list = [s.ship_id for s in user_ships]
        ships_data = await self._context.wows_client.encyclopedia.ships(user_ship_id_list)

        table_rows = []

        for ship in user_ships:
            ship_details = ships_data.get(ship.ship_id)
            if not ship_details:
                continue

            if self.args.tier and self.args.tier != ship_details.tier:
                continue

            if ship_details.name.startswith("["):
                continue

            if self.args.ship and not ship_details.name.lower().startswith(self.args.ship.lower()):
                continue

            table_rows.append([
                ship_details.name,
                str(ship_details.tier),
                str(ship_details.type),
                datetime.utcfromtimestamp(ship.last_battle_time).strftime('%Y-%m-%d %H:%M:%S'),
            ])

            table_rows = table_rows[-min(self.args.limit, 20):]

        headers = [
            "Ship name",
            "Tier",
            "Type",
            "Date",
        ]

        table = tabulate(table_rows, headers = headers, tablefmt = "psql")
        message = f"Last battles of {wows_user.nickname}" \
                  f"\n```\n{table}\n```"

        await self._message.channel.send(message)
