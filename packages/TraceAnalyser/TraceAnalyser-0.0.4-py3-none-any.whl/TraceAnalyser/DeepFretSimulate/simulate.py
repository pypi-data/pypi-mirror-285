import numpy as np
from time import time
import os
import shutil

from TraceAnalyser.DeepFretSimulate.math import generate_traces





class trace_generator():
    
    def __init__(self,
                 n_traces = 100,
                 n_frames = 500,
                 n_colors = 2,
                 n_states = 2,
                 min_state_diff = 0.1,
                 state_means = "random",
                 trans_mat = None,
                 outdir = "",
                 export_mode = "",
                 export_name = "",
                 ):
        
        self.n_traces = n_traces
        self.n_frames = n_frames
        self.n_colors = n_colors
        self.n_states = n_states
        self.outdir = outdir
        self.export_mode = export_mode
        self.export_name = export_name
        self.min_state_diff = min_state_diff
        self.state_means = state_means
        self.trans_mat = trans_mat
        
        self.check_outdir()

        assert n_colors in [1,2], "available colours: 1, 2"
        assert export_mode in ["","text_files", "pickledict","ebfret", "ebFRET_files"], "available export modes: '','text_files', 'pickledict', 'ebfret', 'ebFRET_files'"
        
    def check_outdir(self, overwrite=True, folder_name = "simulated_traces"):
    
        if os.path.exists(self.outdir) == False:
            self.outdir = os.getcwd()
        
        if folder_name != "":
            self.outdir = os.path.join(self.outdir, "deepgapseq_simulated_traces")
            
        if overwrite and os.path.exists(self.outdir):
                shutil.rmtree(self.outdir)

        if os.path.exists(self.outdir) == False:
            os.mkdir(self.outdir)


    def simulate_traces(self):
        
        print("Generating traces...")
        start = time()
        
        df, matrices = generate_traces(
                    n_traces=self.n_traces,
                    trace_length=self.n_frames,
                    state_means=self.state_means,
                    min_state_diff= self.min_state_diff,
                    random_k_states_max=self.n_states,
                    trans_mat = self.trans_mat,
                    D_lifetime = None,
                    A_lifetime = None,
                    discard_unbleached=False,
                    return_matrix=True,
                    reduce_memory=False,
                    run_headless_parallel=False,
                    merge_labels=True,
                    merge_state_labels=False,
        )
        
        stop = time()
        duration = stop - start
        
        len_traces = len(df.name.unique())
        
        print(f"Spent {duration:.1f} s to generate {len_traces} traces")
        
        print(np.unique(df.label))
        
        df.columns = ['DD', 'DA', 'AA', 'DD-bg', 'DA-bg',
               'AA-bg', 'E', 'E_true', 'S', 'frame', 'name', 'label',
               '_bleaches_at', '_noise_level', '_min_state_diff', '_max_n_classes']
        
        trace_dict = []
        
        for name, data in df.groupby("name"):
            
            trace_dict.append(data.to_dict(orient="list"))
            
        return trace_dict, matrices
            
            

        
def compute_transition_matrix(trace_data, trace_states, ignore_states = []):
    

    unique_states = np.unique([state for trace in trace_states for state in trace]).tolist()
    
    if len(ignore_states) > 0:
        unique_states = [state for state in unique_states if state not in ignore_states]
    
    unique_states = sorted(unique_states)
    num_states = len(unique_states)

    # Initialize transition matrix
    transition_matrix = np.zeros((num_states, num_states))
    
    # Fill the matrix with counts
    for trace in trace_states:
        for i in range(len(trace) - 1):
            current_state = int(trace[i])
            next_state = int(trace[i + 1])
            transition_matrix[current_state - 1][next_state - 1] += 1
    
    # Normalize the matrix
    for i in range(num_states):
        row_sum = np.sum(transition_matrix[i])
        if row_sum > 0:
            transition_matrix[i] /= row_sum

    return transition_matrix

def create_random_transition_matrix(n):
    
    transition_matrix = np.zeros((n, n))

    for i in range(n):
        # Generate n random numbers
        row = np.random.rand(n)
        
        # Normalize to make the sum 1
        transition_matrix[i] = row / row.sum()

    return transition_matrix
        







# trans_mat = create_random_transition_matrix(2)
#
#
# generator = trace_generator(n_colors=2,
#                             n_states=2,
#                             n_frames=200,
#                             n_traces=100,
#                             state_means=[0.3,0.8],
#                             # trans_mat=trans_mat,
#                             # min_state_diff=0.2,
#                             )
#
#
# trace_dict, matrics = generator.simulate_traces()
#
#




# with open('simulatedev.pickle', 'wb') as handle:
#     pickle.dump([trans_mat,trace_dict, matrics], handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('simulatedev.pickle', 'rb') as handle:
#     trans_mat, trace_dict, matrics = pickle.load(handle)

# data = trace_dict[8]


# plt.plot(data["E"])
# plt.plot(data["label"])
# plt.show()











# trace_data = [dat["E"] for dat in trace_dict]
# trace_states = [dat["E_true"] for dat in trace_dict]
#
# filtered_trace_data = []
# filtered_trace_states = []
#
# for trace_index, (E_true, trace) in enumerate(zip(trace_states,trace_data)):
#
#     E_true = np.array(E_true)
#     trace = np.array(trace)
#
#     unique_E_states = np.unique(E_true)
#     unique_E_states = sorted(unique_E_states)
#
#     if len(unique_E_states) == 1:
#         if unique_E_states[0] == -1:
#             E_true = np.zeros_like(trace).astype(int)
#         else:
#             E_true = np.zeros_like(trace).astype(int)
#     else:
#         for state_index, E_state in enumerate(unique_E_states):
#
#             E_true[E_true==E_state] = state_index
#
#         crop_indices = np.argwhere(E_true != 0)
#         crop_indices = [np.min(crop_indices), np.max(crop_indices)]
#
#         E_true = E_true[crop_indices[0]:crop_indices[-1]]
#         trace = trace[crop_indices[0]:crop_indices[-1]]
#
#         filtered_trace_data.append(trace)
#         filtered_trace_states.append(E_true)
#
#     trace_data[trace_index] = trace
#     trace_states[trace_index] = E_true
#
#
#
# def plot_efficiency_histogram(trace_data, trace_states):
#
#     combined_traces = np.concatenate(trace_data)
#     combined_states = np.concatenate(trace_states).astype(int)
#
#     for state in np.unique(combined_states):
#
#         plot_label = f"State {state}"
#
#         state_efficiencies = combined_traces[combined_states == state]
#
#         plt.hist(state_efficiencies, bins=20, alpha=0.7,label=str(state), density=True)
#         plt.legend()
#
#         plt.xlabel('FRET Efficiency')
#         plt.ylabel('Frequency')
#
#
# plot_efficiency_histogram(filtered_trace_data, filtered_trace_states)
# trans_mat_eval = compute_transition_matrix(filtered_trace_data, filtered_trace_states)
#
#
#
#
#
#
#
#







