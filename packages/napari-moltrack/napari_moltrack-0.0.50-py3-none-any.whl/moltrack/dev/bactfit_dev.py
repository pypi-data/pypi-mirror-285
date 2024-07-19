import tifffile
import numpy as np
import cv2
import matplotlib.pyplot as plt
from moltrack.bactfit.fit import BactFit
from shapely.geometry import Polygon, Point, LineString, LinearRing
from shapely.ops import nearest_points, split
from scipy.spatial.distance import cdist

mask_path = r"/moltrack/dev/mask.tif"

mask = tifffile.imread(mask_path)

mask_ids = np.unique(mask)

def get_polygon_coords(mask, mask_id):

    cell_mask = np.zeros(mask.shape,dtype = np.uint8)
    cell_mask[mask==mask_id] = 255

    contours, _ = cv2.findContours(cell_mask,
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    cnt = contours[0]

    x, y, w, h = cv2.boundingRect(cnt)
    y1, y2, x1, x2 = y, (y + h), x, (x + w)

    polygon_coords = cnt.reshape(-1,2)

    return polygon_coords


def get_boundary_lines(centerline, polygon):
    try:
        polygon_coords = np.array(polygon.exterior.coords)

        start_point = centerline.coords[0]
        end_point = centerline.coords[-1]

        start_index = np.argmin(cdist(polygon_coords, [start_point]))
        end_index = np.argmin(cdist(polygon_coords, [end_point]))

        start_point = polygon_coords[start_index]
        end_point = polygon_coords[end_index]

        if end_index < start_index:
            length = len(polygon_coords) - start_index + end_index
        else:
            length = end_index - start_index

        # rotate polygon so that start point is at the beginning
        polygon_coords = np.concatenate([polygon_coords[start_index:], polygon_coords[:start_index]], axis=0)
        left_coords = polygon_coords[:length + 1]
        right_coords = polygon_coords[length:]
        right_coords = np.concatenate([right_coords, [polygon_coords[0]]], axis=0)

        # check start of left_coords is equal to start_point, else flip
        if not np.allclose(left_coords[0], start_point):
            left_coords = np.flip(left_coords, axis=0)
        if not np.allclose(right_coords[0], start_point):
            right_coords = np.flip(right_coords, axis=0)

    except:
        left_coords = None
        right_coords = None

    return left_coords, right_coords


def get_mesh(left_coords, right_coords, centerline_coords, n_segments=50, bisector_length=100):
    try:
        line_resolution = n_segments * 10
        centerline = LineString(centerline_coords)

        # resize left and right lines to have the same number of points
        right_line = LineString(right_coords)
        left_line = LineString(left_coords)
        right_line = bf.resize_line(right_line, line_resolution)
        left_line = bf.resize_line(left_line, line_resolution)
        right_coords = np.array(right_line.coords)
        left_coords = np.array(left_line.coords)

        left_indices = []
        right_indices = []

        distances = np.linspace(0, centerline.length, n_segments)
        centerline_segments = [LineString([centerline.interpolate(distance - 0.01), centerline.interpolate(distance + 0.01)]) for distance in distances]

        centerline_segments = centerline_segments[1:-1]

        # iterate over centerline segments and find intersection with left and right lines
        for segment in centerline_segments:
            left_bisector = segment.parallel_offset(bisector_length, 'left')
            right_bisector = segment.parallel_offset(bisector_length, 'right')

            left_bisector = left_bisector.boundary.geoms[1]
            right_bisector = right_bisector.boundary.geoms[0]

            bisector = LineString([left_bisector, right_bisector])

            left_intersection = bisector.intersection(left_line)
            right_intersection = bisector.intersection(right_line)

            if left_intersection.geom_type == "Point" and right_intersection.geom_type == "Point":
                left_index = np.argmin(cdist(left_coords, [left_intersection.coords[0]]))
                right_index = np.argmin(cdist(right_coords, [right_intersection.coords[0]]))

                # check if indices are already in list
                if len(left_indices) == 0:
                    left_indices.append(left_index)
                    right_indices.append(right_index)
                else:
                    # ensure that indices are always increasing
                    max_left = max(left_indices)
                    max_right = max(right_indices)

                    if max_left > left_index:
                        max_left += 1
                        if max_left > len(left_coords) - 2:
                            left_index = None
                        else:
                            left_index = max_left

                    if max_right > right_index:
                        max_right += 1
                        if max_left > len(right_coords) - 2:
                            right_index = None
                        else:
                            right_index = max_right

                    if left_index is not None and right_index is not None:
                        left_indices.append(left_index)
                        right_indices.append(right_index)

        # add start and end points to indices
        left_indices.insert(0, 0)
        right_indices.insert(0, 0)
        left_indices.append(len(left_coords) - 1)
        right_indices.append(len(right_coords) - 1)

        # get coordinates from indices
        left_coords = left_coords[np.array(left_indices)]
        right_coords = right_coords[np.array(right_indices)]
        
        mesh = np.hstack((left_coords, right_coords))
        model = np.vstack((left_coords, np.flipud(right_coords)))

        mesh = mesh + 1
        model = model + 1

    except:
        left_coords = None
        right_coords = None
        mesh = None
        model = None

    return left_coords, right_coords




mask_ids = [30]
mask_id = mask_ids[0]

polygon_coords = get_polygon_coords(mask, mask_id)
polygon = Polygon(polygon_coords)

bf = BactFit()

vertical = bf.get_vertical(polygon)

if vertical:
    polygon = BactFit.rotate_polygon(polygon)

medial_axis_coords, radius = BactFit.get_polygon_medial_axis(polygon)

medial_axis_fit, poly_params = BactFit.fit_poly(medial_axis_coords,
    degree=[1, 2, 3], maxiter=100, minimise_curvature=False)

midline = LineString(medial_axis_fit)
polygon = midline.buffer(radius)

centerline = bf.find_centerline(midline, radius)
centerline_coords = np.array(centerline.coords)

left_coords, right_coords = get_boundary_lines(centerline, polygon)

left_coords, right_coords = get_mesh(left_coords, right_coords, 
                                     centerline_coords, n_segments=50)



# left_coords, right_coords = mesh[:len(mesh) // 2], mesh[len(mesh) // 2:]




# print(start_point, end_point)
# print(left_coords[0], left_coords[-1])
# print(right_coords[0], right_coords[-1])

# left_coords, right_coords, centerline_coords = get_boundary_lines(centerline, polygon)

# midline_coords = np.array(midline.coords)
# centerline_coords = np.array(centerline.coords)
# polygon_coords = np.array(polygon.exterior.coords)



# plt.plot(*midline_coords.T)
plt.plot(*centerline_coords.T)
# plt.plot(*polygon_coords.T)
plt.plot(*left_coords.T)
plt.plot(*right_coords.T)
# plt.plot(*centerline_coords.T)

plt.show()


