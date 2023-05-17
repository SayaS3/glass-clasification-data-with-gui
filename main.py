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
        df = df.drop(columns=["id"])  # Usuń kolumnę 'id' z obliczeń korelacji

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
                          auto_size_columns=True, justification='left')],
                [sg.Text('Wybierz atrybuty do wyświetlenia na wykresie:')],
                [sg.Text('Pierwszy atrybut:'),
                 sg.Combo(attribute_list, size=(30, 1), key='-ATTRIBUTE1-', enable_events=True)],
                [sg.Text('Drugi atrybut:'),
                 sg.Combo(attribute_list, size=(30, 1), key='-ATTRIBUTE2-', enable_events=True)],
                [sg.Button('Wyświetl wykres', key='-PLOT-', disabled=True)]
            ]
            layout_histogram = [
                [sg.Text('Wybierz atrybut do wyświetlenia na histogramie:')],
                [sg.Text('Wybrany atrybut:'),
                 sg.Combo(attribute_list, size=(30, 1), key='-HIST_ATTRIBUTE-', enable_events=True)],
                [sg.Button('Wyświetl histogram', key='-HIST_PLOT-', disabled=True)]
            ]

            tab1 = sg.Tab('Dane', layout_data)
            tab2 = sg.Tab('Miar statystycznych', layout_statistics)
            tab3 = sg.Tab('Korelacje', layout_correlations)
            tab4 = sg.Tab('Histogram', layout_histogram)

            layout = [
                [sg.TabGroup([[tab1, tab2, tab3, tab4]], enable_events=True)]
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
                if event == '-PLOT-':
                    attribute1 = values['-ATTRIBUTE1-']
                    attribute2 = values['-ATTRIBUTE2-']

                    # Pobierz dane dla wybranych atrybutów
                    attribute1_data = [float(row[data[0].index(attribute1)]) for row in data[1:]]
                    attribute2_data = [float(row[data[0].index(attribute2)]) for row in data[1:]]

                    # Tworzenie wykresu
                    plt.scatter(attribute1_data, attribute2_data)
                    plt.xlabel(attribute1)
                    plt.ylabel(attribute2)
                    plt.title(f'Zależność między {attribute1} a {attribute2}')
                    plt.show()

                if event == '-HIST_PLOT-':
                    selected_attribute = values['-HIST_ATTRIBUTE-']
                    if selected_attribute:
                        attribute_data = [float(row[data[0].index(selected_attribute)]) for row in data[1:]]

                        # Tworzenie histogramu
                        plt.hist(attribute_data, bins=10)
                        plt.xlabel(selected_attribute)
                        plt.ylabel('Liczba wystąpień')
                        plt.title(f'Histogram dla atrybutu {selected_attribute}')
                        plt.show()

            window.close()


layout = [
    [sg.Button('Otwórz plik CSV', key='-OPEN-')],
]

window = sg.Window('Aplikacja GUI', layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == '-OPEN-':
        open_csv()

window.close()
