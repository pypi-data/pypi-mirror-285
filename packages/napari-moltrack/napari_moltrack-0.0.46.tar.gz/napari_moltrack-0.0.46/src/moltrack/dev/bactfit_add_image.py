
from moltrack.bactfit.cell import CellList, Cell
from moltrack.bactfit.fileIO import save, load
from moltrack.bactfit.preprocess import data_to_cells, mask_to_cells
import pickle
import tifffile
import matplotlib.pyplot as plt
import numpy as np


mask = tifffile.imread("NIM_MASK.tif")
image2 = tifffile.imread("NIM_DAPI.tif")
image1 = tifffile.imread("NIM_NR.tif")

# cells = []

# for mask_id in np.unique(mask):
    
#     if mask_id > 0:
        
#         cell_mask = np.zeros(mask.shape)
#         cell_mask[mask==mask_id] = 255
        
#         Cell(cell_mask)
        
#         cells.append(Cell(cell_mask))
        
# celllist = CellList(cells)        





celllist = mask_to_cells(mask)
celllist.add_image(image1, "NR")

save("add_image_dev.h5", celllist)
celllist = load("add_image_dev.h5")


cell = celllist.data[20]

cell_image = cell.get_image("NR")
cell_mask = cell.get_image_mask()

plt.imshow(cell_image)
plt.show()
plt.imshow(cell_mask)
plt.show()
