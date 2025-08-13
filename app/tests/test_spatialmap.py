import pandas as pd
import numpy as np
import pytest
import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
import app
from pages.spatialmap import (
    make_defaults,
    make_axes,
    make_layers,
    load_data,
    update_fig,
    make_image_layers,
    get_colorscale,
    get_all_images,
)
from pages.ui import make_image_layer_fig

D_PROTEIN = "CYB5A"
D_SCHEME = "jet"
D_OPACITY = 0.4
D_LAYER = "All"

page_info, defaults, layers, image_layers, cat_opts, value_info, axes, downloads = (
    load_data("S1-12")
)


def test_make_defaults():
    range_data = {
        "CYB5A": [0, 1, True],
        "ALB": [0, 1, False],
    }
    range_df = pd.DataFrame(data=range_data, index=["Min", "Max", "Default"])
    expected = {
        "d_scheme": "haline",
        "d_layer": "All",
        "i_layer": "All",
        "d_category": "All",
        "d_value": "CYB5A",
    }
    assert make_defaults(range_df) == expected


def test_make_axes():
    measurements = {
        "X Min": [0],
        "X Max": [3],
        "X Size": [1],
        "Y Min": [0],
        "Y Max": [3],
        "Y Size": [1],
        "Z Min": [0],
        "Z Max": [3],
        "Z Size": [1],
    }
    df = pd.DataFrame(data=measurements)
    expected_axes = {"X": [0, 1, 2, 3], "Y": [0, 1, 2, 3], "Z": [0, 1, 2, 3]}
    assert make_axes(df) == expected_axes


def test_make_layers():
    z_axis = [0, 1, 2, 3]
    expected_layers = ["All", "Layer 1", "Layer 2", "Layer 3"]
    assert make_layers(z_axis) == expected_layers


def test_make_image_layers():
    # make_image_layers(df: pd.DataFrame, block)
    data = {"Block": ["A", "A", "B"]}
    df = pd.DataFrame(data=data)
    a_expected_layers = ["All", "Image 1", "Image 2"]
    b_expected_layers = ["All", "Image 1"]

    assert make_image_layers(df, "A") == a_expected_layers
    assert make_image_layers(df, "B") == b_expected_layers


def test_get_colorscale():
    expected_scale = [
        [np.float64(0.0), "rgb(255,0,0)"],
        [np.float64(0.67), "rgb(0,0,255)"],
        [np.float64(0.99), "rgb(0,255,0)"],
        [np.float64(1.0), "rgb(255,255,255)"],
    ]
    assert get_colorscale("channel_split") == expected_scale


def test_load_data():
    page_info, defaults, layers, image_layers, cat_opts, value_info, axes, downloads = (
        load_data("S1-12")
    )
    expected_page_info = {
        "Block": "S1-12",
        "Title": "S1-12 Proteomics",
        "Description": "These charts show a 3D proteome mapping of a tissue sample from tissue block S1-12",
    }
    assert page_info == expected_page_info
    expected_defaults = {
        "d_scheme": "haline",
        "d_layer": "All",
        "i_layer": "All",
        "d_category": "All",
        "d_value": "CYB5A",
    }
    assert defaults == expected_defaults
    expected_layers = ["All", "Layer 1", "Layer 2", "Layer 3", "Layer 4"]
    assert layers == expected_layers
    expected_image_layers = ["All", "Image 1", "Image 2", "Image 3", "Image 4"]
    assert image_layers == expected_image_layers
    expected_cat_opts = {
        "Category": "Gland",
        "Label (Only True)": "Pixels with gland tissue",
        "Label (Only False)": "Pixels without gland tissue",
    }
    assert cat_opts == expected_cat_opts
    expected_value_info = {
        "CYB5A": {"Min": -2.9899, "Max": 0.9956},
        "SOD1": {"Min": -1.9876, "Max": 1.9692},
        "CA2": {"Min": -2.9486, "Max": 1.9502},
        "RBP4": {"Min": -1.974, "Max": 1.9958},
        "ALB": {"Min": -2.9672, "Max": 3.9337},
        "TF": {"Min": -0.9777, "Max": 2.9763},
        "CAT": {"Min": -1.9945, "Max": 1.9968},
    }
    assert value_info == expected_value_info
    expected_axes = {
        "X": [0, 50, 100, 150, 200, 250, 300, 350, 400, 450],
        "Y": [0, 50, 100, 150, 200, 250],
        "Z": [0, 50, 100, 150, 200],
    }
    assert axes == expected_axes
    expected_downloads_data = {
        "Name": [
            "S1-12proteomics.xlsx",
        ],
        "Label": ["Download .xlsx"],
        "Desc": [
            "Download the data collected in this study as an Excel spreadsheet",
        ],
        "Block": ["S1-12"],
    }
    expected_downloads = pd.DataFrame(data=expected_downloads_data)
    assert downloads.equals(expected_downloads)


