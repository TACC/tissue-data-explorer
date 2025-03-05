import json

import dash
import dash_bootstrap_components as dbc
import plotly
from dash import dcc, html
from PIL import Image
import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
import app
from pages.ocpage import make_tab_content, update_pic
from pages.constants import FILE_DESTINATION as FD


def test_make_tab_content():
    # no slider, no tabs
    card1 = dbc.Card(
        [
            dbc.Tabs([], id="tabs", active_tab="channel-1", style={"display": "none"}),
            dbc.CardBody(
                [html.Div(id="si-slider-output", className="custom-slicer-div")]
            ),
        ],
        class_name="slicer-card",
    )

    card1j = json.loads(json.dumps(card1, cls=plotly.utils.PlotlyJSONEncoder))
    test1 = make_tab_content(slider=False, points=0, channels=1)
    test1j = json.loads(json.dumps(test1, cls=plotly.utils.PlotlyJSONEncoder))
    assert card1j == test1j

    # tabs but no slider
    card2 = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                        dbc.Tab(label="Channel 1", tab_id="channel-1"),
                        dbc.Tab(label="Channel 2", tab_id="channel-2"),
                    ],
                    id="tabs",
                    active_tab="channel-1",
                )
            ),
            dbc.CardBody(
                [html.Div(id="si-slider-output", className="custom-slicer-div")]
            ),
        ],
        class_name="slicer-card",
    )
    card2j = json.loads(json.dumps(card2, cls=plotly.utils.PlotlyJSONEncoder))
    test2 = make_tab_content(slider=False, points=0, channels=2)
    test2j = json.loads(json.dumps(test2, cls=plotly.utils.PlotlyJSONEncoder))
    assert card2j == test2j

    # tabs and slider
    card3 = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                        dbc.Tab(label="Channel 1", tab_id="channel-1"),
                        dbc.Tab(label="Channel 2", tab_id="channel-2"),
                    ],
                    id="tabs",
                    active_tab="channel-1",
                )
            ),
            dbc.CardBody(
                [
                    html.Div(id="si-slider-output", className="custom-slicer-div"),
                    dcc.Slider(min=1, max=2, step=1, value=1, id="si-slider"),
                ]
            ),
        ],
        class_name="slicer-card",
    )
    card3j = json.loads(json.dumps(card3, cls=plotly.utils.PlotlyJSONEncoder))
    test3 = make_tab_content(slider=True, points=2, channels=2)
    test3j = json.loads(json.dumps(test3, cls=plotly.utils.PlotlyJSONEncoder))
    assert card3j == test3j

    # slider but no tabs
    card4 = dbc.Card(
        [
            dbc.Tabs([], id="tabs", active_tab="channel-1", style={"display": "none"}),
            dbc.CardBody(
                [
                    html.Div(id="si-slider-output", className="custom-slicer-div"),
                    dcc.Slider(min=1, max=2, step=1, value=1, id="si-slider"),
                ]
            ),
        ],
        class_name="slicer-card",
    )
    card4j = json.loads(json.dumps(card4, cls=plotly.utils.PlotlyJSONEncoder))
    test4 = make_tab_content(slider=True, points=2, channels=1)
    test4j = json.loads(json.dumps(test4, cls=plotly.utils.PlotlyJSONEncoder))
    assert card4j == test4j


def test_update_pic():
    data = {
        "block": "S1-1",
        "iset": "S1-1-1",
        "cat": "Optical Clearing",
        "file": "S1-1-1.tif",
        "basefile": "S1-1-1",
        "slices": "5",
        "channels": "1",
        "height": 600,
        "width": 600,
    }
    # no tab, no slider
    pic = Image.open(f"{FD["sci-images"]}/S1-1/S1-1-1/S1-1-1_C00000.png")
    test1 = update_pic(None, False, data)
    assert isinstance(test1, dash._callback.NoUpdate)
    case2 = html.Img(
        src=pic,
        className="custom-slicer-img solo-slicer-img",
        style={"max-height": data["height"], "max-width": data["width"]},
    )
    case2j = json.loads(json.dumps(case2, cls=plotly.utils.PlotlyJSONEncoder))
    test2 = update_pic(None, 1, data)
    test2j = json.loads(json.dumps(test2, cls=plotly.utils.PlotlyJSONEncoder))
    assert isinstance(test2, html.Img)
    assert case2j == test2j

    data = {
        "block": "S1-7",
        "iset": "S1-7-1",
        "cat": "Optical Clearing",
        "file": "S1-7-1.tif",
        "basefile": "S1-7-1",
        "slices": "10",
        "channels": "2",
        "height": 500,
        "width": 1000,
    }

    # tab and slider
    pic2 = Image.open(f"{FD["sci-images"]}/S1-7/S1-7-1/S1-7-1_C00000.png")
    case3 = html.Img(
        src=pic2,
        className="custom-slicer-img solo-slicer-img",
        style={"max-height": data["height"], "max-width": data["width"]},
    )
    case3j = json.loads(json.dumps(case3, cls=plotly.utils.PlotlyJSONEncoder))
    test3 = update_pic("channel-1", 1, data)
    test3j = json.loads(json.dumps(test3, cls=plotly.utils.PlotlyJSONEncoder))
    assert case3j == test3j
