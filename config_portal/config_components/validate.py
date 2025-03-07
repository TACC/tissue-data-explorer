import filetype
import io
import pandas as pd
import nh3
import magic
from pathlib import Path
import os
import re
import shutil
import traceback
from PIL import Image, ImageDraw, ImageOps
import logging
import base64
from collections.abc import Callable
import numpy as np
import sys

from pages import constants

MAX_TITLE_LENGTH = 2048
MAX_FILENAME_LENGTH = 255
FINAL_THUMBNAIL_SIZE = (220, 110)
THUMBNAIL_TILE = (110, 110)
NAMEREG = r"\.\w{3,8}"  # regex to check file name format
VALID_EXTS = {
    "excel": ["xls", "xlsx"],
    "excel/vol": ["xls", "xlsx", "stl", "nrrd", "vti", "obj", "mtl"],
    "3d": ["xls", "xlsx", "obj"],
    "image": [
        # Allows PNG, AVI, Image Cytometry Standard, OME-TIFF, TIFF, CZI, SVS, AFI, SCN, GDAL, ZVI, DCM, NDPI, and VSI extensions
        "png",
        "jpg",
        "avi",
        "ids",
        "ics",
        "ome.tif",
        "ome.tiff",
        "ome.tf2",
        "ome.tf8",
        "ome.btf",
        "tif",
        "tiff",
        "tf2",
        "tf8",
        "btf",
        "czi",
        "svs",
        "afi",
        "scn",
        "gdal",
        "zvi",
        "dcm",
        "ndpi",
        "vsi",
        "zarr",
    ],
}


VALID_MIMES = {
    "excel": [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ],
    "excel/vol": [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",
        "text/xml",
        "text/plain",
    ],
    "3d": [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
    ],
    "image": ["image/tiff", "image/png", "video/x-msvideo", "image/jpeg"],
}
REQUIRED_HEADERS = {
    "si-block": {
        "block-data": [
            "Tissue Block",
            "Organ ID",
            "Organ Description",
            "Order",
            "Anatomical region",
            "Images",
            "Reports",
            "Volumetric Map",
        ],
        "si-files": [
            "Tissue Block",
            "Image Set",
            "Image Category",
            "File",
            "Height",
            "Width",
            "Slices",
            "Channels",
        ],
    },
    "volumetric-map": {
        "meta": [
            "Block",
            "Title",
            "Description",
        ],
        "points_data": [
            "Block ID",
            "X Center",
            "Y Center",
            "Z Center",
            "X Size",
            "Y Size",
            "Z Size",
            "Category",
        ],
        "value_ranges": ["Row Label"],
        "category_labels": [
            "Category",
            "Label (Only True)",
            "Label (Only False)",
        ],
        "vol_measurements": [
            "X Min",
            "X Max",
            "X Size",
            "Y Min",
            "Y Max",
            "Y Size",
            "Z Min",
            "Z Max",
            "Z Size",
        ],
    },
    "downloads": {"downloads": ["Name", "Label", "Desc", "Block"]},
    "obj-files": {"files": ["Organ", "Name", "File", "Color", "Opacity"]},
}

FD = constants.FILE_DESTINATION

