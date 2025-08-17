"""
This is a streamlit application for visualizing resistograph data from a ZIP archive.

It allows users to upload a ZIP file containing resistograph data and nodes, and visualize the data

Instructions to run the code:

1. Install the required packages:
   ```
   pip install streamlit matplotlib pandas
   ```

2. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

Instructions to use the app:

1. Upload a ZIP file containing resistograph data and nodes.
2. Adjust the filter and visualization settings in the sidebar.
3. View the generated plots.

"""

import streamlit as st
import zipfile
import tempfile
import shutil
import os
import matplotlib.pyplot as plt

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plot_resistograph_data import read_resistograph_data, read_nodes, add_resistograph_data, add_scale

st.title("Resistograph Data Visualization")
def sidebar_settings():
    st.sidebar.header("Nastavení filtru")
    window_length = st.sidebar.number_input("Window length", min_value=3, value=201, step=2)
    polyorder = st.sidebar.number_input("Polyorder", min_value=1, value=3, step=1)
    upper_limit = st.sidebar.number_input("Upper limit (mm)", min_value=0, value=250, step=10)

    st.sidebar.header("Nastavení vizualizace")
    min_val = st.sidebar.number_input("Min", value=100, step=10)
    max_val = st.sidebar.number_input("Max", value=200, step=10)
    step = st.sidebar.number_input("Step", value=300, step=10)
    linewidth = st.sidebar.number_input("Line width", value=20, step=1)
    cmap = st.sidebar.selectbox("Colormap", ["gray", "viridis", "plasma", "inferno", "magma", "cividis"])
    scale_length = st.sidebar.number_input("Scale length (mm)", value=250, step=10)
    return window_length, polyorder, upper_limit, min_val, max_val, step, linewidth, cmap, scale_length

def handle_uploaded_file(uploaded_file, settings):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "data.zip")
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    data_dir = temp_dir + "/"
    fig = plot_resistograph(data_dir, settings)
    st.pyplot(fig)
    shutil.rmtree(temp_dir)

def plot_resistograph(data_dir, settings):
    window_length, polyorder, upper_limit, min_val, max_val, step, linewidth, cmap, scale_length = settings
    fig, [ax, cax] = plt.subplots(1, 2, figsize=(8, 6), gridspec_kw={'width_ratios': [40, 1]})
    resistograph_df = read_resistograph_data(
        data_dir,
        upper_limit=upper_limit,
        window_length=window_length,
        polyorder=polyorder
    )
    nodes_df = read_nodes(data_dir)
    ax.plot(nodes_df['x'], nodes_df['y'], 'o')
    add_resistograph_data(
        resistograph_df, nodes_df, ax, cax,
        min=min_val, max=max_val, step=step, linewidth=linewidth,
        cmap=cmap, scale_length=scale_length
    )
    add_scale(ax)
    ax.set_aspect(1)
    plt.tight_layout()
    return fig

settings = sidebar_settings()
uploaded_file = st.file_uploader("Nahraj ZIP archiv s daty", type="zip")
if uploaded_file:
    handle_uploaded_file(uploaded_file, settings)
