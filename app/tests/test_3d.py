import json
import dash_bootstrap_components as dbc
import plotly
import pytest
from dash import dcc, html
import numpy as np
import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
import app
from pages.model3d import (
    display_click_data,
    make_mesh_data,
    make_mesh_fig,
    make_mesh_settings,
    read_obj,
)
from pages.constants import FILE_DESTINATION as FD


def test_read_obj():
    FD["obj-files"]["volumes"]
    vertices, faces = read_obj(f"{FD["obj-files"]["volumes"]}/sphere.obj")
    assert vertices.shape == (482, 3)
    assert faces.shape == (960, 3)

    vertices, faces = read_obj(f"{FD["obj-files"]["volumes"]}/S1_Sphere_Lower_S1-1.obj")
    assert vertices.shape == (8, 3)
    assert faces.shape == (12, 3)

    with pytest.raises(IndexError):
        vertices, faces = read_obj(f"{FD["obj-files"]["summary"]}/obj-files.csv")


def test_make_mesh_settings():
    vertices, faces = read_obj(f"{FD["obj-files"]["volumes"]}/S1_Sphere_Lower_S1-1.obj")
    settings1 = make_mesh_settings(
        vertices,
        faces,
        "S1-1",
        color="cyan",
        opacity=1,
    )

    assert settings1[0]["color"] == "cyan"
    assert settings1[0]["opacity"] == 1

    vertices, faces = read_obj(f"{FD["obj-files"]["volumes"]}/S1_Sphere_Lower_S1-4.obj")
    settings2 = make_mesh_settings(
        vertices,
        faces,
        "S1-4",
        color="#ED780B",
        opacity=0.5,
    )

    y_values = np.array([-10, -10, 0, 0, -10, -10, 0, 0])
    z_values = np.array([-10, -5, -10, -5, -10, -5, -10, -5])

    assert settings2[0]["color"] == "#ED780B"
    assert settings2[0]["opacity"] == 0.5
    assert np.array_equal(settings2[0]["y"], y_values) is True
    assert np.array_equal(settings2[0]["z"], z_values) is True

    settings3 = make_mesh_settings(
        vertices, faces, "S1-4", x_map="x", y_map="z", z_map="y"
    )
    assert np.array_equal(settings3[0]["y"], z_values) is True
    assert np.array_equal(settings3[0]["z"], y_values) is True


def test_make_mesh_data():
    test1 = make_mesh_data(
        "S1-4", f"{FD["obj-files"]["volumes"]}/S1_Sphere_Lower_S1-4.obj"
    )
    assert test1[0]["name"] == "S1-4"

    test2 = make_mesh_data(
        "S1-6", f"{FD["obj-files"]["volumes"]}/S1_Sphere_Middle_S1-6.obj"
    )
    assert test2[0]["name"] == "S1-6"


def test_make_mesh_fig():
    fig1 = make_mesh_fig("S1")
    assert len(fig1["data"]) == 9
    assert fig1["layout"]["height"] == 500


def test_display_click_data():
    click1 = [
        {
            "points": [
                {
                    "x": -392,
                    "y": 1749.50244140625,
                    "z": 746,
                    "curveNumber": 0,
                    "pointNumber": 52662,
                    "i": 28916,
                    "j": 28769,
                    "k": 28768,
                    "bbox": {
                        "x0": 539.0667184592023,
                        "x1": 539.0667184592023,
                        "y0": 401.4491349814796,
                        "y1": 401.4491349814796,
                    },
                }
            ]
        }
    ]
    layout1 = json.loads(
        json.dumps(display_click_data(click1), cls=plotly.utils.PlotlyJSONEncoder)
    )
    testlayout1 = [
        dbc.CardHeader("Block Data"),
        dbc.CardBody(
            [
                html.P("Click on a block to view available datasets"),
            ],
        ),
    ]
    test1 = json.loads(json.dumps(testlayout1, cls=plotly.utils.PlotlyJSONEncoder))
    assert layout1 == test1

    click2 = [
        {
            "points": [
                {
                    "x": -10,
                    "y": 0,
                    "z": -5,
                    "curveNumber": 4,
                    "pointNumber": 0,
                    "i": 0,
                    "j": 1,
                    "k": 3,
                    "bbox": {
                        "x0": 389.40599700379744,
                        "x1": 389.40599700379744,
                        "y0": 318.6925748500662,
                        "y1": 318.6925748500662,
                    },
                }
            ]
        }
    ]
    layout2 = json.loads(
        json.dumps(display_click_data(click2), cls=plotly.utils.PlotlyJSONEncoder)
    )
    testlayout2 = [
        dbc.CardHeader("Block S1-7", class_name="card-title"),
        dbc.CardBody(
            [
                html.P("Anatomical region: Middle"),
                html.P(
                    [
                        dcc.Link(
                            "View scientific images",
                            href="/scientific-images-list/S1-7",
                        )
                    ]
                ),
            ]
        ),
    ]
    test2 = json.loads(json.dumps(testlayout2, cls=plotly.utils.PlotlyJSONEncoder))
    assert layout2 == test2
