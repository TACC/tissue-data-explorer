import dash_bootstrap_components as dbc
from dash import (
    Dash,
    dcc,
    html,
    page_container,
    no_update,
    Input,
    Output,
    State,
)
import json
import os
from flask import Flask, session
import logging
import socket
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_user,
)
from dotenv import load_dotenv
from config_components import ui
from components import header

load_dotenv()

title = header.get_title() + " Configuration"


# layout function
def serve_layout():
    return html.Div(
        children=[
            dcc.Location(id="config-url"),
            header.make_header("config"),
            html.Main(
                dbc.Container(
                    page_container,
                    id="config-content-div",
                    class_name="main-div",
                )
            ),
            header.footer,
        ]
    )


# Flask setup
server = Flask(__name__)
server.config["MAX_LOGIN_ATTEMPTS"] = 3

# Dash setup
app = Dash(
    __name__,
    server=server,
    use_pages=True,
    prevent_initial_callbacks="initial_duplicate",
    suppress_callback_exceptions=True,
    title=title,
    external_stylesheets=[dbc.themes.LUMEN, dbc.icons.FONT_AWESOME],
)

ACCOUNTS = json.loads(os.getenv("ACCOUNTS"))

# Security settings
server.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))
server.config["SESSION_COOKIE_SECURE"] = True
server.config["SESSION_HTTPONLY"] = True

# Login configuration
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"
login_manager.session_protection = "strong"


class User(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    return User(username)


app.layout = serve_layout


@app.callback(
    Output("auth-link", "children"),
    Input("config-url", "pathname"),
)
def update_authentication_status(_):
    if current_user.is_authenticated:
        return html.A(
            [
                html.I(
                    id="auth-icon",
                    className="fa-solid fa-circle-user auth-nav__icon",
                ),
                "Log out",
            ],
            href="/logout",
            className="nav-link",
        )
    return html.A(
        [
            html.I(
                id="auth-icon",
                className="fa-solid fa-circle-user auth-nav__icon",
            ),
            "Log in",
        ],
        href="/login",
        className="nav-link",
    )


@app.callback(
    Output("config-url", "href"),
    Output("output-state", "children"),
    Input("login-button", "n_clicks"),
    State("uname-box", "value"),
    State("pwd-box", "value"),
    prevent_initial_call=True,
)
def auth_button_click(n_clicks_login, username, password):
    if "login_attempts" in session:
        if session["login_attempts"] >= server.config["MAX_LOGIN_ATTEMPTS"]:
            return no_update, ui.failure_alert(
                "Your account has been locked. Please try again later.",
            )
        else:
            session["login_attempts"] += 1
    else:
        session["login_attempts"] = 1
    if n_clicks_login > 0:
        if username not in ACCOUNTS:
            return no_update, ui.failure_alert("Invalid username")
            # return no_update, html.P("Invalid username", className="auth-form__error")
        if ACCOUNTS[username] == password:
            login_user(User(username))
            return "/", ""
        return no_update, ui.failure_alert("Incorrect password")
    else:
        return no_update, no_update


if __name__ == "__main__":
    format_str = f"[%(asctime)s {socket.gethostname()}] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s"
    logging.basicConfig(level="DEBUG", format=format_str)
    app.run_server(host="0.0.0.0", port="8040", debug=True)
