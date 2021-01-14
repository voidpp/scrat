import logging
import logging.config

from configpp.soil import Config
from configpp.tree import Tree, Settings, DatabaseLeaf

logger = logging.getLogger(__name__)

tree = Tree(Settings(
    convert_underscores_to_hypens = True,
    convert_camel_case_to_hypens = True,
))


@tree.root()
class AppConfig:
    database: DatabaseLeaf
    redis: str
    logger: dict
    discord_token: str
    wows_token: str
    web_base_url: str


def load() -> AppConfig:
    config_loader = Config('scrat.yaml')

    if not config_loader.load():
        raise Exception("config not loaded")

    app_config: AppConfig = tree.load(config_loader.data)

    logging.config.dictConfig(app_config.logger)

    logger.debug("config loaded from %s", config_loader.path)

    return app_config
