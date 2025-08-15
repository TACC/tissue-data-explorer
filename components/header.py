import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc

# This import is reported as incorrect in the editor, but is correct in the
# Docker container because this folder is copied into each of the app folders
from pages.constants import FILE_DESTINATION as FD


def get_title():
    labels = pd.read_csv(FD["title"]["publish"])
    return labels.at[0, "title"]


def set_nav(page):
    if page == "config":
        return dbc.Col(
            [
                html.Div(id="auth-link"),
            ],
            className="auth-nav",
            id="auth-nav",
            width="auto",
        )
    elif page == "app":
        return dbc.Col(
            [
                dbc.NavbarToggler(
                    id="navbar-toggler",
                    n_clicks=0,
                ),
                dbc.Collapse(
                    dbc.Nav(
                        id="internal-links",
                        pills=True,
                        horizontal="start",
                        navbar=True,
                    ),
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ],
            width=2,
            md=3,
        )


def make_header(page):
    title = get_title()
    if page == "config":
        page_title = title + " Configuration"
    else:
        page_title = title
    return html.Header(
        dbc.Container(
            [
                dbc.Navbar(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Link(
                                            html.Img(
                                                src="../assets/magnifying-glass-chart-solid.svg",
                                                className="text-light header-img",
                                            ),
                                            href="/",
                                            className="title-link",
                                        ),
                                        html.H1(
                                            dcc.Link(
                                                [page_title],
                                                href="/",
                                                className="title-link",
                                            ),
                                            className="bg-primary text-light title",
                                        ),
                                    ],
                                    width=True,
                                    class_name="title-group",
                                ),
                                set_nav(page),
                            ],
                            justify="between",
                            class_name="w-100",
                            align="center",
                        ),
                    ],
                    class_name="bg-primary text-light w-100",
                    color="primary",
                    dark=True,
                    sticky="top",
                ),
                html.Div(id="breadcrumb"),
            ],
            fluid=True,
            class_name="px-0",
        ),
    )


footer_text = "\u00a9" + " 2024, Texas Advanced Computing Center"
footer = html.Footer(footer_text)
