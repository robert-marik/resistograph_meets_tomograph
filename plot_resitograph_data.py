#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy.signal import savgol_filter
import logging
from matplotlib.collections import LineCollection

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
    parser.add_argument("--meter_length", type=int, default=250)

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

def add_resistograph_data(df, nodes, ax, cax, min=100, max=200, step=300, linewidth=20, cmap='gray', meter_length=250):
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
        neighbor = pos + 1 if pos < 12 else 1
        drill_pos = 0.5 * (nodes.loc[pos] + nodes.loc[neighbor])
        values = df[pos].values
        direction = -drill_pos / np.linalg.norm(drill_pos)

        depth = np.arange(len(values)) / 100000
        x = depth * direction['x'] + drill_pos['x']
        y = depth * direction['y'] + drill_pos['y']

        mask = ~np.isnan(values)
        x, y, values = x[mask], y[mask], np.clip(values[mask], min, max)

        segments = np.column_stack([x, y]).reshape(-1, 1, 2)[::step]
        segments = np.concatenate([segments[:-1], segments[1:]], axis=1)

        lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=linewidth)
        lc.set_array(values[::step])
        ax.add_collection(lc)

        # Meter visualization
        tick_positions = np.arange(meter_length + 1, step=50) / 1000
        xred = tick_positions * direction['x'] + drill_pos['x']
        yred = tick_positions * direction['y'] + drill_pos['y']

        tick_segments = np.column_stack([xred, yred]).reshape(-1, 1, 2)
        tick_segments = np.concatenate([tick_segments[:-1], tick_segments[1:]], axis=1)
        tick_colors = ['red' if i % 2 == 0 else 'black' for i in range(len(xred))]

        lc_ticks = LineCollection(tick_segments, colors=tick_colors, linewidth=4)
        ax.add_collection(lc_ticks)

    ax.axis('off')
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    plt.colorbar(sm, cax=cax)
    return ax

def add_scale(ax, meter_length=250):
    """ Add a scale to the left of the plot.
    Parameters:
    ----------
    ax : matplotlib.axes.Axes
        Axes object to add the scale to.
    meter_length : int
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
        'step': 300,
        'linewidth': 20,
        'cmap': 'gray'
    }
    meter_length = 250

    fig, [ax, cax] = plt.subplots(1, 2, figsize=(8, 6), gridspec_kw={'width_ratios': [40, 1]})
    resistograph_df = read_resistograph_data(data_dir, **settings_filter)
    nodes_df = read_nodes(data_dir)

    ax.plot(nodes_df['x'], nodes_df['y'], 'o')
    add_resistograph_data(resistograph_df, nodes_df, ax, cax, meter_length=meter_length, **settings_plot)
    add_scale(ax, meter_length)

    ax.set_aspect(1)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

# %%
