import os

import dash
import dash_bootstrap_components as dbc
from dash import CeleryManager, DiskcacheManager
from flask import Flask

if "REDIS_URL" in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    print("Using REDIS_URL: ", os.environ["REDIS_URL"])

    from celery import Celery

    celery_broker = Celery(
        __name__, broker=os.environ["REDIS_URL"], backend=os.environ["REDIS_URL"]
    )
    background_callback_manager = CeleryManager(celery_broker)

else:
    # Hard coded Redis url for non-production apps when developing locally
    REDIS_URL = "redis://127.0.0.1:6379"
    print(
        "No REDIS_URL environment variable.\nUsing ", REDIS_URL, " (hard coded) instead"
    )

    from celery import Celery

    celery_broker = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)
    background_callback_manager = CeleryManager(celery_broker)

FONT_AWESOME = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
)


server = Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    title="DysRegNet",
    external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME],
    requests_pathname_prefix=os.getenv("SUBDOMAIN", "/"),
    background_callback_manager=background_callback_manager,
    use_pages=True,
)

app.config.suppress_callback_exceptions = True

app.layout = dbc.Container(
    [
        dbc.NavbarSimple(
            [
                dbc.NavItem(dbc.NavLink(page["name"], href=page["path"]))
                for page in dash.page_registry.values()
            ],
            brand="DysRegNet",
            brand_href="#",
            className="navbar navbar-light bg-light mx-0",
            style={"margin-top": "10px", "border-radius": "10px"},
        ),
        dash.page_container,
    ],
    fluid=True,
)


if __name__ == "__main__":
    debug = os.getenv("DEBUG", "True") == "True"
    app.run_server(debug=debug)
