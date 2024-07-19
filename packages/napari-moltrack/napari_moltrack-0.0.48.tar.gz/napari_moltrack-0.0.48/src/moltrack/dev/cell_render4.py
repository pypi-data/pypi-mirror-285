import pandas as pd
import shapely
import numpy as np
import matplotlib.pyplot as plt
import json
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.strtree import STRtree
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count
from moltrack.bactfit.fit import BactFit
from moltrack.bactfit.cell import ModelCell, Cell, CellList
import traceback
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count, Manager
import pickle 

from moltrack.bactfit.cell import CellList, ModelCell
from moltrack.bactfit.preprocess import mask_to_cells, data_to_cells
from moltrack.bactfit.postprocess import cell_coordinate_transformation
from shapely.geometry import Polygon, Point, LineString, LinearRing


def plot_cell(cell):
    
    if hasattr(cell, "cell_polygon"):
        polygon = cell.cell_polygon
        polygon_coords = np.array(polygon.exterior.coords)
        plt.plot(*polygon_coords.T)
    
    if hasattr(cell, "locs"):
        cell.remove_locs_outside_cell()
        locs = cell.locs
        points = np.stack([locs.x,locs.y]).T
        plt.scatter(*points.T)
        
    plt.show()
    
    




model = ModelCell(length=10, width=5)



with open("segmentations.pkl", "rb") as f:
    segmentations = pickle.load(f)

locs = pd.read_csv("cell_tracks.csv")
locs = locs.to_records(index=False)

# import time

if __name__ == "__main__":
    
    # celllist = data_to_cells(segmentations)
    # celllist.add_localisations(locs)
    # celllist.optimise()

    # with open('celllist.pickle', 'wb') as handle:
    #     pickle.dump(celllist, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('celllist.pickle', 'rb') as handle:
        celllist = pickle.load(handle)
        
    
    
    
    celllist.add_localisations(locs)
    cell = celllist.data[22]
    
    plot_cell(cell)
    # cell.optimise()
    # plot_cell(cell)
    
    
    

    # cell = cell_coordinate_transformation(cell, model)
    
    # plot_cell(cell)
    
    # celllist.transform_locs(method="angular")

    
    


