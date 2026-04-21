import streamlit as st
import pandas as pd
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


def setup():
    st.set_page_config(layout="wide", page_title="Diagram", page_icon='📊️')

# Основная функция Streamlit-приложения
def main():
    setup()

    row1_col1, row1_col2 = st.columns([2, 1])  # Для тепловой карты и фильтров

    # Загружаем данные
    df_all = load_all_excel_data()

    # Левая колонка для отображения тепловой карты
    with row1_col2:
        # Выбор года
        all_years = sorted(df_all['year'].dropna().unique())
        selected_years_heatmap = st.multiselect("Выберите один или несколько лет", all_years, default=all_years)#

        # Фильтрация данных по выбранным годам
        filtered_by_year = df_all[df_all['year'].isin(selected_years_heatmap)]

        # Выбор областей в зависимости от выбранных лет
        all_oblasts = sorted(filtered_by_year['oblast'].dropna().unique())
        selected_region_heatmap = st.multiselect("Выберите один или несколько областей", all_oblasts, default=all_oblasts)#

        # Фильтрация данных по выбранным областям
        filtered_by_region = filtered_by_year[filtered_by_year['oblast'].isin(selected_region_heatmap)]

        # Выбор районов в зависимости от выбранных областей
        all_district = sorted(filtered_by_region['district'].dropna().unique())
        selected_district_heatmap = st.multiselect("Выберите один или несколько районов", all_district, default=all_district)#

        # Фильтрация по выбранным параметрам
        filtered_data = filtered_by_region[
            (filtered_by_region['district'].isin(selected_district_heatmap))
        ]
        # Выбор показателя
        selected_indicator = st.selectbox("Выберите показатель для диаграммы:",
                                                  ["skintemp4", "skintemp5", "skintemp6", "skintemp7", "skintemp8",
                                                   "skintemp9", "skintemp10",
                                                   "snsr4", "snsr5", "snsr6", "snsr7", "snsr8", "snsr9", "snsr10",
                                                   "temp4", "temp5", "temp6", "temp7", "temp8", "temp9", "temp10",
                                                   "evap4", "evap5", "evap6", "evap7", "evap8", "evap9", "evap10",
                                                   "prec4", "prec5", "prec6", "prec7", "prec8", "prec9", "prec10",
                                                   "vswl4", "vswl5", "vswl6", "vswl7", "vswl8", "vswl9", "vswl10",
                                                   "surv_area", "popul_area", "number"
                                                   ])

        with row1_col1:
            # Выбор показателя для диаграммы
            selected_indicator_diagram = selected_indicator

            # Выбор годов
            selected_years_diagram = selected_years_heatmap

            # Построение графика по выбранным годам
            st.subheader(f"📊Динамика изменения показателя по годам")

            # Визуализация графика с точками и связующими линиями
            fig, ax = plt.subplots(figsize=(8, 6))  # Размер графика
            for district in selected_district_heatmap:
                df_district = filtered_data[filtered_data["district"] == district]
                df_district = df_district.sort_values("year")

                ax.plot(
                    df_district["year"],
                    df_district[selected_indicator_diagram],
                    marker='o',
                    linestyle='-',
                    linewidth=2,
                    label=district
                )

            ax.set_xlabel("Год")
            ax.set_ylabel("Значение показателя")
            ax.set_title(f"{selected_indicator_diagram} по годам")
            ax.grid(True)
            ax.legend(title="Районы", loc='upper left', bbox_to_anchor=(1.05, 1))
            ax.set_title(f"{selected_indicator_diagram} по годам")
            ax.grid(True)
            ax.legend(title="Годы", loc='upper left', bbox_to_anchor=(1.05, 1))
            st.pyplot(fig)


if __name__ == "__main__":
    main()
