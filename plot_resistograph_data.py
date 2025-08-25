# This file is part of the resistograph_meets_tomograph project.
# © 2025 Robert Mařík, Valentino Cristini
# Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0)
# See LICENSE file or https://creativecommons.org/licenses/by/4.0/
#%%
"""
This script visualizes resistograph data on a tomogram. 
It processes resistograph data files and node coordinates to generate a plot 
with resistograph data overlaid on a tomographic representation.

Configuration and validation are handled via Pydantic models.
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

# --- NEW: importy pro konfiguraci ---
from pydantic import BaseModel, Field, PositiveInt, DirectoryPath, model_validator
from typing import List, Optional

# Logging configuration
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')

# --- NEW: Pydantic models for configuration ---
class FilterSettings(BaseModel):
    window_length: PositiveInt = Field(201, description="Window length for Savitzky-Golay filter")
    polyorder: int = Field(3, description="Polynomial order for filter")
    upper_limit: int = Field(250, description="Maximum depth in mm")

    @model_validator(mode="after")
    def check_polyorder_vs_window(self):
        if self.polyorder >= self.window_length:
            raise ValueError("polyorder must be smaller than window_length")
        return self


class PlotSettings(BaseModel):
    min: int = Field(100, description="Minimum value for color normalization")
    max: int = Field(200, description="Maximum value for color normalization")
    step: int = Field(200, description="Step for downsampling")
    linewidth: int = Field(20, description="Line width")
    cmap: str = Field("gray", description="Matplotlib colormap")

    @model_validator(mode="after")
    def check_min_max(self):
        if self.max <= self.min:
            raise ValueError("max must be greater than min")
        return self


class GraphSettings(BaseModel):
    yshift: int = Field(100, description="Vertical shift for graphs")
    yscale: int = Field(20, description="Vertical scale factor")
    color: str = Field("C0", description="Color for graphs")


class AppConfig(BaseModel):
    data_dir: DirectoryPath = Field("data/", description="Path to data directory")
    scale_length: int = Field(250, description="Scale bar length in mm")
    add_scale: bool = True

    filter: FilterSettings = FilterSettings()
    plot: PlotSettings = PlotSettings()
    graphs: GraphSettings = GraphSettings()

    cols_bars: Optional[List[int]] = None
    cols_graphs: Optional[List[int]] = None

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

        lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=linewidth)
        lc.set_array(values[::step])
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


def add_resistograph_graphs(resistograph_df, nodes_df, ax, yshift=100, yscale=20, color='C0'):
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
        ax.plot(u, v, transform=trans, color=color)
        ax.fill_between(u, v, 0, where=v >= 0, transform=trans,
                        alpha=0.4, zorder=1000, color=color)
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
import typer
from typing import List

app = typer.Typer()

@app.command()
def main(
    window_length: int = typer.Option(
        201, help="Window length for Savitzky-Golay filter (must be bigger than polyorder)"),
    polyorder: int = typer.Option(
        3, min=1, help="Polynomial order for filter (must be smaller than window_length)"),
    upper_limit: int = 200,
    min: int = 100,
    max: int = 200,
    step: int = 300,
    linewidth: int = 20,
    cmap: str = "gray",
    yshift: int = 100,
    yscale: int = 20,
    color: str = "C0",
    data_dir: str = "data/",
    scale_length: int = 250,
):
    """ Main function to visualize resistograph data on a tomogram.
    It reads the resistograph data and nodes, processes the data, and plots it.
    """

    config = AppConfig(
        data_dir=data_dir,  # může zůstat stejné
        filter=FilterSettings(
            window_length=window_length, 
            polyorder=polyorder, 
            upper_limit=upper_limit),
        plot=PlotSettings(
            min=min, 
            max=max, 
            linewidth=linewidth, 
            cmap=cmap, 
            step=step),
        graphs=GraphSettings(
            yshift=yshift, 
            yscale=yscale, 
            color=color),
        scale_length=scale_length,
        cols_bars = [1,2,3,4,5,6,7,8,9,10,11,12],
        cols_graphs = [1,2,3,4,5,6,7,8,9,10,11,12],
        )    

    fig, [ax, cax] = plt.subplots(1, 2, figsize=(8, 6), gridspec_kw={'width_ratios': [40, 1]})
    resistograph_df = read_resistograph_data(str(config.data_dir), **config.filter.model_dump())
    nodes_df = read_nodes(str(config.data_dir))

    ax.plot(nodes_df['x'], nodes_df['y'], 'o')

    if config.cols_bars:
        add_resistograph_data(resistograph_df.loc[:,config.cols_bars], nodes_df, ax, cax, **config.plot.model_dump())
    if config.cols_graphs:
        add_resistograph_graphs(resistograph_df.loc[:,config.cols_graphs], nodes_df, ax, **config.graphs.model_dump())

    if config.add_scale:
        add_all_scales_along_path(ax, resistograph_df.columns, nodes_df, scale_length=config.scale_length)
        add_scale(ax)

    ax.set_aspect(1)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    app()