def test_uf_cube_opacity():
    def run_tests(tab: str):
        # test that fig1's opacity value is updated as expected
        fig1 = update_fig(
            tab,
            color=D_SCHEME,
            value=D_PROTEIN,
            cubeopacity=0.5,
            pointopacity=0.4,
            layer="All",
            image_layer="All",
            category_selected="All",
            category_data=cat_opts,
            value_range_dict=value_info,
            axes=axes,
            block="S1-12",
        )
        fig2 = update_fig(
            tab,
            color=D_SCHEME,
            value=D_PROTEIN,
            cubeopacity=0,
            pointopacity=0.4,
            layer="All",
            image_layer="All",
            category_selected="All",
            category_data=cat_opts,
            value_range_dict=value_info,
            axes=axes,
            block="S1-12",
        )

        assert fig1["data"][0]["opacity"] == 0.5
        assert fig2["data"][0]["opacity"] == 0
        with pytest.raises(ValueError):
            update_fig(
                tab,
                color=D_SCHEME,
                value=D_PROTEIN,
                cubeopacity=11,
                pointopacity=1,
                layer="All",
                image_layer="All",
                category_selected="All",
                category_data=cat_opts,
                value_range_dict=value_info,
                axes=axes,
                block="S1-12",
            )

    run_tests("cube-tab")
    run_tests("cube-image-tab")


def test_uf_cube_cscheme():
    def run_tests(tab: str):
        # test that fig1's color scheme value is updated as expected
        fig1 = update_fig(
            tab,
            color="inferno",
            value=D_PROTEIN,
            cubeopacity=D_OPACITY,
            pointopacity=D_OPACITY,
            layer="All",
            category_selected="All",
            category_data=cat_opts,
            value_range_dict=value_info,
            axes=axes,
            block="S1-12",
        )

        assert fig1["data"][0]["colorscale"] == (
            (0.0, "#000004"),
            (0.1111111111111111, "#1b0c41"),
            (0.2222222222222222, "#4a0c6b"),
            (0.3333333333333333, "#781c6d"),
            (0.4444444444444444, "#a52c60"),
            (0.5555555555555556, "#cf4446"),
            (0.6666666666666666, "#ed6925"),
            (0.7777777777777778, "#fb9b06"),
            (0.8888888888888888, "#f7d13d"),
            (1.0, "#fcffa4"),
        )

    run_tests("cube-tab")
    run_tests("cube-image-tab")


