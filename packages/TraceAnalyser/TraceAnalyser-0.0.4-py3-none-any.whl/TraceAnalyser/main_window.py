import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from qtpy.QtCore import QThreadPool
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QSizePolicy,QSlider, QLabel)
from functools import partial
import queue
import traceback

from TraceAnalyser.GUI.mainwindow_gui import Ui_MainWindow

from TraceAnalyser.funcs.gui_windows import (_window_utils,
    PlotSettingsWindow, ImportSettingsWindow,
    ExportSettingsWindow, FittingWindow,
    DetectWindow, SmoothingWindow, BleachWindow, CorrectionWindow,
    GroupWindow, SimulatorWindow, ManageWindow, CropWindow)

from TraceAnalyser.funcs.gui_trace_plot_utils import CustomPyQTGraphWidget, _trace_plotting_methods
from TraceAnalyser.funcs.gui_analysis_plot_utils import  CustomMatplotlibWidget, _analysis_plotting_methods
from TraceAnalyser.funcs.gui_import_utils import _import_methods
from TraceAnalyser.funcs.gui_export_utils import _export_methods
from TraceAnalyser.funcs.gui_ebfret_utils import _ebFRET_methods
from TraceAnalyser.funcs.gui_inceptiontime_utils import _inceptiontime_methods
from TraceAnalyser.funcs.gui_HMM_utils import _HMM_methods
from TraceAnalyser.funcs.gui_smoothing_utils import _smoothing_utils
from TraceAnalyser.funcs.gui_bleach_utils import _bleach_utils
from TraceAnalyser.funcs.gui_correction_utils import _correction_utils
from TraceAnalyser.funcs.gui_group_utils import _group_utils
from TraceAnalyser.funcs.gui_simulation_utils import _simulation_utils
from TraceAnalyser.funcs.gui_measure_plot_utils import _measure_plotting_methods
from TraceAnalyser.funcs.gui_trace_plot_overlays import _trace_plot_overlays
from TraceAnalyser.funcs.gui_management_utils import _management_utils
from TraceAnalyser.funcs.gui_detectcrop_utils import _detectcrop_utils

