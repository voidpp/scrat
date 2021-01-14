import logging
from pathlib import Path

from flask import Flask, render_template, request, redirect

from scrat.components.config import load
from scrat.components.database import Database
from scrat.components.link_cache import LinkCache
from scrat.constants import Route, REDIRECT_TOKEN_KEY
from scrat.models import Link

config = load()

app_root_folder = Path(__file__).parent

app = Flask("scrat-web",
            template_folder = app_root_folder / "templates",
            static_folder = str(app_root_folder / "static"),
            )

db = Database(str(config.database))
link_cache = LinkCache(config.redis)

logger = logging.getLogger(__name__)

error_messages = {
    "already_linked": "Already linked",
    "auth_error": "Auth error",
}


@app.route("/")
def index():
    return render_template("index.jinja2")


@app.route(Route.LINK_SUCCESS, strict_slashes = False)
def link_success():
    return render_template("link_success.jinja2")


@app.route(Route.LINK_ERROR, strict_slashes = False)
def link_error():
    return render_template("link_error.jinja2", message = error_messages.get(request.args.get("msg")))


def error(type_: str):
    return redirect(Route.LINK_ERROR + f"?msg={type_}")


@app.route(Route.LINK_REDIRECT, strict_slashes = False)
def link_redirect():
    logger.debug("link-redirect args: %s", request.args)
    status = request.args.get("status")
    if status != "ok":
        return error("auth_error")

    with db.session_scope() as conn:
        wows_user_id = int(request.args["account_id"])
        if conn.query(Link).filter(Link.wows_user_id == wows_user_id).count():
            return error("already_linked")

        token = request.args[REDIRECT_TOKEN_KEY]
        discord_user_id = link_cache.get_discord_user_id(token)
        conn.add(Link(wows_user_id = wows_user_id, discord_user_id = discord_user_id))
        conn.commit()

    return redirect("/link-success")