def test_uf_cube_layer():
    def run_tests(tab: str):
        fig1 = update_fig(
            tab,
            color=D_SCHEME,
            value=D_PROTEIN,
            cubeopacity=D_OPACITY,
            pointopacity=D_OPACITY,
            layer="All",
            category_selected="All",
            category_data=cat_opts,
            value_range_dict=value_info,
            axes=axes,
            block="S1-12",
        )
        fig2 = update_fig(
            tab,
            color=D_SCHEME,
            value=D_PROTEIN,
            cubeopacity=D_OPACITY,
            pointopacity=D_OPACITY,
            layer="Layer 2",
            category_selected="All",
            category_data=cat_opts,
            value_range_dict=value_info,
            axes=axes,
            block="S1-12",
        )
        assert fig1["data"][0]["z"].min() == 0.0
        assert fig1["data"][0]["z"].max() == 199.999
        assert fig2["data"][0]["z"].min() == 50.0
        assert fig2["data"][0]["z"].max() == 99.999

    run_tests("cube-tab")
    run_tests("cube-image-tab")


def test_uf_cube_category():
    def run_tests(tab: str):
        fig1 = update_fig(
            tab,
            color=D_SCHEME,
            value=D_PROTEIN,
            cubeopacity=D_OPACITY,
            pointopacity=D_OPACITY,
            layer="All",
            image_layer="All",
            category_selected="All",
            category_data=cat_opts,
            value_range_dict=value_info,
            axes=axes,
            block="S1-12",
        )
        fig2 = update_fig(
            tab,
            color=D_SCHEME,
            value=D_PROTEIN,
            cubeopacity=D_OPACITY,
            pointopacity=D_OPACITY,
            layer="All",
            image_layer="All",
            category_selected="Pixels with gland tissue",
            category_data=cat_opts,
            value_range_dict=value_info,
            axes=axes,
            block="S1-12",
        )
        fig3 = update_fig(
            tab,
            color=D_SCHEME,
            value=D_PROTEIN,
            cubeopacity=D_OPACITY,
            pointopacity=D_OPACITY,
            layer="All",
            image_layer="All",
            category_selected="Pixels without gland tissue",
            category_data=cat_opts,
            value_range_dict=value_info,
            axes=axes,
            block="S1-12",
        )
        assert len(fig1["data"][0]["z"]) == 1440
        assert len(fig2["data"][0]["z"]) == 336
        assert len(fig3["data"][0]["z"]) == 1104

    run_tests("cube-tab")
    run_tests("cube-image-tab")