app_logger = logging.getLogger(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app_logger.handlers = gunicorn_logger.handlers
app_logger.setLevel(gunicorn_logger.level)


def check_file_type(file, valid_type, filename=None):
    ftype = filetype.guess(file)
    if ftype is None:
        if valid_type == "image" or valid_type == "excel/vol" or valid_type == "3d":
            ftype = magic.from_buffer(file)
            if ftype == "data":
                if filename is None:
                    return False, "Filename missing"
                else:
                    # File content checking is not supported for some needed formats, so just look at extension
                    s = Path(filename).suffix
                    if s[1:] in VALID_EXTS[valid_type]:
                        return True, ""
                    else:
                        return False, f"Invalid file type {s}"
            else:
                # since using magic, need to get mime type from magic and ext from name
                ext = Path(filename).suffix
                mime = magic.from_buffer(file, mime=True)
                if (ext[1:] in VALID_EXTS[valid_type]) and (
                    mime in VALID_MIMES[valid_type]
                ):
                    return True, ""
                else:
                    return False, f"Invalid file type {ext}"
        else:
            return False, f"Invalid file type {ftype.extension}"
    elif (ftype.extension in VALID_EXTS[valid_type]) and (
        ftype.mime in VALID_MIMES[valid_type]
    ):
        return True, ""
    else:
        return False, f"Invalid file type {ftype.extension}"


def check_html_helper(some_text):
    if nh3.is_html(str(some_text)):
        return nh3.clean_text(str(some_text))
    else:
        return some_text


def update_links(column, df):
    link_columns = ["Images", "Reports", "Volumetric Map"]
    i = 0
    if column in link_columns:
        while i < df[column].size:
            links = {
                "Images": f"/scientific-images-list/{df["Tissue Block"].at[i]}",
                "Reports": "/reports",
                "Volumetric Map": f"/volumetric-map/{df["Tissue Block"].at[i]}",
            }
            if not (df[column].at[i] == " "):
                df[column].at[i] = links[column]
            i += 1


def open_excel_from_bytes(file: bytes, worksheet=None) -> pd.DataFrame:
    """Reads an Excel spreadsheet. Returns a dict of DataFrames if no worksheets are
    provided, returns one Dataframe if a worksheet is provided."""
    try:
        dfs = pd.read_excel(
            io.BytesIO(file), sheet_name=worksheet, engine="calamine", na_values=[" "]
        )
        return True, "", dfs
    except ValueError:
        return False, "Worksheet names must match the template.", {}
    except Exception as err:
        return False, f"Import failed with error: {err}", {}


def sanitize_df(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        if df[column].dtype == "object":
            # if column is a string, check for html
            df[column] = df[column].apply(check_html_helper)
    return df


def check_excel_headers(
    file: bytes, which_headers: str, fillna=True
) -> tuple[bool, str, dict]:
    """Checks that the file includes required headers and sanitizes any html.
    Returns (success, error message, dict of DataFrames if successful)
    """
    dfs = {}
    for key in REQUIRED_HEADERS[which_headers].keys():
        dfr = open_excel_from_bytes(file, worksheet=key)
        if dfr[0]:
            df = dfr[2]
        else:
            return False, dfr[1], {}
        if fillna:
            df.fillna(" ", inplace=True)
        # check that required columns are in the workbook
        if set(REQUIRED_HEADERS[which_headers][key]).issubset(
            set(df.columns.to_list())
        ):
            dfs[key] = sanitize_df(df)
        else:
            return (
                False,
                f"Workbook {key} is missing required columns from the template.",
                {},
            )
    return True, "", dfs


def process_si_block_file(file: bytes, which_headers: str) -> tuple[bool, str]:
    header_check = check_excel_headers(file, which_headers)
    if header_check[0]:
        for key in REQUIRED_HEADERS[which_headers].keys():
            if key == "block-data":
                for col in ["Images", "Reports", "Volumetric Map"]:
                    if (
                        col in header_check[2][key].columns
                        and header_check[2][key].dtypes[col] != "object"
                    ):
                        header_check[2][key][col] = header_check[2][key][col].astype(
                            "object"
                        )
                    # calculate link values for main page links
                    update_links(col, header_check[2][key])
            header_check[2][key].to_csv(FD[which_headers][key]["depot"], index=False)
        return (True, "")
    else:
        return (header_check[0], header_check[1])


def check_image_name(
    filename: str, df: pd.DataFrame
) -> tuple[int, str, pd.DataFrame, int, str]:
    """This function checks that the provided image name can be associated with an entry
    in the provided DataFrame. PNGs should be named like:

    {Source file name}_C{Channel number, starting at zero}{sequence number, starting at zero and padded with zeroes to four digits}

    Returns (number of matches, filename stem, df filtered to the relevant row, number of channels, error message)
    """
    ext = Path(filename).suffix
    matches = 0
    namestem = ""
    if ext != ".png":
        try:
            matches = df["File"].eq(filename).sum()
            namestem = Path(filename).stem
            filename_reg = re.escape(filename)
            new_df = df[df["File"].str.fullmatch(filename_reg)]
            channel = None
        except Exception as err:
            return (
                0,
                False,
                False,
                False,
                f"{err}",
            )
    else:
        try:
            nameparts = filename.split("_C")
            if len(nameparts) < 2:
                return (
                    0,
                    False,
                    False,
                    False,
                    f"Filename {filename} must use the sequence _C to separate channel data",
                )
            namestem = "_C".join(nameparts[:-1])
            namestem_reg = re.escape(namestem)
            nr = namestem_reg + NAMEREG
            matches = df["File"].str.contains(nr).sum()
            new_df = df[df["File"].str.contains(nr)]
        except Exception as err:
            return (
                0,
                False,
                False,
                False,
                f"{err}",
            )
        try:
            channel = int(nameparts[-1][0])
        except ValueError:
            return (
                0,
                False,
                False,
                False,
                "You must specify the channel for this image using the sequence _C as a separator",
            )

    if matches != 1:
        return (
            0,
            False,
            False,
            False,
            f"Filename {filename} must match exactly one filename in metadata",
        )
    else:
        return matches, namestem, new_df, channel, ""


def check_png_name_ending(filename: str) -> tuple[bool, str]:
    """Checks that the second half of a PNG follows the required naming convention:

    {Source file name}_C{Channel number, starting at zero}{sequence number, starting at zero and padded with zeroes to four digits}

    Returns (match test result, error message)
    """
    nameparts = filename.split("_C")
    numreg = r"\d{5}\.png"
    nr = re.compile(numreg)
    m = nr.fullmatch(nameparts[-1])
    if m:
        return True, ""
    else:
        return (
            False,
            f"Filename {filename} must contain exactly five consecutive number characters between the _C sequence and the file extension",
        )


def process_sci_image(file: bytes, filename: str) -> tuple[bool, str, str]:
    """This function is called when a user uploads files to the scientific images upload widget.
    It checks that image metadata exists and the image name conforms to naming conventions, then
    saves the image to the depot.

    Returns (check results, error message)
    """
    df = pd.read_csv(FD["si-block"]["si-files"]["publish"])
    if df.empty:
        return False, "You must upload image metadata before uploading images"
    ext = Path(filename).suffix
    # if not a PNG, search for the name exactly
    name_info = check_image_name(filename, df)
    if name_info[0] == 0:
        return False, name_info[4]
    # if PNG, check naming scheme
    if ext == ".png":
        nums_check = check_png_name_ending(filename)
        if not nums_check[0]:
            return nums_check
    # check if destination path exists
    dest = Path(FD["sci-images"]["depot"])
    if not Path.exists(dest):
        Path.mkdir(dest, parents=True)
    with open(os.path.join(FD["sci-images"]["depot"], filename), "wb") as fp:
        fp.write(file)

    return True, ""


def update_title(value: str) -> tuple[str, str, str]:
    """Validate and publish a new app title.
    Returns (title of update toast, description of update, success status)"""
    if value:
        if len(value) > MAX_TITLE_LENGTH:
            return (
                "Title not updated",
                f"Title must be shorter than {MAX_TITLE_LENGTH} characters. Please try again.",
                "failure",
            )
        else:
            try:
                clean_title = check_html_helper(value)
                d = {"title": [clean_title]}
                df = pd.DataFrame(data=d)
                dest = Path(FD["title"]["depot"])
                if not Path.exists(dest.parent):
                    Path.mkdir(dest.parent, parents=True)
                df.to_csv(f"{FD["title"]["depot"]}", index=False)
                p = Path(FD["title"]["depot"])
                t = Path(FD["title"]["publish"])
                shutil.copy2(p, t)
                return (
                    "Title updated",
                    "The configuration has been updated. Refresh the public-facing app to see the changes.",
                    "success",
                )
            except Exception as err:
                app_logger.debug(traceback.print_exc())
                return ("Title not updated", f"{type(err)} {err}", "failure")
    else:
        return ("Title not updated", "Please provide a name.", "failure")


def publish_si_block() -> tuple[str, str, str]:
    """Publish scientific images metadata.
    Returns (title of update toast, description of update, success status)"""
    try:
        for key in FD["si-block"].keys():
            p = Path(FD["si-block"][key]["depot"])
            t = Path(FD["si-block"][key]["publish"])
            shutil.move(p, t)
    except FileNotFoundError as err:
        return ("Metadata not updated", f"{err}", "failure")
    return (
        "Metadata updated",
        "The configuration has been updated. Refresh the public-facing app to see the changes.",
        "success",
    )


def make_thumbnail(imgs):
    w = 0
    h = 0
    for k in range(len(imgs)):
        w += imgs[k].size[0]
        if imgs[k].size[1] > h:
            h = imgs[k].size[1]
    im = Image.new("RGB", (len(imgs) * 110, 110))
    offset = 0
    draw = ImageDraw.Draw(im)
    for m in range(len(imgs)):
        new_im = ImageOps.fit(imgs[m], THUMBNAIL_TILE)
        if m == 0:
            im.paste(new_im)
        else:
            offset += 110
            im.paste(new_im, (offset, 0))
            draw.line(
                [(offset, 0), (offset, h)],
                fill=(255, 255, 255, 255),
                width=2,
            )
    return im


def generate_thumbnails(idx, tdf):
    # get image metadata
    mdf = pd.read_csv(FD["si-block"]["si-files"]["publish"])
    rd = {"Block": [], "Preview": [], "Name": [], "Link": []}
    new_tr = pd.DataFrame(data=rd, dtype="string")

    # get list of unique image sets from the thumbnail dataframe
    parents = tdf["parent"].unique()
    for i in range(parents.size):
        # check how many channels are in the thumbnail dataframe for this parent, and if it matches metadata
        igroup = tdf[tdf["parent"] == parents[i]]  # one row per channel
        igroup = igroup[igroup["filename"].str.endswith(".png")]  # skip non-PNG files
        # if no new PNG files, stop
        if igroup.empty:
            return
        nr = re.escape(parents[i]) + NAMEREG
        new_df = mdf[mdf["File"].str.contains(nr)]  # parent row in metadata
        # how many channels should be in thumbnail
        channels = new_df["Channels"].values[0]
        imgs = []  # images to include in thumbnail
        # compare number of rows in igroup to channels record in mdf
        if igroup.shape[0] < channels:
            # figure out which channel is missing
            actual_channels = igroup["channel"].values
            missing_channels = []
            for k in range(channels):
                if str(k) not in actual_channels:
                    missing_channels.append(k)
            # attempt to find images for any missing channels
            for m in missing_channels:
                p = Path(igroup["destination"].values[0])
                pdir = p.parent
                for file in pdir.iterdir():
                    if file.is_file() and file.suffix == ".png":
                        nameparts = file.name.split("_C")
                        if int(nameparts[-1][0]) == m:
                            # add to imgs and go to next loop iteration
                            imgs.append(Image.open(file))
                            break
            # add images for present channels
            for q in range(igroup.shape[0]):
                imgs.append(Image.open(igroup["destination"].values[q]))
        else:
            for j in range(channels):
                imgs.append(Image.open(igroup["destination"].values[j]))
        im = make_thumbnail(imgs)
        set_name = new_df["Image Set"].values[0]
        dest = Path(f"{FD["sci-images"]["publish"]}/thumbnails/{set_name}")
        thumbnail_loc = (
            f"{FD["thumbnails"]["publish"]}/{set_name}/{parents[i]}_thumbnail.png"
        )
        if not Path.exists(dest):
            Path.mkdir(dest, parents=True)
        ImageOps.cover(im, FINAL_THUMBNAIL_SIZE).save(
            thumbnail_loc,
            optimize=True,
        )
        # add new row to thumbnail records
        display_shared_vol_root = "assets"
        # {"Block": [], "Preview": [], "Name": [], "Link": []}
        new_tr.loc[i] = [
            new_df["Tissue Block"].values[0],
            f"../../{display_shared_vol_root}{thumbnail_loc}",
            new_df["File"].values[0],
            f"/scientific-images/{new_df["Tissue Block"].values[0]}/{set_name}",
        ]
    # update the thumbnails record so that the display app can access the new thumbnails
    update_thumbnails_record(new_tr)


def update_thumbnails_record(new_tr):
    # new_tr: {"Block": [], "Preview": [], "Name": [], "Link": []}
    # try to open thumbnails workbook
    try:
        df = pd.read_csv(FD["thumbnails"]["catalog"])
    except FileNotFoundError:
        # if the file doesn't exist, check if directory exists and create if needed
        dest = Path(f"{FD['thumbnails']['publish']}")
        if not Path.exists(dest):
            Path.mkdir(dest, parents=True)
        new_tr.to_csv(FD["thumbnails"]["catalog"], index=False)
        return
    # check for duplicate records and skip them (file info should stay the same even if image is new)
    df_idx = df.shape[0]
    for i in range(new_tr.shape[0]):
        # look up row in existing df by "Name"
        filename = new_tr.loc[i, "Name"]
        new_df = df[df["Name"].str.contains(filename)]
        # if not found, add new row
        if new_df.empty:
            df.loc[df_idx] = new_tr.loc[i]
    # once all rows are processed, save updated data
    df.to_csv(FD["thumbnails"]["catalog"], index=False)


def update_new_thumbnails_list(
    tdf: pd.DataFrame,
    tdi: int,
    filename: str,
    filestem: str,
    channels: str,
    dest_dir: str,
) -> tuple[pd.DataFrame, int]:
    """
    Checks whether the provided image needs to be added to the list of thumbnail updates.

    Returns the updated dataframe of updates and updated index.
    """
    # pick one img per channel per set for thumbnail
    # check if there is already a row in tdf for the parent & channel of this image
    tdf_needs_new = False
    if tdf["parent"].str.contains(filestem).empty:
        tdf_needs_new = True
    else:
        parent_rows = tdf.loc[(tdf["parent"].str.contains(filestem))]
        if not parent_rows["channel"].str.contains(channels).any():
            tdf_needs_new = True
    if tdf_needs_new:
        dest_loc = f"{dest_dir}/{filename}"
        tdf.loc[tdi] = [
            filename,
            filestem,
            channels,
            dest_loc,
        ]
        tdi += 1
    return tdf, tdi


def move_sci_images(src_path: Path, dest_dir: str, filename: str) -> None:
    """Moves a file to a new location after ensuring the new location exists."""
    try:
        dest = Path(dest_dir)
        if not Path.exists(dest):
            Path.mkdir(dest, parents=True)
        # move to publish dir
        dest_name = Path(f"{dest_dir}/{filename}")
        shutil.move(src_path, dest_name)
    except Exception:
        app_logger.debug(traceback.print_exc())


def publish_sci_images() -> tuple[str, str, str]:
    """This function is called when the user clicks "Publish" in the Scientific Images section.
    It checks that there is image metadata, then processes each image by checking that the image
    name is valid & present in metadata, then capturing any info needed to create thumbnails, and
    moving the image to the public location. It then calls another function to generate thumbnails.

    Returns (title of update toast, description of update, success status)
    """
    # get image location info
    df = pd.read_csv(FD["si-block"]["si-files"]["publish"])
    if df.empty:
        return (
            "Image not published",
            "You must upload image metadata before uploading images",
            "failure",
        )

    p = Path(FD["sci-images"]["depot"])

    # get images in depot
    files = os.listdir(p)

    # start dictionary that will make thumbnails df
    td = {"filename": [], "parent": [], "channel": [], "destination": []}
    tdf = pd.DataFrame(data=td, dtype="string")
    tdi = 0
    # iterate over images in depot
    for file in files:
        child = Path(f"{FD["sci-images"]["depot"]}/{file}")
        # check if a file or dir
        if child.is_file():
            # if file, look up info about destination dir structure
            match_info = check_image_name(child.name, df)
            if match_info[0] == 0:
                return ("Image not published", match_info[4], "failure")
            row = match_info[2]
            if row.empty:
                return (
                    "Image not published",
                    "All images must be present in the image metadata.",
                    "failure",
                )
            try:
                dest_dir = f"{FD["sci-images"]["publish"]}/{row["Tissue Block"].values[0]}/{match_info[1]}"
                tdf, tdi = update_new_thumbnails_list(
                    tdf,
                    tdi,
                    child.name,
                    match_info[1],
                    str(match_info[3]),
                    dest_dir,
                )
                move_sci_images(child, dest_dir, child.name)
            except Exception as err:
                app_logger.debug(traceback.print_exc())
                return ("Image not published", f"{err}", "failure")
    # create thumbnails
    generate_thumbnails(tdi, tdf)
    return ("Images published", "Images transferred successfully", "success")


def process_content(
    content: str, filename: str, filetype: str, which_function: Callable, param=None
) -> tuple[bool, str]:
    """For a given base64 file string, converts the data to bytes, checks the file type for validity,
    and runs the given file processing function.
    Returns (success, error message)"""
    if content == "":
        return False, "One or more files were too large."

    content_type, content_string = content.split(",")
    decoded = base64.b64decode(content_string)
    is_valid_type = check_file_type(decoded, filetype, filename)
    if is_valid_type[0]:
        is_processed = which_function(decoded, param)
        if not is_processed[0]:
            return False, is_processed[1]
        else:
            return True, ""
    else:
        return False, is_valid_type[1]


def is_valid_filename(*args, fn="") -> bool:
    """Returns a boolean: True if the name conforms to rules, False if it is over the max
    length or contains forbidden characters."""
    if len(fn) > MAX_FILENAME_LENGTH:
        return False, f"{fn} exceeds {MAX_FILENAME_LENGTH} characters in length"

    matches = re.findall(r"[^\w\s_()\-.]", fn)

    if len(matches) == 0:
        return True, ""
    else:
        return (
            False,
            f"{fn} contains the following forbidden character sequence(s): {", ".join(matches)}",
        )


def validate_filename_col(col):
    for i in range(col.shape[0]):
        is_valid = is_valid_filename(fn=col.loc[i])
        if is_valid[0] is False:
            return False, is_valid[1]
    return True, ""


def write_excel(dfs: dict, filename: str, loc: str) -> tuple[bool, str]:
    # check that loc exists
    p = Path(loc)
    if not Path.exists(p):
        Path.mkdir(p, parents=True)
    with pd.ExcelWriter(f"{loc}/{filename}", mode="w") as writer:
        df = pd.DataFrame(data={})
        df.to_excel(writer)
    # save into Excel workbook
    try:
        with pd.ExcelWriter(
            f"{loc}/{filename}",
            mode="a",
            engine="openpyxl",
        ) as writer:
            for key in dfs.keys():
                df = sanitize_df(dfs[key])
                df.to_excel(writer, sheet_name=key, index=False)
        return True, ""
    except Exception as err:
        app_logger.debug(traceback.print_exc())
        return False, str(err)


def update_df_entries(
    old_list: pd.DataFrame, new_entries: pd.DataFrame, key_column: str
):
    # TODO: add ability to delete entries (list entries and files)
    ol = old_list.copy()
    valid_names = validate_filename_col(new_entries[key_column])
    if not valid_names[0]:
        return False, valid_names[1], ""
    # drop duplicate names in existing data
    ol.drop_duplicates(subset=[key_column], inplace=True)
    ol.index = range(len(ol))
    new_rows = new_entries.shape[0]
    existing_rows = ol.shape[0]
    to_drop = []
    # add rows to downloads.csv
    for i in range(new_rows):
        # find names existing records that match names in new record
        if ol[key_column].eq(new_entries[key_column].loc[i]).any():
            matches = np.flatnonzero(ol[key_column].eq(new_entries[key_column].loc[i]))
            to_drop.extend(matches[1:])
            ol.iloc[matches[0]] = new_entries.iloc[i]
        else:
            ol.loc[existing_rows + i] = new_entries.iloc[i]
    # drop rows that were duplicated by entries in new upload
    ol.drop(to_drop, inplace=True)
    ol.index = range(len(ol))
    return ol


def update_entries(
    old_loc: str, new_entries: pd.DataFrame, key_column: str
) -> pd.DataFrame:
    """Used with check_downloads_xlsx and process_obj_files"""
    new = False
    try:
        df = pd.read_csv(old_loc)
    except FileNotFoundError:
        df = new_entries
        new = True
        valid_names = validate_filename_col(df[key_column])
        if not valid_names[0]:
            return False, valid_names[1], ""
        # drop duplicate names
        df.drop_duplicates(subset=[key_column], inplace=True)
    if not new:
        df = update_df_entries(df, new_entries, key_column)
    return df


def check_downloads_xlsx(file: bytes, filename: str) -> tuple[bool, str]:
    """Checks downloads.xlsx, which can be uploaded to volumetric map files, for duplicates and
    unsafe filenames, then saves a csv in depot."""
    header_check = check_excel_headers(file, "downloads")
    # update downloads.csv
    if header_check[0]:
        df = update_entries(
            FD["volumetric-map"]["downloads-file"]["depot"],
            header_check[2]["downloads"],
            "Name",
        )
        # save csv
        df.to_csv(FD["volumetric-map"]["downloads-file"]["depot"], index=False)
        # no filename because this file's presence alone should not trigger name update
        return True, ""
    else:
        return False, header_check[1]


def get_volumetric_map_folder(filename):
    """Determines the block name for the download file so that the file can be saved in the
    correct folder"""
    df = pd.read_csv(FD["volumetric-map"]["downloads-file"]["depot"])
    block = df["Block"][df["Name"] == filename]
    if block.empty:
        return (
            False,
            f"{filename} is not present in downloads list. You must add an entry to downloads.xlsx to upload this file.",
        )
    return True, block.iloc[0]


def make_cubes_df(
    points_df: pd.DataFrame, vol_measurements: pd.DataFrame
) -> pd.DataFrame:
    """For each point representing the center of a rectangular prism, calculates eight points representing
    its vertices."""
    # Vertices are ordered as follows:
    # [
    #     [x, y, z],
    #     [x + x_dist, y, z],
    #     [x, y + y_dist, z],
    #     [x + x_dist, y + y_dist, z],
    #     [x, y, z + z_dist],
    #     [x + x_dist, y, z + z_dist],
    #     [x, y + y_dist, z + z_dist],
    #     [x + x_dist, y + y_dist, z + z_dist],
    # ]

    x_transform = vol_measurements.loc[0, "X Size"] / 2
    y_transform = vol_measurements.loc[0, "Y Size"] / 2
    z_transform = vol_measurements.loc[0, "Z Size"] / 2

    transform = {
        "x": [
            -x_transform,
            x_transform - 0.001,
            -x_transform,
            x_transform - 0.001,
            -x_transform,
            x_transform - 0.001,
            -x_transform,
            x_transform - 0.001,
        ],
        "y": [
            -y_transform,
            -y_transform,
            y_transform - 0.001,
            y_transform - 0.001,
            -y_transform,
            -y_transform,
            y_transform - 0.001,
            y_transform - 0.001,
        ],
        "z": [
            -z_transform,
            -z_transform,
            -z_transform,
            -z_transform,
            z_transform - 0.001,
            z_transform - 0.001,
            z_transform - 0.001,
            z_transform - 0.001,
        ],
    }

    cubes_df = pd.DataFrame().reindex(columns=points_df.columns)
    # for each row in the source df, make 8 rows in the new df. Each row represents a vertex of a rectangular
    # prism around the provided point
    for i in points_df.index:
        new_x = [points_df.loc[i, "X Center"] + x for x in transform["x"]]
        new_y = [points_df.loc[i, "Y Center"] + y for y in transform["y"]]
        new_z = [points_df.loc[i, "Z Center"] + z for z in transform["z"]]
        for j in range(8):
            idx = j + (i * 8)
            cubes_df.loc[idx] = points_df.loc[i]
            cubes_df.loc[idx, "X Center"] = new_x[j]
            cubes_df.loc[idx, "Y Center"] = new_y[j]
            cubes_df.loc[idx, "Z Center"] = new_z[j]
    return cubes_df


def check_volumetric_map_data_xlsx(file: bytes) -> tuple[bool, str]:
    header_check = check_excel_headers(file, "volumetric-map", fillna=False)
    if header_check[0]:
        # get block name
        block = header_check[2]["meta"]["Block"].values[0]
        loc = f"{FD["volumetric-map"]["meta"]["depot"]}/{block}"
        # check if loc exists
        dest = Path(loc)
        if not Path.exists(dest):
            Path.mkdir(dest, parents=True)
        for key, item in header_check[2].items():
            if key == "points_data":
                # data must be sorted for Dash to display it correctly
                item.sort_values(by=["X Center", "Y Center", "Z Center"], inplace=True)
            item.to_csv(f"{loc}/{key}.csv", index=False)
        # create cubes csv
        cubes_df = make_cubes_df(
            header_check[2]["points_data"], header_check[2]["vol_measurements"]
        )
        cubes_df.to_csv(f"{loc}/cube_data.csv", index=False)
        return True, ""
    else:
        return False, header_check[1]


def save_generic_file(loc: str, file: bytes, filename: str) -> tuple[bool, str]:
    dest = Path(loc)
    if not Path.exists(dest):
        Path.mkdir(dest, parents=True)
    with open(f"{loc}/{filename}", "wb") as f:
        f.write(file)
    return True, ""


def process_volumetric_map_data(file: bytes, filename: str) -> tuple[bool, str]:
    """Takes a file, checks the headers if metadata file, and saves them file to the depot.
    Overwrites file if it already exists.
    Returns (success, error message)"""
    # throw an error if filename is not valid
    is_valid = is_valid_filename(filename)
    if not is_valid[0]:
        return False, is_valid[1]
    if filename == "volumetric-map-data.xlsx":
        return check_volumetric_map_data_xlsx(file)
    elif filename == "downloads.xlsx":
        return check_downloads_xlsx(file, filename)
    elif Path(filename).suffix == ".xlsx":
        open_results = open_excel_from_bytes(file)
        if open_results[0]:
            try:
                block = get_volumetric_map_folder(filename)
                if not block[0]:
                    return False, block[1]
                loc = f"{FD["volumetric-map"]["downloads"]["depot"]}/{block[1]}"
                return write_excel(open_results[2], filename, loc)
            except Exception as err:
                app_logger.debug(traceback.print_exc())
                return False, str(err)
        else:
            return False, open_results[1]
    else:
        try:
            block = get_volumetric_map_folder(filename)
            if not block[0]:
                return False, block[1]
            loc = f"{FD["volumetric-map"]["downloads"]["depot"]}/{block[1]}"
            return save_generic_file(loc, file, filename)
        except Exception as err:
            app_logger.debug(traceback.print_exc())
            return False, str(err)


def move_dir(src: Path, dest: str) -> bool:
    """Move the contents of one directory to another directory"""
    dest_path = Path(dest)
    if not Path.exists(dest_path):
        Path.mkdir(dest_path, parents=True)
    files_to_move = src.iterdir()
    for file in files_to_move:
        file_dest = dest_path / file.name
        shutil.move(file, file_dest)
    return True


def publish_entries(src: str, dest: str, key_col: str):
    """Publish new entries to a csv file."""
    new_entries = pd.read_csv(src)
    publish_dl_path = Path(dest)
    if not Path.exists(publish_dl_path.parent):
        Path.mkdir(publish_dl_path.parent, parents=True)
    if not Path.exists(publish_dl_path):
        new_entries.to_csv(dest, index=False)
    else:
        old_list = pd.read_csv(dest)
        old_list = update_df_entries(old_list, new_entries, key_col)
        old_list.to_csv(dest, index=False)


def publish_volumetric_map_data() -> tuple[str, str, str]:
    """Publishes volumetric map data.
    Returns (title of update toast, description of update, success status)"""
    # move each folder in the volumetric map depot to shared volume /config
    p = Path(FD["volumetric-map"]["downloads"]["depot"])
    dirs_to_move = [x for x in p.iterdir() if x.is_dir()]
    try:
        for item in dirs_to_move:
            move_dir(
                item, f"{FD["volumetric-map"]["downloads"]["publish"]}/{item.name}"
            )
        # update entries in published downloads.csv
        publish_entries(
            FD["volumetric-map"]["downloads-file"]["depot"],
            FD["volumetric-map"]["downloads-file"]["publish"],
            "Name",
        )
    except FileNotFoundError as err:
        app_logger.debug(traceback.print_exc())
        return ("Metadata not updated", f"{err}", "failure")
    except Exception:
        app_logger.debug(traceback.print_exc())
    return (
        "Metadata updated",
        "The configuration has been updated. Refresh the public-facing app to see the changes.",
        "success",
    )


def process_obj_files(file: bytes, filename: str) -> tuple[bool, str]:
    is_valid = is_valid_filename(filename)
    if not is_valid[0]:
        return False, is_valid[1]
    # process summary file
    if filename == "obj-files.xlsx":
        header_check = check_excel_headers(file, "obj-files", fillna=False)
        if header_check[0]:
            try:
                # add new entries to summary csv
                dest = Path(FD["obj-files"]["summary"]["depot"])
                if not Path.exists(dest):
                    Path.mkdir(dest, parents=True)
                df = update_entries(
                    f"{FD["obj-files"]["summary"]["depot"]}/obj-files.csv",
                    header_check[2]["files"],
                    "File",
                )
                df.to_csv(
                    f"{FD["obj-files"]["summary"]["depot"]}/obj-files.csv", index=False
                )
                return True, ""
            except Exception as err:
                return False, str(err)
        else:
            return False, header_check[1]
    # process any other file
    else:
        loc = FD["obj-files"]["volumes"]["depot"]
        try:
            return save_generic_file(loc, file, filename)
        except Exception as err:
            app_logger.debug(traceback.print_exc())
            return False, f"{err}"


def publish_obj_files():
    """Publishes 3D model files.
    Returns (title of update toast, description of update, success status)"""
    try:
        # move volumes directory
        p = Path(FD["obj-files"]["volumes"]["depot"])
        if Path.exists(p):
            move_dir(p, FD["obj-files"]["volumes"]["publish"])
        # update volume entries
        publish_entries(
            f"{FD["obj-files"]["summary"]["depot"]}/obj-files.csv",
            f"{FD["obj-files"]["summary"]["publish"]}/obj-files.csv",
            "File",
        )
        return (
            "Model files updated",
            "The configuration has been updated. Refresh the public-facing app to see the changes.",
            "success",
        )
    except Exception as err:
        app_logger.debug(traceback.print_exc())
        return ("Model files not updated", f"{err}", "failure")
