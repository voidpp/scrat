from scrat.models import Link

from .base import CommandBase


class Unlink(CommandBase):
    name = "unlink"
    description = "Removes the link between wargaming and your discord account"

    async def process(self):
        with self._context.db.session_scope() as conn:
            link = conn.query(Link).filter(Link.discord_user_id == self._message.author.id).first()
            if not link:
                await self._message.channel.send("No wargaming account linked.")
                return

            conn.delete(link)
            conn.commit()

        await self._message.channel.send("Unlink done")
