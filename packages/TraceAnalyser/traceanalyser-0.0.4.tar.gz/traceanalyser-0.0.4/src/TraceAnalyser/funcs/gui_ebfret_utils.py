import traceback
from TraceAnalyser.funcs.gui_worker import Worker
import numpy as np
import copy

class _ebFRET_methods:

    def get_combo_box_items(self, combo_box):
        items = []
        for index in range(combo_box.count()):
            items.append(combo_box.itemText(index))
        return items

    def populate_ebFRET_options(self):

        try:
            if self.data_dict != {}:

                dataset_names = list(self.data_dict.keys())

                data_names = np.unique([list(value[0].keys()) for key,value in self.data_dict.items()])

                self.fitting_window.ebfret_fit_data.clear()

                # get plot_mode combo box items
                plot_mode_items = self.get_combo_box_items(self.plot_mode)

                if "Trace" in plot_mode_items:
                    self.fitting_window.ebfret_fit_data.addItem("Trace")
                if "Data" in plot_mode_items:
                    self.fitting_window.ebfret_fit_data.addItem("Data")
                if "Donor" in plot_mode_items:
                    self.fitting_window.ebfret_fit_data.addItem("Donor")
                if "Acceptor" in plot_mode_items:
                    self.fitting_window.ebfret_fit_data.addItem("Acceptor")
                if "FRET Efficiency" in plot_mode_items:
                    self.fitting_window.ebfret_fit_data.addItem("FRET Efficiency")
                if "DA" in plot_mode_items:
                    self.fitting_window.ebfret_fit_data.addItem("DA")
                if "AA" in plot_mode_items:
                    self.fitting_window.ebfret_fit_data.addItem("AA")
                if "DD" in plot_mode_items:
                    self.fitting_window.ebfret_fit_data.addItem("DD")
                if "AD" in plot_mode_items:
                    self.fitting_window.ebfret_fit_data.addItem("AD")
                if "ALEX Efficiency" in plot_mode_items:
                    self.fitting_window.ebfret_fit_data.addItem("ALEX Efficiency")

                self.fitting_window.ebfret_fit_dataset.clear()
                self.fitting_window.ebfret_fit_dataset.addItems(dataset_names)

        except:
            self.print_notification(traceback.format_exc())
            pass

    def gapseq_visualise_ebfret(self):

        try:
            if hasattr(self, "ebfret_states"):

                state = self.fitting_window.ebfret_visualisation_state.currentText()
                dataset_name = self.fitting_window.ebfret_fit_dataset.currentText()

                if state.isdigit():
                    state = int(state)

                    state_data = self.ebfret_states.copy()

                    indices = np.where(state_data[:, 0] == state)
                    state_data = np.take(state_data, indices, axis=0)[0]

                    for localisation_index, localisation_number in enumerate(self.ebfret_datadict.keys()):

                        localisation_data = self.data_dict[dataset_name][localisation_number]

                        loc_indices = np.where(state_data[:, 1] == localisation_index + 1)
                        loc_state_data = np.take(state_data, loc_indices, axis=0)[0]

                        loc_states = loc_state_data[:, 2]

                        loc_states -= 1

                        localisation_data["states"] = loc_states

                        self.data_dict[dataset_name][localisation_number] = copy.deepcopy(localisation_data)

                self.compute_state_means(dataset_name=dataset_name)
                self.plot_traces(update_plot = True)

        except:
            self.print_notification(traceback.format_exc())


    def _run_ebFRET_analysis_cleanup(self):

        try:

            pass

            if hasattr(self, "ebfret_states"):
                self.fitting_window.ebfret_visualisation_state.clear()
                unique_state_list = np.unique(self.ebfret_states[:, 0]).astype(int).tolist()
                unique_state_list = [str(state) for state in unique_state_list]
                self.fitting_window.ebfret_visualisation_state.addItems(unique_state_list)
            else:
                self.fitting_window.ebfret_visualisation_state.clear()

            self.gapseq_visualise_ebfret()

        except:
            pass

    def _run_ebFRET_analysis(self, progress_callback):

        try:

            self.print_notification("Building ebFRET analysis dataset...")
            self.ebfret_datadict = self.build_ebFRET_dataset()

            min_states = int(self.fitting_window.ebfret_min_states.currentText())
            max_states = int(self.fitting_window.ebfret_max_states.currentText())

            if min_states > max_states:
                min_states = max_states

            ebfret_data = list(self.ebfret_datadict.values())

            self.print_notification("Uploading ebFRET analysis dataset to MATLAB...")
            self.ebFRET_controller.python_import_ebfret_data(ebfret_data)

            self.print_notification("Running ebFRET analysis...")
            self.ebfret_states = self.ebFRET_controller.run_ebfret_analysis(min_states=min_states, max_states=max_states)

            self.ebfret_states = np.array(self.ebfret_states)

            if len(self.ebfret_states) > 0:

                self.print_notification("Processing ebFRET analysis results...")

                unique_states = np.unique(self.ebfret_states[:, 0])
                self.fitting_window.ebfret_visualisation_state.clear()
                self.fitting_window.ebfret_visualisation_state.addItems([str(int(x)) for x in unique_states])

        except:
            self.print_notification(traceback.format_exc())
            pass


    def run_ebFRET_analysis(self):

        try:

            if self.data_dict != {}:

                if self.ebFRET_controller.check_ebfret_running():

                    worker = Worker(self._run_ebFRET_analysis)
                    worker.signals.finished.connect(self._run_ebFRET_analysis_cleanup)
                    self.threadpool.start(worker)

        except:
            self.print_notification(traceback.format_exc())
            pass


    def build_ebFRET_dataset(self):

        ebfret_dataset = {}

        try:
            if self.data_dict != {}:

                dataset_name = self.fitting_window.ebfret_fit_dataset.currentText()

                data_name = self.fitting_window.ebfret_fit_data.currentText()
                crop_plots = self.fitting_window.ebfret_crop_plots.isChecked()

                for localisation_index, localisation_data in enumerate(self.data_dict[dataset_name]):

                    user_label = localisation_data["user_label"]
                    crop_range = localisation_data["crop_range"]

                    if self.get_filter_status("ebfret", user_label) == False:

                        data = np.array(localisation_data[data_name]).copy()

                        if crop_plots == True and len(crop_range) == 2:
                            crop_range = sorted(crop_range)
                            if crop_range[0] < 0:
                                crop_range[0] = 0
                            if crop_range[1] > len(data):
                                crop_range[1] = len(data)
                            data = data[int(crop_range[0]):int(crop_range[1])]

                        # set NaNs to 0
                        data = np.nan_to_num(data)

                        # # set 0s to random small value
                        # data[data == 0] = np.random.rand() * 1e-10
                        #
                        # data = [float(x) for x in data]

                        if len(data) > 0:
                            ebfret_dataset[localisation_index] = data

        except:
            self.print_notification(traceback.format_exc())
            pass

        return ebfret_dataset


    def _launch_ebFRET(self, progress_callback=None):

        ebFRET_controller = None

        try:
            from TraceAnalyser.funcs.ebfret_utils import ebFRET_controller

            ebFRET_controller = ebFRET_controller()
            progress_callback.emit(10)

            ebfret_dir_status = ebFRET_controller.check_ebfret_dir()
            progress_callback.emit(15)

            matlab_engine_status = ebFRET_controller.check_matlab_engine_installed()
            progress_callback.emit(20)

            if ebfret_dir_status and matlab_engine_status:
                ebFRET_controller.start_engine()
                progress_callback.emit(40)
                ebFRET_controller.start_ebfret()
                progress_callback.emit(100)
                progress_callback.emit(0)

        except:
            self.print_notification(traceback.format_exc())
            progress_callback.emit(0)

        return ebFRET_controller


    def _close_ebFRET(self, progress_callback=None):
        """Close ebFRET GUI."""

        try:

            if hasattr(self, "ebFRET_controller"):
                if self.ebFRET_controller != None:

                    self.ebFRET_controller.close_ebfret()
                    progress_callback.emit(33)
                    self.ebFRET_controller.stop_parrallel_pool()
                    progress_callback.emit(66)
                    self.ebFRET_controller.close_engine()
                    progress_callback.emit(100)
                    progress_callback.emit(0)
        except:
            pass

    def _launch_ebFRET_cleanup(self, ebFRET_controller=None):

        """Cleanup after launching ebFRET GUI."""
        try:
            if ebFRET_controller != None:
                self.ebFRET_controller = ebFRET_controller
                if ebFRET_controller.check_ebfret_running():
                    self.fitting_window.ebfret_connect_matlab.setText(r"Close MATLAB/ebFRET")
                else:
                    self.fitting_window.ebfret_connect_matlab.setText(r"Open MATLAB/ebFRET")
            else:
                self.ebFRET_controller = None
                self.fitting_window.ebfret_connect_matlab.setText(r"Open MATLAB/ebFRET")
        except:
            self.print_notification(traceback.format_exc())
            pass

    def launch_ebFRET(self):

        launch_ebfret = True
        if hasattr(self, "ebFRET_controller"):

            if hasattr(self.ebFRET_controller, "check_ebfret_running"):
                if self.ebFRET_controller.check_ebfret_running():
                    launch_ebfret = False

        if launch_ebfret:
            self.print_notification("launching MATLAB/ebFRET")
            worker = Worker(self._launch_ebFRET)
            worker.signals.result.connect(self._launch_ebFRET_cleanup)
            self.threadpool.start(worker)
        else:
            self.print_notification("closing MATLAB/ebFRET")
            worker = Worker(self._close_ebFRET)
            worker.signals.result.connect(self._launch_ebFRET_cleanup)
            self.threadpool.start(worker)