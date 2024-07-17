from functools import partial
import traceback
from scipy.ndimage import median_filter
import numpy as np

from TraceAnalyser.funcs.gui_worker import Worker



class _bleach_utils:

    def populate_bleach_combos(self):

        try:
            self.update_dataset_selection("bleach_window",
                "bleach_dataset")

        except:
            print(traceback.format_exc())
            pass

    def bleach_detection_finished(self):

        try:

            self.bleach_window.bleach_progressbar.setValue(0)
            self.print_notification("Bleach detection finished")
            self.plot_traces(update_plot=False)

        except:
            print(traceback.format_exc())
            pass

    def detect_bleach_index(self, data, threshold, event_size, n_events_ignored, filter=True):

        bleach_index = None

        try:
            # Convert data to numpy array for efficient computation
            data = np.array(data)

            # Apply median filter to data if filter is True
            if filter:
                data = median_filter(data, size=3)

            # Initialize a binary array based on the threshold
            # 1 for values above the threshold, 0 for values below
            threshold_array = np.where(data >= threshold, 1, 0)

            # Initialize variables to track events and their lengths
            current_event_length = 0
            event_count = 0

            # Iterate through the threshold_array from end to start
            for i in range(len(threshold_array) - 1, -1, -1):
                # If the current value is above the threshold, it's part of an event
                if threshold_array[i] == 1:
                    current_event_length += 1
                    current_event_end = i
                    # If at the start of the data or the previous value is below the threshold,
                    # check if the event is of sufficient size
                    if i == 0 or threshold_array[i - 1] == 0:
                        if current_event_length >= event_size:
                            event_count += 1
                        if event_count > n_events_ignored:
                            bleach_index = i + current_event_length
                            break
                        current_event_length = 0

            # If bleach_index was not set during the loop, check if it's due to insufficient events
            if bleach_index is None:
                bleach_index = 0  # Assuming no bleaching detected means start of the data

        except Exception as e:
            print(traceback.format_exc())

        return bleach_index

    def bleach_detection(self, progress_callback=None):

        try:

            dataset_name = self.bleach_window.bleach_dataset.currentText()
            donor_threshold = self.bleach_window.bleach_donor_threshold.value()
            acceptor_threshold = self.bleach_window.bleach_acceptor_threshold.value()
            event_size = self.bleach_window.bleach_event_size.value()
            n_events_ignored = self.bleach_window.bleach_events_ignored.value()

            if dataset_name == "All Datasets":
                dataset_list = list(self.data_dict.keys())
            else:
                dataset_list = [dataset_name]

            total_traces = 0
            for dataset_name in dataset_list:
                total_traces += len(self.data_dict[dataset_name])

            n_traces = 0
            for dataset_name in dataset_list:
                dataset_data = self.data_dict[dataset_name]

                for localisation_number, localisation_data in enumerate(dataset_data):

                    user_label = localisation_data["user_label"]
                    correction_factors = localisation_data["correction_factors"]

                    if "bleach_dict" not in localisation_data:
                        localisation_data["bleach_dict"] = {}

                    if self.get_filter_status("bleach", user_label) == False:

                        channel_list = list(localisation_data.keys())

                        if "Donor" in channel_list:

                            data = np.array(localisation_data["Donor"])

                            if len(data) > 0:

                                donor_bleach_index = self.detect_bleach_index(data,
                                    donor_threshold, event_size, n_events_ignored)

                                correction_factors["donor_bleach_index"] = donor_bleach_index

                        if "Acceptor" in channel_list:

                            data = np.array(localisation_data["Acceptor"])

                            if len(data) > 0:

                                acceptor_bleach_index = self.detect_bleach_index(data,
                                    acceptor_threshold, event_size, n_events_ignored)

                                correction_factors["acceptor_bleach_index"] = acceptor_bleach_index

                        if "DD" in channel_list:

                            data = np.array(localisation_data["DD"]).copy()

                            if len(data) > 0:

                                if "DA" in channel_list:
                                    data += np.array(localisation_data["DA"]).copy()

                                donor_bleach_index = self.detect_bleach_index(data,
                                    acceptor_threshold, event_size, n_events_ignored)

                                correction_factors["donor_bleach_index"] = donor_bleach_index

                        if "DA" in channel_list:

                            data = np.array(localisation_data["DA"]).copy()

                            if len(data) > 0:

                                acceptor_bleach_index = self.detect_bleach_index(data,
                                    acceptor_threshold, event_size, n_events_ignored)

                                correction_factors["acceptor_bleach_index"] = acceptor_bleach_index

                    n_traces += 1

                    if progress_callback != None:
                        progress = int(((n_traces+1)/total_traces)*100)
                        progress_callback.emit(progress)

        except:
            print(traceback.format_exc())
            pass



    def initialise_bleach_detection(self):

        try:

            if self.data_dict != {}:

                worker = Worker(self.bleach_detection)
                worker.signals.finished.connect(self.bleach_detection_finished)
                worker.signals.progress.connect(partial(self.gui_progrssbar, name="bleach"))
                self.threadpool.start(worker)

        except:
            print(traceback.format_exc())
            pass