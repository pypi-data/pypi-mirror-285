
from moltrack.bactfit.cell import CellList, Cell, ModelCell
from moltrack.bactfit.fileIO import save, load
from shapely.geometry import Point
from moltrack.bactfit.preprocess import data_to_cells, mask_to_cells, get_polygon_midline
from moltrack.bactfit.postprocess import angular_pixel_transformation
import pickle
import tifffile
import matplotlib.pyplot as plt
import numpy as np




celllist = load("add_image_dev.h5")
model = ModelCell(length=50, width=5)


# images = []

# for cell_index, cell in enumerate(celllist.data):
    
#     cell = angular_pixel_transformation(cell, model)
    
#     image = cell.data["NR"]
#     images.append(image)
    
#     # celllist.data[cell_index] = cell
    
#     # break

# images = np.stack(images,axis=0)
# images = np.mean(images, axis=0)

# plt.imshow(images)
# plt.show()


cell = celllist.data[20]

angular_pixel_transformation(cell, model)

polygon_coords = cell


    
# cell_image = cell.get_image("NR")
# cell_mask = cell.get_image_mask()

# curr_dpts = np.product(cell_image.shape)

# polygon = cell.cell_polygon
# midline, width = get_polygon_midline(polygon)

# image_polygon = cell.get_image_polygon()
# cartesian_coords = cartesian_coords(image_polygon)

# cartesian_coords = np.array(cartesian_coords)


# plt.imshow(cell_image)
# plt.scatter(*cartesian_coords.T)
# plt.show()
# plt.imshow(cell_mask)
# plt.show()


# centroid = midline.centroid

# # Get the coordinates of the centroid
# centroid_coords = (centroid.x, centroid.y)
    
