from dash import html, register_page, dcc
import dash_bootstrap_components as dbc


register_page(__name__, title="Log in")

layout = html.Div(
    [
        dcc.Location(id="config-url"),
        html.Div(
            [
                html.H2("Log In"),
                html.Div(children="", id="output-state"),
                html.P(
                    "Please log in to use the application",
                ),
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(
                                [
                                    dbc.Label("Username", html_for="uname-box"),
                                    dbc.Input(
                                        type="text",
                                        id="uname-box",
                                        className="auth-form__field",
                                    ),
                                ],
                                className="c-form__field has-required",
                            ),
                            html.Div(
                                [
                                    dbc.Label("Password", html_for="pwd-box"),
                                    dbc.Input(
                                        type="password",
                                        id="pwd-box",
                                        className="auth-form__field",
                                    ),
                                ],
                                className="c-form__field has-required",
                            ),
                            html.Div(
                                dbc.Button(
                                    children="Login",
                                    n_clicks=0,
                                    type="submit",
                                    id="login-button",
                                    color="primary",
                                    class_name="form-button",
                                ),
                                className="button-div",
                            ),
                        ]
                    ),
                    class_name="form-card",
                ),
            ],
            className="c-form c-form--login",
        ),
        html.Br(),
    ]
)
