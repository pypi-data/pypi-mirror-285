import traceback
from functools import partial
from TraceAnalyser.funcs.gui_worker import Worker
import numpy as np
import math

class _correction_utils:

    def populate_correction_combos(self):

            try:
                self.update_dataset_selection("correction_window",
                    "correction_dataset")
            except:
                print(traceback.format_exc())
                pass


    def correction_factor_detection_finished(self):

        try:

            self.correction_window.correction_progressbar.setValue(0)
            self.print_notification("Correction factor detection finished")
            self.plot_traces(update_plot=False)

        except:
            print(traceback.format_exc())
            pass


    def detect_fret_correction_factors(self, localisation_data):

        gamma = None
        gamma_ranges = []

        try:

            global_gamma = self.correction_window.global_gamma.value()
            use_global_factors = self.correction_window.use_global_factors.isChecked()
            spacer = self.correction_window.bleaching_spacer.value()
            min_frames = self.correction_window.correction_min_frames.value()
            default_frames = self.correction_window.gamma_default_frames.value()

            donor = np.array(localisation_data["Donor"]).copy()
            acceptor = np.array(localisation_data["Acceptor"]).copy()

            correction_factors = localisation_data["correction_factors"]

            gamma_ranges = self.compute_gamma_ranges(correction_factors, len(donor),
                spacer, min_frames, default_frames)

            gamma = self.compute_gamma(donor, acceptor, gamma_ranges)

            if use_global_factors == True:
                if gamma == None:
                    gamma = global_gamma

        except:
            print(traceback.format_exc())
            pass

        return gamma, gamma_ranges



    def compute_gamma_ranges(self, correction_factors, len_data, spacer,
            min_frames, default_frames):

        range1 = None
        range2 = None

        try:

            acceptor_bleach_index = correction_factors["acceptor_bleach_index"]

            if acceptor_bleach_index != None:

                if acceptor_bleach_index - spacer - min_frames >= 0 and acceptor_bleach_index + spacer + min_frames < len_data:

                    if acceptor_bleach_index - spacer - default_frames >= 0:
                        range1_start = acceptor_bleach_index - spacer - default_frames
                    elif acceptor_bleach_index - spacer - min_frames >= 0:
                        range1_start = 0
                    else:
                        range1_start = None

                    range1_end = acceptor_bleach_index - spacer
                    range2_start = acceptor_bleach_index + spacer

                    if acceptor_bleach_index + spacer + default_frames < len_data:
                        range2_end = acceptor_bleach_index + spacer + default_frames
                    elif acceptor_bleach_index + spacer + min_frames < len_data:
                        range2_end = len_data
                    else:
                        range2_end = None

                    range1 = [range1_start, range1_end]
                    range2 = [range2_start, range2_end]

                    if None in range1 or None in range2:
                        range1 = None
                        range2 = None

        except:
            print(traceback.format_exc())
            pass



        return [range1, range2]

    def compute_direct_acceptor(self, DA, AA, correction_factors, min_frames = 1):

        """
        The a_direct correction factor accounts for the direct excitation of the acceptor
        at the donor wavelength (DA), (irrespective of FRET).

        a_t and aa_t are the acceptor intensities upon donor excitation (DA) and direct acceptor excitation (AA)
        respectively, in the time interval after the donor has bleached and before the acceptor has bleached.

         """

        a_direct = None

        try:

            donor_bleach_index = int(correction_factors["donor_bleach_index"])
            acceptor_bleach_index = int(correction_factors["acceptor_bleach_index"])

            # Check if the donor bleaches before the acceptor
            if donor_bleach_index < acceptor_bleach_index:

                    # check if the number of frames between the acceptor and donor bleaching is greater than the minimum
                    bleach_interval = acceptor_bleach_index - donor_bleach_index

                    if bleach_interval >= min_frames:

                        DA = np.array(DA).copy()
                        AA = np.array(AA).copy()

                        # Calculate the a_t and aa_t values
                        a_t = DA[donor_bleach_index:acceptor_bleach_index]
                        aa_t = AA[donor_bleach_index:acceptor_bleach_index]

                        a_direct = np.mean(a_t / aa_t)

                        a_direct = float(a_direct)

                        if math.isinf(a_direct):
                            a_direct = None
                        if math.isnan(a_direct):
                            a_direct = None

        except:
            a_direct = None

        return a_direct

    def compute_donor_leakage(self, DD, DA, correction_factors, min_frames = 1):

        """The Dleakage correction factor accounts for the amount of leakage of the donor emission (DD)
        into the acceptor (DA) emission channel upon donor excitation

        where a_t and d_t are the measured signal in the acceptor (DA) and donor (DD) emission channels, respectively,
        upon donor excitation in the time interval after the acceptor has bleached and before the donor has
        bleached, corresponding to a donor-only signal.

        """

        d_leakage = None

        try:

            donor_bleach_index = int(correction_factors["donor_bleach_index"])
            acceptor_bleach_index = int(correction_factors["acceptor_bleach_index"])

            # Check if the acceptor bleaches before the donor
            if acceptor_bleach_index < donor_bleach_index:

                # Check if the number of frames between the acceptor and donor bleaching is greater than the minimum
                bleach_interval = donor_bleach_index - acceptor_bleach_index
                if bleach_interval > min_frames:

                    # Calculate the a_t and d_t values
                    a_t = DA[acceptor_bleach_index:donor_bleach_index]
                    d_t = DD[acceptor_bleach_index:donor_bleach_index]

                    d_leakage = np.mean(a_t / d_t)

                    d_leakage = float(d_leakage)

                    # Check for invalid values
                    if math.isinf(d_leakage):
                        d_leakage = None
                    if math.isnan(d_leakage):
                        d_leakage = None
        except:
            pass

        return d_leakage

    def compute_gamma(self, DD, DA, gamma_ranges):

        """The γ correction factor accounts for the relative difference in the number of photons measured of the
           acceptor (DA) and the donor (DD) for the same number of excited states.

           A1, A2, D1 and D2 are the average acceptor (DA) and donor (DD) fluorescence intensities, upon donor excitation,
           before and after the acceptor (DA) has bleached.

           """

        gamma = None

        try:

            DA = np.array(DA).copy()
            DD = np.array(DD).copy()

            r1 = gamma_ranges[0]
            r2 = gamma_ranges[1]

            A1 = np.mean(DA[int(r1[0]):int(r1[1])])
            A2 = np.mean(DA[int(r2[0]):int(r2[1])])

            D1 = np.mean(DD[int(r1[0]):int(r1[1])])
            D2 = np.mean(DD[int(r2[0]):int(r2[1])])

            gamma = (A1 - A2) / (D2 - D1)
            gamma = float(gamma)

            if math.isinf(gamma):
                gamma = None
            if math.isnan(gamma):
                gamma = None

        except:
            pass

        return gamma

    def detect_alex_correction_factors(self, localisation_data):

        a_direct = None
        d_leakage = None
        gamma = None
        gamma_ranges = []


        try:

            global_donor_leakage = self.correction_window.global_donor_leakage.value()
            global_direct_excitation = self.correction_window.global_direct_excitation.value()
            global_gamma = self.correction_window.global_gamma.value()
            use_global_factors = self.correction_window.use_global_factors.isChecked()
            spacer = self.correction_window.bleaching_spacer.value()
            min_frames = self.correction_window.correction_min_frames.value()
            default_frames = self.correction_window.gamma_default_frames.value()

            DD = np.array(localisation_data["DD"]).copy()
            DA = np.array(localisation_data["DA"]).copy()
            AA = np.array(localisation_data["AA"]).copy()

            correction_factors = localisation_data["correction_factors"]

            gamma_ranges = self.compute_gamma_ranges(correction_factors, len(DA),
                spacer, min_frames, default_frames)

            a_direct = self.compute_direct_acceptor(DA, AA, correction_factors)
            d_leakage = self.compute_donor_leakage(DD, DA, correction_factors, min_frames)

            gamma = self.compute_gamma(DD, DA, gamma_ranges)

            if use_global_factors == True:
                if a_direct == None:
                    a_direct = float(global_direct_excitation)
                if d_leakage == None:
                    d_leakage = float(global_donor_leakage)
                if gamma == None:
                    gamma = float(global_gamma)

        except:
            print(traceback.format_exc())
            pass

        return a_direct, d_leakage, gamma, gamma_ranges

    def correction_factor_detection(self, progress_callback=None):

        dataset_name = self.correction_window.correction_dataset.currentText()

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

                if self.get_filter_status("correction", user_label) == False:

                    channel_list = list(localisation_data.keys())

                    if set(["Donor","Acceptor"]).issubset(channel_list):

                        factors = self.detect_fret_correction_factors(localisation_data)
                        gamma, gamma_ranges = factors

                        correction_factors["gamma"] = gamma

                        localisation_data["gamma_ranges"] = gamma_ranges

                    if set(["DD","DA","AA"]).issubset(channel_list):

                        factors = self.detect_alex_correction_factors(localisation_data)
                        a_direct, d_leakage, gamma, gamma_ranges = factors

                        correction_factors["a_direct"] = a_direct
                        correction_factors["d_leakage"] = d_leakage
                        correction_factors["gamma"] = gamma

                        localisation_data["gamma_ranges"] = gamma_ranges

    def initialise_correction_factor_detection(self):

        try:

            if self.data_dict != {}:

                worker = Worker(self.correction_factor_detection)
                worker.signals.finished.connect(self.correction_factor_detection_finished)
                worker.signals.progress.connect(partial(self.gui_progrssbar,name="correction"))
                self.threadpool.start(worker)

        except:
            print(traceback.format_exc())
            pass


    def apply_global_correction_factors(self, mode="active", update_efficiencies=True):

        try:

            d_leakage = float(self.correction_window.global_donor_leakage.value())
            a_direct = float(self.correction_window.global_direct_excitation.value())
            gamma = float(self.correction_window.global_gamma.value())

            if self.data_dict != {}:

                for dataset_name, dataset_data in self.data_dict.items():

                    if mode == "active":
                        slider_value = self.plot_localisation_number.value()
                        localisation_number = self.localisation_numbers[slider_value]
                        localisation_list = [localisation_number]
                    else:
                        localisation_list = range(len(dataset_data))

                    for localisation_number in localisation_list:

                        localisation_data = dataset_data[localisation_number]

                        if "correction_factors" not in localisation_data.keys():
                            localisation_data["correction_factors"] = {}

                        correction_factors = localisation_data["correction_factors"]

                        correction_factors["a_direct"] = a_direct
                        correction_factors["d_leakage"] = d_leakage
                        correction_factors["gamma"] = gamma

                        if set(["Donor", "Acceptor"]).issubset(localisation_data):

                            donor = np.array(localisation_data["Donor"]).copy()
                            acceptor = np.array(localisation_data["Acceptor"]).copy()

                            if update_efficiencies:

                                fret_efficiency, corrected = self.compute_fret_efficiency(donor, acceptor, correction_factors)

                                localisation_data["FRET Efficiency"] = fret_efficiency
                                localisation_data["FRET Efficiency Corrected"] = corrected

                        if set(["DD", "DA", "AA"]).issubset(localisation_data):

                            DD = np.array(localisation_data["DD"]).copy()
                            DA = np.array(localisation_data["DA"]).copy()
                            AA = np.array(localisation_data["AA"]).copy()

                            alex_efficiency, stoichiometry, corrected = self.compute_alex_efficiency(DD, DA, AA, correction_factors)

                            localisation_data["ALEX Efficiency"] = alex_efficiency
                            localisation_data["ALEX Efficiency Corrected"] = corrected
                            localisation_data["ALEX Stoichiometry"] = stoichiometry

            self.plot_traces(update_plot=False)

        except:
            print(traceback.format_exc())
            pass

