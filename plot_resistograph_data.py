# This file is part of the resistograph_meets_tomograph project.
# © 2025 Robert Mařík, Valentino Cristini
# Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0)
# See LICENSE file or https://creativecommons.org/licenses/by/4.0/
#%%
"""
This script visualizes resistograph data on a tomogram. It processes resistograph data files 
and node coordinates to generate a plot with resistograph data overlaid on a tomographic 
representation. The script includes functions for data loading, processing, and visualization.
Modules:
--------
- pandas: For data manipulation and analysis.
- numpy: For numerical operations.
- matplotlib.pyplot: For plotting.
- glob: For file path pattern matching.
- scipy.signal.savgol_filter: For smoothing data using the Savitzky-Golay filter.
- logging: For logging messages during execution.
- matplotlib.collections.LineCollection: For creating line collections in the plot.
Functions:
- get_args(): Parses command-line arguments for resistograph data visualization.
- read_nodes(data_dir): Reads and centers node coordinates from a CSV file.
- read_resistograph_file(filepath): Reads a resistograph data file and extracts the data section.
- read_resistograph_data(data_dir, upper_limit, window_length, polyorder): Reads and processes resistograph data from files in a directory.
- add_resistograph_data(df, nodes, ax, cax, min, max, step, linewidth, cmap, scale_length): Adds resistograph data to the plot.
- add_scale(ax): Adds a scale to the left of the plot.
- main(): Main function to visualize resistograph data on a tomogram.
Usage:
------
Run the script to visualize resistograph data. The script reads data from the specified directory, 
processes it, and generates a plot with resistograph data overlaid on a tomogram. The visualization 
parameters can be adjusted using command-line arguments or by modifying the default settings in the script.
Example:
--------
To run the script with default settings:
    python plot_resistograph_data.py
"""
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy.signal import savgol_filter
import logging
from matplotlib.collections import LineCollection
from matplotlib.transforms import Affine2D

# Logging configuration
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')

def get_args():
    """Parse command line arguments for resistograph data visualization.
    Returns:
    -------
    argparse.Namespace
        Parsed command line arguments.
    """
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Visualization of resistograph data on a tomogram.")
    
    # Filtr
    parser.add_argument("--window_length", type=int, default=201)
    parser.add_argument("--polyorder", type=int, default=3)
    parser.add_argument("--upper_limit", type=int, default=200)

    # Vizualizace
    parser.add_argument("--min", type=int, default=100)
    parser.add_argument("--max", type=int, default=200)
    parser.add_argument("--step", type=int, default=300)
    parser.add_argument("--linewidth", type=int, default=20)
    parser.add_argument("--cmap", type=str, default="gray")

    # Ostatní
    parser.add_argument("--data_dir", type=str, default="data/")
    parser.add_argument("--scale_length", type=int, default=250)

    return parser.parse_args()

# === Data Loading ===

def read_nodes(data_dir):
    """ Read nodes from a CSV file in the specified directory.
    The nodes are expected to be in a file named 'nodes.csv' and contain x, y coordinates.
    The method centers the nodes by subtracting the mean.

    Parameters:
    ----------
    data_dir : str
        Directory containing the nodes CSV file.

    Returns:
    -------
    pd.DataFrame
        DataFrame containing the nodes with centered coordinates.
    """
    if not data_dir.endswith('/'):
        data_dir += '/'
    path = f"{data_dir}nodes.csv"
    logging.info(f"Reading nodes from {path}")
    nodes = pd.read_csv(path, header=None)
    nodes -= nodes.mean(axis=0)
    nodes.columns = ['x', 'y']
    nodes.index = nodes.index + 1
    nodes.index.name = "sensor"
    return nodes

def read_resistograph_file(filepath):
    """ Read a resistograph data file and extract the data section.
    The method assumes the data starts after a line containing '[DATA]'.
    It returns a DataFrame with the resistograph data.

    Parameters:
    ----------
    filepath : str
        Path to the resistograph data file.

    Returns:
    -------
    pd.DataFrame
        DataFrame containing the resistograph data.
    """
    logging.info(f"Reading resistograph data from {filepath}")
    df = pd.read_csv(filepath, header=None)
    header_idx = np.argmax(df.iloc[:, 0] == '[DATA]')
    return df.iloc[header_idx + 1:].reset_index(drop=True).astype(float)

