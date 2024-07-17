
import json
import os.path
import traceback
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import pandas as pd
import originpro as op
from functools import partial
from TraceAnalyser.funcs.gui_worker import Worker
import time
import random
import string

class _export_methods:


    def initialise_export(self):

        try:

            export_mode = self.export_settings.export_mode.currentText()

            if export_mode == "JSON Dataset (.json)":
                self.initialise_json_export()

            elif export_mode  == "Excel (.xlsx)":
                self.initialise_excel_export()

            elif export_mode == "OriginLab (.opju)":
                self.initialise_origin_export()

            elif export_mode in ["DAT (.dat)", "CSV (.csv)", "Text (.txt)"]:
                self.initialise_file_export()

            elif export_mode == "ML Dataset":
                self.initialise_ml_export()

            elif export_mode == "Export Trace Summary":
                self.initialise_summary_export()

            elif export_mode == "ebFRET SMD (.mat)":
                self.initialise_ebfret_export()

            elif export_mode == "Nero (.dat)":
                self.initialise_nero_export()


        except:
            print(traceback.format_exc())
            pass

    def populate_export_combos(self):

            try:

                self.update_export_dataset_selection("export_dataset_selection")
                self.update_export_channel_selection("export_dataset_selection", "export_channel_selection")

                for dataset_combo_name in ["export_dataset_selection"]:
                    try:
                        dataset_combo = getattr(self.export_settings, dataset_combo_name)
                        dataset_name = dataset_combo_name
                        channel_name = dataset_combo_name.replace("dataset", "channel")
                        dataset_combo_func = partial(self.update_export_channel_selection, dataset_combo_name, channel_name)
                        dataset_combo.currentIndexChanged.connect(dataset_combo_func)
                    except:
                        print(traceback.format_exc())

            except:
                print(traceback.format_exc())

    def update_export_dataset_selection(self, dataset_combo ="export_dataset_selection"):

        try:

            if len(self.data_dict.keys()) > 0:

                dataset_combo = getattr(self.export_settings, dataset_combo)
                dataset_names = list(self.data_dict.keys())

                if len(dataset_names) > 1:
                    dataset_names.insert(0, "All Datasets")

                dataset_combo.blockSignals(True)
                dataset_combo.clear()
                dataset_combo.addItems(dataset_names)
                dataset_combo.blockSignals(False)

        except:
            print(traceback.format_exc())

    def update_export_channel_selection(self, dataset_combo_name ="export_dataset_selection",
                  channel_combo_name = "export_channel_selection"):

        try:

            export_mode = self.export_settings.export_mode.currentText()

            if export_mode == "Nero (.dat)":
                allowed_channels = ["Data","Trace", "Donor", "Acceptor", "FRET Efficiency",
                                    "ALEX Efficiency", "DD", "AA", "DA", "AD"]
            elif export_mode == "ebFRET SMD (.mat)":
                allowed_channels = ["FRET Data", "Data","Trace", "Donor", "Acceptor", "FRET Efficiency",
                                    "ALEX Efficiency", "DD", "AA", "DA", "AD"]
            else:
                allowed_channels = []


            if len(self.data_dict.keys()) > 0:

                channel_combo = getattr(self.export_settings, channel_combo_name)
                dataset_combo = getattr(self.export_settings, dataset_combo_name)

                export_dataset = dataset_combo.currentText()

                if export_dataset == "All Datasets":
                    dataset_list = list(self.data_dict.keys())
                else:
                    dataset_list = [export_dataset]

                all_export_names = []
                combo_options = []
                self.export_selection_dict = {}

                for dataset_name in dataset_list:
                    for channel_name in self.data_dict[dataset_name][0].keys():
                        if channel_name in ["Data", "Trace","Donor", "Acceptor",
                                            "FRET Efficiency","ALEX Efficiency","DD", "AA", "DA", "AD"]:
                            data_length = len(self.data_dict[dataset_name][0][channel_name])
                            if data_length > 1:
                                if channel_name not in all_export_names:
                                    all_export_names.append(channel_name)

                if set(["Donor", "Acceptor"]).issubset(all_export_names):
                    combo_options.append("FRET Data")
                    self.export_selection_dict["FRET Data"] = ["Donor", "Acceptor"]
                if "FRET Efficiency" in all_export_names:
                    combo_options.append("FRET Efficiency")
                    self.export_selection_dict["FRET Efficiency"] = ["FRET Efficiency"]
                if set(["Donor", "Acceptor", "FRET Efficiency"]).issubset(all_export_names):
                    combo_options.append("FRET Data + FRET Efficiency")
                    self.export_selection_dict["FRET Data + FRET Efficiency"] = ["Donor", "Acceptor", "FRET Efficiency"]
                if "ALEX Efficiency" in all_export_names:
                    combo_options.append("ALEX Efficiency")
                    self.export_selection_dict["ALEX Efficiency"] = ["ALEX Efficiency"]
                if set(["DD","DA","AD","AA"]).issubset(all_export_names):
                    combo_options.append("ALEX Data")
                    self.export_selection_dict["ALEX Data"] = ["DD","DA","AD","AA"]
                if set(["DD","DA","AD","AA","ALEX Efficiency"]).issubset(all_export_names):
                    combo_options.append("ALEX Data + ALEX Efficiency")
                    self.export_selection_dict["ALEX Data + ALEX Efficiency"] = ["DD","DA","AD","AA","ALEX Efficiency"]
                if "Trace" in all_export_names:
                    combo_options.append("Trace")
                    self.export_selection_dict["Trace"] = ["Trace"]
                if "Data" in all_export_names:
                    combo_options.append("Data")
                    self.export_selection_dict["Data"] = ["Data"]
                if "Donor" in all_export_names:
                    combo_options.append("Donor")
                    self.export_selection_dict["Donor"] = ["Donor"]
                if "Acceptor" in all_export_names:
                    combo_options.append("Acceptor")
                    self.export_selection_dict["Acceptor"] = ["Acceptor"]
                if "DD" in all_export_names:
                    combo_options.append("DD")
                    self.export_selection_dict["DD"] = ["DD"]
                if "AA" in all_export_names:
                    combo_options.append("AA")
                    self.export_selection_dict["AA"] = ["AA"]
                if "DA" in all_export_names:
                    combo_options.append("DA")
                    self.export_selection_dict["DA"] = ["DA"]
                if "AD" in all_export_names:
                    combo_options.append("AD")
                    self.export_selection_dict["AD"] = ["AD"]

                combo_options = self.sort_channel_list(combo_options)

                if allowed_channels != []:
                    combo_options = [channel for channel in combo_options if channel in allowed_channels]

                channel_combo.blockSignals(True)
                channel_combo.clear()
                channel_combo.addItems(combo_options)
                channel_combo.blockSignals(False)

        except:
            print(traceback.format_exc())

    def initialise_excel_export(self):

        if self.data_dict != {}:

            export_location = self.export_settings.export_location.currentText()
            split_datasets = self.export_settings.export_split_datasets.isChecked()
            export_dataset_name = self.export_settings.export_dataset_selection.currentText()
            export_channel_name = self.export_settings.export_channel_selection.currentText()
            crop_mode = self.export_settings.export_crop_data.isChecked()
            export_states = self.export_settings.export_fitted_states.isChecked()
            export_state_means = self.export_settings.export_state_means.isChecked()

            export_paths = self.get_export_paths(extension="xlsx")

            if export_location == "Select Directory":
                export_dir = os.path.dirname(export_paths[0])

                export_dir = QFileDialog.getExistingDirectory(self, "Select Directory", export_dir)

                if export_dir != "":
                    export_paths = [os.path.join(export_dir, os.path.basename(export_path)) for export_path in export_paths]
                    export_paths = [os.path.abspath(export_path) for export_path in export_paths]

            worker = Worker(self.export_excel_data, export_dataset_name, export_channel_name,
                            crop_mode, export_states, export_state_means, export_paths, split_datasets)
            worker.signals.progress.connect(partial(self.gui_progrssbar, name="export"))
            worker.signals.finished.connect(self.export_finished)
            self.threadpool.start(worker)


    def initialise_nero_export(self):

        if self.data_dict != {}:
            export_location = self.export_settings.export_location.currentText()
            split_datasets = self.export_settings.export_split_datasets.isChecked()
            export_dataset_name = self.export_settings.export_dataset_selection.currentText()
            export_channel_name = self.export_settings.export_channel_selection.currentText()
            crop_mode = False
            export_states = self.export_settings.export_fitted_states.isChecked()

            export_paths = self.get_export_paths(extension="dat")

            if export_location == "Select Directory":
                export_dir = os.path.dirname(export_paths[0])

                export_dir = QFileDialog.getExistingDirectory(self, "Select Directory", export_dir)

                if export_dir != "":
                    export_paths = [os.path.join(export_dir, os.path.basename(export_path)) for export_path in export_paths]
                    export_paths = [os.path.abspath(export_path) for export_path in export_paths]

            worker = Worker(self.export_nero_data, export_dataset_name, export_channel_name,
                crop_mode, export_paths, split_datasets)
            worker.signals.progress.connect(partial(self.gui_progrssbar, name="export"))
            worker.signals.finished.connect(self.export_finished)
            self.threadpool.start(worker)

    def initialise_ebfret_export(self):

        if self.data_dict != {}:

            export_location = self.export_settings.export_location.currentText()
            split_datasets = self.export_settings.export_split_datasets.isChecked()
            export_dataset_name = self.export_settings.export_dataset_selection.currentText()
            export_channel_name = self.export_settings.export_channel_selection.currentText()
            crop_mode = self.export_settings.export_crop_data.isChecked()
            export_states = self.export_settings.export_fitted_states.isChecked()

            export_paths = self.get_export_paths(extension="mat")

            if export_location == "Select Directory":
                export_dir = os.path.dirname(export_paths[0])

                export_dir = QFileDialog.getExistingDirectory(self, "Select Directory", export_dir)

                if export_dir != "":
                    export_paths = [os.path.join(export_dir, os.path.basename(export_path)) for export_path in export_paths]
                    export_paths = [os.path.abspath(export_path) for export_path in export_paths]

            worker = Worker(self.export_ebFRET_data, export_dataset_name, export_channel_name,
                            crop_mode, export_paths, split_datasets)
            worker.signals.progress.connect(partial(self.gui_progrssbar, name="export"))
            worker.signals.finished.connect(self.export_finished)
            self.threadpool.start(worker)

    def initialise_origin_export(self):

        if self.data_dict != {}:

            export_location = self.export_settings.export_location.currentText()
            split_datasets = self.export_settings.export_split_datasets.isChecked()
            export_dataset_name = self.export_settings.export_dataset_selection.currentText()
            export_channel_name = self.export_settings.export_channel_selection.currentText()
            crop_mode = self.export_settings.export_crop_data.isChecked()
            export_states = self.export_settings.export_fitted_states.isChecked()
            export_state_means = self.export_settings.export_state_means.isChecked()

            export_paths = self.get_export_paths(extension="opju")

            if export_location == "Select Directory":
                export_dir = os.path.dirname(export_paths[0])

                export_dir = QFileDialog.getExistingDirectory(self, "Select Directory", export_dir)

                if export_dir != "":
                    export_paths = [os.path.join(export_dir, os.path.basename(export_path)) for export_path in export_paths]
                    export_paths = [os.path.abspath(export_path) for export_path in export_paths]

            worker = Worker(self.export_origin_data, export_dataset_name, export_channel_name,
                            crop_mode, export_states, export_state_means, export_paths, split_datasets)
            worker.signals.progress.connect(partial(self.gui_progrssbar, name="export"))
            worker.signals.finished.connect(self.export_finished)
            self.threadpool.start(worker)

    def initialise_json_export(self):

        if self.data_dict != {}:

            export_location = self.export_settings.export_location.currentText()

            export_path = self.get_export_paths(extension="json")[0]

            if export_location == "Select Directory":
                export_path, _ = QFileDialog.getSaveFileName(self, "Select Directory", export_path)

            export_dir = os.path.dirname(export_path)

            if os.path.isdir(export_dir) == True:

                worker = Worker(self.export_gapseq_json, export_path)
                worker.signals.progress.connect(partial(self.gui_progrssbar, name="export"))
                worker.signals.finished.connect(self.export_finished)
                self.threadpool.start(worker)

    def initialise_ml_export(self):

        if self.data_dict != {}:

            export_location = self.export_settings.export_location.currentText()
            export_dataset = self.export_settings.export_dataset_selection.currentText()
            export_channel = self.export_settings.export_channel_selection.currentText()
            crop_mode = self.export_settings.export_crop_data.isChecked()
            class_label = self.export_settings.ml_export_class.currentText()

            export_path = self.get_export_paths(extension="txt", ML=True)[0]

            if export_location == "Select Directory":
                export_path, _ = QFileDialog.getSaveFileName(self, "Select Directory", export_path)

            export_dir = os.path.dirname(export_path)

            if os.path.isdir(export_dir) == True:

                worker = Worker(self.export_ml_dataset, export_dataset, export_channel,
                                crop_mode, class_label, export_path)
                worker.signals.progress.connect(partial(self.gui_progrssbar, name="export"))
                worker.signals.finished.connect(self.export_finished)
                self.threadpool.start(worker)

    def initialise_summary_export(self):

        if self.data_dict != {}:

            export_location = self.export_settings.export_location.currentText()
            export_dataset = self.export_settings.export_dataset_selection.currentText()
            export_channel = self.export_settings.export_channel_selection.currentText()
            crop_mode = self.export_settings.export_crop_data.isChecked()

            export_path = self.get_export_paths(extension="csv", summary=True)[0]

            if export_location == "Select Directory":
                export_path, _ = QFileDialog.getSaveFileName(self, "Select Directory", export_path)

            export_dir = os.path.dirname(export_path)

            if os.path.isdir(export_dir) == True:

                worker = Worker(self.export_summary, export_path,
                    export_dataset, export_channel, crop_mode)
                worker.signals.progress.connect(partial(self.gui_progrssbar, name="export"))
                worker.signals.finished.connect(self.export_finished)
                self.threadpool.start(worker)

    def export_summary(self, export_path, export_dataset, export_channel, crop_data, progress_callback=None):

        try:

            if export_dataset == "All Datasets":
                dataset_list = list(self.data_dict.keys())
            else:
                dataset_list = [export_dataset]

            summary_data = []

            iter = 0

            for dataset_name in dataset_list:
                dataset_data = self.data_dict[dataset_name]

                for localisation_number, localisation_data in enumerate(dataset_data):

                    user_label = localisation_data["user_label"]
                    crop_range = localisation_data["crop_range"]
                    file_path = localisation_data["import_path"]
                    file_name = os.path.basename(file_path)
                    state_data = localisation_data["states"].copy()

                    if self.get_filter_status("summary", user_label) == False:

                        for data_name in self.export_selection_dict[export_channel]:

                            trace_data = localisation_data[data_name].copy()

                            if len(state_data) == len(trace_data):

                                if crop_data == True and len(crop_range) == 2:
                                    crop_range = [int(crop_range[0]), int(crop_range[1])]
                                    crop_range = sorted(crop_range)
                                    if crop_range[0] < 0:
                                        crop_range[0] = 0
                                    if crop_range[0] >= 0 and crop_range[1] <= len(trace_data):
                                        trace_data = trace_data[crop_range[0]:crop_range[1]]
                                        state_data = state_data[crop_range[0]:crop_range[1]]

                                change_indices = np.where(np.diff(state_data) != 0)[0] + 1

                                split_trace_data = np.split(trace_data, change_indices)
                                split_state_data = np.split(state_data, change_indices)

                                for data, state in zip(split_trace_data, split_state_data):
                                    state = state[0]

                                    dwell_time = len(data)
                                    intensity = np.mean(data)

                                    state_info = {
                                        "dataset": dataset_name,
                                        "localisation": localisation_number,
                                        "user_label": user_label,
                                        "state": state,
                                        "dwell_time": dwell_time,
                                        f"{data_name}_intensity": intensity,
                                    }
                                    summary_data.append(state_info)

                    iter += 1

                    if progress_callback != None:
                        progress = int((iter / len(dataset_list)) * 100)
                        progress_callback.emit(progress)

            if len(summary_data) > 0:

                summary_data = pd.DataFrame(summary_data)
                summary_data.to_csv(export_path, index=False)

                self.print_notification(f"Exported Trace Summary to {export_path}")

        except:
            print(traceback.format_exc())
            pass


    def export_ml_dataset(self, export_dataset, export_channel,
            crop_mode, class_label, export_path, progress_callback=None):

        try:

            ml_data = self.get_ml_data(export_dataset, export_channel,
                crop_mode,class_label)

            if ml_data != {}:

                with open(export_path, "w") as f:
                    json.dump(ml_data, f, cls=npEncoder)

                self.print_notification(f"Exported ML data to {export_path}")

        except:
            print(traceback.format_exc())

    def initialise_file_export(self):

        if self.data_dict != {}:

            export_mode = self.export_settings.export_mode.currentText()
            export_location = self.export_settings.export_location.currentText()
            split_datasets = self.export_settings.export_split_datasets.isChecked()
            export_dataset_name = self.export_settings.export_dataset_selection.currentText()
            export_channel_name = self.export_settings.export_channel_selection.currentText()
            crop_mode = self.export_settings.export_crop_data.isChecked()
            data_separator = self.export_settings.export_separator.currentText()
            export_states = self.export_settings.export_fitted_states.isChecked()
            export_state_means = self.export_settings.export_state_means.isChecked()

            if export_mode == "DAT (.dat)":
                export_paths = self.get_export_paths(extension="dat")
            if export_mode == "Text (.txt)":
                export_paths = self.get_export_paths(extension="txt")
            if export_mode == "CSV (.csv)":
                export_paths = self.get_export_paths(extension="csv")

            if data_separator.lower() == "space":
                data_separator = " "
            elif data_separator.lower() == "tab":
                data_separator = "\t"
            elif data_separator.lower() == "comma":
                data_separator = ","

            if export_location == "Select Directory":
                export_dir = os.path.dirname(export_paths[0])

                export_dir = QFileDialog.getExistingDirectory(self, "Select Directory", export_dir)

                if export_dir != "":
                    export_paths = [os.path.join(export_dir, os.path.basename(export_path)) for export_path in export_paths]
                    export_paths = [os.path.abspath(export_path) for export_path in export_paths]

            worker = Worker(self.export_dat, export_dataset_name, export_channel_name,
                            crop_mode, export_states, export_state_means, data_separator, export_paths, split_datasets)
            worker.signals.progress.connect(partial(self.gui_progrssbar, name="export"))
            worker.signals.finished.connect(self.export_finished)
            self.threadpool.start(worker)

    def get_export_paths(self, extension="json", ML=False, summary=False):

        export_paths = []

        import_paths = [value[0]["import_path"] for key, value in self.data_dict.items()]

        if ML == True:
            ml_string = "_ML"
        elif summary == True:
            ml_string = "_summary"
        else:
            ml_string = ""

        for import_path in import_paths:

            export_filename = os.path.basename(import_path)
            export_dir = os.path.dirname(import_path)

            if "_gapseq" not in export_filename:
                export_filename = export_filename.split(".")[0] + f"_gapseq{ml_string}.{extension}"
            else:
                export_filename = export_filename.split(".")[0] + f"{ml_string}.{extension}"

            export_path = os.path.join(export_dir, export_filename)
            export_path = os.path.abspath(export_path)

            export_paths.append(export_path)

        return export_paths

    def infer_efficiency(self, data, ia_range=[10,20]):

        E = np.array(data)  # Ensure data is in numpy array form for vectorized operations
        # Generate random IA values within the specified range for each efficiency value
        IA = np.random.uniform(low=ia_range[0], high=ia_range[1], size=E.shape)
        ID = IA * (1 - E) / E  # Calculate ID based on the efficiency values and randomly chosen IA

        return ID, IA


    def populate_ebfret_session(self, export_dataset_name, export_channel_name,
            crop_data, progress_callback=None):

        try:

            ebfret_session = {"series": {"file": [],"label": [],"group": [],"time": [],
                                         "donor": [],"acceptor": [],"signal": [],
                                         "crop": [], "exclude": []},
                              "controls": {"ensemble": [{"min": 2, "max": 6, "value":2}],
                                           "series":[],
                                           "run_analysis":[False]},
                              "analysis": [[]],
                              # "analysis": {"dim":[[], [{"states":2}], [{"states":3}],[{"states":4}], [{"states":5}], [{"states":6}]],
                              #              "viterbi":[[]]},
                              }

            if export_dataset_name == "All Datasets":
                dataset_list = list(self.data_dict.keys())
            else:
                dataset_list = [export_dataset_name]

            n_traces = 0

            for dataset_name in dataset_list:
                dataset_data = self.data_dict[dataset_name]

                for localisation_number, localisation_data in enumerate(dataset_data):
                    user_label = localisation_data["user_label"]
                    crop_range = localisation_data["crop_range"]
                    file_path = localisation_data["import_path"]
                    file_name = os.path.basename(file_path)
                    states = localisation_data["states"]

                    if self.get_filter_status("data", user_label) == False:

                        n_traces += 1
                        session_values = []

                        for data_name in self.export_selection_dict[export_channel_name]:
                            data = localisation_data[data_name]

                            if crop_data == True and len(crop_range) == 2:
                                crop_range = [int(crop_range[0]), int(crop_range[1])]
                                crop_range = sorted(crop_range)
                                if crop_range[0] < 0:
                                    crop_range[0] = 0
                                if crop_range[0] >= 0 and crop_range[1] <= len(data):
                                    data = data[crop_range[0]:crop_range[1]]

                            data = np.nan_to_num(data)
                            session_values.append(data)

                        if len(session_values) == 1:
                            signal = session_values[0]
                            donor, acceptor = self.infer_efficiency(signal)
                        else:
                            donor, acceptor = session_values
                            signal = acceptor/(donor + acceptor)

                        session_label = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
                        time_data = np.expand_dims(np.arange(1, len(session_values[0])+1), -1).astype(float).tolist()

                        donor = np.expand_dims(donor, -1).astype(float).tolist()
                        acceptor = np.expand_dims(acceptor, -1).astype(float).tolist()
                        signal = np.expand_dims(signal, -1).astype(float).tolist()
                        crop = {"min": 1, "max": len(signal)-1}

                        ebfret_session["series"]["file"].append(file_name)
                        ebfret_session["series"]["label"].append(session_label)
                        ebfret_session["series"]["group"].append("group 1")
                        ebfret_session["series"]["time"].append(time_data)
                        ebfret_session["series"]["donor"].append(donor)
                        ebfret_session["series"]["acceptor"].append(acceptor)
                        ebfret_session["series"]["signal"].append(signal)
                        ebfret_session["series"]["crop"].append(crop)
                        ebfret_session["series"]["exclude"].append(False)

            ebfret_session["controls"]["series"] = [{"value":1, "min": 1, "max": n_traces,}]

        except:
            print(traceback.format_exc())
            pass

        return ebfret_session




    def populate_smd_dict(self, export_dataset_name, export_channel_name,
            crop_data, progress_callback=None):

        try:

            columns = ["donor","acceptor","fret"]

            smd_dict = {"attr": {"data_package": "TraceAnalyser"},
                        "columns": columns,
                        "data": {"attr": [], "id": [], "index": [], "values": []},
                        "id": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
                        "type": "TraceAnalyser",
                        }

            if export_dataset_name == "All Datasets":
                dataset_list = list(self.data_dict.keys())
            else:
                dataset_list = [export_dataset_name]

            for dataset_name in dataset_list:
                dataset_data = self.data_dict[dataset_name]

                for localisation_number, localisation_data in enumerate(dataset_data):

                    user_label = localisation_data["user_label"]
                    crop_range = localisation_data["crop_range"]
                    file_path = localisation_data["import_path"]
                    file_name = os.path.basename(file_path)
                    states = localisation_data["states"]

                    if self.get_filter_status("data", user_label) == False:

                        smd_values = []

                        for data_name in self.export_selection_dict[export_channel_name]:

                            data = localisation_data[data_name]

                            if crop_data == True and len(crop_range) == 2:
                                crop_range = [int(crop_range[0]), int(crop_range[1])]
                                crop_range = sorted(crop_range)
                                if crop_range[0] < 0:
                                    crop_range[0] = 0
                                if crop_range[0] >= 0 and crop_range[1] <= len(data):
                                    data = data[crop_range[0]:crop_range[1]]

                            data = np.nan_to_num(data)
                            # data[data <= 0] = np.random.rand() * 1e-10
                            smd_values.append(data)

                        if len(smd_values) == 1:
                            data = smd_values[0]
                            # data = np.random.uniform(low=-1, high=1, size=data.shape)
                            ID, IA = self.infer_efficiency(data)
                            fret = IA/(ID + IA)
                            smd_values = [list(ID), list(IA), list(fret)]
                        elif len(smd_values) == 2:
                            ID, IA = smd_values
                            fret = IA/(ID + IA)
                            smd_values = [list(ID), list(IA), list(fret)]

                        smd_index = np.expand_dims(np.arange(1, len(smd_values[0])+1), -1).astype(float).tolist()
                        smd_values = np.stack(smd_values, axis=1).tolist()

                        lowerbound = np.min(smd_values)

                        smd_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
                        smd_attr = {
                            "file":os.path.basename(file_path),
                            "layer" :data_name,
                            "localisation_number" :localisation_number,
                            "lowerbound" :lowerbound,
                            "group": "group 1",
                            "restart" :0,
                            "crop_min" :0,
                            "crop_max" :20,
                        }

                        smd_dict["data"]["attr"].append(smd_attr)
                        smd_dict["data"]["id"].append(smd_id)
                        smd_dict["data"]["index"].append(smd_index)
                        smd_dict["data"]["values"].append(smd_values)

        except:
            print(traceback.format_exc())
            smd_dict = {}

        return smd_dict


    def export_nero_data(self, export_dataset_name, export_channel_name,
            crop_mode, export_paths = [], split_datasets = False, progress_callback=None):
        try:
            if self.data_dict != {}:

                if split_datasets == False:

                    export_path = export_paths[0]

                    export_data_dict = self.get_export_data("data", export_dataset_name,
                        export_channel_name, crop_mode, export_states=False, progress_callback=progress_callback)

                    export_data = export_data_dict["data"]
                    export_data = np.stack(export_data, axis=1)

                    export_indices = np.array(export_data_dict["index"]).astype(int)
                    export_indices += 1

                    export_data = pd.DataFrame(export_data)
                    export_data.columns = export_indices

                    export_data.to_csv(export_path, index=False, sep=" ")

                    self.print_notification(f"Exported Nero data to {export_path}")

                else:

                    for export_dataset_name, export_path in zip(self.data_dict.keys(), export_paths):

                        export_data_dict = self.get_export_data("data", export_dataset_name,
                            export_channel_name, crop_mode, export_states=False, progress_callback=progress_callback)

                        export_data = export_data_dict["data"]
                        export_data = np.stack(export_data, axis=1)

                        export_indices = np.array(export_data_dict["index"]).astype(int)
                        export_indices += 1

                        export_data = pd.DataFrame(export_data)
                        export_data.columns = export_indices

                        export_data.to_csv(export_path, index=False, sep=" ")

                        self.print_notification(f"Exported Nero data to {export_path}")

        except:
            print(traceback.format_exc())




    def export_ebFRET_data(self, export_dataset_name, export_channel_name,
            crop_mode, export_paths = [], split_datasets = False, progress_callback=None):

        try:

            if split_datasets == False:

                export_path = export_paths[0]

                smd_dict  = self.populate_smd_dict(export_dataset_name, export_channel_name,
                    crop_mode, progress_callback)

                # smd_dict  = self.populate_ebfret_session(export_dataset_name, export_channel_name,
                #     crop_mode, progress_callback)

                import mat4py
                mat4py.savemat(export_path, smd_dict)

                self.print_notification(f"Exported SMD data to {export_path}")

            else:

                for export_dataset_name, export_path in zip(self.data_dict.keys(), export_paths):

                    smd_dict = self.populate_ebfret_session(export_dataset_name,
                        export_channel_name, crop_mode, progress_callback)

                    import mat4py
                    mat4py.savemat(export_path, smd_dict)

                self.print_notification(f"Exported SMD data to {export_path}")








        except:
            print(traceback.format_exc())



    def export_excel_data(self, export_dataset_name, export_channel_name,
            crop_mode, export_states=False, export_state_means = False,
            export_paths = [], split_datasets = False, progress_callback=None):

        try:
            if self.data_dict != {}:

                if split_datasets == False:

                    export_path = export_paths[0]

                    export_data_dict = self.get_export_data("excel",
                        export_dataset_name, export_channel_name, crop_mode,
                        export_states,export_state_means,
                        progress_callback=progress_callback)

                    export_data = export_data_dict["data"]

                    max_length = max([len(data) for data in export_data])

                    export_data = [np.pad(data, (0, max_length - len(data)), mode="constant", constant_values=np.nan) for data in export_data]

                    export_data = np.stack(export_data, axis=0).T

                    export_data = pd.DataFrame(export_data)

                    export_data.columns = [export_data_dict["index"],
                                           export_data_dict["dataset"],
                                           export_data_dict["data_name"],
                                           export_data_dict["user_label"],]

                    export_data.columns.names = ['Index', 'Dataset', 'Data', 'Class', 'Nucleotide']

                    with pd.ExcelWriter(export_path) as writer:
                        export_data.to_excel(writer, sheet_name='Trace Data', index=True, startrow=1, startcol=1)

                    self.print_notification(f"Exported data to {export_path}")

                else:

                    for export_dataset_name, export_path in zip(self.data_dict.keys(), export_paths):

                        export_data_dict = self.get_export_data("excel",
                            export_dataset_name, export_channel_name, crop_mode,
                            export_states, export_state_means,
                            progress_callback=progress_callback)

                        export_data = np.stack(export_data_dict["data"], axis=0).T

                        export_data = pd.DataFrame(export_data)

                        export_data.columns = [export_data_dict["index"],
                                               export_data_dict["dataset"],
                                               export_data_dict["data_name"],
                                               export_data_dict["user_label"],]

                        export_data.columns.names = ['Index', 'Dataset', 'Data', 'Class', 'Nucleotide']

                        with pd.ExcelWriter(export_path) as writer:
                            export_data.to_excel(writer, sheet_name='Trace Data', index=True, startrow=1, startcol=1)

        except:
            print(traceback.format_exc())

    def export_origin_data(self, export_dataset_name, export_channel_name,
            crop_mode, export_states=False, export_state_means=False, export_paths = [],
            split_datasets = False, progress_callback=None):

         try:

             if self.data_dict != {}:
                 if split_datasets == False:
                     export_path = export_paths[0]

                     export_data_dict = self.get_export_data("origin",
                         export_dataset_name, export_channel_name, crop_mode,
                         export_states, export_state_means,
                         progress_callback=progress_callback)

                     export_data = export_data_dict["data"]

                     max_length = max([len(data) for data in export_data])

                     export_data = [np.pad(data, (0, max_length - len(data)), mode="constant", constant_values=np.nan) for data in export_data]

                     export_data = np.stack(export_data, axis=0).T

                     export_data = pd.DataFrame(export_data)

                     export_data.columns = export_data_dict["data_name"]

                     if os.path.exists(export_path):
                         os.remove(export_path)

                     if op.oext:
                         op.set_show(False)

                     op.new()

                     wks = op.new_sheet()
                     wks.cols_axis('YY')
                     wks.from_df(export_data, addindex=True)

                     for i in range(len(export_data_dict["data_name"])):

                         index = export_data_dict["index"][i]
                         dataset = export_data_dict["dataset"][i]
                         user_label = export_data_dict["user_label"][i]

                         wks.set_label(i, dataset, 'Dataset')
                         wks.set_label(i, index, 'Index')
                         wks.set_label(i, user_label, 'User Label')

                         if progress_callback is not None:
                             progress = int(((i + 1) / len(export_data_dict["data_name"]))*100)
                             progress_callback.emit(progress)

                     op.save(export_path)

                     if op.oext:
                         op.exit()

                     self.print_notification(f"Exported data to {export_path}")

                 else:

                     n_datasets = len(self.data_dict.keys())

                     for export_dataset_name, export_path in zip(self.data_dict.keys(), export_paths):

                         export_data_dict = self.get_export_data("origin",
                             export_dataset_name, export_channel_name, crop_mode,
                             export_states, export_state_means,
                             progress_callback=progress_callback)

                         export_dataset = np.stack(export_data_dict["data"], axis=0).T

                         export_dataset = pd.DataFrame(export_dataset)

                         export_dataset.columns = export_data_dict["data_name"]

                         export_dataset.columns = export_data_dict["data_name"]

                         if os.path.exists(export_path):
                             os.remove(export_path)

                         if op.oext:
                             op.set_show(False)

                         op.new()

                         wks = op.new_sheet()
                         wks.cols_axis('YY')
                         wks.from_df(export_dataset, addindex=True)

                         for i in range(len(export_data_dict["data_name"])):
                             index = export_data_dict["index"][i]
                             dataset = export_data_dict["dataset"][i]
                             user_label = export_data_dict["user_label"][i]

                             wks.set_label(i, dataset, 'Dataset')
                             wks.set_label(i, index, 'Index')
                             wks.set_label(i, user_label, 'User Label')

                             if progress_callback is not None:
                                 progress = int(((i + 1) / len(export_data_dict["data_name"]))*100)
                                 progress_callback.emit(progress)

                         op.save(export_path)

                         if op.oext:
                             op.exit()

                         self.print_notification(f"Exported data to {export_path}")



         except:
             print(traceback.format_exc())

    def export_dat(self, export_dataset_name, export_channel_name, crop_mode,
            export_states = False, export_state_means = False,
            data_separator=",", export_paths = [], split_datasets = False, progress_callback=None):

            try:

                if self.data_dict != {}:
                    if split_datasets == False:

                        export_path = export_paths[0]

                        export_dir = os.path.dirname(export_path)

                        if os.path.exists(export_dir):

                            export_data_dict = self.get_export_data("data",
                                export_dataset_name, export_channel_name, crop_mode,
                                export_states, export_state_means,
                                progress_callback = progress_callback)

                            export_dataset = np.stack(export_data_dict["data"], axis=0).T

                            export_dataset = pd.DataFrame(export_dataset)

                            export_dataset.columns = [export_data_dict["index"],
                                                      export_data_dict["dataset"],
                                                      export_data_dict["data_name"],
                                                      export_data_dict["user_label"],]

                            export_dataset.to_csv(export_path, sep=data_separator, index=False, header=True)

                            self.print_notification(f"Exported data to {export_path}")

                    else:

                        for export_dataset_name, export_path in zip(self.data_dict.keys(), export_paths):

                            export_dir = os.path.dirname(export_path)

                            if os.path.exists(export_dir):

                                export_data_dict = self.get_export_data("data",
                                    export_dataset_name, export_channel_name, crop_mode,
                                    export_states, export_state_means,
                                    progress_callback=progress_callback,)

                                export_dataset = np.stack(export_data_dict["data"], axis=0).T

                                export_dataset = pd.DataFrame(export_dataset)

                                export_dataset.columns = [export_data_dict["index"],
                                                          export_data_dict["dataset"],
                                                          export_data_dict["data_name"],
                                                          export_data_dict["user_label"],]

                                export_dataset.to_csv(export_path, sep=data_separator, index=False, header=True)

                                self.print_notification(f"Exported data to {export_path}")

            except:
                print(traceback.format_exc())

    def get_ml_data(self, export_dataset_name, export_channel_name,
            crop_data, ml_label):

        try:

            ml_dict = {"data":[],
                       "states":[],
                       "ml_label":[],
                       "dataset":[],
                       "channels":[],
                       "bleach_range":[],
                       "user_label":[],
                       "file_name": [],
                       "import_path": [],
                       "crop_data": crop_data
                       }

            if export_dataset_name == "All Datasets":
                dataset_list = list(self.data_dict.keys())
            else:
                dataset_list = [export_dataset_name]

            channel_list = self.export_selection_dict[export_channel_name]

            for dataset_name in dataset_list:

                dataset_data = self.data_dict[dataset_name]

                for localisation_number, localisation_data in enumerate(dataset_data):

                    user_label = localisation_data["user_label"]
                    crop_range = localisation_data["crop_range"]
                    file_path = localisation_data["import_path"]
                    file_name = os.path.basename(file_path)
                    states = list(localisation_data["states"])

                    loc_data = []
                    loc_bleach_ranges = []
                    loc_channels = []

                    if self.get_filter_status("ML", user_label) == False:

                        for channel_name in channel_list:

                            data = localisation_data[channel_name]

                            if "bleach_dict" in localisation_data.keys():
                                bleach_dict = localisation_data["bleach_dict"]
                                bleach_range = bleach_dict[channel_name]
                            else:
                                bleach_range = None

                            if crop_data == True and len(crop_range) == 2:
                                crop_range = [int(crop_range[0]), int(crop_range[1])]
                                crop_range = sorted(crop_range)
                                if crop_range[0] < 0:
                                    crop_range[0] = 0
                                if crop_range[0] >= 0 and crop_range[1] <= len(data):
                                    data = data[crop_range[0]:crop_range[1]]

                            loc_data.append(list(data))
                            loc_channels.append(channel_name)
                            loc_bleach_ranges.append(bleach_range)

                        ml_dict["data"].append(loc_data)
                        ml_dict["states"].append(states)
                        ml_dict["channels"].append(loc_channels)
                        ml_dict["dataset"].append(dataset_name)
                        ml_dict["file_name"].append(file_name)
                        ml_dict["import_path"].append(file_path)
                        ml_dict["user_label"].append(user_label)
                        ml_dict["ml_label"].append(ml_label)
                        ml_dict["bleach_range"].append(loc_bleach_ranges)

        except:
            ml_dict = {}
            print(traceback.format_exc())

        return ml_dict

    def get_export_data(self, export_mode, export_dataset_name, export_channel_name,
            crop_data, export_states=False, export_state_means=False,
            pad_data = True, pad_value = np.nan, progress_callback = None):

        loc_index = []
        loc_dataset = []
        loc_user_label = []
        loc_data = []
        loc_states = []
        loc_data_name = []
        loc_file_name = []
        loc_path = []

        if export_dataset_name == "All Datasets":
            dataset_list = list(self.data_dict.keys())
        else:
            dataset_list = [export_dataset_name]

        n_traces = 0
        for dataset_name in dataset_list:
            dataset_data = self.data_dict[dataset_name]
            for localisation_number, localisation_data in enumerate(dataset_data):
                user_label = localisation_data["user_label"]
                if self.get_filter_status(export_mode, user_label) == False:
                    n_traces += 1

        iter = 0

        for dataset_name in dataset_list:

            dataset_data = self.data_dict[dataset_name]

            for localisation_number, localisation_data in enumerate(dataset_data):

                user_label = localisation_data["user_label"]
                crop_range = localisation_data["crop_range"]
                file_path = localisation_data["import_path"]
                file_name = os.path.basename(file_path)
                states = localisation_data["states"]

                if self.get_filter_status(export_mode, user_label) == False:

                    for data_name in self.export_selection_dict[export_channel_name]:

                        data = localisation_data[data_name]
                        state_means_x, state_means_y = localisation_data["state_means"][data_name]
                        states = localisation_data["states"]

                        if crop_data == True and len(crop_range) == 2:
                            crop_range = [int(crop_range[0]), int(crop_range[1])]
                            crop_range = sorted(crop_range)
                            if crop_range[0] < 0:
                                crop_range[0] = 0
                            if crop_range[0] >= 0 and crop_range[1] <= len(data):
                                data = data[crop_range[0]:crop_range[1]]
                                state_means_y = state_means_y[crop_range[0]:crop_range[1]]
                                states = states[crop_range[0]:crop_range[1]]
                        else:
                            if len(state_means_y) < len(data):
                                state_indeces = state_means_x
                                padded_state_means_y = [pad_value] * len(data)
                                for index, value in zip(state_indeces, state_means_y):
                                    padded_state_means_y[index] = value
                                state_means_y = padded_state_means_y
                            if len(states) < len(data):
                                state_indeces = state_means_x
                                padded_states = [pad_value] * len(data)
                                for index, value in zip(state_indeces, states):
                                    padded_states[index] = value
                                states = padded_states

                        loc_index.append(int(localisation_number))
                        loc_dataset.append(str(dataset_name))
                        loc_user_label.append(str(user_label))
                        loc_data.append(list(data))
                        loc_states.append(list(states))
                        loc_data_name.append(str(data_name))
                        loc_file_name.append(str(file_name))
                        loc_path.append(str(file_path))

                        if export_states:

                            loc_index.append(localisation_number)
                            loc_dataset.append(dataset_name)
                            loc_user_label.append(user_label)
                            loc_data.append(states)
                            loc_data_name.append(data_name+"_states")
                            loc_file_name.append(file_name)
                            loc_path.append(file_path)

                        if export_state_means:

                            loc_index.append(localisation_number)
                            loc_dataset.append(dataset_name)
                            loc_user_label.append(user_label)
                            loc_data.append(state_means_y)
                            loc_data_name.append(data_name+"_state_mean")
                            loc_file_name.append(file_name)
                            loc_path.append(file_path)

                    iter += 1

                    if progress_callback is not None:
                        progress = int(((iter+1) / n_traces) * 100)
                        progress_callback.emit(progress)

        export_data_dict = {"index": loc_index,
                            "dataset": loc_dataset,
                            "user_label": loc_user_label,
                            "data": loc_data,
                            "states": loc_states,
                            "data_name": loc_data_name,
                            "file_name": loc_file_name,
                            "path": loc_path,
                            }

        if pad_data == True:

            data = export_data_dict["data"]

            max_length = max([len(data) for data in data])

            if pad_data == True:
                for dat_index, dat in enumerate(data):

                    dat = np.array(dat)

                    if np.issubdtype(dat.dtype, np.integer) and np.isnan(pad_value):
                        dat = dat.astype(float)

                    dat_pad = np.pad(dat, (0, max_length - len(dat)), mode="constant", constant_values=pad_value)
                    data[dat_index] = list(dat_pad)

            export_data_dict["data"] = data

        return export_data_dict

    def export_gapseq_json(self, export_path, progress_callback = None):

        try:

            # export gapseq data as a json file

            if self.data_dict != {}:

                dataset_names = self.data_dict.keys()

                json_dataset_dict = self.build_json_dict(dataset_names=dataset_names)

                with open(export_path, "w") as f:
                    json.dump(json_dataset_dict, f, cls=npEncoder)

                self.print_notification(f"Exported data to {export_path}")

        except:
            print(traceback.format_exc())

    def get_filter_status(self, export_mode = "data", user_label = ""):

        if export_mode.lower() == "data":
            user_filter = self.export_settings.export_user_group.currentText()
        elif export_mode.lower() == "excel":
            user_filter = self.export_settings.export_user_group.currentText()
        elif export_mode.lower() == "origin":
            user_filter = self.export_settings.export_user_group.currentText()
        elif export_mode.lower() == "ml":
            user_filter = self.export_settings.export_user_group.currentText()
        elif export_mode.lower() == "summary":
            user_filter = self.export_settings.export_user_group.currentText()
        elif export_mode.lower() == "smooth":
            user_filter = self.smoothing_window.smooth_user_group.currentText()
        elif export_mode.lower() == "bleach":
            user_filter = self.bleach_window.bleach_user_group.currentText()
        elif export_mode.lower() == "correction":
            user_filter = self.correction_window.correction_user_group.currentText()
        elif export_mode.lower() == "detect_crop":
            user_filter = self.crop_window.crop_user_group.currentText()
        elif export_mode.lower() == "ebfret":
            user_filter = self.fitting_window.ebfret_user_group.currentText()
        elif export_mode.lower() == "analysis":
            user_filter = self.analysis_user_group.currentText()
        elif export_mode.lower() == "inceptiontime":
            user_filter = self.detect_window.detect_user_group.currentText()
        elif export_mode.lower() == "hmm":
            user_filter = self.fitting_window.hmm_user_group.currentText()
        elif export_mode.lower() == "group":
            user_filter = self.group_window.group_user_group.currentText()
        elif export_mode.lower() == "manage":
            user_filter = self.manage_window.delete_group_label.currentText()

        filter = False

        if user_filter != "None":
            if user_label != user_filter:
                filter = True

        return filter

    def json_dict_report(self, json_dataset):

        try:

            if json_dataset != {}:

                json_dataset = json_dataset.copy()

                json_report = {}
                dataset_traces = {}

                if "data" in json_dataset.keys():
                    data_dict = json_dataset["data"]
                else:
                    data_dict = json_dataset

                for dataset in data_dict.keys():

                    data = data_dict[dataset]

                    if dataset not in json_report.keys():
                        json_report[dataset] = {}

                    dataset_traces[dataset] = len(data)

                    for json_dict in data:

                        json_dict_keys = json_dict.keys()

                        for key in json_dict_keys:

                            if key not in json_report[dataset].keys():
                                json_report[dataset][key] = 0

                            json_report[dataset][key] += 1

                n_datasets = len(json_report.keys())
                unique_channels = list(set([key for dataset in json_report.keys() for key in json_report[dataset].keys()]))
                unique_n_traces = np.unique([value for dataset in json_report.keys() for value in json_report[dataset].values()])
                total_traces = sum([value for dataset in json_report.keys() for value in json_report[dataset].values()])

                try:
                    # size of json_dataset
                    json_dataset_size = len(json.dumps(json_dataset, indent=4, cls=npEncoder))
                    json_dataset_size_mb = json_dataset_size / 1000000
                except:
                    json_dataset_size_mb = 0

                print(f"JSON Dataset report:")
                print(f" N datasets: {n_datasets}")
                print(f" Dataset traces: {list(dataset_traces.values())}")
                print(f" Unique channels: {unique_channels}")
                print(f" N traces: {unique_n_traces}")
                print(f" Total traces: {total_traces}")
                print(f" Size: {json_dataset_size_mb} MB")

        except:
            print(traceback.format_exc())


    def build_json_dict(self, dataset_names = []):

        try:

            json_dataset_dict = {"metadata":{}, "data":{}}

            json_list_keys = ["Data", "Trace", "Donor", "Acceptor",
                              "FRET Efficiency", "ALEX Efficiency",
                              "DD", "AA", "DA", "AD",
                              "states",
                              "break_points", "crop_range", "gamma_ranges",
                              'gap_label', 'sequence_label', 'picasso_loc',]

            json_var_keys = ["user_label", "import_path", "ml_label"]
            json_dict_keys = ["bleach_dict","measure_dict"]

            if len(dataset_names) == 0:
                dataset_names = self.data_dict.keys()

            for dataset_name in dataset_names:

                dataset_data = self.data_dict[dataset_name]

                if dataset_name not in json_dataset_dict.keys():
                    json_dataset_dict["data"][dataset_name] = []

                for localisation_number, localisation_data in enumerate(dataset_data):

                    json_localisation_dict = {}

                    for key, value in localisation_data.items():

                        if key in json_list_keys:
                            if key in ["gap_label", "sequence_label"]:
                                json_localisation_dict[key] = str(value)
                            elif key == "states":
                                json_localisation_dict[key] = np.array(value).astype(int).tolist()
                            else:
                                json_localisation_dict[key] = list(value)

                        if key in json_var_keys:
                            json_localisation_dict[key] = value

                        if key in json_dict_keys:
                            json_localisation_dict[key] = value

                    json_dataset_dict["data"][dataset_name].append(json_localisation_dict)

        except:
            print(traceback.format_exc())

        return json_dataset_dict

    def export_finished(self):

        self.export_settings.export_progressbar.setValue(100)
        time.sleep(1)
        self.export_settings.export_progressbar.setValue(0)



class npEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int32):
            return int(obj)
        return json.JSONEncoder.default(self, obj)