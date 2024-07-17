from functools import partial
import traceback
from TraceAnalyser.funcs.gui_worker import Worker
import numpy as np

class _detectcrop_utils:

    def update_detectcrop_options(self, n_checkbox=3):

        try:

            n_checkbox = 3

            for i in range(1, n_checkbox+1):

                checkbox = getattr(self.crop_window, f"threshold{i}")
                channel_combo = getattr(self.crop_window, f"threshold{i}_channel")
                criterion_combo = getattr(self.crop_window, f"threshold{i}_criterion")
                value_spinbox = getattr(self.crop_window, f"threshold{i}_value")

                if checkbox.isChecked():
                    channel_combo.setDisabled(False)
                    criterion_combo.setDisabled(False)
                    value_spinbox.setDisabled(False)
                else:
                    channel_combo.setDisabled(True)
                    criterion_combo.setDisabled(True)
                    value_spinbox.setDisabled(True)

        except:
            print(traceback.format_exc())
            pass

    def populate_detectcrop_combos(self, n_checkbox=3):

        try:

            window = "crop_window"
            dataset = "crop_dataset"
            channel_dict = "crop_channel_dict"

            # clear exisitng events

            self.update_dataset_selection(window, dataset)

            for i in range(1, n_checkbox+1):

                checkbox = getattr(self.crop_window, f"threshold{i}")

                self.update_channel_selection(window,
                    dataset, f"threshold{i}_channel",
                    channel_dict,True)

                update_func = partial(
                    self.update_channel_selection,
                    window, dataset,
                    f"threshold{i}_channel",
                    channel_dict
                )

                self.crop_window.crop_dataset.currentIndexChanged.connect(update_func)

                checkbox.stateChanged.connect(self.update_detectcrop_options)

        except:
            print(traceback.format_exc())
            pass

    def initialise_crop_detection(self):

        try:

            if self.data_dict != {}:

                worker = Worker(self.crop_range_detection)
                worker.signals.finished.connect(self.crop_range_detection_finished)
                worker.signals.progress.connect(partial(self.gui_progrssbar, name="crop"))
                self.threadpool.start(worker)

        except:
            print(traceback.format_exc())
            pass


    def crop_range_detection_function(self, data, criterion, value):

        crop_index = None

        try:
            # Convert data to numpy array for efficient computation
            data = np.array(data)

            # Initialize a binary array based on the threshold
            # 1 for values above the threshold, 0 for values below
            if criterion == "Above":
                threshold_array = np.where(data <= value, 1, 0)
            else:
                threshold_array = np.where(data >= value, 1, 0)

            # Find the indices of the non-zero elements in the threshold array
            # These are the indices of the data that are above the threshold
            threshold_indices = np.nonzero(threshold_array)[0]

            if len(threshold_indices) > 0:
                crop_index = threshold_indices[0]

        except:
            pass

        return crop_index


    def crop_range_detection(self, progress_callback, n_checkbox=3):

        try:
            dataset_name = self.crop_window.crop_dataset.currentText()

            if dataset_name == "All Datasets":
                dataset_list = list(self.data_dict.keys())
            else:
                dataset_list = [dataset_name]

            total_traces = 0
            for dataset_name in dataset_list:
                total_traces += len(self.data_dict[dataset_name])

            check_box_dict = {}
            for i in range(1, n_checkbox+1):
                checkbox = getattr(self.crop_window, f"threshold{i}")
                if checkbox.isChecked():
                    channel_combo = getattr(self.crop_window, f"threshold{i}_channel")
                    criterion_combo = getattr(self.crop_window, f"threshold{i}_criterion")
                    value_spinbox = getattr(self.crop_window, f"threshold{i}_value")

                    check_box_dict[i] = {"channel": channel_combo.currentText(),
                                         "criterion": criterion_combo.currentText(),
                                         "value": float(value_spinbox.value())}

            if check_box_dict != {}:

                n_traces = 0
                for dataset_name in dataset_list:

                    dataset_data = self.data_dict[dataset_name]

                    for localisation_number, localisation_data in enumerate(dataset_data):

                        user_label = localisation_data["user_label"]

                        if self.get_filter_status("detect_crop", user_label) == False:

                            index_list = []

                            for args in check_box_dict.values():

                                data = localisation_data[args["channel"]]
                                criterion = args["criterion"]
                                value = args["value"]

                                crop_index = self.crop_range_detection_function(data,
                                    criterion, value)

                                if crop_index is not None:
                                    index_list.append(crop_index)

                            if index_list != []:

                                crop_index = max(index_list)

                                if crop_index > 0 and crop_index < len(data):
                                    crop_range = [0, crop_index]
                                elif crop_index == 0:
                                    crop_range = []
                                elif crop_index == len(data):
                                    crop_range = [0, len(data)]

                                localisation_data["crop_range"] = crop_range

        except:
            print(traceback.format_exc())
            pass

    def crop_range_detection_finished(self):

        self.plot_traces(update_plot=False)

        self.print_notification("Crop range detection complete")