def read_resistograph_data(data_dir, upper_limit=0, window_length=201, polyorder=3):
    """ Read resistograph data from files in the specified directory.
    The method reads all files with the extension `.dpa` and extracts the data section.
    The processed data is stored in a pandas DataFrame.

    Parameters:
    ----------
    data_dir : str
        Directory containing resistograph data files.
    upper_limit : int
        Ignore the data deeper than this limit.
    window_length : int
        Window length for Savitzky-Golay filter.
    polyorder : int
        Polynomial order for Savitzky-Golay filter.

    Returns:
    -------
    pd.DataFrame
        DataFrame containing processed resistograph data.
    """
    if not data_dir.endswith('/'):
        data_dir += '/'
    filepaths = sorted(glob.glob(f"{data_dir}*.dpa"))
    data_frames = {i: read_resistograph_file(fp) for i, fp in enumerate(filepaths)}
    df = pd.concat(data_frames, axis=1)
    df.columns = [i[0] + 1 for i in df.columns]
    df.index = df.index / 100
    df.index.name = "depth/mm"
    df.columns.name = "position"
    df = df.loc[:upper_limit]
    # return df
    return df.apply(lambda col: savgol_filter(col, window_length, polyorder))

# === Plotting Functions ===

def add_resistograph_data(df, nodes, ax, cax, min=100, max=200, step=300, linewidth=20, cmap='gray'):
    """ Add resistograph data to the plot.

    Parameters:
    ----------
    df : pd.DataFrame
        DataFrame containing resistograph data.
    nodes : pd.DataFrame
        DataFrame containing nodes coordinates.
    ax : matplotlib.axes.Axes
        Axes object to plot the resistograph data on.
    cax : matplotlib.axes.Axes
        Axes object for the colorbar.
    min : int
        Minimum value for the color map.
    max : int
        Maximum value for the color map.
    step : int
        Step for downsampling the data for visualization.
    linewidth : int
        Line width for the resistograph lines.

    Returns:
    -------
    matplotlib.axes.Axes
        The axes with the resistograph data added.
    """
    logging.info(f"Adding resistograph data to the plot with {len(df.columns)} columns.")
    cmap = plt.get_cmap(cmap)
    norm = plt.Normalize(min, max)

    for pos in df.columns:
        drill_pos = get_drilling_start(pos, nodes)['coordinates']
        values = df[pos].values
        direction = -drill_pos / np.linalg.norm(drill_pos)

        depth = np.arange(len(values)) / 100000
        x, y = (depth.reshape(-1,1) * direction + drill_pos).T
        mask = ~np.isnan(values)
        x, y, values = x[mask], y[mask], np.clip(values[mask], min, max)

        segments = np.column_stack([x, y]).reshape(-1, 1, 2)[::step]
        segments = np.concatenate([segments[:-1], segments[1:]], axis=1)

        lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=linewidth#, alpha=1
                            )
        lc.set_array(values[::step])
        #lc.set_antialiaseds(False)
        ax.add_collection(lc)

    ax.axis('off')
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    plt.colorbar(sm, cax=cax)
    return ax

def add_scale(ax):
    """ Add a scale to the left of the plot.
    Parameters:
    ----------
    ax : matplotlib.axes.Axes
        Axes object to add the scale to.
    scale_length : int
        The length of the scale in mm (default is 250mm).

    Returns:
    -------
    matplotlib.axes.Axes
        The axes with the scale added.
    """
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    scale_segments = np.array([
        [[x0, y0], [x0 + 0.05, y0]],
        [[x0 + 0.05, y0], [x0 + 0.10, y0]]
    ])
    scale_colors = ['red', 'black']
    lc = LineCollection(scale_segments, colors=scale_colors, linewidth=8)
    ax.add_collection(lc)
    ax.text(x0 + 0.05, y0 - 0.005, '5cm', fontsize=10, ha='center', va='top')
    ax.text(x0 + 0.10, y0 - 0.005, '10cm', fontsize=10, ha='center', va='top')
    return ax

def get_drilling_start(i, nodes_df):
    """
    Get the starting point and angle of the drilling for a given index.

    Parameters
    ----------
    i : int
        Index of the drilling position.
    nodes_df : pd.DataFrame
        DataFrame containing node information.

    Returns
    -------
    dict
        A dictionary containing the coordinates and angle of the drilling start.
    """
    ncols = nodes_df.shape[0]
    j = i + 1 if i + 1 <= ncols else 1
    ox, oy = (nodes_df.loc[[i, j], ['x', 'y']].mean())
    angle = np.degrees(np.arctan2(-oy, -ox))
    return {'coordinates': np.array([ox, oy]), 'angle': angle}

