from TraceAnalyser.GUI.plotsettings_gui import Ui_Form as plotsettings_gui
from TraceAnalyser.GUI.importwindow_gui import Ui_Form as importwindow_gui
from TraceAnalyser.GUI.exportsettings_gui import Ui_Form as exportwindow_gui
from TraceAnalyser.GUI.fittingwindow_gui import Ui_Form as fittingwindow_gui
from TraceAnalyser.GUI.detectwindow_gui import Ui_Form as detectwindow_gui
from TraceAnalyser.GUI.smoothingwindow_gui import Ui_Form as smoothingwindow_gui
from TraceAnalyser.GUI.bleachwindow_gui import Ui_Form as bleachwindow_gui
from TraceAnalyser.GUI.correctionwindow_gui import Ui_Form as correctionwindow_gui
from TraceAnalyser.GUI.groupwindow_gui import Ui_Form as groupwindow_gui
from TraceAnalyser.GUI.simulatorwindow_gui import Ui_Form as simulatorwindow_gui
from TraceAnalyser.GUI.managewindow_gui import Ui_Form as managewindow_gui
from TraceAnalyser.GUI.cropwindow_gui import Ui_Form as cropwindow_gui



from qtpy.QtWidgets import QDialog
from PyQt5.QtCore import Qt
import traceback


