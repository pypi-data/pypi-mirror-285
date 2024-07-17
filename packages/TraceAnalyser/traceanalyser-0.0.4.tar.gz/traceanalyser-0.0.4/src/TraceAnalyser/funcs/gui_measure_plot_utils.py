from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from TraceAnalyser.funcs.gui_worker import Worker
import traceback
import numpy as np
import pandas as pd
import os
from PyQt5.QtWidgets import QFileDialog


class CustomMatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize matplotlib figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)

        # Setup layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        # Handle mouse press event
        if event.modifiers():  # Check for any specific modifiers you need
            click_position = event.pos()
            # Convert click position to axes coordinates
            axes_coord = self.axes.transData.inverted().transform((click_position.x(), click_position.y()))
            print("Clicked at:", axes_coord)
            # You can add your logic here

        super().mousePressEvent(event)

class _measure_plotting_methods:

    def initialise_measure_plot(self):

        try:

            self.print_notification("Drawing measurement plot...")

            if self.data_dict != {}:
                worker = Worker(self._initialise_measure_plot)
                worker.signals.result.connect(self.plot_measurement_histogram)
                self.threadpool.start(worker)
                pass

        except:
            print(traceback.format_exc())



    def compile_meassure_histogram_data(self):

        try:

            trace_data = []
            trace_index_data = []
            measure_index_data = []

            self.measure_graph_canvas.axes.clear()

            dataset = self.measure_graph_data.currentText()
            channel = self.measure_graph_channel.currentText()
            measurement_label = self.measure_label.currentText()

            for localisation_index, localisation_data in enumerate(self.data_dict[dataset]):
                if "measure_dict" in localisation_data.keys():
                    if measurement_label in localisation_data["measure_dict"].keys():
                        measure_ranges = localisation_data["measure_dict"][measurement_label]

                        for range_index, range in enumerate(measure_ranges):
                            if range != []:
                                data = localisation_data[channel][range[0]:range[1]]

                                if len(data) > 0:
                                    trace_data.append(data)
                                    trace_index_data.append([localisation_index]*len(data))
                                    measure_index_data.append([range_index]*len(data))

        except:
            print(traceback.format_exc())
            trace_data = []

        return trace_data, trace_index_data, measure_index_data

    def _initialise_measure_plot(self,progress_callback=None):

        trace_data, trace_index_data, measure_index_data = self.compile_meassure_histogram_data()
        histogram_data = self.compute_measurement_histogram(trace_data, trace_index_data, measure_index_data)

        return histogram_data


    def compute_measurement_histogram(self, trace_data,trace_index_data, measure_index_data):

        try:

            exposure_time = self.measure_exposure_time.value()

            histogram_data = {"metric":"", "values": [],"trace_index": [],"measure_index": []}

            histogram_selection = self.measure_histogram_dataset.currentText()

            if len(trace_data) != {}:

                histogram_data["metric"] = histogram_selection

                if histogram_selection != "Raw Data":

                    for data, trace_index, measure_index in zip(trace_data, trace_index_data, measure_index_data):

                        if histogram_selection == "Mean":
                            value = np.mean(data)
                        elif histogram_selection == "Median":
                            value = np.median(data)
                        elif histogram_selection == "Standard Deviation":
                            value = np.std(data)
                        elif histogram_selection == "Dwell Times (Seconds)":
                            value = len(data) * exposure_time * 1e-3
                        elif histogram_selection == "Dwell Times (Frames)":
                            value = len(data)

                        histogram_data["values"].append(value)
                        histogram_data["trace_index"].append(trace_index[0])
                        histogram_data["measure_index"].append(measure_index[0])

                else:

                    histogram_data["values"] = np.concatenate(trace_data).tolist()
                    histogram_data["trace_index"] = np.concatenate(trace_index_data).tolist()
                    histogram_data["measure_index"] = np.concatenate(measure_index_data).tolist()

        except:
            print(traceback.format_exc())

        self.measure_histogram_data = histogram_data

        return histogram_data


    def plot_measurement_histogram(self, histogram_data):

        try:

            histogram_dataset = self.measure_graph_data.currentText()
            histogram_channel = self.measure_graph_channel.currentText()
            measure_label = self.measure_label.currentText()

            exposure_time = self.measure_exposure_time.value()

            histogram_selection = self.measure_histogram_dataset.currentText()
            histogram_mode = self.measure_histogram_mode.currentText()
            xaxis = self.measure_histogram_xaxis.currentText()
            bin_size = self.measure_histogram_bin_size.currentText()

            x_label = f"{histogram_selection}"
            title = f"{histogram_dataset} - {histogram_channel}\n{measure_label} Histogram"

            if bin_size.isdigit():
                bin_size = int(bin_size)
            else:
                bin_size = "auto"

            if histogram_mode.lower() == "frequency":
                ylabel = "Frequency"
                density = False
            else:
                ylabel = "Probability"
                density = True

            self.measure_graph_canvas.axes.clear()
            plot = False

            data = histogram_data["values"]

            if data != []:

                lower_limit, upper_limit = np.percentile(data, [1, 99])
                lower_limit = lower_limit - (upper_limit - lower_limit) * 0.1
                upper_limit = upper_limit + (upper_limit - lower_limit) * 0.1

                self.measure_graph_canvas.axes.hist(data, bins=bin_size, alpha=0.5, label=measure_label, density=density)
                self.measure_graph_canvas.axes.set_xlabel(x_label)
                self.measure_graph_canvas.axes.set_ylabel(ylabel)
                self.measure_graph_canvas.axes.legend()

                self.measure_graph_canvas.axes.set_xlim(lower_limit, upper_limit)
                self.measure_graph_canvas.axes.autoscale(enable=True, axis='y')

                if xaxis.lower() == "linear":
                    self.measure_graph_canvas.axes.set_xscale('linear')
                else:
                    self.measure_graph_canvas.axes.set_xscale('log')

                self.measure_graph_canvas.axes.set_title(title)

                self.measure_graph_canvas.canvas.draw()
                plot = True


            if plot == False:
                self.measure_graph_canvas.axes.clear()
                self.measure_graph_canvas.canvas.draw()

        except:
            print(traceback.format_exc())


    def export_measure_histogram_data(self):

        try:
            trace_data, trace_index_data, measure_index_data = self.compile_meassure_histogram_data()
            histogram_data = self.compute_measurement_histogram(trace_data, trace_index_data, measure_index_data)

            histogram = self.measure_histogram_dataset.currentText()
            histogram_dataset = self.measure_graph_data.currentText()
            histogram_channel = self.measure_graph_channel.currentText()
            measure_label = self.measure_label.currentText()

            metric = f"{histogram_channel}-{histogram}"

            export_data = []

            histogram_values = histogram_data["values"]
            trace_index_values = histogram_data["trace_index"]
            measure_index_values = histogram_data["measure_index"]

            for value, trace_index, measure_index in zip(histogram_values, trace_index_values, measure_index_values):

                dat = {"dataset": histogram_dataset,
                       "trace": trace_index,
                       "measurement": measure_index,
                       "label": measure_label,
                       metric: value,
                       }

                export_data.append(dat)

            if export_data != []:

                export_data = pd.DataFrame(export_data)

                import_path = self.data_dict[histogram_dataset][0]["import_path"]
                export_path = str(import_path)

                export_dir = os.path.dirname(export_path)
                file_name = os.path.basename(export_path)
                file_name = file_name.split(".")[0] + f"_{metric}_{measure_label}_measurement_data.csv"

                export_path = os.path.join(export_dir, file_name)
                export_path = os.path.normpath(export_path)

                export_path = QFileDialog.getSaveFileName(self, "Save File", export_path, "CSV Files (*.csv,*.txt,*.dat)")[0]

                if export_path != "":
                    export_data.to_csv(export_path, index=False)
                    self.print_notification(f"Exported histogram data to {export_path}")

        except:
            print(traceback.format_exc())