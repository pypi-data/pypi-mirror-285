from functools import partial
import traceback
import numpy as np

from TraceAnalyser.funcs.gui_worker import Worker



class _group_utils:


    def update_group_options(self):

        try:

            # get list of QCheckBoxes in group_window
            group_options = ["intensity"]

            group_window = self.group_window

            for group_name in group_options:

                checkbox = getattr(group_window, f"group_{group_name}")
                channel_combo = getattr(group_window, f"group_{group_name}_channel")
                criterion_combo = getattr(group_window, f"group_{group_name}_criterion")
                value_spinbox = getattr(group_window, f"group_{group_name}_value")

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

    def populate_group_combos(self):

        try:
            self.update_dataset_selection("group_window",
                "group_dataset")

            self.update_channel_selection("group_window",
                "group_dataset", "group_intensity_channel",
                "group_channel_dict")

            update_func = partial(self.update_channel_selection,
                "group_window",
                "group_dataset", "group_intensity_channel",
                "group_channel_dict")

            self.group_window.group_dataset.currentIndexChanged.connect(update_func)

        except:
            print(traceback.format_exc())
            pass


    def trace_grouping_finished(self):

        try:
            self.group_window.group_progressbar.setValue(0)
            self.print_notification("Trace Grouping complete")
            self.plot_traces(update_plot=False)

        except:
            print(traceback.format_exc())
            pass


    def group_by_intensity(self, localisation_data):

        try:

            grouped_user_group = self.group_window.grouped_user_group.currentText()
            channel = self.group_window.group_intensity_channel.currentText()
            criterion = self.group_window.group_intensity_criterion.currentText()
            value = self.group_window.group_intensity_value.value()

            if channel in localisation_data.keys():
                data = np.array(localisation_data[channel]).copy()

                if criterion.lower() == "above" and data.max() > value:
                    filter = True
                elif criterion.lower() == "below" and data.min() < value:
                    filter = True
                else:
                    filter = False

                if filter:
                    localisation_data["user_label"] = grouped_user_group

        except:
            print(traceback.format_exc())

        return localisation_data


    def trace_grouping(self, progress_callback = None):

        try:

            dataset_name = self.group_window.group_dataset.currentText()
            filter_intensity = self.group_window.group_intensity.isChecked()

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

                    if self.get_filter_status("group", user_label) == False:

                        if filter_intensity:
                            self.group_by_intensity(localisation_data)

                    if progress_callback != None:
                        progress = int(((n_traces+1)/total_traces)*100)
                        progress_callback.emit(progress)


        except:
            print(traceback.format_exc())
            pass



    def init_trace_grouping(self):

        try:

            if self.data_dict != {}:

                worker = Worker(self.trace_grouping)
                worker.signals.finished.connect(self.trace_grouping_finished)
                worker.signals.progress.connect(partial(self.gui_progrssbar, name="group"))
                self.threadpool.start(worker)
        except:
            print(traceback.format_exc())
            pass

