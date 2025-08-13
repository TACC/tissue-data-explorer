FILE_DESTINATION = {
    "si-block": {
        "block-data": {"depot": "./depot/blocks.csv", "publish": "/config/blocks.csv"},
        "si-files": {
            "depot": "./depot/image-sets.csv",
            "publish": "/config/image-sets.csv",
        },
    },
    "volumetric-map": {
        "meta": {
            "depot": "./depot/volumetric-map",
            "publish": "/config/volumetric-map",
        },
        "downloads": {
            "depot": "./depot/volumetric-map",
            "publish": "/config/volumetric-map",
        },
        "downloads-file": {
            "depot": "./depot/volumetric-map/downloads.csv",
            "publish": "/config/volumetric-map/downloads.csv",
        },
    },
    "image-layer": {"depot": "./depot/layers", "publish": "/config/volumetric-map"},
    "obj-files": {
        "summary": {"depot": "./depot/obj", "publish": "/config/obj"},
        "volumes": {"depot": "./depot/obj/volumes", "publish": "/config/obj/volumes"},
    },
    "sci-images": {
        "depot": "./depot/scientific-images",
        "publish": "/config/scientific-images",
    },
    "thumbnails": {
        "publish": "/config/scientific-images/thumbnails",
        "catalog": "/config/scientific-images/thumbnails/thumbnails.csv",
    },
    "title": {"depot": "./config/labels.csv", "publish": "/config/labels.csv"},
    "reports": {"depot": "./depot/reports.csv", "publish": "/config/reports.csv"},
}