class _window_utils:


    def sort_channel_list(self, channel_list):

        try:

            reference_list = ["All Channels",
                              "Data",
                              "Trace",
                              "Donor", "Acceptor",
                              "FRET Efficiency",
                              "FRET Data",
                              "FRET Data + FRET Efficiency",
                              "FRET Correction Data",
                              "DD", "AA", "DA", "AD",
                              "ALEX Efficiency",
                              "ALEX Data",
                              "ALEX Data + ALEX Efficiency"
                              "ALEX Correction Data",
                              ]

            order = {key: i for i, key in enumerate(reference_list)}

            # Sort the actual list based on the order defined in the reference list
            sorted_list = sorted(channel_list, key=lambda x: order.get(x, float('inf')))

        except:
            pass

        return sorted_list

    def update_dataset_selection(self, window_name, dataset_combo):

        try:
            if len(self.data_dict.keys()) > 0:

                window = getattr(self, window_name)

                dataset_combo = getattr(window, dataset_combo)
                dataset_names = list(self.data_dict.keys())

                if len(dataset_names) > 1:
                    dataset_names.insert(0, "All Datasets")

                dataset_combo.blockSignals(True)
                dataset_combo.clear()
                dataset_combo.addItems(dataset_names)
                dataset_combo.blockSignals(False)

        except:
            print(traceback.format_exc())

    def update_channel_selection(self, window_name,
            dataset_combo_name, channel_combo_name,
            channel_dict_name = "channel_dict",
            single_channel = False):

        try:

            channel_dict = {}

            if len(self.data_dict.keys()) > 0:

                window = getattr(self, window_name)

                channel_combo = getattr(window, channel_combo_name)
                dataset_combo = getattr(window, dataset_combo_name)

                if hasattr(self, channel_dict_name) == False:
                    setattr(self, channel_dict_name, {})

                channel_dict = getattr(self, channel_dict_name)

                export_dataset = dataset_combo.currentText()

                if export_dataset == "All Datasets":
                    dataset_list = list(self.data_dict.keys())
                else:
                    dataset_list = [export_dataset]

                channel_names = []
                combo_options = []

                for dataset_name in dataset_list:
                    for channel_name in self.data_dict[dataset_name][0].keys():
                        if channel_name in ["Data","Trace", "Donor", "Acceptor", "FRET Efficiency", "ALEX Efficiency", "DD", "AA", "DA", "AD"]:
                            data_length = len(self.data_dict[dataset_name][0][channel_name])
                            if data_length > 1:
                                if channel_name not in channel_names:
                                    channel_names.append(channel_name)

                if single_channel == False:

                    if set(["Donor", "Acceptor"]).issubset(channel_names):
                        combo_options.append("FRET Data")
                        channel_dict["FRET Data"] = ["Donor", "Acceptor"]
                    if set(["Donor", "Acceptor", "FRET Efficiency"]).issubset(channel_names):
                        combo_options.append("FRET Data + FRET Efficiency")
                        channel_dict["FRET Data + FRET Efficiency"] = ["Donor", "Acceptor", "FRET Efficiency"]
                    if set(["DD", "DA", "AD", "AA"]).issubset(channel_names):
                        combo_options.append("ALEX Data")
                        channel_dict["ALEX Data"] = ["DD", "DA", "AD", "AA"]
                    if set(["DD", "DA", "AD", "AA", "ALEX Efficiency"]).issubset(channel_names):
                        combo_options.append("ALEX Data + ALEX Efficiency")
                        channel_dict["ALEX Data + ALEX Efficiency"] = ["DD", "DA", "AD", "AA", "ALEX Efficiency"]

                if "Trace" in channel_names:
                    combo_options.append("Trace")
                    channel_dict["Trace"] = ["Trace"]
                if "Data" in channel_names:
                    combo_options.append("Data")
                    channel_dict["Data"] = ["Data"]
                if "Donor" in channel_names:
                    combo_options.append("Donor")
                    channel_dict["Donor"] = ["Donor"]
                if "Acceptor" in channel_names:
                    combo_options.append("Acceptor")
                    channel_dict["Acceptor"] = ["Acceptor"]
                if "DD" in channel_names:
                    combo_options.append("DD")
                    channel_dict["DD"] = ["DD"]
                if "AA" in channel_names:
                    combo_options.append("AA")
                    channel_dict["AA"] = ["AA"]
                if "DA" in channel_names:
                    combo_options.append("DA")
                    channel_dict["DA"] = ["DA"]
                if "AD" in channel_names:
                    combo_options.append("AD")
                    channel_dict["AD"] = ["AD"]
                if "FRET Efficiency" in channel_names:
                    combo_options.append("FRET Efficiency")
                    channel_dict["FRET Efficiency"] = ["FRET Efficiency"]
                if "ALEX Efficiency" in channel_names:
                    combo_options.append("ALEX Efficiency")
                    channel_dict["ALEX Efficiency"] = ["ALEX Efficiency"]

                combo_options = self.sort_channel_list(combo_options)

                if len(combo_options) > 1 and single_channel == False:
                    combo_options.insert(0, "All Channels")
                    channel_dict["All Channels"] = channel_names

                channel_combo.blockSignals(True)
                channel_combo.clear()
                channel_combo.addItems(combo_options)
                channel_combo.blockSignals(False)

        except:
            print(traceback.format_exc())

        return channel_dict

    def toggle_simulator_window(self):

        print("Toggling Simulation Window")

        if self.simulator_window.isHidden() or self.simulator_window.isActiveWindow() == False:
            if self.current_dialog != self.simulator_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.simulator_window.show()
            self.simulator_window.raise_()
            self.simulator_window.activateWindow()
            self.simulator_window.setFocus()

            self.current_dialog = self.simulator_window

        else:
            self.simulator_window.hide()
            self.activateWindow()


    def toggle_correction_window(self):

            if self.correction_window.isHidden() or self.correction_window.isActiveWindow() == False:
                if self.current_dialog != self.correction_window:
                    if self.current_dialog != None:
                        self.current_dialog.hide()
                        self.current_dialog.close()

                self.correction_window.show()
                self.correction_window.raise_()
                self.correction_window.activateWindow()
                self.correction_window.setFocus()

                self.current_dialog = self.correction_window

            else:
                self.correction_window.hide()
                self.activateWindow()


    def toggle_bleach_window(self):

        if self.bleach_window.isHidden() or self.bleach_window.isActiveWindow() == False:
            if self.current_dialog != self.bleach_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.bleach_window.show()
            self.bleach_window.raise_()
            self.bleach_window.activateWindow()
            self.bleach_window.setFocus()

            self.current_dialog = self.bleach_window

        else:
            self.bleach_window.hide()
            self.activateWindow()

    def toggle_smoothing_window(self):
        if self.smoothing_window.isHidden() or self.smoothing_window.isActiveWindow() == False:
            if self.current_dialog != self.smoothing_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.smoothing_window.show()
            self.smoothing_window.raise_()
            self.smoothing_window.activateWindow()
            self.smoothing_window.setFocus()

            self.current_dialog = self.smoothing_window

        else:
            self.smoothing_window.hide()
            self.activateWindow()

    def toggle_detect_window(self):
        if self.detect_window.isHidden() or self.detect_window.isActiveWindow() == False:
            if self.current_dialog != self.detect_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.detect_window.show()
            self.detect_window.raise_()
            self.detect_window.activateWindow()
            self.detect_window.setFocus()

            self.current_dialog = self.detect_window

        else:
            self.detect_window.hide()
            self.activateWindow()

    def toggle_fitting_window(self):
        if self.fitting_window.isHidden() or self.fitting_window.isActiveWindow() == False:
            if self.current_dialog != self.fitting_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.populate_ebFRET_options()
            self.populate_HMM_options()

            self.fitting_window.show()
            self.fitting_window.raise_()
            self.fitting_window.activateWindow()
            self.fitting_window.setFocus()

            # self.fitting_window.exec_()

            self.current_dialog = self.fitting_window

        else:
            self.fitting_window.hide()
            self.activateWindow()

    def toggle_plot_settings(self):
        if self.plot_settings.isHidden() or self.plot_settings.isActiveWindow() == False:
            if self.current_dialog != self.fitting_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.plot_settings.show()
            self.plot_settings.raise_()
            self.plot_settings.activateWindow()
            self.plot_settings.setFocus()
            # self.plot_settings.exec_()

            self.current_dialog = self.plot_settings

        else:
            self.plot_settings.hide()
            self.activateWindow()

    def toggle_import_settings(self):
        if self.import_settings.isHidden() or self.import_settings.isActiveWindow() == False:
            if self.current_dialog != self.fitting_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.import_settings.show()
            self.import_settings.raise_()
            self.import_settings.activateWindow()
            self.import_settings.setFocus()
            # self.import_settings.exec_()

            self.current_dialog = self.import_settings

        else:
            self.import_settings.hide()
            self.activateWindow()

    def toggle_export_settings(self):
        if self.export_settings.isHidden() or self.export_settings.isActiveWindow() == False:
            if self.current_dialog != self.fitting_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.export_settings.show()
            self.export_settings.raise_()
            self.export_settings.activateWindow()
            self.export_settings.setFocus()
            # self.export_settings.exec_()

            self.current_dialog = self.export_settings

        else:
            self.export_settings.hide()
            self.activateWindow()

    def toggle_group_window(self):
        if self.group_window.isHidden() or self.group_window.isActiveWindow() == False:
            if self.current_dialog != self.group_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.group_window.show()
            self.group_window.raise_()
            self.group_window.activateWindow()
            self.group_window.setFocus()

            self.current_dialog = self.group_window

        else:
            self.group_window.hide()
            self.activateWindow()

    def toggle_manage_window(self):

        if self.manage_window.isHidden() or self.manage_window.isActiveWindow() == False:
            if self.current_dialog != self.manage_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.manage_window.show()
            self.manage_window.raise_()
            self.manage_window.activateWindow()
            self.manage_window.setFocus()

            self.current_dialog = self.manage_window

        else:
            self.manage_window.hide()
            self.activateWindow()

    def toggle_crop_window(self):

        if self.crop_window.isHidden() or self.crop_window.isActiveWindow() == False:
            if self.current_dialog != self.crop_window:
                if self.current_dialog != None:
                    self.current_dialog.hide()
                    self.current_dialog.close()

            self.crop_window.show()
            self.crop_window.raise_()
            self.crop_window.activateWindow()
            self.crop_window.setFocus()

            self.current_dialog = self.crop_window

        else:
            self.crop_window.hide()
            self.activateWindow()




