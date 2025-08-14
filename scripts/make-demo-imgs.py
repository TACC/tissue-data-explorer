import numpy as np
from PIL import Image

"""
This script was used to create the images used in the test data for the image viewer 
and the layered images in the volumetric map vidualization.
"""

stacks = [
    (5, 1, (600, 600), "S1-1-1"),
    (1, 5, (500, 1000), "S1-1-2"),
    (5, 5, (500, 1000), "S1-1-3"),
    (10, 2, (500, 1000), "S1-7-1"),
    (3, 3, (600, 300), "S1-7-2"),
    (1, 1, (600, 600), "S1-14-1"),
    # (1, 1, (600, 1000), "S1-12"),
]

for dim_set in stacks:
    stack = []
    # set the area where the cluster of points will occur
    loc_x = np.random.randint(low=0, high=dim_set[2][0])
    loc_y = np.random.randint(low=0, high=dim_set[2][1])

    for i in range(dim_set[1]):
        channel = []
        for j in range(dim_set[0]):
            # make all-black array
            imarray = np.zeros(shape=(dim_set[2][0], dim_set[2][1], 3), dtype=np.int16)
            # make an all-white array
            # imarray = np.full(
            #     shape=(dim_set[2][0], dim_set[2][1], 3), dtype=np.uint8, fill_value=255
            # )

            # generate x and y positions
            cluster_size = 10000
            x = np.random.normal(
                loc=loc_x, scale=dim_set[2][0] // 20, size=cluster_size
            )
            y = np.random.normal(
                loc=loc_y, scale=dim_set[2][1] // 20, size=cluster_size
            )
            # set the points where x and y are true
            for k in range(cluster_size):
                this_x = int(x[k] // 1) % dim_set[2][0]
                this_y = int(y[k] // 1) % dim_set[2][1]
                val = np.random.rand(1) * 255
                if i == 0:
                    # first channel gets white image
                    imarray[this_x, this_y, 0] = val
                    imarray[this_x, this_y, 1] = val
                    imarray[this_x, this_y, 2] = val
                elif i == 1:
                    # red
                    imarray[this_x, this_y, 0] = val
                    # to make an image with a white background, the other color values need to be set to 0
                    # imarray[this_x, this_y, 1] = 0
                    # imarray[this_x, this_y, 2] = 0
                elif i == 2:
                    # green
                    imarray[this_x, this_y, 1] = val
                elif i == 3:
                    # blue
                    imarray[this_x, this_y, 2] = val
                elif i == 4:
                    # purple
                    imarray[this_x, this_y, 0] = val
                    imarray[this_x, this_y, 2] = val
            im = Image.fromarray(imarray.astype("uint8")).convert("RGB")
            # save to PNG
            im.save(f"./output/{dim_set[3]}_C{i}{j:04}.png")
            # append to channel
            channel.append(im)
        channel[0].save(
            f"./output/{dim_set[3]}_C{i}.tif", save_all=True, append_images=channel[1:]
        )
