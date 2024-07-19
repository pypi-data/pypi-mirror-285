import trackpy as tp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import numpy as np
from scipy.spatial.distance import squareform, pdist
import pickle
import time
from numba import njit



@njit
def calculate_msd_numba(x_disp, y_disp, max_lag):
    msd_list = np.zeros(max_lag + 1)
    for lag in range(1, max_lag + 1):
        squared_displacements = np.zeros(len(x_disp) - lag)
        for i in range(len(x_disp) - lag):
            dx = np.sum(x_disp[i:i+lag])
            dy = np.sum(y_disp[i:i+lag])
            squared_displacements[i] = dx**2 + dy**2
        msd_list[lag] = np.mean(squared_displacements)
    return msd_list

def calculate_track_stats(df, pixel_size, time_step):
    # Convert columns to numpy arrays for faster computation
    x = df['x'].values
    y = df['y'].values

    # Calculate the displacements using numpy diff
    x_disp = np.diff(x, prepend=x[0]) * pixel_size
    y_disp = np.diff(y, prepend=y[0]) * pixel_size

    # Calculate the squared displacements
    sq_disp = x_disp**2 + y_disp**2

    # Calculate the MSD using numba
    max_lag = len(x) - 1
    msd_list = calculate_msd_numba(x_disp, y_disp, max_lag)

    # Calculate speed
    speed = np.sqrt(x_disp**2 + y_disp**2) / time_step

    # Create time array
    time = np.arange(0, max_lag + 1) * time_step
    
    if len(time) >= 4 and len(msd_list) >= 4:  # Ensure there are enough points to fit
        slope, intercept = np.polyfit(time[:4], msd_list[:4], 1)
        apparent_diffusion = abs(slope / 4)  # the slope of MSD vs time gives 4D in 2D
    else:
        apparent_diffusion = 0

    # Append results to the dataframe
    df['x_disp'] = x_disp
    df['y_disp'] = y_disp
    df['sq_disp'] = sq_disp
    df['lagt'] = time
    df['msd'] = msd_list
    df["diffusion"] = apparent_diffusion
    df['speed'] = speed

    return df



path = r"D:\1 Rho-PAmCherry FOV\24-05-02 RhoPAM-plasmid-NusGsfGFP poorM9_17.03.43_18_Channel1_moltrack_tracks.csv"
path = r"D:\1 Rho-PAmCherry FOV\24-05-02 RhoPAM-plasmid-NusGsfGFP poorM9_17.03.43_18_dataset_channel_moltrack_tracks.csv"

df = pd.read_csv(path, sep=",")

# Constants for the conversion
pixel_size_nm = 100
pixel_size_um = 100 *1e-3
exposure_time_ms = 10
exposure_time_s = exposure_time_ms * 1e-3
fps = 1 / exposure_time_s

diffusion_coefficients = []

msd_values = []

time_start = time.time()

for particle in df.particle.unique():
    
    particle_df = df[df.particle == particle].copy()
    particle_df = particle_df[["particle", "frame", "x", "y"]]
    
    
    msd_df = calculate_track_stats(particle_df, 
                                    pixel_size_um, 
                                    exposure_time_s)
    
    msd_values.append(msd_df)
    
    # # Calculate MSD using trackpy
    # msd_df = tp.motion.msd(particle_df, mpp=pixel_size_um, fps=fps, max_lagtime=100)
    
    # msd_df = msd_df[["lagt","msd"]]
    
    # msd_df = msd_df[msd_df["msd"] > 0]
    
    # msd_values.append(msd_df)
    
    # break
    
    
time_end = time.time()
time_elapsed = time_end-time_start

print(f"time elapsed: {time_elapsed}")


# with open('msd.pkl', 'wb') as f:
#     pickle.dump(msd_values, f)

# with open('msd.pkl', "rb") as f:
#     msd_values = pickle.load(f)
    
msd_values = pd.concat(msd_values)
msd_values = msd_values.reset_index(drop=True)

grouped = msd_values.groupby('lagt')['msd'].agg(['mean', 'std',"sem"]).reset_index()

grouped = grouped.iloc[:100]

plt.figure(figsize=(10, 6))
plt.errorbar(grouped['lagt'], grouped['mean'], yerr=grouped['sem'], fmt='o', capsize=5, capthick=2)
plt.xlabel('Time (S)')
plt.ylabel('Mean MSD')
plt.title('Mean MSD with Error Bars')
plt.grid(True)
plt.show()
    




    
    # print(len(msd_df), len(particle_df))

    
    # break
    
    
#     # Linear fit to first 10 points of msd vs time
#     msd_values = msd_df['msd'].values
#     time = msd_df['lagt'].values
    
#     if len(time) >= 10 and len(msd_values) >= 10:  # Ensure there are enough points to fit
#         slope, intercept = np.polyfit(time[:10], msd_values[:10], 1)
#         apparent_diffusion = slope / 4  # the slope of MSD vs time gives 4D in 2D
        
#         if apparent_diffusion > 0:
#             diffusion_coefficients.append(apparent_diffusion)

# bin_edges = np.histogram_bin_edges(diffusion_coefficients, bins=50)
# bin_edges = bin_edges[2:]  # Removes the first bin edge

# # Plotting the histogram of diffusion coefficients
# plt.hist(diffusion_coefficients, bins=bin_edges)
# plt.xlabel('Apparent Diffusion Coefficient ($\mu m^2/s$)')
# plt.ylabel('Frequency')
# plt.show()
