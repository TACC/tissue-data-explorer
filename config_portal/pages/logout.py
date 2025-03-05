from dash import Input, Output, callback, dcc, html, no_update, register_page
import dash_bootstrap_components as dbc

from flask_login import current_user, logout_user

register_page(__name__, title="Log out")

layout = html.Div(
    [
        dcc.Location(id="config-url"),
        html.H2("Log Out"),
        html.P(
            "Click the button to log out",
        ),
        html.Div(
            [
                dcc.Link(
                    dbc.Button(
                        children="Log out",
                        n_clicks=0,
                        type="submit",
                        id="logout-button",
                    ),
                    id="logout-link",
                    href="/login",
                )
            ],
            className="button-div",
        ),
    ],
)


@callback(
    Output("logout-link", "href"),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True,
)
def search(n_clicks):
    if current_user.is_authenticated:
        logout_user()
        return "/login"
    else:
        return no_update
