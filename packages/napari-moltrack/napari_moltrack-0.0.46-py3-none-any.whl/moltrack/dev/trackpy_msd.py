import trackpy as tp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import numpy as np
from scipy.spatial.distance import squareform, pdist

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

for particle in df.particle.unique():
    
    particle_df = df[df.particle == particle].copy()
    particle_df = particle_df[["particle", "frame", "x", "y"]]
    
    # Calculate MSD using trackpy
    msd_df = tp.motion.msd(particle_df, mpp=pixel_size_um, fps=fps, max_lagtime=100)
    
    # Linear fit to first 10 points of msd vs time
    msd_values = msd_df['msd'].values
    time = msd_df['lagt'].values
    
    if len(time) >= 10 and len(msd_values) >= 10:  # Ensure there are enough points to fit
        slope, intercept = np.polyfit(time[:10], msd_values[:10], 1)
        apparent_diffusion = slope / 4  # the slope of MSD vs time gives 4D in 2D
        
        if apparent_diffusion > 0:
            diffusion_coefficients.append(apparent_diffusion)

bin_edges = np.histogram_bin_edges(diffusion_coefficients, bins=50)
bin_edges = bin_edges[2:]  # Removes the first bin edge

# Plotting the histogram of diffusion coefficients
plt.hist(diffusion_coefficients, bins=bin_edges)
plt.xlabel('Apparent Diffusion Coefficient ($\mu m^2/s$)')
plt.ylabel('Frequency')
plt.show()
