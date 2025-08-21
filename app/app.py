"""
This is a streamlit application for visualizing resistograph data from a ZIP archive.

It allows users to upload a ZIP file containing resistograph data and nodes, and visualize the data with custom settings.

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
3. Select which columns you want to display using `st.pills`.
4. Enable/disable scale and graph options.

"""

import streamlit as st
import zipfile
import tempfile
import shutil
import os
import matplotlib.pyplot as plt
import io
import streamlit.components.v1 as components

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plot_resistograph_data import (
    read_resistograph_data,
    read_nodes,
    add_resistograph_data,
    add_resistograph_graphs,
    add_scale,
    add_all_scales_along_path
)

st.title("Resistograph Data Visualization")

# ---------------------------
# Sidebar nastavení
# ---------------------------
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

    st.sidebar.header("Volby")
    show_scale = st.sidebar.checkbox("Zobrazit pomocné měřítko", value=True)
    show_graphs = st.sidebar.checkbox("Zobrazit grafy podél dráhy", value=True)

    st.sidebar.header("Parametry grafů podél dráhy")
    yshift = st.sidebar.number_input("yshift", min_value=0, max_value=1000, value=100)
    yscale = st.sidebar.number_input("yscale", min_value=1, max_value=1000, value=20)

    return (window_length, polyorder, upper_limit, min_val, max_val, step,
            linewidth, cmap, scale_length, show_scale, show_graphs, yshift, yscale)


# ---------------------------
# Funkce na vykreslení
# ---------------------------
def plot_resistograph(resistograph_df, nodes_df, settings, selected_cols_bars, selected_cols_graphs):
    (window_length, polyorder, upper_limit, min_val, max_val, step, linewidth, cmap,
     scale_length, show_scale, show_graphs, yshift, yscale) = settings

    fig, [ax, cax] = plt.subplots(1, 2, figsize=(8, 6), gridspec_kw={'width_ratios': [40, 1]})
    ax.plot(nodes_df['x'], nodes_df['y'], 'o')

    if selected_cols_bars:
        add_resistograph_data(
            resistograph_df[selected_cols_bars], nodes_df, ax, cax,
            min=min_val, max=max_val, step=step, linewidth=linewidth,
            cmap=cmap
        )

    if show_graphs and selected_cols_graphs:
        add_resistograph_graphs(
            resistograph_df[selected_cols_graphs], nodes_df, ax,
            yshift=yshift, yscale=yscale
        )

    if show_scale:
        add_all_scales_along_path(ax, resistograph_df.columns, nodes_df, scale_length=scale_length)
        add_scale(ax)

    ax.set_aspect(1)
    plt.tight_layout()
    return fig


# ---------------------------
# Generátor Jupyter kódu
# ---------------------------
def generate_notebook_code(settings, selected_cols_bars, selected_cols_graphs):
    (window_length, polyorder, upper_limit, min_val, max_val, step, linewidth, cmap,
     scale_length, show_scale, show_graphs, yshift, yscale) = settings

    notebook_code = f"""
import zipfile
import tempfile
import shutil
import os
import matplotlib.pyplot as plt

from plot_resistograph_data import (
    read_resistograph_data,
    read_nodes,
    add_resistograph_data,
    add_resistograph_graphs,
    add_scale,
    add_all_scales_along_path
)

# ---- Nastavení ----
window_length = {window_length}
polyorder = {polyorder}
upper_limit = {upper_limit}

min_val = {min_val}
max_val = {max_val}
step = {step}
linewidth = {linewidth}
cmap = "{cmap}"
scale_length = {scale_length}

show_scale = {show_scale}
show_graphs = {show_graphs}
yshift = {yshift}
yscale = {yscale}

# ---- cesta k ZIP souboru ----
zip_file = "data.zip"   # změň na cestu k tvému ZIPu

temp_dir = tempfile.mkdtemp()
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(temp_dir)

resistograph_df = read_resistograph_data(
    temp_dir,
    upper_limit=upper_limit,
    window_length=window_length,
    polyorder=polyorder
)
nodes_df = read_nodes(temp_dir)

selected_cols_bars = {selected_cols_bars}
selected_cols_graphs = {selected_cols_graphs}

fig, [ax, cax] = plt.subplots(1, 2, figsize=(8, 6), gridspec_kw={{'width_ratios': [40, 1]}})
ax.plot(nodes_df['x'], nodes_df['y'], 'o')

if selected_cols_bars:
    add_resistograph_data(
        resistograph_df[selected_cols_bars], nodes_df, ax, cax,
        min=min_val, max=max_val, step=step, linewidth=linewidth,
        cmap=cmap
    )

if show_graphs and selected_cols_graphs:
    add_resistograph_graphs(
        resistograph_df[selected_cols_graphs], nodes_df, ax,
        yshift=yshift, yscale=yscale
    )

if show_scale:
    add_all_scales_along_path(ax, resistograph_df.columns, nodes_df, scale_length=scale_length)
    add_scale(ax)

ax.set_aspect(1)
plt.tight_layout()
plt.show()

shutil.rmtree(temp_dir)
"""
    return notebook_code


# ---------------------------
# Hlavní aplikace
# ---------------------------
settings = sidebar_settings()
tab1, tab2 = st.tabs(["Aplikace", "Jupyter kód"])

selected_cols_bars = []
selected_cols_graphs = []

with tab1:
    uploaded_file = st.file_uploader("Nahraj ZIP archiv s daty", type="zip")
    if uploaded_file:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "data.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.read())
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        data_dir = temp_dir + "/"

        (window_length, polyorder, upper_limit, min_val, max_val, step, linewidth, cmap,
         scale_length, show_scale, show_graphs, yshift, yscale) = settings

        resistograph_df = read_resistograph_data(
            data_dir,
            upper_limit=upper_limit,
            window_length=window_length,
            polyorder=polyorder
        )
        nodes_df = read_nodes(data_dir)

        all_cols = list(resistograph_df.columns)
        st.subheader("Vyberte sloupce pro pruhy")
        selected_cols_bars = st.pills("Sloupce pro pruhy", all_cols, default=all_cols, selection_mode='multi')

        if show_graphs:
            st.subheader("Vyberte sloupce pro grafy podél dráhy")
            selected_cols_graphs = st.pills("Sloupce pro grafy", all_cols, default=all_cols, selection_mode='multi', key="sec")

        fig = plot_resistograph(resistograph_df, nodes_df, settings, selected_cols_bars, selected_cols_graphs)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        st.image(buf.getvalue())

        shutil.rmtree(temp_dir)

with tab2:
    notebook_code = generate_notebook_code(settings, selected_cols_bars, selected_cols_graphs)
    st.code(notebook_code, language="python")
