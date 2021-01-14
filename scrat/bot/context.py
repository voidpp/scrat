from dataclasses import dataclass

from wows_api_async import Wows

from scrat.components.config import AppConfig
from scrat.components.database import Database
from scrat.components.link_cache import LinkCache


@dataclass
class Context:
    wows_client: Wows
    link_cache: LinkCache
    db: Database
    config: AppConfig
