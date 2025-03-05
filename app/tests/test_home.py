from dash import page_registry
import os
import sys
import pandas as pd
from pathlib import Path

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
import app
from pages.home import read_blocks
from pages.constants import FILE_DESTINATION as FD

thumbnails = pd.read_csv(FD["thumbnails"]["catalog"])
blocks = read_blocks()


def test_links():
    relative_paths = []
    for page in page_registry.values():
        relative_paths.append(page["relative_path"])
    for i in range(blocks["Images"].size):
        if blocks["Images"][i] != " ":
            block_name = blocks["Images"][i].split("/")[-1]
            assert block_name in thumbnails["Block"].values
    for k in range(blocks["Volumetric Map"].size):
        if blocks["Volumetric Map"][k] != " ":
            # check that each block has a folder in volumetric-map
            p = Path(FD["volumetric-map"])
            dirs = [x.name for x in p.iterdir() if x.is_dir()]
            block = blocks["Volumetric Map"][k].split("/")[-1]
            assert block in dirs
