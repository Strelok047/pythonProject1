import streamlit as st
import pandas as pd
import leafmap.foliumap as leafmap
import matplotlib.pyplot as plt

# Функция для загрузки всех данных из Excel
def load_all_excel_data():
    excel_path = r"C:\Users\bekzh\Desktop\дипломка\drive-download-20250412T210352Z-001_with_coord01\combined_data_separate_sheets_with_coordinates.xlsx"
    excel_data = pd.ExcelFile(excel_path)
    all_data = []

    for sheet in excel_data.sheet_names:
        df = excel_data.parse(sheet)
        df["agrozone"] = sheet  # Добавим название листа как столбец
        all_data.append(df)

    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df

# Функция для генерации палитры цветов
def generate_colors(n):
    colors = plt.cm.get_cmap('tab20', n)  # Используем табличную палитру цветов с нужным количеством
    return [colors(i) for i in range(n)]
def setup():
    st.set_page_config(layout="wide", page_title="Heatmap with markers📍", page_icon='🌡️')

# Основная функция Streamlit-приложения
def main():
    setup()
    st.title("🌡️ Тепловая карта по районам и годам")

    row1_col1, row1_col2 = st.columns([5, 1])

    # Загружаем данные
    df_all = load_all_excel_data()
    with row1_col2:
        # Выбор года
        all_years = sorted(df_all['year'].dropna().unique())
        selected_years = st.multiselect("Выберите один или несколько лет", all_years, default=all_years)

        # Выбор регионов
        all_region = sorted(df_all['oblast'].dropna().unique())
        selected_region = st.multiselect("Выберите один или несколько областей", all_region, default=all_region)

        # Фильтрация по выбранным параметрам
        filtered_data = df_all[
            (df_all['year'].isin(selected_years)) &
            (df_all['oblast'].isin(selected_region))
        ]

    # Отображаем таблицу выбранных данных
    st.subheader(f"📊 Данные за выбранные года и области")
    st.write(filtered_data)
    with row1_col1:
        # Проверка наличия координат и числового значения
        if {'latitude', 'longitude', 'number'}.issubset(filtered_data.columns):
            # Удаляем строки с NaN
            filtered_data_clean = filtered_data.dropna(subset=['latitude', 'longitude', 'number'])

            if not filtered_data_clean.empty:
                # Группируем по координатам и считаем количество записей в каждой группе
                grouped_data = filtered_data_clean.groupby(['latitude', 'longitude']).agg({
                    'number': 'sum',  # Суммируем числовые значения (можно использовать другие агрегатные функции)
                    'oblast': 'first'  # Берем первое значение области для каждого уникального места
                }).reset_index()

                # Генерация палитры цветов для уникальных значений в agrozone
                unique_oblasts = grouped_data['oblast'].unique()
                num_colors = len(unique_oblasts)
                colors = generate_colors(num_colors)

                # Создаём карту
                m = leafmap.Map(center=[51.1694, 71.4491], zoom=5)

                # Добавляем тепловую карту
                m.add_heatmap(
                    grouped_data,
                    latitude="latitude",
                    longitude="longitude",
                    value="number",  # Числовое значение для тепловой карты
                    name="Heatmap Layer",
                    radius=20,
                )


                m.add_points_from_xy(
                    grouped_data,
                    x="longitude",
                    y="latitude",
                    color_column=None,  # Убираем color_column, если его использовать неудобно
                    icon_names=["gear", "map", "leaf", "globe"],  # Можно заменить на другие иконки
                    spin=True,
                    add_legend=True,
                    layer_name=f"Маркеры",
                )

                # Отображаем карту
                m.to_streamlit(height=700)

            else:
                st.warning("Нет данных с координатами и значениями для отображения тепловой карты.")
        else:
            st.error("В Excel-данных отсутствуют столбцы 'latitude', 'longitude' и/или 'number'.")

if __name__ == "__main__":
    main()
