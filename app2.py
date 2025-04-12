from io import BytesIO
import streamlit as st
import geemap
from geemap.foliumap import Map
import geopandas as gpd
import zipfile
import tempfile
import os
import matplotlib.pyplot as plt
import ee
import random

def setup():
    st.set_page_config(layout="wide", page_title="Satellite imagery", page_icon='🛰️')
    st.header("🛰️ Satellite Imagery")

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

    MapObj = Map()
    roi = None

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

                if gdf.empty:
                    st.error("Файл прочитан, но в нём нет данных.")
                    return

                # Выбор поля для окраски
                st.sidebar.markdown("### Выберите поле для раскраски")
                column_to_color = st.sidebar.selectbox("Поле для окраски:", gdf.columns)

                # Получаем уникальные значения
                unique_values = sorted(gdf[column_to_color].unique())

                # UI: выбор цвета для каждого значения
                st.sidebar.markdown("### Настройка цветов")
                user_colors = {}
                for val in unique_values:
                    user_colors[str(val)] = st.sidebar.color_picker(
                        f"Цвет для «{val}»", "#" + ''.join(random.choices('0123456789ABCDEF', k=6))
                    )

                # Формируем словарь стилей
                style_dict = {
                    str(val): {
                        "color": user_colors[str(val)],
                        "fillColor": user_colors[str(val)],
                        "width": 1,
                        "fillOpacity": 0.7,
                    }
                    for val in unique_values
                }

                # Отображение matplotlib-графика
                fig, ax = plt.subplots()
                gdf.plot(ax=ax, column=column_to_color, legend=True)
                plt.xticks(rotation=90, fontsize=7)
                plt.yticks(fontsize=7)
                plt.title("Агроклиматические зоны")

                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)

                with row2_col1:
                    st.image(buf, caption=f"Зоны по: {column_to_color}")

                # Преобразование в ee.FeatureCollection
                roi = geemap.geopandas_to_ee(gdf)

            else:
                st.error("Shapefile (.shp) не найден в архиве.")

    with row1_col1:
        MapObj.to_streamlit(height=600)


if __name__ == "__main__":
    main()
