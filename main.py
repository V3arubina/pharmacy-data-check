import os
import pandas as pd

# Путь к папке Входящие
sbis_folder = "Входящие"

# Заготовка под итоговый DataFrame
sbis_df_list = []

# Чтение всех файлов из папки
for filename in os.listdir(sbis_folder):
    if filename.endswith(".csv"):
        file_path = os.path.join(sbis_folder, filename)
        df = pd.read_csv(file_path, sep=';', encoding='1251', skiprows=1, header=None)
        sbis_df_list.append(df)

# Объединяем все таблицы в одну
sbis_df = pd.concat(sbis_df_list, ignore_index=True)

# Названия столбцов
sbis_df.columns = [
    "Дата", "Номер", "Сумма", "Статус", "Примечание", "Комментарий", "Контрагент",
    "ИНН_КПП", "Организация", "ИНН_КПП_2", "Тип_документа", "Имя_файла",
    "Дата_1", "Номер_1", "Сумма_1", "Сумма_НДС", "Ответственный", "Подразделение",
    "Код", "Дата_2", "Время", "Тип_пакета", "Идентификатор_пакета", "Запущено_в_обработку",
    "Получено_контрагентом", "Завершено", "Увеличение_суммы", "НДC", "Уменьшение_суммы", "НДС_2"
]


#Аптеки
apteka_folder = "Аптеки/csv/correct"

docs = ["СчФктр", "УпдДоп", "УпдСчфДоп", "ЭДОНакл"]

# Создаем папку для результатов
from datetime import datetime
today = datetime.today().strftime('%Y-%m-%d')
output_dir = os.path.join("Результат", today)
os.makedirs(output_dir, exist_ok=True)

# Проходим по файлам
for filename in os.listdir(apteka_folder):
    if not filename.endswith(".csv"):
        continue

    file_path = os.path.join(apteka_folder, filename)
    df_apteka = pd.read_csv(file_path, sep=';', encoding='1251')

    # Обработка "ЕАПТЕКА"
    df_apteka.loc[df_apteka['Поставщик'] == 'ЕАПТЕКА', 'Номер накладной'] += '/15'

    # Добавим нужные столбцы
    df_apteka["Номер счет-фактуры"] = ""
    df_apteka["Сумма счет-фактуры"] = ""
    df_apteka["Дата счет-фактуры"] = ""
    df_apteka["Сравнение дат"] = ""

    # Проходим по строкам
    for i, row in df_apteka.iterrows():
        doc_number = row['Номер накладной']
        doc_date = row['Дата накладной']

        # Поиск подходящих записей в sbis_df
        matched = sbis_df[sbis_df['Номер'] == doc_number]
        matched = matched[matched['Тип_документа'].isin(docs)]

        if not matched.empty:
            first = matched.iloc[0]
            sbis_date = pd.to_datetime(first['Дата'], dayfirst=True).strftime('%d.%m.%Y')

            df_apteka.at[i, "Номер счет-фактуры"] = first['Номер']
            df_apteka.at[i, "Сумма счет-фактуры"] = first['Сумма']
            df_apteka.at[i, "Дата счет-фактуры"] = sbis_date

            # Сравнение дат
            if doc_date != sbis_date:
                df_apteka.at[i, "Сравнение дат"] = "Не совпадает!"

    # Оставляем только нужные столбцы
    needed_cols = [
        '№ п/п', 'Штрих-код партии', 'Наименование товара', 'Поставщик',
        'Дата приходного документа', 'Номер приходного документа',
        'Дата накладной', 'Номер накладной', 'Номер счет-фактуры',
        'Сумма счет-фактуры', 'Кол-во',
        'Сумма в закупочных ценах без НДС', 'Ставка НДС поставщика',
        'Сумма НДС', 'Сумма в закупочных ценах с НДС', 'Дата счет-фактуры', 'Сравнение дат'
    ]

    df_result = df_apteka[needed_cols]

    # Сохраняем
    file_no_ext = os.path.splitext(filename)[0]
    output_path = os.path.join(output_dir, f"{file_no_ext} - результат.xlsx")
    df_result.to_excel(output_path, index=False)
    print(f"Обработан: {filename}")