class ManageWindow(QDialog, managewindow_gui):

    def __init__(self, parent):
        super(ManageWindow, self).__init__()
        self.setupUi(self)  # Set up the user interface from Designer.
        self.setWindowTitle("Dataset Management")  # Set the window title

        self.AnalysisGUI = parent

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Escape:
                self.close()
            else:
                self.AnalysisGUI.keyPressEvent(event)
                super().keyPressEvent(event)
        except:
            pass


class GroupWindow(QDialog, groupwindow_gui):

        def __init__(self, parent):
            super(GroupWindow, self).__init__()
            self.setupUi(self)  # Set up the user interface from Designer.
            self.setWindowTitle("Group Traces")  # Set the window title

            self.AnalysisGUI = parent

        def keyPressEvent(self, event):
            try:
                if event.key() == Qt.Key_Escape:
                    self.close()
                else:
                    self.AnalysisGUI.keyPressEvent(event)
                    super().keyPressEvent(event)
            except:
                pass

class CorrectionWindow(QDialog, correctionwindow_gui):

        def __init__(self, parent):
            super(CorrectionWindow, self).__init__()
            self.setupUi(self)  # Set up the user interface from Designer.
            self.setWindowTitle("Correction")  # Set the window title

            self.AnalysisGUI = parent

        def keyPressEvent(self, event):
            try:
                if event.key() == Qt.Key_Escape:
                    self.close()
                else:
                    self.AnalysisGUI.keyPressEvent(event)
                    super().keyPressEvent(event)
            except:
                pass


