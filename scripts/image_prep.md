# Preparing optical clearing files for display on the website
This document details how to use the `convert-czi-to-png.ijm` script to create PNG images that are 600px or less in height and an appropriate resolution for display on the website. This ensures that the images will fit on the viewer page and the website will load in a reasonable timeframe.

This script has not been tested with source files of types other than .czi, but can potentially be adapted for other file types.

## Generate PNGs from CZI files

1. Download the original image files

2. Move all .czi files into their own folder, and sort them into subfolders by tissue block

3. Replace any parentheses in filenames

4. Update `scripts/convert-czi-to-png.ijm` with the locations of the input folder and a destination folder. Then, run the macro. If the macro fails, you may need to separate out the largest files for another run.

5. Once you have completed a successful run of the ImageJ macro, save the output file `oc-dims.csv` in another location to preserve its content, and proceed with processing any leftover files. For large .czi files, this probably means running the script again just on those files. If you have to do this multiple times, save the content of `oc-dims.csv` elsewhere after each successful run because the file will be overwritten on the next run. 

6. Once all of the images have been converted to PNGs, use the `oc-dims.csv` output to create a new entry for each image set in the `si-files` tab of the image metadata spreadsheet. Make sure each value in the "Image Set" column is unique.

7. Upload the image metadata spreadsheet to the section of the configuration portal titled "Update tissue block and scientific image metadata".

8. Upload the PNGs and source files to the section of the configuration portal titled "Update scientific images".

9. Test that individual pages are working for each new optical clearing file.

## Manually processing images in Fiji
The `convert-czi-to-png.ijm` macro automates steps that can be performed manually in the Fiji image editing software. Here are some examples for source files of other types.
  * For .jpg files, resize the file if its height is greater than 600px, and save a copy of the file as a .png.
  * For .avi files, create an image sequence by opening the file in Fiji, then selecting Save As.. -> Image Sequence. 
    * Set the directory to your preference
    * Set format as PNG
    * Add the characters _C0 to the end of the filename (for consistency with how `scripts/convert-czi-to-png.ijm` names files)
    * Start at: 0
    * Digits: 4
  * Create an entry for each image set in the `si-files` tab of the image metadata spreadsheet.