class AnalysisGUI(QtWidgets.QMainWindow,
    Ui_MainWindow, _trace_plotting_methods,
    _import_methods, _export_methods,
    _ebFRET_methods,
    _analysis_plotting_methods, _inceptiontime_methods,
    _HMM_methods, _window_utils, _smoothing_utils,
    _bleach_utils, _correction_utils, _group_utils,
    _simulation_utils, _measure_plotting_methods,
    _trace_plot_overlays, _management_utils,
    _detectcrop_utils):

    def __init__(self):
        super(AnalysisGUI, self).__init__()

        self.setupUi(self)  # Set up the user interface from Designer.
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        self.plot_settings = PlotSettingsWindow(self)
        self.import_settings = ImportSettingsWindow(self)
        self.export_settings = ExportSettingsWindow(self)
        self.fitting_window = FittingWindow(self)
        self.detect_window = DetectWindow(self)
        self.smoothing_window = SmoothingWindow(self)
        self.bleach_window = BleachWindow(self)
        self.correction_window = CorrectionWindow(self)
        self.group_window = GroupWindow(self)
        self.simulator_window = SimulatorWindow(self)
        self.manage_window = ManageWindow(self)
        self.crop_window = CropWindow(self)

        self.setWindowTitle("TraceAnalyser")  # Set the window title

        #create pyqt graph container
        self.graph_container = self.findChild(QWidget, "graph_container")
        self.graph_container.setLayout(QVBoxLayout())
        self.graph_container.setMinimumWidth(100)

        self.graph_canvas = CustomPyQTGraphWidget(self)
        self.graph_container.layout().addWidget(self.graph_canvas)
        self.graph_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # create analysis matplotlib graph container
        self.analysis_graph_container = self.findChild(QWidget, "analysis_graph_container")
        self.analysis_graph_container.setLayout(QVBoxLayout())
        self.analysis_graph_container.setMinimumWidth(100)

        self.analysis_graph_canvas = CustomMatplotlibWidget(self)
        self.analysis_graph_container.layout().addWidget(self.analysis_graph_canvas)
        self.analysis_graph_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # create measure matplotlib graph container
        self.measure_graph_container = self.findChild(QWidget, "measure_graph_container")
        self.measure_graph_container.setLayout(QVBoxLayout())
        self.measure_graph_container.setMinimumWidth(100)

        self.measure_graph_canvas = CustomMatplotlibWidget(self)
        self.measure_graph_container.layout().addWidget(self.measure_graph_canvas)
        self.measure_graph_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.plotsettings_button = self.findChild(QtWidgets.QPushButton, "plotsettings_button")
        self.plotsettings_button.clicked.connect(self.toggle_plot_settings)

        self.import_settings.import_simulated.clicked.connect(self.import_simulated_data)
        self.actionImport_I.triggered.connect(self.toggle_import_settings)
        self.actionExport_E.triggered.connect(self.toggle_export_settings)
        self.actionFit_Hidden_States_F.triggered.connect(self.toggle_fitting_window)
        self.actionDetect_Binding_Events_D.triggered.connect(self.toggle_detect_window)
        self.actionSmooth_Traces.triggered.connect(self.toggle_smoothing_window)
        self.actionDetect_Bleaching.triggered.connect(self.toggle_bleach_window)
        self.actionCorrection_Factors.triggered.connect(self.toggle_correction_window)
        self.actionGroup_Traces.triggered.connect(self.toggle_group_window)
        self.actionSimulate_Traces.triggered.connect(self.toggle_simulator_window)
        self.actionTrace_Management.triggered.connect(self.toggle_manage_window)
        self.actionDetect_Crop_Range.triggered.connect(self.toggle_crop_window)

        self.export_settings.export_mode.currentIndexChanged.connect(self.update_export_options)
        self.export_settings.export_data.clicked.connect(self.initialise_export)

        self.fitting_window.ebfret_connect_matlab.clicked.connect(self.launch_ebFRET)
        self.fitting_window.ebfret_run_analysis.clicked.connect(self.run_ebFRET_analysis)
        self.fitting_window.ebfret_visualisation_state.currentIndexChanged.connect(self.gapseq_visualise_ebfret)

        self.fitting_window.hmm_detect_states.clicked.connect(self.detect_hmm_states)

        self.plot_settings.crop_reset_active.clicked.connect(partial(self.reset_graphics_overlays,
            mode = "crop", loc_mode ="active"))
        self.plot_settings.crop_reset_all.clicked.connect(partial(self.reset_graphics_overlays,
            mode = "crop", loc_mode ="all"))

        self.plot_settings.measurment_reset_active.clicked.connect(partial(self.reset_graphics_overlays,
            mode = "measurement", loc_mode ="active"))
        self.plot_settings.measurment_reset_all.clicked.connect(partial(self.reset_graphics_overlays,
            mode = "measurement", loc_mode ="all"))

        self.plot_settings.bleach_reset_active.clicked.connect(partial(self.reset_graphics_overlays,
            mode = "bleach", loc_mode ="active"))
        self.plot_settings.bleach_reset_all.clicked.connect(partial(self.reset_graphics_overlays,
            mode = "bleach", loc_mode ="all"))

        self.plot_settings.gamma_reset_active.clicked.connect(partial(self.reset_graphics_overlays,
            mode = "gamma", loc_mode ="active"))
        self.plot_settings.gamma_reset_all.clicked.connect(partial(self.reset_graphics_overlays,
            mode = "gamma", loc_mode ="all"))


        self.data_dict = {}

        self.plot_localisation_number.valueChanged.connect(lambda: self.update_slider_label("plot_localisation_number"))
        self.plot_localisation_number.valueChanged.connect(partial(self.plot_traces, update_plot=False))

        self.plot_mode.currentIndexChanged.connect(self.initialise_plot)
        self.plot_data.currentIndexChanged.connect(self.initialise_plot)

        self.plot_settings.plot_split_lines.stateChanged.connect(partial(self.plot_traces, update_plot=True))
        self.plot_settings.plot_showx.stateChanged.connect(partial(self.plot_traces, update_plot=True))
        self.plot_settings.plot_showy.stateChanged.connect(partial(self.plot_traces, update_plot=True))

        self.plot_settings.plot_user_group.currentIndexChanged.connect(self.initialise_plot)
        self.plot_settings.plot_measurement_label.currentIndexChanged.connect(self.initialise_plot)

        self.plot_settings.plot_measurement_label.editTextChanged.connect(self.update_measurement_labels)

        self.plot_settings.show_crop_range.stateChanged.connect(partial(self.plot_traces, update_plot=False))
        self.plot_settings.show_gamma_range.stateChanged.connect(partial(self.plot_traces, update_plot=False))
        self.plot_settings.show_bleach_range.stateChanged.connect(partial(self.plot_traces, update_plot=False))
        self.plot_settings.show_measurement_range.stateChanged.connect(partial(self.plot_traces, update_plot=False))
        self.plot_settings.crop_plots.stateChanged.connect(partial(self.plot_traces, update_plot=False))

        self.plot_settings.plot_show_correction_factors.stateChanged.connect(partial(self.plot_traces, update_plot=False))
        self.plot_settings.plot_show_ml_predictions.stateChanged.connect(partial(self.plot_traces, update_plot=False))

        self.plot_settings.plot_normalise.stateChanged.connect(partial(self.plot_traces, update_plot=False))
        self.plot_settings.show_detected_states.stateChanged.connect(partial(self.plot_traces, update_plot=False))
        self.plot_settings.plot_downsample.currentIndexChanged.connect(partial(self.plot_traces, update_plot=False))

        self.smoothing_window.live_smooth.stateChanged.connect(partial(self.plot_traces, update_plot=False))
        self.smoothing_window.smooth_type.currentIndexChanged.connect(partial(self.plot_traces, update_plot=False))
        self.smoothing_window.smooth_option1.currentIndexChanged.connect(partial(self.plot_traces, update_plot=False))
        self.smoothing_window.smooth_option2.currentIndexChanged.connect(partial(self.plot_traces, update_plot=False))

        self.group_window.group_intensity.stateChanged.connect(self.update_group_options)
        self.group_window.group_traces.clicked.connect(self.init_trace_grouping)

        self.bleach_window.detect_bleach.clicked.connect(self.initialise_bleach_detection)

        self.plot_data.currentIndexChanged.connect(self.update_plot_mode_combo)

        self.import_settings.import_data.clicked.connect(self.import_data_files)
        self.import_settings.import_json.clicked.connect(self.import_gapseq_json)
        self.import_settings.import_legacy_ml.clicked.connect(self.import_ml_data)
        self.import_settings.import_deepFRET.clicked.connect(self.import_deepfret_data)

        self.detect_window.detect_inceptiontime.clicked.connect(self.detect_inceptiontime_states)
        self.detect_window.label_singletrace.clicked.connect(self.update_singletrace_labels)
        self.detect_window.label_multitrace.clicked.connect(self.update_multitrace_labels)

        self.smoothing_window.apply_smooth.clicked.connect(self.initialise_trace_smoothing)
        self.smoothing_window.smooth_type.currentIndexChanged.connect(self.update_smooth_options)

        self.correction_window.detect_correction_factors.clicked.connect(self.initialise_correction_factor_detection)
        self.correction_window.global_correction_active.clicked.connect(partial(self.apply_global_correction_factors, mode = "active"))
        self.correction_window.global_correction_all.clicked.connect(partial(self.apply_global_correction_factors, mode = "all"))

        self.simulator_window.simulate_traces.clicked.connect(self.initialise_simulation)

        self.simulator_window.checkBoxDlifetime.stateChanged.connect(self.update_simulation_options)
        self.simulator_window.checkBoxALifetime.stateChanged.connect(self.update_simulation_options)
        self.simulator_window.checkBoxTransitionProbability.stateChanged.connect(self.update_simulation_options)
        self.simulator_window.checkBoxRandomState.stateChanged.connect(self.update_simulation_options)
        self.simulator_window.checkBoxNoise.stateChanged.connect(self.update_simulation_options)
        self.simulator_window.checkBoxMismatch.stateChanged.connect(self.update_simulation_options)
        self.simulator_window.checkBoxScaler.stateChanged.connect(self.update_simulation_options)
        self.simulator_window.checkBoxBleedthrough.stateChanged.connect(self.update_simulation_options)

        self.fitting_window.hmm_package.currentIndexChanged.connect(self.update_hmm_fit_algo)

        self.draw_analysis_plot.clicked.connect(self.initialise_analysis_plot)
        self.draw_transmat_plot.clicked.connect(self.initialise_transmat_plot)
        self.measure_analysis_plot.clicked.connect(self.initialise_measure_plot)

        self.export_analysis_data.clicked.connect(self.export_analysis_histogram_data)
        self.export_measure_data.clicked.connect(self.export_measure_histogram_data)

        self.manage_window.manage_delete_active_trace.clicked.connect(self.delete_active_trace)
        self.manage_window.manage_delete_traces.clicked.connect(self.delete_traces)
        self.manage_window.manage_delete_dataset.clicked.connect(self.delete_dataset)
        self.manage_window.manage_rename_dataset.clicked.connect(self.rename_dataset)
        self.manage_window.manage_rename_measurement_label.clicked.connect(self.rename_measurement_label)

        self.manage_window.assign_ml_labels.clicked.connect(self.assign_ml_labels)

        self.crop_window.detect_crop.clicked.connect(self.initialise_crop_detection)

        self.analysis_histogram.currentIndexChanged.connect(self.update_histogram_options)

        # Set the color of the status bar text
        self.statusBar().setStyleSheet("QStatusBar{color: red;}")

        self.threadpool = QThreadPool()

        self.export_settings.export_mode.currentIndexChanged.connect(self.format_export_settings)

        self.format_export_settings()
        self.update_hmm_fit_algo()
        self.update_smooth_options()
        self.update_group_options()
        self.update_simulation_options()
        self.update_export_options()
        self.update_detectcrop_options()
        self.update_histogram_options()

        self.current_dialog = None
        self.updating_combos = False

        self.plot_queue = queue.Queue()


    def update_histogram_options(self):

        try:
            histogram = self.analysis_histogram.currentText()

            if histogram == "Raw Data":
                self.analysis_state.hide()
                self.analysis_state.setVisible(False)
                self.analysis_state_label.hide()
                self.analysis_state_label.setVisible(False)

                self.analysis_exposure_time.hide()
                self.analysis_exposure_time.setVisible(False)
                self.analysis_exposure_time_label.hide()
                self.analysis_exposure_time_label.setVisible(False)

            elif histogram == "Dwell Times (Seconds)":

                self.analysis_state.show()
                self.analysis_exposure_time.setVisible(True)
                self.analysis_state_label.show()
                self.analysis_exposure_time_label.show()

                self.analysis_exposure_time.show()
                self.analysis_exposure_time.setVisible(True)
                self.analysis_exposure_time_label.show()
                self.analysis_exposure_time_label.setVisible(True)

            else:
                self.analysis_state.show()
                self.analysis_state.setVisible(True)
                self.analysis_state_label.show()
                self.analysis_state_label.setVisible(True)

                self.analysis_exposure_time.hide()
                self.analysis_exposure_time.setVisible(False)
                self.analysis_exposure_time_label.hide()
                self.analysis_exposure_time_label.setVisible(False)

        except:
            print(traceback.format_exc())



    def update_export_options(self):

        try:

            export_mode = self.export_settings.export_mode.currentText()

            control_dict = {"dataset_selection": "export_dataset_selection",
                            "channel_selection": "export_channel_selection",
                            "user_group": "export_user_group",
                            "separator": "export_separator",
                            "split_datasets": "export_split_datasets",
                            "fitted_states": "export_fitted_states",
                            "state_means": "export_state_means",
                            "crop_data": "export_crop_data",
                            "ml_class": "ml_export_class",
                            }

            hidden_controls = []

            if export_mode == "JSON Dataset (.json)":

                hidden_controls = ["dataset_selection","channel_selection",
                                   "user_group",
                                   "separator", "split_datasets",
                                   "fitted_states", "crop_data",
                                   "ml_class"]

            elif export_mode in ["Excel (.xlsx)","OriginLab (.opju)"]:

                hidden_controls = ["separator","ml_class"]

            elif export_mode in ["DAT (.dat)","CSV (.csv)","Text (.txt)"]:

                hidden_controls = ["ml_class"]

            elif export_mode == "ML Dataset":

                hidden_controls = []

            elif export_mode == "Export Trace Summary":

                    hidden_controls = ["separator", "split_datasets",
                                       "fitted_states", "state_means", "crop_data",
                                       "ml_class"]

            elif export_mode == "Nero (.dat)":

                    hidden_controls = ["separator","fitted_states","state_means",
                                       "crop_data", "ml_class"]

            elif export_mode == "ebFRET SMD (.mat)":

                        hidden_controls = ["separator",
                                           "fitted_states", "state_means",
                                           "ml_class"]

            for control in control_dict:

                control_name = control_dict[control]
                control_label = control_name + "_label"

                control_widget = getattr(self.export_settings, control_name)

                if hasattr(self.export_settings, control_label):
                    control_label_widget = getattr(self.export_settings, control_label)
                else:
                    control_label_widget = None

                if control in hidden_controls:
                    control_widget.hide()
                    if control_label_widget is not None:
                        control_label_widget.hide()
                else:
                    control_widget.show()
                    if control_label_widget is not None:
                        control_label_widget.show()

                if set(hidden_controls).issubset(["separator", "split_datasets",
                                   "fitted_states", "crop_data",
                                   "ml_class"]):

                    self.export_settings.settings_label.show()
                else:
                    self.export_settings.settings_label.hide()

            self.update_export_channel_selection()

        except:
            print(traceback.format_exc())
            pass


    def update_measurement_labels(self):

        try:

            pass

            # index = self.plot_settings.plot_measurement_label.currentIndex()
            # label = self.plot_settings.plot_measurement_label.currentText()
            #
            # combo = self.measure_label
            # combo.setItemText(index, label)
            #
            # slider_value = self.plot_localisation_number.value()
            # localisation_number = self.localisation_numbers[slider_value]
            #
            # for dataset in self.data_dict:
            #     localisation_dict = self.data_dict[dataset][localisation_number]
            #
            #     if "measure_dict" in localisation_dict.keys():
            #         dict_keys = list(localisation_dict["measure_dict"].keys())
            #         updated_key = dict_keys[index]
            #
            #         localisation_dict["measure_dict"][label] = localisation_dict["measure_dict"].pop(updated_key)

        except:
            print(traceback.format_exc())
            pass


    def dev_function(self):

        print("Dev function")
        self.update_histogram_options()

    def enterEvent(self, event):
        self.setFocus()

    def gui_progrssbar(self,progress, name):

        if name.lower() == "inceptiontime":
            self.detect_window.inceptiontime_progressbar.setValue(progress)
        if name.lower() == "hmm":
            self.fitting_window.hmm_progressbar.setValue(progress)
        if name.lower() == "smooth":
            self.smoothing_window.smooth_progressbar.setValue(progress)
        if name.lower() == "bleach":
            self.bleach_window.bleach_progressbar.setValue(progress)
        if name.lower() == "correction":
            self.correction_window.correction_progressbar.setValue(progress)
        if name.lower() == "group":
            self.group_window.group_progressbar.setValue(progress)
        if name.lower() == "export":
            self.export_settings.export_progressbar.setValue(progress)



    def format_export_settings(self):

        export_mode = self.export_settings.export_mode.currentText()

        if "csv" in export_mode.lower():

            self.export_settings.export_separator.clear()
            self.export_settings.export_separator.addItems(["Comma"])

        else:
            self.export_settings.export_separator.clear()
            self.export_settings.export_separator.addItems(["Tab","Comma", "Space"])


    def closeEvent(self, event):

        self._close_ebFRET()
        self.plot_settings.close()
        self.import_settings.close()
        self.export_settings.close()
        self.fitting_window.close()
        self.detect_window.close()
        self.smoothing_window.close()
        self.bleach_window.close()
        self.correction_window.close()
        self.group_window.close()
        self.simulator_window.close()
        self.manage_window.close()
        self.crop_window.close()

    def keyPressEvent(self, event):
        try:

            if event.key() in [Qt.Key_1,Qt.Key_2,Qt.Key_3,Qt.Key_4,Qt.Key_5,Qt.Key_6,Qt.Key_7,Qt.Key_8,Qt.Key_9]:
                self.classify_traces(mode = "user", key = chr(event.key()))
            elif event.key() in [Qt.Key_Left,Qt.Key_Right]:
                self.update_localisation_number(event.key())
            elif event.key() == Qt.Key_Space:
                self.toggle_plot_settings()
            elif event.key() == Qt.Key_I:
                self.toggle_import_settings()
            elif event.key() == Qt.Key_E:
                self.toggle_export_settings()
            elif event.key() == Qt.Key_F:
                self.toggle_fitting_window()
            elif event.key() == Qt.Key_D:
                self.delete_active_trace()
            elif event.key() == Qt.Key_X:
                self.toggle_checkbox(self.plot_settings.plot_showx)
            elif event.key() == Qt.Key_Y:
                self.toggle_checkbox(self.plot_settings.plot_showy)
            elif event.key() == Qt.Key_N:
                self.toggle_checkbox(self.plot_settings.plot_normalise)
            elif event.key() == Qt.Key_S:
                self.toggle_checkbox(self.plot_settings.plot_split_lines)
            elif event.key() == Qt.Key_Escape:
                self.close()  # Close the application on pressing the Escape key
            elif event.key() == Qt.Key_F1:
                self.dev_function()
            elif event.key() == Qt.Key_P:
                self.initialise_analysis_plot()

            # Add more key handling as needed
            else:
                super().keyPressEvent(event)  # Important to allow unhandled key events to propagate
        except:
            print(traceback.format_exc())
            pass

    def print_notification(self, message):
        self.statusBar().showMessage(message, 5000)
        print(message)

    def toggle_checkbox(self, checkbox):
        checkbox.setChecked(not checkbox.isChecked())

    def classify_traces(self, mode = "user", key= ""):

        if self.data_dict != {}:

            slider_value = self.plot_localisation_number.value()
            localisation_number = self.localisation_numbers[slider_value]

            for dataset_name in self.data_dict.keys():
                self.data_dict[dataset_name][localisation_number]["user_label"] = key

            self.plot_traces(update_plot=False)

    def update_localisation_number(self, key):

        if self.data_dict != {}:

            localisation_number = self.plot_localisation_number.value()
            dataset_name = self.plot_data.currentText()

            if key == Qt.Key_Left:
                new_localisation_number = localisation_number - 1
            elif key == Qt.Key_Right:
                new_localisation_number = localisation_number + 1
            else:
                new_localisation_number = localisation_number

            if dataset_name not in self.data_dict.keys():
                dataset_name = list(self.data_dict.keys())[0]

            if new_localisation_number >= 0 and new_localisation_number < len(self.data_dict[dataset_name]):
                self.plot_localisation_number.setValue(new_localisation_number)
                self.plot_traces(update_plot=True)


    def update_slider_label(self, slider_name):

        label_name = slider_name + "_label"

        self.slider = self.findChild(QSlider, slider_name)
        self.label = self.findChild(QLabel, label_name)

        slider_value = self.slider.value()
        self.label.setText(str(slider_value))





def start_gui(blocking=True):

    dark_stylesheet = """
        QMainWindow {background-color: #2e2e2e;}
        QMenuBar {background-color: #2e2e2e;}
        QMenuBar::item {background-color: #2e2e2e;color: #ffffff;}
        QMenu {background-color: #2e2e2e;border: 1px solid #1e1e1e;}
        QMenu::item {color: #ffffff;}
        QMenu::item:selected {background-color: #5e5e5e;}
    """

    # to launch the GUI from the console such that it is editable:
    # from TraceAnalyser.GUI.analysis_gui import start_gui
    # gui = start_gui(False)

    app = QtWidgets.QApplication.instance()  # Check if QApplication already exists
    if not app:  # Create QApplication if it doesn't exist
        app = QtWidgets.QApplication(sys.argv)

    app.setStyleSheet(dark_stylesheet)  # Apply the dark theme
    mainwindow = AnalysisGUI()
    mainwindow.show()

    if blocking:
        app.exec()  # Start the event loop

    return mainwindow

