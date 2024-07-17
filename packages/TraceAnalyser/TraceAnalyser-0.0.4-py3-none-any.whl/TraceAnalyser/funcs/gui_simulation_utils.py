import traceback

import numpy as np

from TraceAnalyser.funcs.gui_worker import Worker
from TraceAnalyser.DeepFretSimulate.utils import numstring_to_ls
from TraceAnalyser.DeepFretSimulate.math import generate_traces

class _simulation_utils():


    def update_simulation_options(self):

        simwin = self.simulator_window

        """Refreshes UI to e.g. disable some input boxes"""
        for inputBox, checkBox in ((simwin.inputDonorMeanLifetime, simwin.checkBoxDlifetime),
                                   (simwin.inputAcceptorMeanLifetime, simwin.checkBoxALifetime),
                                   (simwin.inputTransitionProbabilityHi, simwin.checkBoxTransitionProbability,),
                                   (simwin.inputFretStateMeans, simwin.checkBoxRandomState),
                                   (simwin.inputNoiseHi, simwin.checkBoxNoise),
                                   (simwin.inputMismatchHi, simwin.checkBoxMismatch),
                                   (simwin.inputScalerHi, simwin.checkBoxScaler),
                                   (simwin.inputBleedthroughHi, simwin.checkBoxBleedthrough),
                                   ):
            inputBox.setDisabled(checkBox.isChecked())

        simwin.inputMaxRandomStates.setEnabled(simwin.checkBoxRandomState.isChecked())



    def update_simulation_variables(self):

        try:

            simwin = self.simulator_window

            self.sim_n_traces = int(simwin.simulate_n_traces.value())
            self.sim_trace_len = int(simwin.inputTraceLength.value())

            # Scramble probability
            self.sim_scramble_prob = float(simwin.inputScrambleProbability.value())

            # Scramble decouple probability
            self.sim_scramble_decouple_prob = float(simwin.inputScrambleDecoupleProbability.value())

            # Aggregation probability
            self.sim_aggregate_prob = float(simwin.inputAggregateProbability.value())

            # Max aggregate size
            self.sim_max_aggregate_size = int(simwin.inputMaxAggregateSize.value())

            # FRET state means
            if simwin.checkBoxRandomState.isChecked():
                self.sim_fret_means = "random"
            else:
                if hasattr(self, "sim_fret_means"):
                    old_fret_means = self.sim_fret_means
                else:
                    old_fret_means = float(simwin.inputFretStateMeans.text())

                new_fret_means = sorted(numstring_to_ls(simwin.inputFretStateMeans.text()))
                if not new_fret_means:
                    self.sim_fret_means = 0

                if new_fret_means != old_fret_means:
                    self.sim_fret_means = new_fret_means

            # Max number of random states
            self.sim_max_random_states = int(simwin.inputMaxRandomStates.value())

            # Minimum FRET state difference
            self.sim_min_fret_diff = float(simwin.inputMinFretStateDiff.value())

            # Donor mean lifetime
            if simwin.checkBoxDlifetime.isChecked():
                self.sim_donor_lifetime = None
            else:
                self.sim_donor_lifetime = int(simwin.inputDonorMeanLifetime.value())

            # Acceptor mean lifetime
            if simwin.checkBoxALifetime.isChecked():
                self.sim_acceptor_lifetime = None
            else:
                self.sim_acceptor_lifetime = int(simwin.inputAcceptorMeanLifetime.value())

            # Blinking probability
            self.sim_blinking_prob = float(simwin.inputBlinkingProbability.value())

            # Fall-off probability
            self.sim_fall_off_prob = float(simwin.inputFalloffProbability.value())

            # Fall-off lifetime
            self.sim_fall_off_lifetime = int(simwin.inputFalloffMeanLifetime.value())

            # Transition Probability
            if simwin.checkBoxTransitionProbability.isChecked():
                self.sim_transition_prob = float(simwin.inputTransitionProbabilityLo.value())
            else:
                self.sim_transition_prob = (float(simwin.inputTransitionProbabilityLo.value()), float(simwin.inputTransitionProbabilityHi.value()),)

            # Noise
            if simwin.checkBoxNoise.isChecked():
                self.sim_noise = float(simwin.inputNoiseLo.value())
            else:
                self.sim_noise = (float(simwin.inputNoiseLo.value()), float(simwin.inputNoiseHi.value()),)

            # Acceptor-only mismatch
            if simwin.checkBoxMismatch.isChecked():
                self.sim_aa_mismatch = float(simwin.inputMismatchLo.value())
            else:
                self.sim_aa_mismatch = (float(simwin.inputMismatchLo.value()), float(simwin.inputMismatchHi.value()),)

            # Donor Bleedthrough
            if simwin.checkBoxBleedthrough.isChecked():
                self.sim_bleed_through = float(simwin.inputBleedthroughLo.value())
            else:
                self.sim_bleed_through = (float(simwin.inputBleedthroughLo.value()), float(simwin.inputBleedthroughHi.value()),)

            # Scaler
            if simwin.checkBoxScaler.isChecked():
                self.sim_scaling_factor = float(simwin.inputScalerLo.value())
            else:
                self.sim_scaling_factor = (float(simwin.inputScalerLo.value()), float(simwin.inputScalerHi.value()),)

        except:
            print(traceback.format_exc())



    def _simulate_traces_result(self, simulated_traces):

        try:

            if len(simulated_traces) == 0:
                self.print_notification("No traces simulated")
            else:
                n_traces = len(simulated_traces)

                self.print_notification(f"Simulated {int(n_traces)} simulated traces")

                self.data_dict["Simulated Traces"] = simulated_traces

                self.populate_bleach_dicts()
                self.populate_correction_factors()

                self.compute_efficiencies()
                self.compute_state_means()

                self.populate_combos()

                self.plot_localisation_number.setValue(0)

                self.initialise_plot()

        except:
            print(traceback.format_exc())

    def _simulate_traces(self, progress_callback):

        try:
            """Generate traces to show in the GUI (examples) or for export"""
            n_traces = self.sim_n_traces


            df = generate_traces(
                n_traces=n_traces,
                aa_mismatch=self.sim_aa_mismatch,
                state_means=self.sim_fret_means,
                min_state_diff=self.sim_min_fret_diff,
                random_k_states_max=self.sim_max_random_states,
                max_aggregate_size=self.sim_max_aggregate_size,
                aggregation_prob=self.sim_aggregate_prob,
                scramble_prob=self.sim_scramble_prob,
                scramble_decouple_prob=self.sim_scramble_decouple_prob,
                trace_length=self.sim_trace_len,
                trans_prob=self.sim_transition_prob,
                blink_prob=self.sim_blinking_prob,
                bleed_through=self.sim_bleed_through,
                noise=self.sim_noise,
                D_lifetime=self.sim_donor_lifetime,
                A_lifetime=self.sim_acceptor_lifetime,
                au_scaling_factor=self.sim_scaling_factor,
                falloff_prob=self.sim_fall_off_prob,
                falloff_lifetime=self.sim_fall_off_lifetime,
                discard_unbleached=False,
                # progressbar_callback=progress_callback,
                # callback_every=update_every_nth,
                return_matrix=False,
                reduce_memory=False,
                run_headless_parallel=False,
                merge_state_labels=True,
            )

            df.columns = ['DD', 'DA', 'AA', 'DD-bg', 'DA-bg', 'AA-bg',
                          'E', 'E_true', 'S', 'frame', 'name', 'label',
                          '_bleaches_at', '_noise_level', '_min_state_diff', '_max_n_classes']

            df.drop(columns=['DD-bg', 'DA-bg', 'AA-bg',
                             'E',
                             'S', 'frame',
                             '_bleaches_at',
                             '_noise_level',
                             '_min_state_diff',
                             '_max_n_classes'],
                inplace=True)


            n_traces  = df.name.nunique()

            if n_traces > 0:

                simulated_traces = []
                unique_states = []

                for name, data in df.groupby("name"):

                    data.drop(columns=["name"], inplace=True)

                    for key,value in data.items():
                        data[key] = np.array(value.tolist())

                    loc_data = data.to_dict(orient="list")
                    loc_data["state_means"] = {}
                    loc_data["user_label"] = 0
                    loc_data["break_points"] = []
                    loc_data["gamma_ranges"] = []
                    loc_data["AD"] = np.array([])
                    loc_data["states"] = []
                    loc_data["bleach_dict"] = {}
                    loc_data["correction_factors"] = {}
                    loc_data["crop_range"] = []
                    loc_data["filter"] = False
                    loc_data["import_path"] = "DeepFRET-simulated"

                    simulated_traces.append(loc_data)

                    E_true = loc_data["E_true"]

                    unique_states.extend(np.unique(E_true).tolist())

                unique_states = np.unique(unique_states).tolist()
                unique_states = sorted(unique_states)

                for name, data in df.groupby("name"):

                    E_true = data.to_dict(orient="list")["E_true"]

                    states = np.array(E_true)

                    for state in unique_states:
                        state_index = unique_states.index(state)

                        states[states == state] = state_index

                    simulated_traces[int(name)]["states"] = states

        except:
            print(traceback.format_exc())
            pass

        return simulated_traces



    def initialise_simulation(self):

        self.update_simulation_variables()
        self.update_simulation_options()

        worker = Worker(self._simulate_traces)
        worker.signals.result.connect(self._simulate_traces_result)
        self.threadpool.start(worker)


