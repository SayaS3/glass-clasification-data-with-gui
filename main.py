import PySimpleGUI as sg
import csv
import statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_statistics(data):
    headers = data[0]
    data = data[1:]

    statistics_data = []
    for col in range(len(headers)):
        if headers[col] == "id":
            continue
        column_values = [float(row[col]) for row in data]
        min_val = min(column_values)
        max_val = max(column_values)
        std_dev = statistics.stdev(column_values)
        median_val = statistics.median(column_values)
        mode_val = statistics.mode(column_values)

        statistics_data.append([headers[col], min_val, max_val, std_dev, median_val, mode_val])

    return statistics_data

def calculate_correlations(data):
    headers = data[0]
    data = data[1:]

    df = pd.DataFrame(data, columns=headers)
    if "id" in df.columns:
        df = df.drop(columns=["id"])  # Usuń kolumnę "id" z obliczeń korelacji

    correlations = df.corr().round(2)
    correlations_data = correlations.values.tolist()
    correlations_headers = correlations.columns.tolist()

    return correlations_data, correlations_headers

def open_csv():
    file_path = sg.popup_get_file('Wybierz plik CSV', file_types=(("CSV Files", "*.csv"),))
    if file_path:
        with open(file_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            data = list(csv_reader)

            statistics_data = calculate_statistics(data)
            correlations_data, correlations_headers = calculate_correlations(data)

            # Przekształć dane korelacji w listę z nagłówkami atrybutów
            correlations_table_data = [[header] + row for header, row in zip(correlations_headers, correlations_data)]
            correlations_table_data.insert(0, [""] + correlations_headers)  # Dodaj wiersz nagłówków

            attribute_list = data[0][1:]  # Lista atrybutów bez "id"
            column_list = list(range(len(attribute_list)))  # Lista numerów kolumn

            layout_data = [
                [sg.Table(values=data[1:], headings=data[0], auto_size_columns=True, justification='left')]
            ]
            layout_statistics = [
                [sg.Table(values=statistics_data,
                          headings=['Atrybut', 'Min', 'Max', 'Odchylenie std', 'Mediana', 'Moda'],
                          auto_size_columns=True, justification='left')]
            ]
            layout_correlations = [
                [sg.Table(values=correlations_table_data,
                          headings=[""] + correlations_headers,
                          auto_size_columns=True, justification='left')],
            ]
            layout_histogram = [
                [sg.Text('Wybierz atrybut do wyświetlenia na histogramie:')],
                [sg.Text('Wybrany atrybut:'),
                 sg.Combo(attribute_list, size=(30, 1), key='-HIST_ATTRIBUTE-', enable_events=True)],
                [sg.Button('Wyświetl histogram', key='-HIST_PLOT-', disabled=True)]
            ]
            layout_subtable = [
                [sg.Text('Liczba wierszy do wyświetlenia:'),
                 sg.Slider(range=(0, len(data) - 1), default_value=0, orientation='horizontal', key='-SUBTABLE_ROWS-',
                           enable_events=True)],
                [sg.Text('Wybierz kolumny do podtablicy:')],
                [sg.Listbox(column_list, size=(10, 6), key='-SUBTABLE_COLUMNS-', select_mode='extended',
                            enable_events=True)],
                [sg.Button('Utwórz podtablicę', key='-CREATE_SUBTABLE-', disabled=True)],
                [sg.Multiline('', key='-SUBTABLE_DATA-', size=(60, 15), autoscroll=True, disabled=True)]
            ]

            tab1 = sg.Tab('Dane', layout_data)
            tab2 = sg.Tab('Miar statystycznych', layout_statistics)
            tab3 = sg.Tab('Korelacje', layout_correlations)
            tab4 = sg.Tab('Histogram', layout_histogram)
            tab5 = sg.Tab('Podtabela', layout_subtable)

            layout = [
                [sg.Text('Wybierz atrybuty do wyświetlenia na wykresie:')],
                [sg.Text('Pierwszy atrybut:'),
                 sg.Combo(attribute_list, size=(30, 1), key='-ATTRIBUTE1-', enable_events=True)],
                [sg.Text('Drugi atrybut:'),
                 sg.Combo(attribute_list, size=(30, 1), key='-ATTRIBUTE2-', enable_events=True)],
                [sg.Button('Wyświetl wykres', key='-PLOT-', disabled=True)],
                [sg.TabGroup([[tab1, tab2, tab3, tab4, tab5]], enable_events=True)]
            ]

            window = sg.Window('Dane CSV', layout)

            while True:
                event, values = window.read()
                if event == sg.WINDOW_CLOSED:
                    break
                if event == '-ATTRIBUTE1-' or event == '-ATTRIBUTE2-':
                    attribute1 = values['-ATTRIBUTE1-']
                    attribute2 = values['-ATTRIBUTE2-']
                    if attribute1 != attribute2:
                        window['-PLOT-'].update(disabled=False)
                    else:
                        window['-PLOT-'].update(disabled=True)
                if event == '-HIST_ATTRIBUTE-':
                    selected_attribute = values['-HIST_ATTRIBUTE-']
                    if selected_attribute:
                        window['-HIST_PLOT-'].update(disabled=False)
                    else:
                        window['-HIST_PLOT-'].update(disabled=True)
                if event == '-SUBTABLE_ROWS-':
                    num_rows = int(values['-SUBTABLE_ROWS-'])
                    selected_columns = values['-SUBTABLE_COLUMNS-']
                    if num_rows > 0 and selected_columns:
                        subtable_data = [data[row_index] for row_index in range(num_rows)]
                        subtable_data = [[row[col_index] for col_index in selected_columns] for row in subtable_data]
                        header = selected_columns
                        subtable_data = [header] + subtable_data
                        subtable_data_text = '\n'.join(['\t'.join(map(str, row)) for row in subtable_data])
                        window['-SUBTABLE_DATA-'].update(value=subtable_data_text, disabled=False)

                        window['-CREATE_SUBTABLE-'].update(disabled=False)
                if event == '-CREATE_SUBTABLE-':
                    num_rows = int(values['-SUBTABLE_ROWS-'])
                    selected_columns = values['-SUBTABLE_COLUMNS-']
                    if num_rows > 0 and selected_columns:
                        subtable_data = [data[row_index + 1] for row_index in range(num_rows)]
                        subtable_data = [[row[col_index] for col_index in selected_columns] for row in subtable_data]

                        sg.popup('Podtabela utworzona!', title='Informacja')
                        sg.popup_scrolled('Podtabela:', '\n'.join([str(row) for row in subtable_data]),
                                          title='Podtabela')
                    else:
                        sg.popup('Nie wybrano odpowiednich kolumn lub liczby wierszy!', title='Błąd')
                if event == '-PLOT-':
                    attribute1 = values['-ATTRIBUTE1-']
                    attribute2 = values['-ATTRIBUTE2-']
                    if attribute1 != attribute2:
                        x = [float(row[attribute_list.index(attribute1) + 1]) for row in data[1:]]
                        y = [float(row[attribute_list.index(attribute2) + 1]) for row in data[1:]]
                        plt.scatter(x, y)
                        plt.xlabel(attribute1)
                        plt.ylabel(attribute2)
                        plt.title('Wykres zależności między atrybutami')
                        plt.show()
                if event == '-HIST_PLOT-':
                    selected_attribute = values['-HIST_ATTRIBUTE-']
                    if selected_attribute:
                        column_data = [float(row[attribute_list.index(selected_attribute) + 1]) for row in data[1:]]
                        plt.hist(column_data, bins=10)
                        plt.xlabel(selected_attribute)
                        plt.ylabel('Liczba wystąpień')
                        plt.title('Histogram')
                        plt.show()

            window.close()


open_csv()
