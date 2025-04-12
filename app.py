from io import BytesIO
import streamlit as st
import geemap.foliumap as geemap
import geopandas as gpd
import zipfile
import tempfile
import os
import matplotlib.pyplot as plt
import ee
import random

# Кешируем функцию загрузки и обработки shapefile
@st.cache_resource
def load_shapefile(uploaded_shp_file):
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
            return gdf
    return None

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

    # Кнопка сброса
    if st.sidebar.button("Сбросить загрузку"):
        st.session_state.pop("user_colors", None)
        st.rerun()

    row1_col1, row1_col2 = st.columns([5, 1])
    row2_col1, row2_col2, row2_col3 = st.columns([1, 1, 1])

    Map = geemap.Map()

    uploaded_shp_file = st.sidebar.file_uploader("Загрузите архив с Shapefile (.zip)", type=["zip"])

    # Загрузка и кеширование GeoDataFrame
    if uploaded_shp_file is not None and "gdf" not in st.session_state:
        gdf = load_shapefile(uploaded_shp_file)
        if gdf is not None:
            st.session_state.gdf = gdf
            st.session_state.user_colors = {}  # сброс палитры при новой загрузке

    # Работа с загруженным gdf
    if "gdf" in st.session_state:
        gdf = st.session_state.gdf

        if gdf.empty:
            st.error("Shapefile прочитан, но он пустой.")
            return

        # Выпадающий список с placeholder
        column_to_color = st.sidebar.selectbox("##### Поля для окраски",
            options=gdf.columns,
            index=None,
            placeholder="Выберите поле для окраски"
        )

        if column_to_color:
            # Генерация и сохранение цветов
            unique_values = sorted(gdf[column_to_color].unique())
            st.sidebar.markdown("### Настройка цветов")

            if "user_colors" not in st.session_state:
                st.session_state.user_colors = {}

            rerun_needed = False

            for val in unique_values:
                val_str = str(val)
                if val_str not in st.session_state.user_colors:
                    st.session_state.user_colors[val_str] = "#" + ''.join(random.choices('0123456789ABCDEF', k=6))

            for val in unique_values:
                val_str = str(val)
                current_color = st.session_state.user_colors[val_str]
                new_color = st.sidebar.color_picker(
                    f"Цвет для «{val_str}»", current_color, key=f"color_{val_str}"
                )
                if new_color != current_color:
                    st.session_state.user_colors[val_str] = new_color
                    rerun_needed = True

            if rerun_needed:
                st.rerun()

            user_colors = st.session_state.user_colors

            # График
            gdf['color'] = gdf[column_to_color].astype(str).map(user_colors)
            fig, ax = plt.subplots()
            gdf.plot(ax=ax, color=gdf['color'])
            plt.xticks(rotation=90, fontsize=7)
            plt.yticks(fontsize=7)
            plt.title(f"Категории: {column_to_color}")

            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            with row2_col1:
                st.image(buf, caption=f"Зоны по полю: {column_to_color}", use_container_width=True)

            # 👉 Обновленная таблица с цветами
            with row2_col2:
                st.markdown("### Таблица данных")
                st.dataframe(gdf, use_container_width=True)

            # 💡 Стиль по полю и цвету
            def style_function(feature):
                val = str(feature["properties"].get(column_to_color))
                color = user_colors.get(val, "#3388ff")
                return {
                    "color": color,
                    "fillColor": color,
                    "weight": 1,
                    "fillOpacity": 0.5
                }

            Map.add_gdf(gdf, "Полигоны", style_function=style_function)

            # Центрирование карты
            centroid = gdf.geometry.centroid.iloc[0]
            Map.setCenter(centroid.x, centroid.y, zoom=6)

    # Отображение карты
    with row1_col1:
        Map.to_streamlit(height=600)


if __name__ == "__main__":
    main()
