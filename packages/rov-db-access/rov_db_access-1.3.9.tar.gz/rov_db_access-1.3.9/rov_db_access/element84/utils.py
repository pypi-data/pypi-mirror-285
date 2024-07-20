import rasterio


def download_asset(asset, dest):
    with rasterio.open(asset.href) as src:
        arr = src.read()
        meta = src.meta.copy()

    with rasterio.open(dest, "w", **meta) as dst:
        dst.write(arr)
    