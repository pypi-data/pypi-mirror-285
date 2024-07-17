from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QCheckBox
import numpy as np
import pyqtgraph as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import traceback
from functools import partial
import uuid
import copy
import re
from PyQt5.QtGui import QColor, QFont



class _trace_plot_overlays:

    def reset_graphics_overlays(self, mode = "crop", loc_mode="active"):

        slider_value = self.plot_localisation_number.value()
        localisation_number = self.localisation_numbers[slider_value]

        if mode == "crop":
            range_name = "crop_range"
            range_value = []
        elif mode == "gamma":
            range_name = "gamma_ranges"
            range_value = []
        elif mode == "measurement":
            range_name = "measure_dict"
            range_value = {}

        for dataset_name in self.data_dict.keys():

            if loc_mode == "active":
                loc_list = [localisation_number]
            else:
                loc_list = range(len(self.data_dict[dataset_name]))

            for localisation_number in loc_list:

                localisation_data = self.data_dict[dataset_name][localisation_number]

                if mode != "bleach":
                    if range_name in localisation_data.keys():
                        localisation_data[range_name] = range_value
                else:
                    localisation_data["correction_factors"]["donor_bleach_index"] = None
                    localisation_data["correction_factors"]["acceptor_bleach_index"] = None

        self.plot_traces(update_plot=False)

    def initialise_bleach_ref(self, dataset, plot_labels,
            colour = (0, 0, 255, 50)):

        bleach_ref_name = str(uuid.uuid4())
        setattr(self, bleach_ref_name, pg.LinearRegionItem(brush=colour, ))
        bleach_ref = getattr(self, bleach_ref_name)

        bleach_ref.name = f"bleach_ref[{bleach_ref_name}]"

        update_function = partial(self.update_bleach_range, mode="drag",
            plot_labels=plot_labels, dataset=dataset)

        finish_function = partial(self.update_correction_factors, dataset=dataset)

        bleach_ref.sigRegionChanged.connect(update_function)
        bleach_ref.sigRegionChangeFinished.connect(finish_function)

        return bleach_ref

    def initialise_crop_region(self, colour = (255, 0, 0, 50)):

        crop_region_name = str(uuid.uuid4())
        setattr(self, crop_region_name, pg.LinearRegionItem(brush=colour))
        crop_region = getattr(self, crop_region_name)
        crop_region.sigRegionChanged.connect(partial(self.update_crop_range, mode="drag"))

        crop_region.name = f"crop_region[{crop_region_name}]"

        self.unique_crop_regions.append(crop_region)

        return crop_region

    def initialise_gamma_refs(self, dataset, plot_labels,
        colour = (255, 0, 255, 50)):

        gamma1_ref_name = str(uuid.uuid4())
        setattr(self, gamma1_ref_name, pg.LinearRegionItem(brush=colour))
        gamma1_ref = getattr(self, gamma1_ref_name)

        update_function = partial(self.update_gamma_ranges, mode="drag", ref=1,
            plot_labels=plot_labels, dataset=dataset)
        finish_function = partial(self.update_correction_factors, dataset=dataset)

        gamma1_ref.sigRegionChanged.connect(update_function)
        gamma1_ref.sigRegionChangeFinished.connect(finish_function)

        gamma2_ref_name = str(uuid.uuid4())
        setattr(self, gamma2_ref_name, pg.LinearRegionItem(brush=colour))
        gamma2_ref = getattr(self, gamma2_ref_name)

        update_function = partial(self.update_gamma_ranges, mode="drag", ref=2,
            plot_labels=plot_labels, dataset=dataset)
        finish_function = partial(self.update_correction_factors, dataset=dataset)

        gamma2_ref.sigRegionChanged.connect(update_function)
        gamma2_ref.sigRegionChangeFinished.connect(finish_function)

        gamma1_ref.name = f"gamma1_ref[{gamma1_ref_name}]"
        gamma2_ref.name = f"gamma2_ref[{gamma2_ref_name}]"

        self.unique_gamma1_refs.append(gamma1_ref)
        self.unique_gamma2_refs.append(gamma2_ref)

        return [gamma1_ref, gamma2_ref]

    def update_correction_factors(self, event=None, dataset ="", localisation_number = None,
            update_efficiencies = True):

        try:

            if localisation_number == None:
                slider_value = self.plot_localisation_number.value()
                localisation_number = self.localisation_numbers[slider_value]

            if dataset in self.data_dict.keys():

                localisation_dict = self.data_dict[dataset][localisation_number]

                localisation_dict_keys = list(localisation_dict.keys())

                if "gamma_ranges" in localisation_dict_keys:
                    gamma_ranges = localisation_dict["gamma_ranges"]
                else:
                    gamma_ranges = []

                if "correction_factors" not in localisation_dict_keys:
                    localisation_dict["correction_factors"] = {}

                correction_factors = localisation_dict["correction_factors"]

                if set(["Donor", "Acceptor"]).issubset(localisation_dict_keys):

                    donor = np.array(localisation_dict["Donor"]).copy()
                    acceptor = np.array(localisation_dict["Acceptor"]).copy()

                    gamma = self.compute_gamma(donor, acceptor, gamma_ranges)

                    correction_factors["gamma"] = gamma

                    if update_efficiencies:

                        fret_efficiency, corrected = self.compute_fret_efficiency(donor, acceptor, correction_factors)

                        localisation_dict["FRET Efficiency"] = fret_efficiency
                        localisation_dict["FRET Efficiency Corrected"] = corrected

                if set(["DD", "DA", "AA"]).issubset(localisation_dict_keys):

                    DD = np.array(localisation_dict["DD"]).copy()
                    DA = np.array(localisation_dict["DA"]).copy()
                    AA = np.array(localisation_dict["AA"]).copy()

                    a_direct = self.compute_direct_acceptor(DA, AA, correction_factors)
                    d_leakage = self.compute_donor_leakage(DD, DA, correction_factors)
                    gamma = self.compute_gamma(DD, DA, gamma_ranges)

                    correction_factors["gamma"] = gamma
                    correction_factors["a_direct"] = a_direct
                    correction_factors["d_leakage"] = d_leakage

                    if update_efficiencies:

                        alex_efficiency, stoichiometry, corrected = self.compute_alex_efficiency(DD, DA, AA, correction_factors)

                        localisation_dict["ALEX Efficiency"] = alex_efficiency
                        localisation_dict["ALEX Efficiency Corrected"] = corrected
                        localisation_dict["ALEX Stoichiometry"] = stoichiometry

            self.plot_traces(update_plot=False)

        except:
            print(traceback.format_exc())
            pass

    def update_bleach_range(self, event, mode = "click", plot_labels = [], dataset = ""):

        try:

            slider_value = self.plot_localisation_number.value()
            localisation_number = self.localisation_numbers[slider_value]
            localisation_dict = self.data_dict[dataset][localisation_number]

            correction_factors = localisation_dict["correction_factors"]

            if mode == "click":

                donor_channels = ["Donor", "DD"]
                acceptor_channels = ["Acceptor", "DA"]

                bleach_index = event

                if type(plot_labels) == list:

                    if set(plot_labels).issubset(donor_channels):
                        correction_factors["donor_bleach_index"] = bleach_index

                    if set(plot_labels).issubset(acceptor_channels):
                        correction_factors["acceptor_bleach_index"] = bleach_index

                self.plot_traces(update_plot=False)

            else:

                if self.plot_grid != {}:

                    bleach_index = list(event.getRegion())[0]

                    donor_refs = self.donor_bleach_refs[dataset]
                    acceptor_refs = self.acceptor_bleach_refs[dataset]

                    if event in donor_refs:
                        correction_factors["donor_bleach_index"] = int(bleach_index)

                        for bleach_ref in donor_refs:
                            if event == bleach_ref:
                                bleach_ref.blockSignals(True)
                                active_bleach_range = bleach_ref.getRegion()
                                updated_bleach_range = [bleach_index, active_bleach_range[1]]
                                bleach_ref.setRegion(updated_bleach_range)
                                bleach_ref.blockSignals(False)

                    if event in acceptor_refs:
                        correction_factors["acceptor_bleach_index"] = int(bleach_index)

                        for bleach_ref in acceptor_refs:
                            if event == bleach_ref:
                                bleach_ref.blockSignals(True)
                                active_bleach_range = bleach_ref.getRegion()
                                updated_bleach_range = [bleach_index, active_bleach_range[1]]
                                bleach_ref.setRegion(updated_bleach_range)
                                bleach_ref.blockSignals(False)

        except:
            print(traceback.format_exc())
            pass

    def update_gamma_ranges(self, event, mode = "click", ref=1,
            plot_labels=[], dataset=""):

        slider_value = self.plot_localisation_number.value()
        localisation_number = self.localisation_numbers[slider_value]

        initial_width = self.correction_window.gamma_default_frames.value()

        if mode == "click":

            gamma_ranges = self.data_dict[dataset][localisation_number]["gamma_ranges"]

            if len(gamma_ranges) == 0:
                gamma_ranges.append([event - initial_width, event + initial_width])
            else:
                update_range = False
                for index, range in enumerate(gamma_ranges):
                    if event > range[0] and event < range[1]:
                        update_range = True
                        break

                if update_range:
                    gamma_ranges[index] = [event - initial_width, event + initial_width]
                else:
                    gamma_ranges.append([event - initial_width, event + initial_width])

                if len(gamma_ranges) > 2:
                    gamma_ranges.pop(0)

            self.data_dict[dataset][localisation_number]["gamma_ranges"] = gamma_ranges
            self.plot_traces(update_plot=False)

        else:

            gamma_range = list(event.getRegion())

            if ref == 1:
                for region in self.unique_gamma1_refs:
                    if region != event:
                        region.blockSignals(True)
                        region.setRegion(gamma_range)
                        region.blockSignals(False)
            else:
                for region in self.unique_gamma2_refs:
                    if region != event:
                        region.blockSignals(True)
                        region.setRegion(gamma_range)
                        region.blockSignals(False)

            gamma_range1 = list(self.unique_gamma1_refs[0].getRegion())
            gamma_range2 = list(self.unique_gamma2_refs[0].getRegion())

            gamma_ranges = [gamma_range1, gamma_range2]

            self.data_dict[dataset][localisation_number]["gamma_ranges"] = gamma_ranges

    def initialise_text_overlay(self, plot, text=" ", dataset=""):

        try:
            text_ref = pg.TextItem(text, anchor=(0, 0))

            font = QFont()
            font.setPointSize(12)
            text_ref.setFont(font)
            font.setBold(True)
            text_ref.setColor(QColor(255, 255, 255))

            plot.addItem(text_ref)
            plot.getViewBox().sigRangeChanged.connect(lambda: self.update_text_position(plot, text_ref, dataset))
        except:
            print(traceback.format_exc())
            pass

    def get_plot_text(self, dataset):

        plot_text = ""

        try:

            show_correction_factors = self.plot_settings.plot_show_correction_factors.isChecked()
            show_ml_predictions = self.plot_settings.plot_show_ml_predictions.isChecked()

            slider_value = self.plot_localisation_number.value()
            localisation_number = self.localisation_numbers[slider_value]

            localisation_dict = self.data_dict[dataset][localisation_number]

            if show_correction_factors:
                if "correction_factors" in localisation_dict.keys():

                    correction_factors = localisation_dict["correction_factors"].copy()

                    for factor_name, factor_value in correction_factors.items():

                        if factor_name in ["gamma", "d_leakage", "a_direct"]:

                            if factor_name == "gamma":
                                display_name = "Gamma"
                            elif factor_name == "d_leakage":
                                display_name = "Donor Leakage"
                            elif factor_name == "a_direct":
                                display_name = "Direct Acceptor"

                            if type(factor_value) == float or type(factor_value) == int:

                                if np.isnan(factor_value) == False:
                                    plot_text += f"{display_name}: {factor_value:.4f}\n"
                                else:
                                    plot_text += f"{display_name}: NaN\n"
                            else:
                                plot_text += f"{display_name}: {factor_value}\n"

            if show_ml_predictions:
                if "pred_plot_label" in self.data_dict[dataset][localisation_number].keys():
                    pred = self.data_dict[dataset][localisation_number]["pred_plot_label"]
                    plot_text += (f" \nPred:{pred}")
                if "ml_label" in self.data_dict[dataset][localisation_number].keys():
                    ml_label = self.data_dict[dataset][localisation_number]["ml_label"]
                    if isinstance(ml_label, int):
                        plot_text += (f" \nML Label:{ml_label}")

        except:
            print(traceback.format_exc())

        return plot_text

    def update_text_position(self, plot, text_ref, dataset=""):

        try:

            text_ref.setText("XXX")

            view_box = plot.getViewBox()

            # Get the size of one pixel in data coordinates
            dx, dy = view_box.viewPixelSize()

            # Calculate the offset in data coordinates based on desired pixel offset
            pixel_offset_x = 10 * dx
            pixel_offset_y = -10 * dy  # Negative because y-axis is inverted

            # Get the current view range
            view_range = view_box.viewRange()

            # Calculate new position based on view range and pixel offset
            new_x = view_range[0][0] + pixel_offset_x
            new_y = view_range[1][1] + pixel_offset_y

            text_ref.setPos(new_x, new_y)

            plot_text = self.get_plot_text(dataset)
            text_ref.setText(plot_text)
            text_ref.setZValue(100)

        except:
            print(traceback.format_exc())
            pass

    def update_measure_range(self, event, xpos=None, mode="click", dataset=None, plot_labels=None,
            plot=None, range_index=None):

        slider_value = self.plot_localisation_number.value()
        localisation_number = self.localisation_numbers[slider_value]
        measurement_index = self.plot_settings.plot_measurement_label.currentText()

        default_range = 10

        if mode == "click":

            try:

                localisation_dict = self.data_dict[dataset][localisation_number]

                if "measure_dict" not in localisation_dict.keys():
                    localisation_dict["measure_dict"] = {}

                measure_dict = localisation_dict["measure_dict"].copy()

                if measurement_index not in measure_dict.keys():
                    measure_dict[measurement_index] = []

                measure_ranges = measure_dict[measurement_index]

                data_length = len(localisation_dict[plot_labels[0]])

                if xpos > 0 and xpos < data_length:

                    updated_range = [int(xpos) - default_range//2, int(xpos) + default_range//2]

                    if updated_range[0] < 0:
                        updated_range[0] = 0

                    if updated_range[1] > data_length:
                        updated_range[1] = data_length

                    # Check if the new range is within any existing ranges
                    if measure_ranges == []:
                        measure_ranges.append(updated_range)
                    else:
                        range_removed = False
                        for range in measure_ranges:
                            if xpos > range[0] and xpos < range[1]:
                                measure_ranges.remove(range)
                                range_removed = True
                        if range_removed == False:
                            measure_ranges.append(updated_range)

                for dataset_name in self.data_dict.keys():

                    localisation_dict = self.data_dict[dataset_name][localisation_number]

                    if "measure_dict" not in localisation_dict.keys():
                        localisation_dict["measure_dict"] = {}

                    measure_dict = localisation_dict["measure_dict"].copy()

                    if measurement_index not in measure_dict.keys():
                        measure_dict[measurement_index] = []

                    measure_dict[measurement_index] = measure_ranges

                    localisation_dict["measure_dict"] = measure_dict

                self.plot_traces(update_plot=False)

            except:
                print(traceback.format_exc())
                pass

        if mode == "drag":

            for dataset in self.data_dict.keys():

                if hasattr(self, "measure_refs"):

                    if dataset in self.measure_refs.keys():
                        measure_refs = self.measure_refs[dataset][localisation_number]

                        updated_range = event.getRegion()
                        updated_range = [int(updated_range[0]), int(updated_range[1])]

                        for ref_plot, refs in measure_refs.items():
                            if ref_plot != plot:
                                region = refs[range_index]
                                region.setRegion(updated_range)

            measure_ranges = []
            for item in plot.items:
                if isinstance(item, pg.LinearRegionItem):
                    region = item.getRegion()
                    measure_ranges.append([int(region[0]), int(region[1])])

            for dataset_name in self.data_dict.keys():

                localisation_dict = self.data_dict[dataset_name][localisation_number]

                if "measure_dict" not in localisation_dict.keys():
                    localisation_dict["measure_dict"] = {}

                measure_dict = localisation_dict["measure_dict"].copy()

                if measurement_index not in measure_dict.keys():
                    measure_dict[measurement_index] = []

                measure_dict[measurement_index] = measure_ranges

                localisation_dict["measure_dict"] = measure_dict

    def update_crop_range(self, event, mode ="click", plot_labels=[], dataset=""):

        slider_value = self.plot_localisation_number.value()
        localisation_number = self.localisation_numbers[slider_value]

        if mode == "click":

            for dataset_name in self.plot_info.keys():
                plot_channel = self.plot_info[dataset_name][0]
                break

            for dataset_name in self.data_dict.keys():

                crop_range = self.data_dict[dataset_name][localisation_number]["crop_range"].copy()
                data_length = self.data_dict[dataset_name][localisation_number][plot_channel].shape[0]

                if event < 0:
                    event = 0
                if event > data_length:
                    event = data_length

                event = int(event)

                crop_range.append(event)

                if len(crop_range) > 2:
                    crop_range.pop(0)

                self.data_dict[dataset_name][localisation_number]["crop_range"] = crop_range

                self.plot_traces(update_plot=False)

        elif mode == "drag":

            crop_range = list(event.getRegion())

            for region in self.unique_crop_regions:
                if region != event:
                    region.setRegion(crop_range)

            for dataset_name in self.data_dict.keys():
                self.data_dict[dataset_name][localisation_number]["crop_range"] = crop_range

    def initialise_measure_ref(self, dataset, plot, localisation_number,
            measure_range, range_index, colour = (0, 255, 0, 50)):

        try:

            if hasattr(self, "measure_refs") == False:
                self.measure_refs = {}

            measure_ref_name = str(uuid.uuid4())
            setattr(self, measure_ref_name, pg.LinearRegionItem(brush=colour))
            measure_ref = getattr(self, measure_ref_name)

            measure_ref.setRegion(measure_range)
            measure_ref.name = f"measure_range[{measure_ref_name}]"

            update_function = partial(self.update_measure_range,
                mode="drag", dataset=dataset, plot=plot,range_index=range_index)
            measure_ref.sigRegionChanged.connect(update_function)

            localisation_dict = self.data_dict[dataset][localisation_number]

            if dataset not in self.measure_refs:
                self.measure_refs[dataset] = {}
            if localisation_number not in self.measure_refs[dataset]:
                self.measure_refs[dataset][localisation_number] = {}
            if plot not in self.measure_refs[dataset][localisation_number]:
                self.measure_refs[dataset][localisation_number][plot] = []
            if measure_ref not in self.measure_refs[dataset][localisation_number][plot]:
                self.measure_refs[dataset][localisation_number][plot].append(measure_ref)

        except:
            print(traceback.format_exc())
            pass

        return measure_ref

    def plot_measure_ranges(self, plot_grid):

        try:

            slider_value = self.plot_localisation_number.value()
            measurement_index = self.plot_settings.plot_measurement_label.currentText()
            localisation_number = self.localisation_numbers[slider_value]

            for plot_index, grid in enumerate(self.plot_grid.values()):

                plot_dataset = grid["plot_dataset"]
                sub_axes = grid["sub_axes"]
                unique_sub_axes = grid["unique_sub_axes"]
                localisation_dict = self.data_dict[plot_dataset][localisation_number]

                if hasattr(self, "measure_refs") == False:
                    self.measure_refs = {}

                for plot_index, plot in enumerate(sub_axes):

                    measure_range_refs = []
                    for item in plot.items:
                        if isinstance(item, pg.LinearRegionItem):
                            if "measure_range" in item.name:
                                measure_range_refs.append(item)

                    for ref in measure_range_refs:
                        plot.removeItem(ref)

                if self.plot_settings.show_measurement_range.isChecked():

                    for plot_index, plot in enumerate(unique_sub_axes):

                        if "measure_dict" in localisation_dict.keys():
                            if measurement_index in localisation_dict["measure_dict"].keys():

                                measure_ranges = localisation_dict["measure_dict"][measurement_index]

                                for range_index, measure_range in enumerate(measure_ranges):

                                    measure_ref = self.initialise_measure_ref(plot_dataset,
                                        plot,localisation_number,measure_range, range_index)

                                    plot.addItem(measure_ref)

        except:
            print(traceback.format_exc())
            pass

    def plot_crop_ranges(self, crop_plots, crop_range, crop_region, crop_regions, plot):

        show_crop_range = self.plot_settings.show_crop_range.isChecked()

        if crop_plots == False and show_crop_range == True and len(crop_range) == 2:
            if crop_region in plot.items:
                crop_region.blockSignals(True)
                crop_region.setRegion(crop_range)
                crop_region.blockSignals(False)
            else:
                plot.addItem(crop_region)
                crop_region.blockSignals(True)
                crop_region.setRegion(crop_range)
                crop_region.blockSignals(False)
        else:
            for crop_region in crop_regions:
                plot.removeItem(crop_region)

    def plot_bleach_correction_ranges(self, localisation_dict, sub_axes, plot_labels,
            donor_bleach_refs, acceptor_bleach_refs):

        try:

            show_bleach = self.plot_settings.show_bleach_range.isChecked()

            if show_bleach == True:

                correction_factors = localisation_dict["correction_factors"]

                donor_bleach_index = correction_factors["donor_bleach_index"]
                acceptor_bleach_index = correction_factors["acceptor_bleach_index"]

                for plot, plot_label in zip(sub_axes, plot_labels):

                    if plot_label in ["Donor","DD"] and donor_bleach_index != None:
                        len_data = len(localisation_dict[plot_label])
                        bleach_range = np.array([donor_bleach_index, len_data-1])

                        for bleach_ref in donor_bleach_refs:
                            if bleach_ref != None:

                                if bleach_ref not in plot.items:
                                    plot.addItem(bleach_ref)

                                bleach_ref.blockSignals(True)
                                bleach_ref.setRegion(bleach_range)
                                bleach_ref.blockSignals(False)

                    elif plot_label in ["Acceptor","DA"] and acceptor_bleach_index != None:

                        len_data = len(localisation_dict[plot_label])
                        bleach_range = np.array([acceptor_bleach_index, len_data-1])

                        for bleach_ref in acceptor_bleach_refs:
                            if bleach_ref != None:

                                if bleach_ref not in plot.items:
                                    plot.addItem(bleach_ref)

                                bleach_ref.blockSignals(True)
                                bleach_ref.setRegion(bleach_range)
                                bleach_ref.blockSignals(False)

                    else:
                        for bleach_ref in donor_bleach_refs:
                            if bleach_ref != None:
                                bleach_ref.blockSignals(True)
                                plot.removeItem(bleach_ref)
                                bleach_ref.blockSignals(False)
                        for bleach_ref in acceptor_bleach_refs:
                            if bleach_ref != None:
                                bleach_ref.blockSignals(True)
                                plot.removeItem(bleach_ref)
                                bleach_ref.blockSignals(False)
            else:
                for plot in sub_axes:
                    for bleach_ref in donor_bleach_refs:
                        if bleach_ref != None:
                            bleach_ref.blockSignals(True)
                            plot.removeItem(bleach_ref)
                            bleach_ref.blockSignals(False)
                    for bleach_ref in acceptor_bleach_refs:
                        if bleach_ref != None:
                            bleach_ref.blockSignals(True)
                            plot.removeItem(bleach_ref)
                            bleach_ref.blockSignals(False)

        except:
            print(traceback.format_exc())
            pass

    def plot_gamma_correction_ranges(self, localisation_dict, sub_axes,
            plot_lines_labels, gamma_refs, gamma_ranges):

        try:
            show_gamma = self.plot_settings.show_gamma_range.isChecked()

            if show_gamma == True:

                for plot_index, (plot_label, plot, [gamma_ref1, gamma_ref2]) in enumerate(zip(plot_lines_labels,
                        sub_axes, gamma_refs)):

                    update_gamma = False

                    if plot_label in ["Donor", "Acceptor", "DD", "DA"] and show_gamma == True:

                        if "gamma_ranges" in localisation_dict.keys():
                            gamma_ranges = localisation_dict["gamma_ranges"]

                            if type(gamma_ranges) == list and len(gamma_ranges) >= 1:
                                if type(gamma_ranges[0]) == list:
                                    update_gamma = True

                    if update_gamma == True:

                        if gamma_ref1 not in plot.items:
                            plot.addItem(gamma_ref1)
                            gamma_ref1.blockSignals(True)
                            gamma_ref1.setRegion(gamma_ranges[0])
                            gamma_ref1.blockSignals(False)
                        else:
                            gamma_ref1.blockSignals(True)
                            gamma_ref1.setRegion(gamma_ranges[0])
                            gamma_ref1.blockSignals(False)

                        if len(gamma_ranges) == 2:

                            if gamma_ref2 not in plot.items:
                                plot.addItem(gamma_ref2)
                                gamma_ref2.blockSignals(True)
                                gamma_ref2.setRegion(gamma_ranges[1])
                                gamma_ref2.blockSignals(False)
                            else:
                                gamma_ref2.blockSignals(True)
                                gamma_ref2.setRegion(gamma_ranges[1])
                                gamma_ref2.blockSignals(False)

                    else:
                        if gamma_ref1 in plot.items:
                            plot.removeItem(gamma_ref1)
                        if gamma_ref2 in plot.items:
                            plot.removeItem(gamma_ref2)

            else:
                for plot, [gamma_ref1, gamma_ref2] in zip(sub_axes, gamma_refs):
                    if gamma_ref1 in plot.items:
                        plot.removeItem(gamma_ref1)
                    if gamma_ref2 in plot.items:
                        plot.removeItem(gamma_ref2)

        except:
            print(traceback.format_exc())
            pass

