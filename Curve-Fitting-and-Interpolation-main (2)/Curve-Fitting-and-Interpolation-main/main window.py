import sys
from sklearn.metrics import mean_absolute_error
import matplotlib.patches as mpatches
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtGui, QtWidgets
from maingui import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ####################################################################
        # Variables:
        self.main_graph_figure = Figure()
        self.main_graph_canvas = FigureCanvas(self.main_graph_figure)
        self.ui.main_graph_layout.addWidget(self.main_graph_canvas)

        self.error_map_figure = Figure()
        self.error_map_canvas = FigureCanvas(self.error_map_figure)
        self.ui.verticalLayout.addWidget(self.error_map_canvas)

        # To make the text box take only numbers
        self.onlyInt = QIntValidator()
        self.ui.lineEdit.setValidator(self.onlyInt)
        self.ui.lineEdit_2.setValidator(self.onlyInt)

        self.time_value = []
        self.amplitude_value = []
        self.number_of_chunks = 0
        self.degree_of_polynomial = 0
        self.overlap_percentage = 0
        self.full_signal_array = []
        self.full_matrix_error_map = []
        self.row_of_error_map = []
        self.ui.tableWidget.setRowCount(6)
        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setColumnWidth(0, 200)

        self.ui.tableWidget.setHorizontalHeaderLabels("Variable;Value".split(";"))
        #####################################################################
        # Buttons' Functions
        self.set_combo_box_items()
        self.ui.lineEdit.setText("0")
        self.ui.lineEdit_2.setText("0")
        self.ui.lineEdit_3.setText("0")
        self.ui.lineEdit_4.setText("0")
        self.ui.browse_button.clicked.connect(self.browse_signal_file)
        self.ui.chunks_button.clicked.connect(self.set_number_of_chunks)
        self.ui.degree_button.clicked.connect(self.set_degree_of_polynomial)
        self.ui.one_main_chunk_button.clicked.connect(self.display_one_main_chunk)
        self.ui.pushButton_3.clicked.connect(self.plot_data_splitted_with_chunks)
        self.ui.pushButton.clicked.connect(self.error_map)
        self.ui.pushButton_2.clicked.connect(self.reset)

    def browse_signal_file(self):
        try:
            file_name = QFileDialog.getOpenFileName(filter="CSV (*.csv)")[0]
            data_frame = pd.read_csv(file_name)
            self.time_value = data_frame.iloc[:, 0].values
            self.amplitude_value = data_frame.iloc[:, 1].values
            print(len(self.amplitude_value))
            # Plot the signal
            self.plot_browsed_signal()

        except Exception as e:
            print(e)

    def plot_browsed_signal(self):
        try:
            axes = self.main_graph_figure.gca()
            axes.cla()
            axes.grid(True)
            axes.set_facecolor((1, 1, 1))
            axes.plot(self.time_value, self.amplitude_value, "b", label="Original Signal")
            axes.set_xlabel("Time Value")
            axes.set_ylabel("Amplitude Value")
            axes.set_title("BioSignal")
            axes.legend()
            self.main_graph_canvas.draw()
            self.main_graph_canvas.flush_events()
        except Exception as e:
            print(e)

    def set_number_of_chunks(self):
        try:
            if 0 < int(self.ui.lineEdit.text()) < 10:
                self.number_of_chunks = int(self.ui.lineEdit.text())
                self.ui.lineEdit.clear()
                # print(self.number_of_chunks)
                self.ui.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("Number OF Chunks"))
                self.ui.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(str(self.number_of_chunks)))
                # self.ui.label_10.setText(str(self.number_of_chunks))
            else:
                self.ui.lineEdit.clear()
                print("Invalid Number of Chunks")
        except Exception as e:
            print(e)

    def set_degree_of_polynomial(self):
        try:
            if 0 < int(self.ui.lineEdit_3.text()) < 10:
                self.degree_of_polynomial = int(self.ui.lineEdit_3.text())
                self.ui.lineEdit_3.clear()
                # print(self.degree_of_polynomial)
                self.ui.tableWidget.setItem(1, 0, QtWidgets.QTableWidgetItem("Degree Of Polynomial"))
                self.ui.tableWidget.setItem(1, 1, QtWidgets.QTableWidgetItem(str(self.degree_of_polynomial)))
                # self.ui.label_11.setText(str(self.degree_of_polynomial))
            else:
                self.ui.lineEdit_3.clear()
                print("Poor Conditioned Polynomial Degree choose between 1 ~ 9")
        except Exception as e:
            print(e)

    def set_overlap_percentage(self):
        try:
            if self.ui.lineEdit_4.text() != "":
                if 0 <= int(self.ui.lineEdit_4.text()) < 26:
                    self.overlap_percentage = int(self.ui.lineEdit_4.text()) / 100.0
                    self.ui.lineEdit_4.clear()
                    # print(self.overlap_percentage)
                    self.ui.tableWidget.setItem(2, 0, QtWidgets.QTableWidgetItem("Overlap Percentage"))
                    self.ui.tableWidget.setItem(2, 1, QtWidgets.QTableWidgetItem(str(self.overlap_percentage)))
                    # self.ui.label_12.setText(str(self.overlap_percentage))
                else:
                    self.ui.lineEdit_4.clear()
                    print("Enter Number between 0 ~ 25")
        except Exception as e:
            print(e)

    def display_one_main_chunk(self):
        try:
            degree_of_polynomial = int(self.ui.lineEdit_2.text())
            self.ui.lineEdit_2.clear()
            coefficients_of_fitted_eqn = np.polyfit(self.time_value, self.amplitude_value, degree_of_polynomial)
            amplitude_fitted_values = np.polyval(coefficients_of_fitted_eqn, self.time_value)

            error_percentage = round(mean_absolute_error(self.amplitude_value, amplitude_fitted_values) * 100, 5)
            self.ui.tableWidget.setItem(3, 0, QtWidgets.QTableWidgetItem("Error Percentage Of Polynomial"))
            self.ui.tableWidget.setItem(3, 1, QtWidgets.QTableWidgetItem(str(error_percentage)))

            latex_equation_format = self.polynomial_to_latex(coefficients_of_fitted_eqn)
            # print(latex_equation_format)
            # print(error_percentage)
            self.ui.label_14.setText(str(error_percentage) + "%")
            ax_2 = self.main_graph_figure.gca()
            ax_2.cla()
            ax_2.grid(True)
            ax_2.set_facecolor((1, 1, 1))
            ax_2.plot(self.time_value, self.amplitude_value, "b", label="Original Signal")
            ax_2.plot(self.time_value, amplitude_fitted_values, "r--",
                      label=f"Fitted Signal with polynomial of degree {degree_of_polynomial}.")
            ax_2.set_xlabel("Time Value")
            ax_2.set_ylabel("Amplitude Value")
            ax_2.set_title("BioSignal")
            leg_1 = ax_2.legend(loc="lower center")
            red_patch = mpatches.Patch(color='red', label=latex_equation_format)
            leg_2 = ax_2.legend(handles=[red_patch], loc="upper center")
            ax_2.add_artist(leg_1)
            self.main_graph_canvas.draw()
            self.main_graph_canvas.flush_events()
        except Exception as e:
            print(e)

    def chunks_divider(self):
        try:
            self.full_signal_array = []
            length_of_data = len(self.time_value)
            for i in range(self.number_of_chunks):
                start = int((i * length_of_data / self.number_of_chunks))
                end = int(((i + 1) * length_of_data / self.number_of_chunks))
                # print(start)
                # print(end)
                coeff = np.polyfit(self.time_value[start: end], self.amplitude_value[start: end],
                                   self.degree_of_polynomial)
                fitted_data = np.polyval(coeff, self.time_value[start:end])
                self.full_signal_array.extend(fitted_data)
                # print(len(self.full_signal_array))
        except Exception as e:
            print(e)

    def plot_data_splitted_with_chunks(self):
        try:
            self.chunks_divider()
            ax_3 = self.main_graph_figure.gca()
            ax_3.cla()
            ax_3.grid(True)
            ax_3.set_facecolor((1, 1, 1))
            ax_3.plot(self.time_value, self.amplitude_value, "b", label="Original Signal")
            ax_3.plot(self.time_value, self.full_signal_array, "r--",
                      label=f"Fitted Signal with {self.number_of_chunks} Chunks and polynomial of degree {self.degree_of_polynomial}.")
            ax_3.legend(loc="best")
            self.main_graph_canvas.draw()
            self.main_graph_canvas.flush_events()
        except Exception as e:
            print(e)

    def polynomial_to_latex(self, list_of_coefficients):
        # Note In the code Below I want the coefficients to be from x to the power 0 and increasing through degrees
        # So i need to reverse my coefficients as it was collected in decreasing order
        list_of_coefficients = list_of_coefficients[::-1]
        full_equation_string = ""  # The resulting string
        for i, a in enumerate(list_of_coefficients):
            if int(a) == a:  # Remove the trailing .0
                a = int(a)
            a = round(a, 5)
            if i == 0:  # First coefficient, no need for X
                if a > 0:
                    full_equation_string += "{a} + ".format(a=a)
                elif a < 0:  # Negative a is printed like (a)
                    full_equation_string += "({a}) + ".format(a=a)
                # a = 0 is not displayed
            elif i == 1:  # Second coefficient, only X and not X**i
                if a == 1:  # a = 1 does not need to be displayed
                    full_equation_string += "x + "
                elif a > 0:
                    full_equation_string += "{a}x + ".format(a=a)
                elif a < 0:
                    full_equation_string += "({a})x + ".format(a=a)
            else:
                if i == (len(list_of_coefficients) - 1):
                    if a == 1:
                        # A special care needs to be addressed to put the exponent in {..} in LaTeX
                        full_equation_string += "x^{i}".format(i=i)
                    elif a > 0:
                        full_equation_string += "{a}x^{i}".format(a=a, i=i)
                    elif a < 0:
                        full_equation_string += "({a})x^{i}".format(a=a, i=i)
                else:
                    if a == 1:
                        # A special care needs to be addressed to put the exponent in {..} in LaTeX
                        full_equation_string += "x^{i} + ".format(i=i)
                    elif a > 0:
                        full_equation_string += "{a}x^{i} + ".format(a=a, i=i)
                    elif a < 0:
                        full_equation_string += "({a})x^{i} + ".format(a=a, i=i)
        full_equation_string = "$" + full_equation_string + "$"
        return full_equation_string

    def set_combo_box_items(self):
        self.ui.comboBox.addItems(["Number Of Chunks", "Degree of Polynomial"])
        self.ui.comboBox_2.addItems(["Degree of Polynomial", "Number Of Chunks"])

    def dividing_chunks_using_overlap_percentage(self):
        try:
            self.set_overlap_percentage()
            chunks_overall_data = []
            time_overall_data = []
            chunk_data = []
            time_data = []
            start = 0
            length_of_data = len(self.time_value)
            chunk_length = int(length_of_data / (self.number_of_chunks - (self.number_of_chunks - 1) * self.overlap_percentage))
            moving_step = int(chunk_length * (1 - self.overlap_percentage) + 0.5)
            for i in range(0, self.number_of_chunks):
                chunk_data = list(self.amplitude_value[start: start + chunk_length])
                time_data = list(self.time_value[start: start + chunk_length])
                chunks_overall_data.append(chunk_data)
                time_overall_data.append(time_data)
                start += moving_step
                # print(chunk_data)
            # print(chunks_overall_data)
            return time_overall_data, chunks_overall_data
        except Exception as e:
            print(e)

    def error_map(self):
        try:
            progress_bar_value = 0
            time_overall_data, chunks_overall_data = self.dividing_chunks_using_overlap_percentage()
            self.full_matrix_error_map = []
            x_axis_element = self.ui.comboBox.currentIndex()
            y_axis_element = self.ui.comboBox_2.currentIndex()
            # print(x_axis_element, y_axis_element)
            if (x_axis_element == 0) and (y_axis_element == 0):
                # Number Of Chunks is on X_axis, Polynomial Degree is on Y-axis:
                for chunk_number in range(0, self.number_of_chunks):
                    chunk_data = chunks_overall_data[chunk_number]
                    time_data = time_overall_data[chunk_number]
                    self.row_of_error_map = []
                    for degree in range(1, self.degree_of_polynomial + 1):
                        coefficients_of_fitted_eqn = np.polyfit(time_data, chunk_data,
                                                                degree)
                        amplitude_fitted_values = np.polyval(coefficients_of_fitted_eqn, time_data)
                        error_percentage = mean_absolute_error(chunk_data, amplitude_fitted_values) * 100
                        self.row_of_error_map.append(error_percentage)

                    progress_bar_value += chunk_number * 5
                    self.ui.progressBar.setValue(progress_bar_value)
                    self.full_matrix_error_map.append(self.row_of_error_map)

                # Plotting the Error Map:
                error_ax = self.error_map_figure.gca()
                error_ax.imshow(self.full_matrix_error_map)
                error_ax.set_xlabel("Number Of Chunks")
                error_ax.set_ylabel("Polynomial Degree")
                error_ax.set_title("Error Map!")
                error_ax.set_xticks([])
                error_ax.set_yticks([])
                self.error_map_canvas.draw()
                self.error_map_canvas.flush_events()
                self.ui.progressBar.setValue(100)

            elif (x_axis_element == 1) and (y_axis_element == 1):
                # Number Of Chunks is on Y_axis, Polynomial Degree is on X-axis:
                for degree in range(1, self.degree_of_polynomial + 1):
                    self.row_of_error_map = []
                    for chunk_number in range(0, self.number_of_chunks):
                        chunk_data = chunks_overall_data[chunk_number]
                        time_data = time_overall_data[chunk_number]
                        coefficients_of_fitted_eqn = np.polyfit(time_data, chunk_data,
                                                                degree)
                        amplitude_fitted_values = np.polyval(coefficients_of_fitted_eqn, time_data)
                        error_percentage = mean_absolute_error(chunk_data, amplitude_fitted_values) * 100
                        self.row_of_error_map.append(error_percentage)

                    progress_bar_value += degree * 5
                    self.ui.progressBar.setValue(progress_bar_value)
                    self.full_matrix_error_map.append(self.row_of_error_map)

                # Plotting the Error Map:
                error_ax = self.error_map_figure.gca()
                error_ax.imshow(self.full_matrix_error_map)
                error_ax.set_xlabel("Polynomial Degree")
                error_ax.set_ylabel("Number Of Chunks")
                error_ax.set_title("Error Map!")
                error_ax.set_xticks([])
                error_ax.set_yticks([])
                self.error_map_canvas.draw()
                self.error_map_canvas.flush_events()
                self.ui.progressBar.setValue(100)

            else:
                print("Invalid Axes Elements! Choose Two different elements from each combo box")

        except Exception as e:
            print(e)

    def reset(self):
        try:
            axes = self.error_map_figure.gca()
            axes.cla()
            axes_1 = self.main_graph_figure.gca()
            axes_1.cla()
            self.time_value = 0
            self.amplitude_value = 0
            self.overlap_percentage = 0
            self.number_of_chunks = 0
            self.degree_of_polynomial = 0
            self.ui.lineEdit.setText("0")
            self.ui.lineEdit_2.setText("0")
            self.ui.lineEdit_3.setText("0")
            self.ui.lineEdit_4.setText("0")
            self.ui.tableWidget.clear()
            self.ui.progressBar.setValue(0)
            self.error_map_canvas.draw()
            self.error_map_canvas.flush_events()
            self.main_graph_canvas.draw()
            self.main_graph_canvas.flush_events()
        except Exception as e:
            print(e)


    # def create_combo_box_chunks_names(self, number_of_chunks):
    #     try:
    #         self.ui.chunks_combo_box.clear()
    #         for chunk_number in range(1, int(number_of_chunks)+1):
    #             self.ui.chunks_combo_box.addItem(f"chunk: {chunk_number}")
    #     except Exception as e:
    #         print(e)

    # def polynomial_interpolation(self, time_value, amplitude_value, order_of_polynomial):
    #     try:
    #         coefficients_of_fitted_eqn = np.polyfit(time_value, amplitude_value, order_of_polynomial)
    #         amplitude_fitted_values = np.polyval(coefficients_of_fitted_eqn, time_value)
    #         return amplitude_fitted_values
    #     except Exception as e:
    #         print(e)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Curve Fitting and Interpolation")
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