def test_uf_cube_image_layer():
    fig1 = update_fig(
        "cube-image-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        image_layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    fig2 = update_fig(
        "cube-image-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        image_layer="Layer 2",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    assert fig1["data"][0]["z"].min() == 0.0
    assert fig1["data"][0]["z"].max() == 199.999
    assert len(fig1["data"]) == 5
    assert fig2["data"][0]["z"].min() == 0.0
    assert fig2["data"][0]["z"].max() == 199.999
    assert len(fig2["data"]) == 2


# def make_image_layer_fig(
#     axes,
#     image_layer="All",
#     metadata=None,
#     imgs: list = None,
#     colorscale=None,
#     opacity=1,
# )

# def update_fig(
#     tab,
#     color="haline",
#     value="",
#     cubeopacity=0.4,
#     pointopacity=0.1,
#     layer="All",
#     image_layer="All",
#     image_opacity=1,
#     category_selected="All",
#     category_data={},
#     value_range_dict={},
#     axes={},
#     block="",
# )


def test_uf_image_layer_layer():
    fig1 = update_fig(
        "image-layer-tab",
        value=D_PROTEIN,
        image_layer="All",
        image_opacity=1,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    fig2 = update_fig(
        "image-layer-tab",
        value=D_PROTEIN,
        image_layer="Layer 3",
        image_opacity=1,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )

    fig1_0_z = []
    for row in fig1["data"][0]["z"]:
        fig1_0_z.extend(row)

    fig1_3_z = []
    for row in fig1["data"][3]["z"]:
        fig1_3_z.extend(row)

    fig2_0_z = []
    for row in fig2["data"][0]["z"]:
        fig2_0_z.extend(row)

    assert len(fig1["data"]) == 4
    assert min(fig1_0_z) == 0.0
    assert max(fig1_0_z) == 0.0
    assert min(fig1_3_z) == 150.00
    assert max(fig1_3_z) == 150.00

    assert len(fig2["data"]) == 1
    assert min(fig2_0_z) == 100.0
    assert max(fig2_0_z) == 100.0


def test_uf_image_layer_colorscale():
    fig1 = update_fig(
        "image-layer-tab",
        value=D_PROTEIN,
        image_layer="All",
        image_opacity=1,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    cs1 = (
        (np.float64(0.0), "rgb(255,0,0)"),
        (np.float64(0.67), "rgb(0,0,255)"),
        (np.float64(0.99), "rgb(0,255,0)"),
        (np.float64(1.0), "rgb(255,255,255)"),
    )

    img_info, imgs = get_all_images("S1-12")
    fig2 = make_image_layer_fig(
        axes=axes,
        image_layer="All",
        metadata=img_info,
        imgs=imgs,
        colorscale=None,
        opacity=1,
    )
    cs2 = (
        (0.0, "rgb(255,255,255)"),
        (0.125, "rgb(240,240,240)"),
        (0.25, "rgb(217,217,217)"),
        (0.375, "rgb(189,189,189)"),
        (0.5, "rgb(150,150,150)"),
        (0.625, "rgb(115,115,115)"),
        (0.75, "rgb(82,82,82)"),
        (0.875, "rgb(37,37,37)"),
        (1.0, "rgb(0,0,0)"),
    )

    assert fig1["data"][0]["colorscale"] == cs1
    assert fig2["data"][0]["colorscale"] == cs2


def test_uf_image_layer_opacity():
    fig1 = update_fig(
        "image-layer-tab",
        value=D_PROTEIN,
        image_layer="All",
        image_opacity=1,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    fig2 = update_fig(
        "image-layer-tab",
        value=D_PROTEIN,
        image_layer="Layer 3",
        image_opacity=0.4,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )

    assert fig1["data"][0]["opacity"] == 1
    assert fig2["data"][0]["opacity"] == 0.4


def test_uf_point_opacity():
    # test that fig2's opacity value is updated as expected
    fig1 = update_fig(
        "point-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=0.5,
        layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    fig2 = update_fig(
        "point-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=0,
        layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )

    assert fig1["data"][0]["opacity"] == 0.5
    assert fig2["data"][0]["opacity"] == 0
    with pytest.raises(ValueError):
        update_fig(
            "point-tab",
            color=D_SCHEME,
            value=D_PROTEIN,
            cubeopacity=D_OPACITY,
            pointopacity=11,
            layer="All",
            category_selected="All",
            category_data=cat_opts,
            value_range_dict=value_info,
            axes=axes,
            block="S1-12",
        )


def test_uf_point_cscheme():
    # test that fig2's color scheme value is updated as expected
    fig1 = update_fig(
        "point-tab",
        color="inferno",
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )

    assert fig1["data"][0]["colorscale"] == (
        (0.0, "#000004"),
        (0.1111111111111111, "#1b0c41"),
        (0.2222222222222222, "#4a0c6b"),
        (0.3333333333333333, "#781c6d"),
        (0.4444444444444444, "#a52c60"),
        (0.5555555555555556, "#cf4446"),
        (0.6666666666666666, "#ed6925"),
        (0.7777777777777778, "#fb9b06"),
        (0.8888888888888888, "#f7d13d"),
        (1.0, "#fcffa4"),
    )


def test_uf_point_layer():
    fig1 = update_fig(
        "point-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    fig2 = update_fig(
        "point-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="Layer 3",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    assert fig1["data"][0]["z"].min() == 25.0
    assert fig1["data"][0]["z"].max() == 175.0
    assert fig2["data"][0]["z"].min() == 125.0
    assert fig2["data"][0]["z"].max() == 125.0


def test_uf_layer_cscheme():
    # test that fig3's color scheme value is updated as expected
    fig1 = update_fig(
        "layer-tab",
        color="inferno",
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )

    assert fig1["data"][0]["colorscale"] == (
        (0.0, "#000004"),
        (0.1111111111111111, "#1b0c41"),
        (0.2222222222222222, "#4a0c6b"),
        (0.3333333333333333, "#781c6d"),
        (0.4444444444444444, "#a52c60"),
        (0.5555555555555556, "#cf4446"),
        (0.6666666666666666, "#ed6925"),
        (0.7777777777777778, "#fb9b06"),
        (0.8888888888888888, "#f7d13d"),
        (1.0, "#fcffa4"),
    )


def test_uf_layer_layer():
    fig1 = update_fig(
        "layer-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    fig2 = update_fig(
        "layer-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="Layer 2",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    f1l1maxes = []
    f1l1mins = []
    for nlist in fig1["data"][0]["z"]:
        f1l1maxes.append(max(nlist))
        f1l1mins.append(min(nlist))
    f1l4maxes = []
    f1l4mins = []
    for nlist in fig1["data"][3]["z"]:
        f1l4maxes.append(max(nlist))
        f1l4mins.append(min(nlist))
    assert min(f1l1mins) == 25
    assert max(f1l1maxes) == 25
    assert min(f1l4mins) == 175
    assert max(f1l4maxes) == 175

    f2l1maxes = []
    f2l1mins = []
    for nlist in fig2["data"][0]["z"]:
        f2l1maxes.append(max(nlist))
        f2l1mins.append(min(nlist))
    assert min(f2l1mins) == 75.0
    assert max(f2l1maxes) == 75.0

    with pytest.raises(IndexError):
        fig2["data"][1]


def test_uf_sphere_cscheme():
    # test that fig4's color scheme value is updated as expected
    fig1 = update_fig(
        "sphere-tab",
        color="inferno",
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )

    assert fig1["data"][0]["colorscale"] == (
        (0.0, "#000004"),
        (0.1111111111111111, "#1b0c41"),
        (0.2222222222222222, "#4a0c6b"),
        (0.3333333333333333, "#781c6d"),
        (0.4444444444444444, "#a52c60"),
        (0.5555555555555556, "#cf4446"),
        (0.6666666666666666, "#ed6925"),
        (0.7777777777777778, "#fb9b06"),
        (0.8888888888888888, "#f7d13d"),
        (1.0, "#fcffa4"),
    )


def test_uf_sphere_layer():
    fig1 = update_fig(
        "sphere-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    fig2 = update_fig(
        "sphere-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="Layer 4",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    assert fig1["data"][0]["z"].min() == 11.0
    assert fig1["data"][0]["z"].max() == 39.0
    assert fig2["data"][0]["z"].min() == 161.0
    assert fig2["data"][0]["z"].max() == 189.0


def test_uf_sphere_category():
    fig1 = update_fig(
        "sphere-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    fig2 = update_fig(
        "sphere-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        category_selected="Pixels with gland tissue",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )
    fig3 = update_fig(
        "sphere-tab",
        color=D_SCHEME,
        value=D_PROTEIN,
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        category_selected="Pixels without gland tissue",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )

    assert len(fig1["data"]) == 165
    assert len(fig2["data"]) == 39
    assert len(fig3["data"]) == 126


def test_uo_protein():
    # test that max and min values for the specified protein are as expected
    fig1 = update_fig(
        "cube-tab",
        color=D_SCHEME,
        value="ALB",
        cubeopacity=D_OPACITY,
        pointopacity=D_OPACITY,
        layer="All",
        category_selected="All",
        category_data=cat_opts,
        value_range_dict=value_info,
        axes=axes,
        block="S1-12",
    )

    assert min(fig1["data"][0]["intensity"]) == value_info["ALB"]["Min"]
    assert max(fig1["data"][0]["intensity"]) == value_info["ALB"]["Max"]
