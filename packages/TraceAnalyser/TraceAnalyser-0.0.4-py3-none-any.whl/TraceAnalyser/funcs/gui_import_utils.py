import os
import pickle
import numpy as np
from PyQt5.QtWidgets import QFileDialog
import traceback
import pandas as pd
import json
import copy

class _import_methods:


    def import_deepfret_data(self):

        try:

            dataset_name = "DeepFRET Simulated"

            self.data_dict = {}
            n_traces = 0

            desktop = os.path.expanduser("~/Desktop")
            paths, _ = QFileDialog.getOpenFileNames(self, "Open Files", desktop, "DeepGapSeq Simulated Traces (*.txt)")

            deepfret_format_error = False
            expected_deepfret_cols = ['D-Dexc-bg', 'A-Dexc-bg', 'A-Aexc-bg',
                                      'D-Dexc-rw', 'A-Dexc-rw','A-Aexc-rw', 'S', 'E']

            if len(paths) > 0:

                if dataset_name not in self.data_dict.keys():
                    self.data_dict[dataset_name] = []

                self.print_notification(f"Importing {len(paths)} DeepFRET traces")

                for path in paths:

                    data = pd.read_table(path, sep="\t", skiprows=6)

                    if data.columns.tolist() != expected_deepfret_cols:

                        file_name = os.path.basename(path)
                        self.print_notification(f"DeepFRET format error in file: {file_name}")

                    else:

                        DD = data["D-Dexc-rw"].values
                        DA = data["A-Dexc-rw"].values
                        AA = data["A-Aexc-rw"].values
                        AD = np.zeros_like(DD)

                        loc_data = {"FRET Efficiency": [],
                                    "ALEX Efficiency": [],
                                    "states": [],
                                    "state_means": {},
                                    "user_label": 0,
                                    "break_points": [],
                                    "gamma_ranges": [],
                                    "bleach_dict ": {},
                                    "correction_factors": {},
                                    "crop_range": [],
                                    "filter": False,
                                    "import_path": path,
                                    "DD": DD,
                                    "DA": DA,
                                    "AA": AA,
                                    "AD": AD,
                                    }

                        self.data_dict[dataset_name].append(loc_data)
                        n_traces += 1

            if n_traces > 1:

                self.print_notification(f"Imported {int(n_traces)} DeepFRET traces")

                self.populate_bleach_dicts()
                self.populate_correction_factors()

                self.compute_efficiencies()
                self.compute_state_means()

                self.populate_combos()

                self.plot_localisation_number.setValue(0)

                self.initialise_plot()

        except:
            print(traceback.format_exc())
            pass

    def import_simulated_data(self):

        try:

            desktop = os.path.expanduser("~/Desktop")
            path, _ = QFileDialog.getOpenFileName(self, "Open Files", desktop, "DeepGapSeq Simulated Traces (*.pkl)")

            if os.path.isfile(path):

                self.data_dict = {}
                n_traces = 0

                file_name = os.path.basename(path)

                self.print_notification("Loading simulated data from: " + file_name)

                with open(path, 'rb') as handle:
                    trace_dictionary = pickle.load(handle)

                dataset_name = "Data"

                trace_data = trace_dictionary["data"]
                trace_labels = trace_dictionary["labels"]

                self.data_dict[dataset_name] = []

                for i in range(len(trace_data)):

                    try:

                        data = trace_data[i]

                        if len(data.shape) == 1:
                            donor_data = []
                            acceptor_data = []
                            # efficiency_data = data
                        elif data.shape[-1] == 2:
                            donor_data = data[:,0]
                            acceptor_data = data[:,1]
                            # efficiency_data = np.divide(acceptor_data, donor_data)
                        else:
                            donor_data = []
                            acceptor_data = []
                            # efficiency_data = []

                        labels = trace_labels[i]

                        self.data_dict[dataset_name].append({"Donor": donor_data,
                                                             "Acceptor": acceptor_data,
                                                             # "FRET Efficiency": efficiency_data,
                                                             "states": labels,
                                                             "filter": False,
                                                             "state_means": {},
                                                             "user_label" : 0,
                                                             "break_points" : [],
                                                             "crop_range" : [],
                                                             "gamma_ranges" : [],
                                                             "bleach_dict ": {},
                                                             "correction_factors": {},
                                                             "import_path" : path,
                                                             })
                    except:
                        pass

                if n_traces > 1:

                    self.print_notification(f"Imported {int(n_traces)} simulated traces")

                    self.populate_bleach_dicts()
                    self.populate_correction_factors()

                    self.compute_efficiencies()
                    self.compute_state_means()

                    self.populate_combos()

                    self.plot_localisation_number.setValue(0)

                    self.initialise_plot()

        except:
            print(traceback.format_exc())

    def import_data_files(self):

        try:

            self.data_dict = {}
            n_traces = 0

            file_format = self.import_settings.import_data_file_format.currentText()
            traces_per_file = self.import_settings.import_data_traces_per_file.currentText()
            sep = self.import_settings.import_data_separator.currentText()
            column_format = self.import_settings.import_data_column_format.currentText()
            skiprows = int(self.import_settings.import_data_skip_rows.currentText())
            skipcolumns = int(self.import_settings.import_data_skip_columns.currentText())
            dataset_mode = int(self.import_settings.import_data_dataset_mode.currentIndex())

            if sep.lower() == "space":
                sep = " "
            if sep.lower() == "tab":
                sep == "\t"
            if sep.lower() == ",":
                sep == ","

            column_names = column_format.split("-")
            column_names = [col for col in column_names]

            desktop = os.path.expanduser("~/Desktop")

            paths, _ = QFileDialog.getOpenFileNames(self,
                "Open File(s)",
                desktop,
                f"Data Files (*{file_format})")

            if len(paths) > 0:

                self.print_notification(f"Importing {len(paths)} files")

                if dataset_mode == 1:
                    dataset_names = [os.path.basename(path) for path in paths]
                else:
                    dataset_names = [os.path.basename(paths[0])]*len(paths)

                for path_index, path in enumerate(paths):

                    dataset_name = dataset_names[path_index]

                    if dataset_name not in self.data_dict.keys():
                        self.data_dict[dataset_name] = []

                    if file_format in [".dat", ".txt"]:
                        data = pd.read_table(path, sep=sep,skiprows=skiprows)
                    elif file_format == ".csv":
                        data = pd.read_csv(path, skiprows=skiprows)
                    elif file_format == ".xlsx":
                        data = pd.read_excel(path, skiprows=skiprows, index_col=0)

                    if skipcolumns > 0:
                        data = data.iloc[:,skipcolumns:]

                    n_rows, n_columns = data.shape

                    import_error = False
                    if n_columns == 1:
                        self.print_notification(f"Importing {dataset_name} as a single columns, incorrect separator?")
                        import_error = True
                    elif traces_per_file == "Multiple" and n_columns % len(column_names) != 0:
                        n_columns = n_columns - (n_columns % len(column_names))

                    if import_error == False:

                        if traces_per_file == "Multiple":
                            import_range = range(0, n_columns, len(column_names))
                        else:
                            import_range = range(0, len(column_names))

                        for i in import_range:

                            loc_data = {"FRET Efficiency": [], "ALEX Efficiency": [],
                                        "states": [],"state_means": {},
                                        "user_label": 0,
                                        "break_points": [], "gamma_ranges": [],
                                        "bleach_dict ": {}, "correction_factors": {},
                                        "crop_range" : [], "filter": False,
                                        "import_path" : path,
                                        }

                            # Select the current group of four columns
                            group = data.iloc[:, i:i + len(column_names)]

                            group.columns = column_names
                            group_dict = group.to_dict(orient="list")

                            if self.import_settings.import_data_alex.isChecked():
                                alex_dict = self.get_alex_data(group_dict["Donor"], group_dict["Acceptor"])

                                for key, value in alex_dict.items():
                                    loc_data[key] = np.array(value)
                            else:
                                for key, value in group_dict.items():
                                    loc_data[key] = np.array(value)

                            self.data_dict[dataset_name].append(loc_data)
                            n_traces += 1

            if n_traces > 1:

                self.print_notification(f"Imported {int(n_traces)} traces")

                self.populate_bleach_dicts()
                self.populate_correction_factors()

                self.compute_efficiencies()
                self.compute_state_means()

                self.populate_combos()

                self.plot_localisation_number.setValue(0)

                self.initialise_plot()

        except:
            print(traceback.format_exc())
            pass

    def import_gapseq_json(self):

        try:
            expected_data = {"Trace": np.array([]),"Data": np.array([]),
                             "Donor": np.array([]), "Acceptor": np.array([]),
                             "FRET Efficiency": np.array([]), "ALEX Efficiency": np.array([]),
                             "gap_label": np.array([]), "sequence_label": np.array([]),
                             "picasso_loc": np.array([]),
                             "DD": np.array([]), "DA": np.array([]),
                             "AA": np.array([]), "AD": np.array([]),
                             "filter": False, "state_means": {}, "states": np.array([]),
                             "user_label": 0, "ml_label": None,
                             "break_points": [], "crop_range": [],
                             "gamma_ranges": [], "import_path": "",
                             "bleach_dict ": {}, "correction_factors": {},"measure_dict": {},
                             }

            if "bleach_dict" not in expected_data.keys():
                expected_data["bleach_dict"] = {}
            if "correction_factors" not in expected_data.keys():
                expected_data["correction_factors"] = {}

            desktop = os.path.expanduser("~/Desktop")

            paths, _ = QFileDialog.getOpenFileNames(self,"Open File(s)", desktop,f"Data Files (*.json)")

            self.data_dict = {}

            n_traces = 0
            n_datasets = 0

            if len(paths) > 0:

                self.print_notification(f"Importing {len(paths)} JSON files...")

                for path in paths:

                    import_data = json.load(open(path, "r"))

                    for dataset_name, dataset_data in import_data["data"].items():

                        if dataset_name not in self.data_dict.keys():
                            self.data_dict[dataset_name] = []
                            n_datasets += 1

                        for localisation_index, localisation_data in enumerate(dataset_data):

                            localisation_dict = {}

                            if len(localisation_data.keys()) > 0:

                                for key, value in localisation_data.items():

                                    if key in expected_data.keys():
                                        expected_type = type(expected_data[key])

                                        if expected_type == type(np.array([])):
                                            value = np.array(value)

                                        localisation_dict[key] = value

                                for key, value in expected_data.items():
                                    if key not in localisation_dict.keys():
                                        localisation_dict[key] = value

                                localisation_dict["import_path"] = path

                                self.data_dict[dataset_name].append(localisation_dict)
                                n_traces += 1

            if n_traces > 0:

                self.print_notification(f"Imported {n_traces} traces from {n_datasets} datasets.")

                self.populate_bleach_dicts()
                self.populate_correction_factors()

                self.compute_efficiencies()
                self.compute_state_means()

                self.populate_combos()

                self.plot_localisation_number.setValue(0)

                self.initialise_plot()

        except:
            print(traceback.format_exc())
            pass
    def import_ml_data(self):

        try:

            self.data_dict = {}
            n_traces = 0

            desktop = os.path.expanduser("~/Desktop")
            paths, _ = QFileDialog.getOpenFileNames(self, "Open Files", desktop, "ML Data (*.txt)")

            legacy_expected_keys = ["data", "label", "data_class"]
            expected_keys = ["data","states","ml_label","dataset","channels",
                             "user_label","import_path"]

            if len(paths) > 0:

                self.print_notification(f"Importing {len(paths)} files")

                for path in paths:

                    try:

                        with open(path) as f:
                            d = json.load(f)

                        import_mode = None
                        import_error = False
                        if set(legacy_expected_keys).issubset(d.keys()):
                            import_mode = "legacy"
                        elif set(expected_keys).issubset(d.keys()):
                            import_mode = "new"
                        else:
                            import_error = True

                        if import_error == False:

                            if import_mode == "legacy":
                                n_imported_traces = self.import_legacy_ml_data(d, path)
                            if import_mode == "new":
                                n_imported_traces = self.import_new_ml_data(d, path)

                            n_traces += n_imported_traces

                    except:
                        print(traceback.format_exc())
                        pass

            if n_traces > 1:

                self.print_notification(f"Imported {int(n_traces)} ML traces")

                self.populate_bleach_dicts()
                self.populate_correction_factors()

                self.compute_efficiencies()
                self.compute_state_means()

                self.populate_combos()

                self.plot_localisation_number.setValue(0)

                self.initialise_plot()

        except:
            print(traceback.format_exc())
            pass

    def import_new_ml_data(self, imported_data, path):

        n_traces = 0

        for i in range(len(imported_data["data"])):
            try:

                data = imported_data["data"][i]
                dataset = imported_data["dataset"][i]
                channels = imported_data["channels"][i]

                if "bleach_range" in imported_data.keys():
                    bleach_ranges = imported_data["bleach_range"][i]
                else:
                    bleach_ranges = [None]*len(channels)

                if dataset not in self.data_dict.keys():
                    self.data_dict[dataset] = []

                loc_data = {"FRET Efficiency": [], "ALEX Efficiency": [],
                            "states": [], "state_means": {},
                            "user_label": 0,
                            "break_points": [], "gamma_ranges": [],
                            "crop_range": [], "filter": False,
                            "import_path": path,
                            "DD": [], "DA": [], "AA": [], "AD": [],
                            "bleach_dict": {}, "correction_factors": {}}

                for channel_data, channel_name, bleach_range in zip(data, channels, bleach_ranges):

                    loc_data[channel_name] = channel_data

                    if bleach_range is None:
                        bleach_range = [len(channel_data), len(channel_data)]

                    loc_data["bleach_dict"][channel_name] = bleach_range

                loc_data["user_label"] = imported_data["user_label"][i]
                loc_data["states"] = imported_data["states"][i]
                loc_data["import_path"] = imported_data["states"][i]

                self.data_dict[dataset].append(loc_data)
                n_traces += 1

            except:
                print(traceback.format_exc())
                pass

        return n_traces

    def import_legacy_ml_data(self, imported_data, path,
            dataset_name="ML Dataset"):

        try:

            n_traces = 0

            file_name = os.path.basename(path)

            traces = imported_data["data"]
            user_labels = imported_data["data_class"]

            dataset_n_traces = len(traces)

            self.print_notification(f"Importing {file_name} with {dataset_n_traces} traces")

            if dataset_name not in self.data_dict.keys():
                self.data_dict[dataset_name] = []

            for i, (trace, user_label) in enumerate(zip(traces, user_labels)):

                loc_data = {"Trace": trace,
                            "user_label": user_label,
                            "FRET Efficiency": [], "ALEX Efficiency": [],
                            "states": [], "state_means": {},
                            "break_points": [], "gamma_ranges": [],
                            "crop_range": [], "filter": False,
                            "import_path": path, }

                self.data_dict[dataset_name].append(loc_data)
                n_traces += 1

        except:
            print(traceback.format_exc())
            pass

        return n_traces

    def compute_state_means(self, dataset_name=None):

        def _compute_state_means(data, labels, print_data=False):

            unique_labels = np.unique(labels)

            labels = np.array(labels).astype(int).copy()
            data = np.array(data).astype(float).copy()

            if len(unique_labels) == 1:
                state_means = [np.mean(data)]*len(data)
            else:
                state_means = np.zeros(len(data))
                for state in np.unique(labels):
                    state_mean = np.mean(data[labels == state])
                    indices = np.where(labels == state)[0]
                    state_means[indices] = state_mean

            return state_means

        if dataset_name is None:
            dataset_names = self.data_dict.keys()
        else:
            dataset_names = [dataset_name]

        for dataset_name in dataset_names:
            for i in range(len(self.data_dict[dataset_name])):
                trace_data = self.data_dict[dataset_name][i]
                crop_range = copy.deepcopy(trace_data["crop_range"])

                labels = np.array(trace_data["states"])

                if "state_means" not in trace_data:
                    trace_data["state_means"] = {}

                for plot in ["Data","Trace","Donor", "Acceptor",
                             "FRET Efficiency", "ALEX Efficiency",
                             "DD", "AA", "DA", "AD"]:

                    if plot in trace_data.keys():
                        plot_data = np.array(trace_data[plot]).copy()

                        try:

                            if len(plot_data) > 0 and len(labels) > 0:

                                if len(plot_data) == len(labels):

                                    if plot == "Donor" and i == 17:
                                        print_data = True
                                    else:
                                        print_data = False

                                    state_means_y = _compute_state_means(plot_data, labels, print_data=print_data)
                                    state_means_x = np.arange(len(state_means_y))

                                    state_means_x = list(state_means_x)
                                    state_means_y = list(state_means_y)

                                    trace_data["state_means"][plot] = [state_means_x, state_means_y]

                                else:

                                    plot_data = plot_data[int(crop_range[0]):int(crop_range[1])]
                                    state_means_y = _compute_state_means(plot_data, labels)
                                    state_means_x = np.arange(int(crop_range[0]),int(crop_range[1]))

                                    state_means_x = list(state_means_x)
                                    state_means_y = list(state_means_y)

                                    trace_data["state_means"][plot] = [state_means_x, state_means_y]

                            else:
                                trace_data["state_means"][plot] = [[], []]

                        except:
                            trace_data["state_means"][plot] = [[], []]

                self.data_dict[dataset_name][i] = copy.deepcopy(trace_data)

    def get_alex_data(self, donor, acceptor):

        alex_first_frame = self.import_settings.alex_firstframe_excitation.currentIndex()

        donor = np.array(donor)
        acceptor = np.array(acceptor)

        if alex_first_frame == 0:
            "donor excitaton first"

            DD = donor[::2] #every second element, starting from 0
            AD = donor[1::2]  # every second element, starting from 1

            DA = acceptor[::2] #every second element, starting from 0
            AA = acceptor[1::2] #every second element, starting from 1

        else:
            "acceptor excitation first"

            AA = acceptor[::2] #every second element, starting from 0
            DA = acceptor[1::2]  # every second element, starting from 1

            AD = donor[::2] #every second element, starting from 0
            DD = donor[1::2] #every second element, starting from 1

        alex_dict = {"DD": DD, "DA": DA,
                     "AA": AA, "AD": AD}

        return alex_dict

    def populate_trace_graph_combos(self):

        self.plot_mode.clear()

        plot_names = []
        plot_channels = []

        for dataset_name in self.data_dict.keys():
            for plot_name, plot_value in self.data_dict[dataset_name][0].items():
                if plot_name in ["Data","Trace","Donor", "Acceptor", "FRET Efficiency", "ALEX Efficiency", "DD", "AA", "DA", "AD"]:
                    if len(plot_value) > 0:
                        plot_names.append(plot_name)

        if "Trace" in plot_names:
            plot_channels.append("Trace")
        if "Data" in plot_names:
            plot_channels.append("Data")
        if "Donor" in plot_names:
            plot_channels.append("Donor")
        if "Acceptor" in plot_names:
            plot_channels.append("Acceptor")
        if set(["Donor", "Acceptor"]).issubset(plot_names):
            plot_channels.append("FRET Data")
        if set(["Donor", "Acceptor", "FRET Efficiency"]).issubset(plot_names):
            plot_channels.append("FRET Efficiency")
            plot_channels.append("FRET Data + FRET Efficiency")
        if set(["DD", "AA", "DA", "AD"]).issubset(plot_names):
            plot_channels.append("DD")
            plot_channels.append("AA")
            plot_channels.append("DA")
            plot_channels.append("AD")
            plot_channels.append("ALEX Data")
        if set(["DD", "AA", "DA", "AD", "ALEX Efficiency"]).issubset(plot_names):
            plot_channels.append("ALEX Efficiency")
            plot_channels.append("ALEX Data + ALEX Efficiency")
        if set(["Donor", "Acceptor"]).issubset(plot_names):
            plot_channels.append("Correction Data")
        if set(["DD","DA"]).issubset(plot_names):
            plot_channels.append("Correction Data")

        plot_channels = list(set(plot_channels))
        plot_channels = self.sort_channel_list(plot_channels)

        self.plot_mode.addItems(plot_channels)

        self.plot_data.clear()
        if len(self.data_dict.keys()) == 1:
            self.plot_data.addItems(list(self.data_dict.keys()))
        else:
            self.plot_data.addItem("All Datasets")
            self.plot_data.addItems(list(self.data_dict.keys()))

    def update_plot_data_combo(self):

        try:

            plot_datasets = list(self.data_dict.keys())
            plot_datasets = list(set(plot_datasets))

            if len(plot_datasets) > 1:
                plot_datasets.insert(0, "All Datasets")

            self.plot_data.clear()
            self.plot_data.addItems(plot_datasets)

        except:
            print(traceback.format_exc())
            pass

    def update_plot_mode_combo(self):

        try:

            current_plot_mode = self.plot_mode.currentText()

            self.plot_mode.clear()

            plot_channels = []

            if self.plot_data.currentText() == "All Datasets":
                plot_datasets = list(self.data_dict.keys())
            else:
                plot_datasets = [self.plot_data.currentText()]

            for dataset_name in plot_datasets:
                if dataset_name in self.data_dict.keys():
                    for plot_name, plot_value in self.data_dict[dataset_name][0].items():
                        if plot_name in ["Data","Trace","Donor", "Acceptor", "FRET Efficiency","ALEX Efficiency", "DD", "AA", "DA", "AD"]:
                            if len(plot_value) > 0:
                                plot_channels.append(plot_name)

            if set(["Donor", "Acceptor"]).issubset(plot_channels):
                plot_channels.insert(0, "FRET Data")
            if set(["Donor", "Acceptor", "FRET Efficiency"]).issubset(plot_channels):
                plot_channels.insert(0, "FRET Efficiency")
                plot_channels.insert(0, "FRET Data + FRET Efficiency")
            if set(["DD", "AA", "DA", "AD"]).issubset(plot_channels):
                plot_channels.insert(0, "ALEX Data")
            if set(["DD", "AA", "DA", "AD", "ALEX Efficiency"]).issubset(plot_channels):
                plot_channels.insert(0, "ALEX Efficiency")
                plot_channels.insert(0, "ALEX Data + ALEX Efficiency")
            if set(["Donor", "Acceptor"]).issubset(plot_channels):
                plot_channels.insert(0, "FRET Correction Data")
            if set(["DD","DA","AA"]).issubset(plot_channels):
                plot_channels.insert(0, "ALEX Correction Data")

            plot_channels = list(set(plot_channels))
            plot_channels = self.sort_channel_list(plot_channels)

            if len(plot_channels) > 1:
                plot_channels.insert(0, "All Channels")

            self.plot_mode.blockSignals(True)

            self.plot_mode.addItems(plot_channels)

            if current_plot_mode in plot_channels:
                self.plot_mode.setCurrentIndex(self.plot_mode.findText(current_plot_mode))

            self.plot_mode.blockSignals(False)

        except:
            print(traceback.format_exc())
            pass

    def populate_analysis_graph_combos(self):

        self.analysis_graph_channel.clear()

        plot_names = []

        for dataset_name in self.data_dict.keys():
            for plot_name, plot_value in self.data_dict[dataset_name][0].items():
                if plot_name in ["Data","Trace","Donor", "Acceptor", "FRET Efficiency","ALEX Efficiency", "DD", "AA", "DA", "AD"]:
                    if len(plot_value) > 0:
                        plot_names.append(plot_name)
        if "Trace" in plot_names:
            self.analysis_graph_channel.addItem("Trace")
        if "Data" in plot_names:
            self.analysis_graph_channel.addItem("Data")
        if "Donor" in plot_names:
            self.analysis_graph_channel.addItem("Donor")
        if "Acceptor" in plot_names:
            self.analysis_graph_channel.addItem("Acceptor")
        if set(["Donor", "Acceptor", "FRET Efficiency"]).issubset(plot_names):
            self.analysis_graph_channel.addItem("FRET Efficiency")
        if set(["DD", "AA", "DA", "AD"]).issubset(plot_names):
            self.analysis_graph_channel.addItem("DD")
            self.analysis_graph_channel.addItem("AA")
            self.analysis_graph_channel.addItem("DA")
            self.analysis_graph_channel.addItem("AD")
        if set(["DD", "AA", "DA", "AD", "ALEX Efficiency"]).issubset(plot_names):
            self.analysis_graph_channel.addItem("ALEX Efficiency")

        self.analysis_graph_dataset.clear()
        self.analysis_graph_dataset.addItems(list(self.data_dict.keys()))

    def populate_measure_graph_combos(self):

        self.measure_graph_channel.clear()

        plot_names = []

        for dataset_name in self.data_dict.keys():
            for plot_name, plot_value in self.data_dict[dataset_name][0].items():
                if plot_name in ["Data", "Trace","Donor", "Acceptor", "FRET Efficiency","ALEX Efficiency", "DD", "AA", "DA", "AD"]:
                    if len(plot_value) > 0:
                        plot_names.append(plot_name)
        if "Trace" in plot_names:
            self.measure_graph_channel.addItem("Trace")
        if "Data" in plot_names:
            self.measure_graph_channel.addItem("Data")
        if "Donor" in plot_names:
            self.measure_graph_channel.addItem("Donor")
        if "Acceptor" in plot_names:
            self.measure_graph_channel.addItem("Acceptor")
        if set(["Donor", "Acceptor", "FRET Efficiency"]).issubset(plot_names):
            self.measure_graph_channel.addItem("FRET Efficiency")
        if set(["DD", "AA", "DA", "AD"]).issubset(plot_names):
            self.measure_graph_channel.addItem("DD")
            self.measure_graph_channel.addItem("AA")
            self.measure_graph_channel.addItem("DA")
            self.measure_graph_channel.addItem("AD")
        if set(["DD", "AA", "DA", "AD", "ALEX Efficiency"]).issubset(plot_names):
            self.measure_graph_channel.addItem("ALEX Efficiency")

        self.measure_graph_data.clear()
        self.measure_graph_data.addItems(list(self.data_dict.keys()))



    def populate_combos(self):

        self.updating_combos = True

        self.update_plot_data_combo()
        self.update_plot_mode_combo()

        self.populate_export_combos()
        self.populate_detect_combos()
        self.populate_measurement_combos()

        self.populate_analysis_graph_combos()
        self.populate_measure_graph_combos()

        self.populate_smooth_combos()
        self.populate_bleach_combos()
        self.populate_correction_combos()
        self.populate_group_combos()
        self.populate_management_combos()
        self.populate_detectcrop_combos()

        self.updating_combos = False

    def populate_bleach_dicts(self):

        try:

            if self.data_dict != {}:

                for dataset_name, dataset_data in self.data_dict.items():

                    dataset_dict = self.data_dict[dataset_name]

                    for localisation_index, localisation_dict in enumerate(dataset_dict):

                        if "bleach_dict" not in localisation_dict.keys():
                            localisation_dict["bleach_dict"] = {}

                        for channel in localisation_dict.keys():

                            if channel in ["Donor","Acceptor", "DD","DA","AA","AD"]:

                                if channel not in localisation_dict["bleach_dict"].keys():

                                    data = localisation_dict[channel]
                                    localisation_dict["bleach_dict"][channel] = [len(data), len(data)]

        except:
            print(traceback.format_exc())
            pass

    def populate_correction_factors(self):

            try:

                if self.data_dict != {}:

                    for dataset_name, dataset_data in self.data_dict.items():

                        dataset_dict = self.data_dict[dataset_name]

                        for localisation_index, localisation_dict in enumerate(dataset_dict):

                            if "correction_factors" not in localisation_dict.keys():
                                localisation_dict["correction_factors"] = {}

                            correction_factors = localisation_dict["correction_factors"]

                            if "donor_bleach_index" not in correction_factors.keys():
                                correction_factors["donor_bleach_index"] = None
                            if "acceptor_bleach_index" not in correction_factors.keys():
                                correction_factors["acceptor_bleach_index"] = None
                            if "gamma" not in correction_factors.keys():
                                correction_factors["gamma"] = None
                            if "a_direct" not in correction_factors.keys():
                                correction_factors["a_direct"] = None
                            if "d_leakage" not in correction_factors.keys():
                                correction_factors["d_leakage"] = None
            except:
                print(traceback.format_exc())
                pass


    def compute_efficiencies(self):

        try:

            if self.data_dict != {}:

                for dataset_name, dataset_data in self.data_dict.items():

                    dataset_dict = self.data_dict[dataset_name]

                    for localisation_index, localisation_dict in enumerate(dataset_dict):
                        localisation_dict_keys = list(localisation_dict.keys())

                        if set(["Donor", "Acceptor"]).issubset(localisation_dict_keys):

                            donor = np.array(localisation_dict["Donor"])
                            acceptor = np.array(localisation_dict["Acceptor"])

                            if len(donor) == len(acceptor):

                                correction_factors = localisation_dict["correction_factors"]

                                fret_efficiency, corrected = self.compute_fret_efficiency(donor, acceptor, correction_factors)

                                localisation_dict["FRET Efficiency"] = fret_efficiency
                                localisation_dict["FRET Efficiency Corrected"] = corrected

                        if set(["DD", "DA","AA"]).issubset(localisation_dict_keys):

                            DD = np.array(localisation_dict["DD"])
                            DA = np.array(localisation_dict["DA"])
                            AA = np.array(localisation_dict["AA"])

                            if len(DD) == len(DA) == len(AA):

                                correction_factors = localisation_dict["correction_factors"]

                                alex_efficiency, stoichiometry, corrected = self.compute_alex_efficiency(DD, DA, AA, correction_factors)

                                localisation_dict["ALEX Efficiency"] = alex_efficiency
                                localisation_dict["ALEX Efficiency Corrected"] = corrected
                                localisation_dict["ALEX Stoichiometry"] = stoichiometry

        except:
            print(traceback.format_exc())
            pass


    def compute_fret_efficiency(self, donor, acceptor, correction_factors=None, clip=True):

        corrected = False
        gamma = None

        try:

            if "gamma" in correction_factors.keys():
                gamma = correction_factors["gamma"]

                if type(gamma) in [int, float]:
                    corrected = True
                else:
                    gamma = 1

            donor = np.array(donor).copy()
            acceptor = np.array(acceptor).copy()

            donor = self.preprocess_efficiecy_data(donor)
            acceptor = self.preprocess_efficiecy_data(acceptor)

            fret_efficiency = acceptor / ((donor*gamma)+acceptor)

        except:
            print(traceback.format_exc())
            fret_efficiency = np.array([])
            pass

        return fret_efficiency, corrected

    def compute_alex_efficiency(self, DD, DA, AA, correction_factors=None, clip=True):

        corrected = False
        corrected_DA = False

        try:

            if "gamma" in correction_factors.keys():
                gamma = correction_factors["gamma"]

                if type(gamma) in [int, float] and gamma != None:
                    corrected = True
                else:
                    gamma = 1

            if "a_direct" in correction_factors.keys():
                a_direct = correction_factors["a_direct"]

            if "d_leakage" in correction_factors.keys():
                d_leakage = correction_factors["d_leakage"]

            if type(d_leakage) in [int, float] and d_leakage != None:
                if type(a_direct) in [int, float] and a_direct != None:
                    corrected_DA = True

            DD = np.array(DD).copy()
            DA = np.array(DA).copy()
            AA = np.array(AA).copy()

            DA = self.preprocess_efficiecy_data(DA)
            DD = self.preprocess_efficiecy_data(DD)
            AA = self.preprocess_efficiecy_data(AA)

            if corrected_DA:
                DA = DA - (d_leakage * DD) - (a_direct * AA)

            efficiency = DA/((DD*gamma)+DA)
            stoichiometry = ((gamma*DD) + DA) / ((gamma*DD) + DA + AA)

        except:
            print(traceback.format_exc())
            efficiency = np.array([])
            stoichiometry = np.array([])
            pass

        return efficiency, stoichiometry, corrected

    def preprocess_efficiecy_data(self, data, lower_limit=0):

        try:

            closest_values = [v for v in data if v > lower_limit]

            if len(closest_values) > 0:

                closest_greater_value = min(closest_values, key=lambda x: x - lower_limit)

                # Replace values below the limit with the closest greater value
                processed_data = [v if v > lower_limit else closest_greater_value for v in data]

            else:
                processed_data = data

        except:
            processed_data = data

        return np.array(processed_data)
