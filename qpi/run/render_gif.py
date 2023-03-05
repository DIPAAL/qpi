import io
import os

import imageio.v2 as imageio
import matplotlib
import numpy as np
import psycopg2
import rasterio as rio
from matplotlib import colors
from rasterio.plot import show
import matplotlib.pyplot as plt

from qpi.helper_functions import get_connection

conn = get_connection()

query = """
SELECT dd.year AS year, dd.month_of_year AS month, dd.day_of_month AS day, ST_AsGDALRaster(ST_Union(dr.rast), 'COG') AS raster
FROM fact_cell_heatmap
JOIN dim_raster dr on fact_cell_heatmap.raster_id = dr.raster_id
JOIN dim_date dd on fact_cell_heatmap.date_id = dd.date_id
GROUP BY dd.year, dd.month_of_year, dd.day_of_month
"""

# if temp_results folder is empty besides .gitignore
if len(os.listdir("temp_results")) == 1:
    print("temp_results is empty, creating files")
    cur = conn.cursor()
    cur.execute(query)

    # fetch the returned COG geotiff
    geotiff_bin = cur.fetchall()

    # save the geotiffs to files
    for year, month, day, geotiff in geotiff_bin:
        with open(f"temp_results/{year}_{month}_{day}.tiff", "wb") as f:
            f.write(geotiff)

time_per_step = 0.1

files = [os.path.join("temp_results", f) for f in os.listdir("temp_results")]
files.sort()

sattelite = rio.open("references/danish_waters_3034.tiff")


def make_frame(f: str) -> io.BytesIO:
    with rio.open(f) as raster:
        fig, ax = plt.subplots(figsize=(20, 10))

        # show both rasters src and sattelite
        show(sattelite, ax=ax)

        # use a logarithmic colormap to show raster
        show(raster, ax=ax, cmap='turbo', norm=colors.LogNorm(vmin=1))



        # swarp the y axis
        ax.set_ylim(ax.get_ylim()[::-1])

        # add a title
        ax.set_title(f)

        # add a legend
        # sm = plt.cm.ScalarMappable(cmap="RdYlGn", norm=plt.Normalize(vmin=0, vmax=100))
        # sm._A = []
        # cbar = fig.colorbar(sm)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        plt.close(fig)
        return buffer


frames = [imageio.imread(make_frame(f)) for f in files]

frames = np.array(frames)
imageio.mimsave('out.mp4', frames, duration=time_per_step)
