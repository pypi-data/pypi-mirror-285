import tifffile
import numpy as np
import cv2
import matplotlib.pyplot as plt
from moltrack.bactfit.fit import BactFit
from moltrack.bactfit.preprocess import mask_to_cells, data_to_cells
from shapely.geometry import Polygon, Point, LineString, LinearRing
from shapely.ops import nearest_points, split
from scipy.spatial.distance import cdist
import pickle


with open("segmentations.pkl", "rb") as f:
    segmentations = pickle.load(f)

if __name__ == "__main__":
    celllist = data_to_cells(segmentations)

    print(True)

    # cell = celllist.data[0]
    # cell.optimise()
    # print(cell.fit_error)

    # celllist.optimise(parallel=True)