def add_resistograph_graphs(resistograph_df, nodes_df, ax, yshift=100, yscale=20):
    """
    Add resistograph graphs to the plot.

    Parameters
    ----------
    resistograph_df : pd.DataFrame
        DataFrame containing resistograph data.
    nodes_df : pd.DataFrame
        DataFrame containing node information.
    ax : matplotlib.axes.Axes
        Axes object to add the graphs to.
    yshift : int
        Vertical shift for the graphs (default is 100).
    yscale : int
        Vertical scale for the graphs (default is 20).

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the resistograph graphs added.
    """
    resistograph_df = (
        (resistograph_df.index / 1000)
        .to_series()
        .pipe(lambda idx: resistograph_df.set_index(idx))
    )
    resistograph_df = ((resistograph_df - yshift).clip(lower=0))
    resistograph_df = resistograph_df.div(resistograph_df.max()).div(yscale)
    u = resistograph_df.index.values

    for i in resistograph_df.columns:
        driling_start = get_drilling_start(i, nodes_df)
        T = Affine2D().rotate_deg(driling_start['angle']).translate(*driling_start['coordinates'])
        v = resistograph_df[i].values
        trans = T + ax.transData
        ax.plot(u, v, transform=trans, color='C0')
        ax.fill_between(u, v, 0, where=v >= 0, transform=trans,
                        alpha=0.4, zorder=1000, color='C0')
    return ax

def add_scale_along_path(ax, drill_pos, scale_length=250, scale_step=50):
        """
        Add a scale along the path of the drill position.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axes object to add the scale to.
        drill_pos : np.ndarray
            The starting position of the drill.
        scale_length : int
            Length of the scale in mm (default is 250mm).
        scale_step : int
            Step size for the scale ticks in mm (default is 50mm).

        Returns
        -------
        matplotlib.axes.Axes
            The axes with the scale added.
        """
        # Scale visualization
        direction = -drill_pos / np.linalg.norm(drill_pos)

        tick_positions = np.arange(scale_length + 1, step=scale_step) / 1000
        xred = tick_positions * direction[0] + drill_pos[0]
        yred = tick_positions * direction[1] + drill_pos[1]

        tick_segments = np.column_stack([xred, yred]).reshape(-1, 1, 2)
        tick_segments = np.concatenate([tick_segments[:-1], tick_segments[1:]], axis=1)
        tick_colors = ['red' if i % 2 == 0 else 'black' for i in range(len(xred))]

        lc_ticks = LineCollection(tick_segments, colors=tick_colors, linewidth=4)
        ax.add_collection(lc_ticks) 
        return ax     

def add_all_scales_along_path(ax, drill_positions, nodes_df, scale_length=250):
    """
    Add scale bars along the path of the drill positions.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes object to add the scale bars to.
    drill_positions : list
        List of drill positions.
    nodes_df : pandas.DataFrame
        DataFrame containing node information.
    scale_length : int
        Length of the scale bars in mm (default is 250mm).

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the scale bars added.
    """
    for drill_pos in drill_positions:
        drill_coordinates = get_drilling_start(drill_pos, nodes_df)
        add_scale_along_path(ax, drill_coordinates['coordinates'], scale_length)     
    return ax   

# %%
# === Main ===

def main():
    """ Main function to visualize resistograph data on a tomogram.
    It reads the resistograph data and nodes, processes the data, and plots it.
    """

    data_dir = "data/"
    settings_filter = {
        'window_length': 201,
        'polyorder': 3,
        'upper_limit': 250
    }
    settings_plot = {
        'min': 100,
        'max': 200,
        'step': 200,
        'linewidth': 20,
        'cmap': 'gray'
    }
    settings_graphs = {
        'yshift': 100,
        'yscale': 20
    }
    scale_length = 250
    add_scale = True
    # subset of columns
    cols_bars = [1,2,3,4,5, 11, 12]
    cols_bars = []
    cols_graphs = [6,7,8,9,10]

    fig, [ax, cax] = plt.subplots(1, 2, figsize=(8, 6), gridspec_kw={'width_ratios': [40, 1]})
    resistograph_df = read_resistograph_data(data_dir, **settings_filter)
    nodes_df = read_nodes(data_dir)

    ax.plot(nodes_df['x'], nodes_df['y'], 'o')

    add_resistograph_data(resistograph_df.loc[:,cols_bars], nodes_df, ax, cax, **settings_plot)
    add_resistograph_graphs(resistograph_df.loc[:,cols_graphs], nodes_df, ax, **settings_graphs)
    if add_scale:
        add_all_scales_along_path(ax, resistograph_df.columns, nodes_df, scale_length=scale_length)
        add_scale(ax)
    #ax.axis('off')
    #cax.axis('off')

    ax.set_aspect(1)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

# %%
