from io import BytesIO
import streamlit as st
import geemap.foliumap as geemap
import geopandas as gpd
import zipfile
import tempfile
import os
import matplotlib.pyplot as plt
import ee

# Авторизация Earth Engine (нужна при первом запуске)
try:
    ee.Initialize()
except Exception:
    ee.Authenticate()
    ee.Initialize()

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

                # Выбор поля для раскраски
                st.sidebar.markdown("### Выберите поле для раскраски")
                column_to_color = st.sidebar.selectbox("Поле для окраски:", gdf.columns)

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

                # Палитра и стили
                unique_values = gdf[column_to_color].unique()
                unique_values.sort()
                palette = geemap.random_color_hex(len(unique_values))

                style_dict = {}
                for val, color in zip(unique_values, palette):
                    style_dict[str(val)] = {
                        "color": color,
                        "fillColor": color,
                        "width": 1,
                        "fillOpacity": 0.7,
                    }

                styled_fc = geemap.style_by_attribute(roi, column=column_to_color, style_dict=style_dict)

                # Добавление слоя с popup'ами
                popup_fields = [col for col in gdf.columns if gdf[col].dtype == 'object' or gdf[col].dtype.name == 'category']
                Map.addLayer(styled_fc, {}, "Styled Shapefile")
                Map.add_ee_layer_control()
                Map.addLayerControl()

                Map.setCenter(*gdf.geometry.centroid.iloc[0].coords[0], zoom=6)

                # Включение всплывающих подсказок
                Map.add_child(geemap.ee_tile_popup(styled_fc, fields=popup_fields))
            else:
                st.error("Shapefile (.shp) не найден в архиве.")

    with row1_col1:
        Map.to_streamlit(height=600)

if __name__ == "__main__":
    main()