class BleachWindow(QDialog, bleachwindow_gui):

    def __init__(self, parent):
        super(BleachWindow, self).__init__()
        self.setupUi(self)  # Set up the user interface from Designer.
        self.setWindowTitle("Bleach Correction")  # Set the window title

        self.AnalysisGUI = parent

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Escape:
                self.close()
            else:
                self.AnalysisGUI.keyPressEvent(event)
                super().keyPressEvent(event)
        except:
            pass




class SmoothingWindow(QDialog, smoothingwindow_gui):

    def __init__(self, parent):
        super(SmoothingWindow, self).__init__()
        self.setupUi(self)  # Set up the user interface from Designer.
        self.setWindowTitle("Smooth Traces")  # Set the window title

        self.AnalysisGUI = parent

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Escape:
                self.close()
            else:
                self.AnalysisGUI.keyPressEvent(event)
                super().keyPressEvent(event)
        except:
            pass

class DetectWindow(QDialog, detectwindow_gui):

    def __init__(self, parent):
        super(DetectWindow, self).__init__()
        self.setupUi(self)  # Set up the user interface from Designer.
        self.setWindowTitle("Detect Dynamic/Static States")  # Set the window title

        self.AnalysisGUI = parent

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_D:
                self.close()
            elif event.key() == Qt.Key_Escape:
                self.close()
            else:
                self.AnalysisGUI.keyPressEvent(event)
                super().keyPressEvent(event)
        except:
            pass

class FittingWindow(QDialog, fittingwindow_gui):

    def __init__(self, parent):
        super(FittingWindow, self).__init__()

        self.setupUi(self)  # Set up the user interface from Designer.
        self.setWindowTitle("Fit Hidden States")  # Set the window title

        self.AnalysisGUI = parent

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_F:
                self.close()
            elif event.key() == Qt.Key_Escape:
                self.close()
            else:
                self.AnalysisGUI.keyPressEvent(event)
                super().keyPressEvent(event)
        except:
            pass

class ImportSettingsWindow(QDialog, importwindow_gui):

    def __init__(self, parent):
        super(ImportSettingsWindow, self).__init__()
        self.setupUi(self)  # Set up the user interface from Designer.
        self.setWindowTitle("Import Settings")  # Set the window title

        self.AnalysisGUI = parent

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_I:
                self.close()
            elif event.key() == Qt.Key_Escape:
                self.close()
            else:
                self.AnalysisGUI.keyPressEvent(event)
                super().keyPressEvent(event)
        except:
            pass

class ExportSettingsWindow(QDialog, exportwindow_gui):

    def __init__(self, parent):
        super(ExportSettingsWindow, self).__init__()
        self.setupUi(self)  # Set up the user interface from Designer.
        self.setWindowTitle("Export Settings")  # Set the window title

        self.AnalysisGUI = parent

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_E:
                self.close()
            elif event.key() == Qt.Key_Escape:
                self.close()
            else:
                self.AnalysisGUI.keyPressEvent(event)
                super().keyPressEvent(event)
        except:
            pass

class PlotSettingsWindow(QDialog, plotsettings_gui):

    def __init__(self, parent):
        super(PlotSettingsWindow, self).__init__()
        self.setupUi(self)  # Set up the user interface from Designer.
        self.setWindowTitle("Plot Settings")  # Set the window title

        self.AnalysisGUI = parent

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Space:
                self.close()
            elif event.key() == Qt.Key_Escape:
                self.close()
            else:
                self.AnalysisGUI.keyPressEvent(event)
                super().keyPressEvent(event)
        except:
            pass


class SimulatorWindow(QDialog, simulatorwindow_gui):

    def __init__(self, parent):
        super(SimulatorWindow, self).__init__()
        self.setupUi(self)  # Set up the user interface from Designer.
        self.setWindowTitle("Simulator")  # Set the window title

        self.AnalysisGUI = parent

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Escape:
                self.close()
            else:
                self.AnalysisGUI.keyPressEvent(event)
                super().keyPressEvent(event)
        except:
            pass


class CropWindow(QDialog, cropwindow_gui):

    def __init__(self, parent):
        super(CropWindow, self).__init__()
        self.setupUi(self)  # Set up the user interface from Designer.
        self.setWindowTitle("Crop Traces")  # Set the window title

        self.AnalysisGUI = parent

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Escape:
                self.close()
            else:
                self.AnalysisGUI.keyPressEvent(event)
                super().keyPressEvent(event)
        except:
            pass