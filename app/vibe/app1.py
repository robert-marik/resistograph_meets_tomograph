import streamlit as st
import zipfile
import tempfile
import shutil
import os
import matplotlib.pyplot as plt
from plot_resistograph_data import read_resistograph_data, read_nodes, add_resistograph_data, add_scale

st.title("Resistograph Data Visualization")

uploaded_file = st.file_uploader("Nahraj ZIP archiv s daty", type="zip")

if uploaded_file:
    # Vytvoření dočasné složky
    temp_dir = tempfile.mkdtemp()

    # Rozbalení ZIP souboru
    zip_path = os.path.join(temp_dir, "data.zip")
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    data_dir = temp_dir + "/"

    # Parametry z main()
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
    scale_length = 250

    # Generování grafu
    fig, [ax, cax] = plt.subplots(1, 2, figsize=(8, 6), gridspec_kw={'width_ratios': [40, 1]})
    resistograph_df = read_resistograph_data(data_dir, **settings_filter)
    nodes_df = read_nodes(data_dir)

    ax.plot(nodes_df['x'], nodes_df['y'], 'o')
    add_resistograph_data(resistograph_df, nodes_df, ax, cax, scale_length=scale_length, **settings_plot)
    add_scale(ax)

    ax.set_aspect(1)
    plt.tight_layout()

    # Zobrazení ve Streamlitu
    st.pyplot(fig)

    # Úklid
    shutil.rmtree(temp_dir)
