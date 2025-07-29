import os
import sys
import pandas as pd

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
import app
from pages.constants import FILE_DESTINATION as FD

thumbnails = pd.read_csv(FD["thumbnails"]["catalog"])
s_imgs = pd.read_csv(FD["si-block"]["si-files"])


def test_oc_page_links():
    # check that each link on the images summary pages references an image set in ocpage
    for i in range(thumbnails["Link"].size):
        link_data = thumbnails.at[i, "Link"].split("/")
        link_si = link_data[-1]
        link_block = link_data[-2]
        assert link_si in s_imgs["Image Set"].values
        assert link_block in s_imgs["Tissue Block"].values
