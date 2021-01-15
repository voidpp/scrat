from httpx import AsyncClient

from .base import CommandBase


class OnlinePlayers(CommandBase):
    name = "online-players"
    description = "The number of online players on the EU server."

    async def process(self):
        url = "https://api.worldoftanks.eu/wgn/servers/info/"
        params = {
            "application_id": self._context.config.wows_token,
            "game": "wows",
            "fields": "players_online",
        }
        async with AsyncClient() as http_client:
            resp = await http_client.get(url, params = params)

            data = resp.json()

            await self.send(str(data["data"]["wows"][0]["players_online"]))
