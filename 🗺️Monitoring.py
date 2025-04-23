from io import BytesIO
import streamlit as st
import geemap.foliumap as geemap
import geopandas as gpd
import zipfile
import tempfile
import os
import matplotlib.pyplot as plt
import random

def setup():
    st.set_page_config(layout="wide", page_title="Monitoring", page_icon='🗺️')
    st.header("🗺️️Monitoring")

# def Navbar():
#     with st.sidebar:
#         st.page_link('🗺️Monitoring.py', label='Monitoring', icon='🗺️')
#         st.page_link('pages/🌡️Heatmap2.py', label='️Heatmap', icon='🌡️')
#         st.page_link('pages/📖About.py', label='About', icon='📖')

def main():
    setup()

    row1_col1, row1_col2 = st.columns([5, 1])
    row2_col1, row2_col2  = st.columns([1, 1])

    Map = geemap.Map()

    # Центрируем карту на Астане (Нур-Султан)
    Map.setCenter(71.4491, 51.1694, zoom=6)  # Координаты Астаны

    # uploaded_shp_file = st.sidebar.file_uploader("Загрузите архив с Shapefile (.zip)", type=["zip"])
    #
    # if uploaded_shp_file is not None:
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         with zipfile.ZipFile(uploaded_shp_file, 'r') as zip_ref:
    #             zip_ref.extractall(tmpdir)
    #
    #         shapefile_path = None
    #         for root, dirs, files in os.walk(tmpdir):
    #             for file in files:
    #                 if file.endswith(".shp"):
    #                     shapefile_path = os.path.join(root, file)
    #                     break
    #
    #         if shapefile_path:
    #             gdf = gpd.read_file(shapefile_path)
    #
    #             if gdf.empty:
    #                 st.error("Файл прочитан, но в нём нет данных.")
    #                 return

    # Указываем путь к локальному Shapefile и CSV файлу (или URL)
    shapefile_path = "C:/Users/bekzh/Desktop/дипломка/agroclim_N_C_E.zip"  # Укажите путь к архиву Shapefile
    csv_file_path = "C:/Users/bekzh/Desktop/дипломка/aggregated_results_split.csv"  # Укажите путь к CSV файлу

    if shapefile_path and csv_file_path:
        # Извлекаем Shapefile из архива
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(shapefile_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

            shapefile_file = None
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    if file.endswith(".shp"):
                        shapefile_file = os.path.join(root, file)
                        break

            if shapefile_file:
                gdf = gpd.read_file(shapefile_file)

                if gdf.empty:
                    st.error("Файл прочитан, но в нём нет данных.")
                    return
        # # Загрузка CSV данных
        # csv_data = pd.read_csv(csv_file_path)

        with row1_col2:

            # Добавление heatmap через st.toggle
            #show_heatmap = st.toggle("Показать heatmap")

            # if show_heatmap:
            #     # Преобразование данных CSV в список координат для heatmap
            #     heat_data = []
            #     for _, row in csv_data.iterrows():
            #         region_id = row['Region ID']
            #         sum_number = row['Sum of Number']
            #         region_data = gdf[gdf['ADM2_PCODE'] == region_id]  # Используем правильное имя столбца
            #         if not region_data.empty:
            #             lat = region_data.geometry.centroid.y.iloc[0]
            #             lon = region_data.geometry.centroid.x.iloc[0]
            #             heat_data.append([lat, lon, sum_number])
            #
            #     # Добавление heatmap на карту
            #     if heat_data:
            #         folium_map = Map.folium_map()  # Используем Map.to_folium() вместо Map.folium_map
            #         HeatMap(heat_data).add_to(folium_map)
            #     else:
            #         st.error("Нет данных для отображения heatmap.")

            column_to_color = st.selectbox("##### Поля для окраски",
                options=gdf.columns,
                index=None,
                placeholder="Выберите поле для окраски"
            )

            if st.button("Сбросить"):
                st.session_state.pop("user_colors", None)
                st.rerun()

            if column_to_color:
                unique_values = sorted(gdf[column_to_color].unique())
                st.markdown("### Настройка цветов")

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
                    new_color = st.color_picker(
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
                    st.markdown(
                        f"<div style='text-align: center; font-size: 36px'>Полигоны по полю: {column_to_color}</div>",
                        unsafe_allow_html=True)
                    st.image(buf, use_container_width=True)

                # Обновленная таблица с цветами
                with row2_col2:
                    st.markdown("### Таблица данных")
                    st.dataframe(gdf)

                # Стиль по полю и цвету
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
                Map.setCenter(centroid.x, centroid.y, zoom=10)

        # Отображение карты
        with row1_col1:
            Map.to_streamlit(height=870)

if __name__ == "__main__":
    main()
