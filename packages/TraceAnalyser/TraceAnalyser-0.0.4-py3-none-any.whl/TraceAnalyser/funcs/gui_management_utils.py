import traceback

class _management_utils:

    def populate_management_combos(self):

        try:

            dataset_names = list(self.data_dict.keys())

            delete_combo = self.manage_window.delete_dataset_combo
            rename_combo = self.manage_window.rename_dataset_combo
            ml_dataset_combo = self.manage_window.ml_dataset

            delete_combo.clear()
            delete_combo.addItems(dataset_names)

            rename_combo.clear()
            rename_combo.addItems(dataset_names)

            ml_dataset_combo.clear()
            ml_dataset_combo.addItems(dataset_names)

        except:
            print(traceback.format_exc())
            pass


    def get_current_measurement_labels(self, default_n_labels=5):

        try:

            measure_labels = []

            for dataset in self.data_dict.keys():
                for localisation_dict in self.data_dict[dataset]:
                    if "measure_dict" in localisation_dict.keys():
                        labels = list(localisation_dict["measure_dict"].keys())
                        measure_labels.extend(labels)

            measure_labels = list(set(measure_labels))

            if len(measure_labels) < default_n_labels:
                while len(measure_labels) < default_n_labels:
                    measure_labels.append(f"Label{len(measure_labels) + 1}")

        except:
            print(traceback.format_exc())
            pass

        return measure_labels


    def populate_measurement_combos(self, measure_labels = [], default_n_labels=5):

        try:

            if len(measure_labels) == 0:
                measure_labels = self.get_current_measurement_labels()

            combo_list = [self.manage_window.manage_measurement_label,
                          self.plot_settings.plot_measurement_label,
                          self.measure_label,
                          ]

            if len(measure_labels) < default_n_labels:
                while len(measure_labels) < default_n_labels:
                    measure_labels.append(f"Label{len(measure_labels) + 1}")

            for combo in combo_list:
                combo.blockSignals(True)
                combo.clear()
                combo.addItems(measure_labels)
                combo.blockSignals(False)

        except:
            print(traceback.format_exc())
            pass



    def rename_measurement_label(self):

        try:

            old_name = self.manage_window.manage_measurement_label.currentText()
            new_name = self.manage_window.manage_new_measurement_label.text()

            if new_name == "":
                self.print_notification("Please enter a new label name")
            else:
                measure_labels = self.get_current_measurement_labels()

                if new_name in measure_labels:

                    self.print_notification(f"Measurement label already exists: {new_name}")

                else:

                    index = measure_labels.index(old_name)
                    measure_labels[index] = new_name

                    for dataset in self.data_dict.keys():
                        for localisation_dict in self.data_dict[dataset]:
                            if "measure_dict" not in localisation_dict.keys():
                                localisation_dict["measure_dict"] = {}

                            measure_dict = localisation_dict["measure_dict"]

                            if old_name in measure_dict.keys():
                                measure_dict[new_name] = measure_dict.pop(old_name)

                            for label in measure_labels:
                                if label not in measure_dict.keys():
                                    measure_dict[label] = []

                    self.populate_measurement_combos(measure_labels)

                    self.print_notification(f"Renamed measurement label: {old_name} -> {new_name}")
                    self.plot_traces(update_plot=False)

        except:
            print(traceback.format_exc())
            pass


    def assign_ml_labels(self):

        try:

            dataset = self.manage_window.ml_dataset.currentText()
            ml_label = self.manage_window.ml_label.currentText()

            ml_label = int(ml_label.split(" ")[0])

            if dataset in self.data_dict.keys():
                for localisation_dict in self.data_dict[dataset]:
                    localisation_dict["ml_label"] = int(ml_label)

            self.print_notification(f"Assigned ML label {ml_label} to {dataset}")
            self.plot_traces(update_plot=False)

        except:
            print(traceback.format_exc())


    def delete_active_trace(self):

        try:

            slider_value = self.plot_localisation_number.value()
            localisation_number = self.localisation_numbers[slider_value]

            for dataset in self.data_dict.keys():
                for index, localisation_data in enumerate(self.data_dict[dataset]):
                    if index == localisation_number:
                        del self.data_dict[dataset][index]

            self.initialise_plot()
            self.print_notification(f"Deleted trace: {localisation_number}")

        except:
            print(traceback.format_exc())
            pass




    def delete_traces(self):

        try:

            if self.data_dict != {}:

                dataset_name = list(self.data_dict.keys())[0]

                delete_list = []

                for localisation_index, localisation_data in enumerate(self.data_dict[dataset_name]):

                    user_label = localisation_data["user_label"]

                    if self.get_filter_status("manage", user_label) == False:

                        delete_list.append(localisation_index)

                for dataset_name in self.data_dict.keys():
                    for index in delete_list:
                            del self.data_dict[dataset_name][index]

                self.initialise_plot()

                self.print_notification(f"Deleting {len(delete_list)} traces from {dataset_name}...")
        except:
            print(traceback.format_exc())
            pass

    def delete_dataset(self):

        try:

            dataset = self.manage_window.delete_dataset_combo.currentText()

            del self.data_dict[dataset]

            self.populate_management_combos()
            self.populate_combos()
            self.initialise_plot()

            self.print_notification(f"Deleted dataset: {dataset}")

            if self.data_dict == {}:
                self.graph_canvas.clear()


        except:
            print(traceback.format_exc())
            pass

    def rename_dataset(self):

        try:

            old_dataset_name = self.manage_window.rename_dataset_combo.currentText()
            new_dataset_name = self.manage_window.manage_new_dataset_name.text()

            current_names = list(self.data_dict.keys())

            if new_dataset_name in current_names:
                self.print_notification(f"Dataset name already exists: {new_dataset_name}")
            else:
                if new_dataset_name != "":

                    self.data_dict[new_dataset_name] = self.data_dict.pop(old_dataset_name)

                    self.populate_management_combos()
                    self.populate_combos()
                    self.initialise_plot()

                    self.print_notification(f"Renamed dataset: {old_dataset_name} -> {new_dataset_name}")

                    combo = self.manage_window.rename_dataset_combo
                    combo.setCurrentIndex(combo.findText(new_dataset_name))

                else:
                    self.print_notification("Dataset name cannot be empty.")

        except:
            print(traceback.format_exc())
            pass