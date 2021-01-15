from urllib.parse import urlencode

from .base import CommandBase
from ...constants import REDIRECT_TOKEN_KEY, Route


class Link(CommandBase):
    name = "link"
    description = "Creates a link between wargaming and your discord account"

    async def process(self):
        await self._message.channel.send("Check your private messages to continue.")
        await self.start_link()

    async def start_link(self):
        token = await self._context.link_cache.store_discord_user_id(self._message.author.id)

        redirect_uri = self._context.config.web_base_url + Route.LINK_REDIRECT + "?" + urlencode({REDIRECT_TOKEN_KEY: token})

        url_params = {
            "application_id": self._context.config.wows_token,
            "redirect_uri": redirect_uri,
        }

        url = "https://api.worldoftanks.eu/wot/auth/login/?" + urlencode(url_params)

        await self._message.author.send(f"To link your account follow this url: {url} (the link is valid for 60 minutes)")
