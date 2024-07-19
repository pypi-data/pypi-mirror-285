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



model = ModelCell(length=10, width=5)



with open("segmentations.pkl", "rb") as f:
    segmentations = pickle.load(f)

locs = pd.read_csv("cell_tracks.csv")
locs = locs.to_records(index=False)

import time

if __name__ == "__main__":
    
    celllist = data_to_cells(segmentations)
    celllist.remove_locs_outside_cells(locs)
    
    cell = celllist.data[22]
    cell.optimise()
    
    # locs = cell.locs
    # locs = pd.DataFrame(locs)
    # locs = [locs]*10
    # locs = pd.concat(locs,axis=0)
    # locs = locs.to_records(index=False)
    # cell.locs = locs
    
    
    
    start_time = time.time()
    cell_coordinate_transformation(cell, model)
    end_time = time.time()
    
    print(f"elapsed time: {end_time-start_time}")
    
    


