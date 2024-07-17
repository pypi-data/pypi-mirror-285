import os.path

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from TraceAnalyser.funcs.gui_worker import Worker
import queue
import traceback
import numpy as np
import matplotlib.pyplot as plt
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


class _analysis_plotting_methods:

    def initialise_analysis_plot(self):

        try:

            self.print_notification("Drawing analysis plot...")

            if self.data_dict != {}:

                worker = Worker(self._initialise_analysis_plot)
                worker.signals.finished.connect(self.update_analysis_graph_canvas)
                self.threadpool.start(worker)
                pass

        except:
            print(traceback.format_exc())


    def _initialise_analysis_plot(self, progress_callback=None):

        trace_data_list, state_data_list = self.compile_analysis_histogram_data()
        histogram_data = self.compute_histograms(trace_data_list, state_data_list)

        self.plot_analysis_histogram(histogram_data)


    def compile_analysis_histogram_data(self):

        try:

            trace_data_list = []
            state_data_list = []

            self.analysis_graph_canvas.axes.clear()

            dataset = self.analysis_graph_dataset.currentText()
            mode = self.analysis_graph_channel.currentText()
            crop = self.analysis_crop_traces.isChecked()

            for localisation_index, localisation_data in enumerate(self.data_dict[dataset]):

                user_label = localisation_data["user_label"]
                crop_range = localisation_data["crop_range"]

                if self.get_filter_status("analysis", user_label) == False:

                    trace_data = localisation_data[mode]
                    state_data = localisation_data["states"]

                    if len(trace_data) > 0:

                        if crop == True and len(crop_range) == 2:
                            trace_data = trace_data[crop_range[0]:crop_range[1]]
                            state_data = state_data[crop_range[0]:crop_range[1]]

                        trace_data_list.append(trace_data)
                        state_data_list.append(state_data)

        except:
            print(traceback.format_exc())
            pass

        return trace_data_list, state_data_list


    def compute_histograms(self, trace_data, state_data):

        histogram_data = {}

        try:

            histogram_selection = self.analysis_histogram.currentText()
            state_selection = self.analysis_state.currentText()
            exposure_time = self.analysis_exposure_time.value()
            exclude_partial = self.analysis_exclude_partial.isChecked()

            if len(trace_data) > 0:

                histogram_data = {"metric":histogram_selection,
                                  "values": {},
                                  "trace_index": {},
                                  "data_index":{}}

                if "Raw Data" not in histogram_selection:

                    state_data_flat = np.array([item for sublist in state_data for item in sublist])
                    n_states = len(np.unique(state_data_flat))

                    if len(state_data) == len(trace_data) and n_states > 0:

                        for trace_dat, state_dat in zip(trace_data, state_data):

                            change_indices = np.where(np.diff(state_dat) != 0)[0] + 1

                            split_trace_data = np.split(trace_dat, change_indices)
                            split_state_data = np.split(state_dat, change_indices)

                            for state_index, (data, state) in enumerate(zip(split_trace_data, split_state_data)):

                                append = True

                                if exclude_partial == True:
                                    if state_index == 0 or state_index == n_states:
                                        append=False

                                if append == True:

                                    state = state[0]

                                    if state_selection == "All States" or str(state) == state_selection:

                                        if state not in histogram_data["values"].keys():
                                            histogram_data["values"][state] = []

                                        if histogram_selection == "Intensity":
                                            values = data.tolist()
                                        elif histogram_selection == "Centres":
                                            centres = np.mean(data)
                                            values = [centres]
                                            # values = [centres]*len(data)
                                        elif histogram_selection == "Noise":
                                            noise = np.std(data)
                                            values = [noise]
                                            # values = [noise]*len(data)
                                        elif histogram_selection == "Dwell Times (Frames)":
                                            dwell_time = len(data)
                                            values = [dwell_time]
                                            # values = [dwell_time]*len(data)
                                        elif histogram_selection == "Dwell Times (Seconds)":
                                            dwell_time = len(data)
                                            dwell_time = dwell_time * exposure_time * 1e-3
                                            values = [dwell_time]
                                            # values = [dwell_time] * len(data)

                                        histogram_data["values"][state].extend(values)

                else:

                    values = np.concatenate(trace_data).tolist()
                    histogram_data["values"][0] = values


        except:
            print(traceback.format_exc())
            pass

        return histogram_data

    def plot_analysis_histogram(self, histogram_data):

        try:

            if histogram_data != {}:

                histogram_dataset = self.analysis_graph_dataset.currentText()
                histogram_channel = self.analysis_graph_channel.currentText()

                histogram = self.analysis_histogram.currentText()
                histogram_type = self.analysis_histogram_type.currentText().lower()

                bin_size = self.analysis_histogram_bin_size.currentText()
                xaxis = self.analysis_histogram_xaxis.currentText()


                if bin_size.isdigit():
                    bin_size = int(bin_size)
                else:
                    bin_size = "auto"

                if histogram_type.lower() == "frequency":
                    ylabel = "Frequency"
                    density = False
                else:
                    ylabel = "Probability"
                    density = True

                if histogram == "Raw Data":
                    x_label = f"Intensity"
                    title = f"{histogram_dataset} - {histogram_channel}\nIntensity Histogram"
                elif histogram == "Intensity":
                    x_label = f"Intensity"
                    title = f"{histogram_dataset} - {histogram_channel}\nState Intensity Histogram"
                elif histogram == "Centres":
                    x_label = f"Centres"
                    title = f"{histogram_dataset} - {histogram_channel}\nState Centres Histogram"
                elif histogram == "Noise":
                    x_label = f"Noise"
                    title = f"{histogram_dataset} - {histogram_channel}\nState Noise Histogram"
                elif histogram == "Dwell Times (Frames)":
                    x_label = f"Dwell Times (Frames)"
                    title = f"{histogram_dataset} - {histogram_channel}\nState Dwell Times Histogram"
                elif histogram == "Dwell Times (Seconds)":
                    x_label = f"Dwell Times (Seconds)"
                    title = f"{histogram_dataset} - {histogram_channel}\nState Dwell Times Histogram"

                fig, ax = plt.subplots()

                all_data = []

                states = list(histogram_data["values"].keys())
                states = sorted(states)

                for state in states:

                    if histogram != "Raw Data":
                        plot_label = f"State {int(state)}"
                    else:
                        plot_label = histogram_channel

                    histogram_values = histogram_data["values"][state]

                    all_data.extend(histogram_values)

                    if len(histogram_values) > 0:

                        counts, bin_edges = np.histogram(histogram_values, bins=bin_size, density=density)
                        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

                        # Plot using matplotlib's bar function
                        width = np.diff(bin_edges)
                        ax.bar(bin_centers, counts, align='center', width=width, alpha=0.5, label=plot_label)

                if len(all_data) > 0:

                    ax.legend()
                    ax.set_xlabel(x_label)
                    ax.set_ylabel(ylabel)

                    if xaxis.lower() == "linear":
                        ax.set_xscale('linear')
                    else:
                        ax.set_xscale('log')

                    lower_limit, upper_limit = np.percentile(all_data, [1, 99])
                    lower_limit = lower_limit - (upper_limit - lower_limit) * 0.1
                    upper_limit = upper_limit + (upper_limit - lower_limit) * 0.1

                    ax.set_xlim(lower_limit, upper_limit)
                    ax.autoscale(enable=True, axis='y')
                    ax.set_title(title)

                    fig.canvas.draw()
                    fig.tight_layout()
                    self.plot_queue.put((fig, ax))

                else:
                    self.print_notification("No data to plot")
                    self.analysis_graph_canvas.axes.clear()
                    self.analysis_graph_canvas.canvas.draw()

        except:
            print(traceback.format_exc())
            pass

    def update_analysis_graph_canvas(self):

        try:
            fig, ax = self.plot_queue.get_nowait()

            # Replace the figure in the canvas
            self.analysis_graph_canvas.canvas.figure = fig

            # Update the canvas
            self.analysis_graph_canvas.canvas.draw()

            self.print_notification("Analysis graph updated")

        except queue.Empty:
            # Handle the case where the queue is empty
            pass
        except Exception as e:
            print(f"Error updating plot: {e}")
            traceback.print_exc()


    def _display_transmat(self, progress_callback=None):

        transmat = None

        try:

            dataset = self.analysis_graph_dataset.currentText()

            transmat_data = []

            for localisation_index, localisation_data in enumerate(self.data_dict[dataset]):

                user_label = localisation_data["user_label"]

                if self.get_filter_status("analysis", user_label) == False:

                    state_data = localisation_data["states"]

                    if len(state_data) > 0:

                        transmat_data.append(state_data)

            transmat_data = np.concatenate(transmat_data, axis=0).astype(int)
            transmat = self.calculate_transition_matrix(transmat_data)

            if transmat is not None:

                self.analysis_graph_canvas.axes.clear()

                N = len(transmat)

                fig, ax = plt.subplots()
                cax = ax.matshow(transmat, cmap='Blues')

                ax.set_xticks(np.arange(N))
                ax.set_yticks(np.arange(N))
                ax.set_xticklabels([f'State {i}' for i in range(N)], va='center', ha='center')
                ax.set_yticklabels([f'State {i}' for i in range(N)], rotation=90, va='center', ha='center')

                for i in range(N):
                    for j in range(N):
                        c = transmat[j, i]
                        ax.text(i, j, f'{c:.3f}', va='center', ha='center', fontweight='bold', fontsize=12)

                fig.canvas.draw()
                fig.tight_layout()

                self.plot_queue.put((fig, ax))
                self.update_analysis_graph_canvas()

        except:
            print(traceback.format_exc())
            pass

        return transmat


    def initialise_transmat_plot(self):

        self.print_notification("Drawing Transition Matrix...")

        if self.data_dict != {}:

            worker = Worker(self._display_transmat)
            worker.signals.finished.connect(self.update_analysis_graph_canvas)
            self.threadpool.start(worker)


    def calculate_transition_matrix(self, predictions, num_states=None):

        if num_states is None:
            num_states = len(set(predictions))

        num_states = int(num_states)

        # Initialize the transition counts and state occurrence matrices
        transition_counts = np.zeros((num_states, num_states))
        state_occurrences = np.zeros(num_states)

        # Iterate through the state sequence to count transitions and occurrences
        for i in range(len(predictions) - 1):
            current_state = predictions[i]
            next_state = predictions[i + 1]
            transition_counts[current_state, next_state] += 1
            state_occurrences[current_state] += 1

        # Calculate transition probabilities
        transition_matrix = transition_counts / state_occurrences[:, None]

        # Handle any states that do not occur in the sequence
        transition_matrix[np.isnan(transition_matrix)] = 0

        return transition_matrix


    def export_analysis_histogram_data(self):

        try:

            histogram = self.analysis_histogram.currentText()
            state_selection = self.analysis_state.currentText()
            histogram_dataset = self.analysis_graph_dataset.currentText()
            histogram_channel = self.analysis_graph_channel.currentText()
            group_label = self.analysis_user_group.currentText()

            trace_data_list, state_data_list = self.compile_analysis_histogram_data()
            histogram_data = self.compute_histograms(trace_data_list, state_data_list)

            if histogram == "Raw Data":
                metric = f"{histogram_channel} Intensity"
            elif histogram == "Intensity":
                metric = f"{histogram_channel} Intensity"
            elif histogram == "Centres":
                metric = f"{histogram_channel} Centres"
            elif histogram == "Noise":
                metric = f"{histogram_channel} Noise"
            elif histogram == "Dwell Times (Frames)":
                metric = f"{histogram_channel} Dwell Times (Frames)"
            elif histogram == "Dwell Times (Seconds)":
                metric = f"{histogram_channel} Dwell Times (Seconds)"

            export_data = []

            if histogram_data != {}:

                for state_index, state in enumerate(histogram_data["values"].keys()):

                    if state_selection == "All States" or str(state) == state_selection:

                        histogram_values = histogram_data["values"][state]

                        for value in histogram_values:

                            if "Raw Data" in histogram:
                                dat = {"dataset": histogram_dataset,
                                       "group": group_label,
                                       metric: value,
                                       }
                            else:
                                dat = {"dataset": histogram_dataset,
                                       "group": group_label,
                                       metric: value,
                                       "state": state,
                                       }

                            if dat["group"] in ["None",None]:
                                dat.pop("group")

                            export_data.append(dat)

            export_data = pd.DataFrame(export_data)

            import_paths = [value[0]["import_path"] for key, value in self.data_dict.items()]
            export_path = import_paths[0]

            export_dir = os.path.dirname(export_path)
            file_name = os.path.basename(export_path)
            file_name = file_name.split(".")[0] + f"_{metric}_histogram_data.csv"

            export_path = os.path.join(export_dir, file_name)
            export_path = os.path.normpath(export_path)

            export_path = QFileDialog.getSaveFileName(self, "Save File", export_path, "CSV Files (*.csv,*.txt,*.dat)")[0]

            if export_path != "":
                export_data.to_csv(export_path, index=False)
                self.print_notification(f"Exported histogram data to {export_path}")

        except:
            print(traceback.format_exc())
            pass