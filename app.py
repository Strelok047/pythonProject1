from io import BytesIO
import streamlit as st
import geemap.foliumap as geemap
import geopandas as gpd
import zipfile
import tempfile
import os
import matplotlib.pyplot as plt

def setup():
    st.set_page_config(layout="wide", page_title="Satellite imagery", page_icon='🛰️')
    st.header("🛰️Satellite Imagery")

def Navbar():
    with st.sidebar:
        st.page_link('app.py', label='Satellite imagery', icon='🛰️')
        st.page_link('pages/graph.py', label='Graph', icon='📈')
        st.page_link('pages/about.py', label='About', icon='📖')

def main():
    setup()
    Navbar()

    row1_col1, row1_col2 = st.columns([5, 1])
    row2_col1, row2_col2, row2_col3 = st.columns([1, 1, 1])

    Map = geemap.Map()
    roi = None

    # Загрузка архива с шейп-файлом
    uploaded_shp_file = st.sidebar.file_uploader("Загрузите архив с Shapefile (.zip)", type=["zip"])

    if uploaded_shp_file is not None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(uploaded_shp_file, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

            shapefile_path = None
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    if file.endswith(".shp"):
                        shapefile_path = os.path.join(root, file)
                        break

            if shapefile_path:
                gdf = gpd.read_file(shapefile_path)

                # Отображение графика
                fig, ax = plt.subplots()
                gdf.plot(ax=ax)
                plt.xticks(rotation=90, fontsize=7)
                plt.yticks(fontsize=7)

                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)

                with row2_col1:
                    st.image(buf, caption='Geopandas Plot')
            else:
                st.error("Shapefile (.shp) not found in the uploaded zip file.")

            if not gdf.empty:
                roi = geemap.geopandas_to_ee(gdf)
                Map.centerObject(roi, zoom=10)
                Map.addLayer(roi, {}, "Shapefile Layer")

    with row1_col1:
        Map.to_streamlit(height=600)

if __name__ == "__main__":
    main()
