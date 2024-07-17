
import numpy as np
import pickle
import traceback
import matplotlib.pyplot as plt

from TraceAnalyser.funcs.gui_HMM_utils import (pg_fit_hmm, hmmlearn_fit_hmm, pg_predict_hmm,
    hmmlearn_predict_hmm, reasign_hmm_states)



def detect_hmm(dataset = [], n_states = 2, n_init = 100, hmm_package = "Pomegranate", hmm_mode="allf", n_iter=10000,
        min_length=2, max_transitions=100):

    if hmm_mode == "all":
        concat_traces = True
    else:
        concat_traces = False

    print("Fitting HMM Model(s)...")

    hmm_models = {}
    
    n_traces = len(dataset)

    for trace_index, fit_data in enumerate(dataset):
        
        if type(fit_data) != list:
            fit_data = np.expand_dims(fit_data, axis=1)
            dataset[trace_index] = fit_data
                
    if concat_traces == False:
        
        for trace_index, fit_data in enumerate(dataset):
            
            if hmm_package == "Pomegranate":
                model = pg_fit_hmm(fit_data, n_states, n_iter, n_init)
            elif hmm_package == "HMM Learn":
                model = hmmlearn_fit_hmm(fit_data, n_states, n_iter, n_init)
    
            hmm_models[trace_index] = model
    else:
    
        if hmm_package == "Pomegranate":
            model = pg_fit_hmm(dataset, n_states)
        elif hmm_package == "HMM Learn":
            
            lengths = [len(trace) for trace in dataset]
            fit_dataset = np.concatenate(dataset, axis=0)
            
            print(len(fit_dataset))
    
            model = hmmlearn_fit_hmm(fit_dataset, n_states, lengths=lengths)

    if model != None:
        for trace_index in np.arange(n_traces).tolist():
            hmm_models[int(trace_index)] = model

    print("Predicting HMM states...")

    combined_predictions = []

    for trace_index, fit_data in enumerate(dataset):
        
        predictions = np.zeros_like(fit_data.shape[0]).tolist()
        
        try:

            model = hmm_models[trace_index]
            
            if model != None:
    
                if hmm_package == "Pomegranate":
                    predictions = pg_predict_hmm(model, fit_data)
                elif hmm_package == "HMM Learn":
                    predictions = hmmlearn_predict_hmm(model, fit_data)
        
                if predictions is not None:
                    if len(predictions) == len(fit_data):
                        # predictions = correct_hmm_predictions(predictions, min_length, max_transitions)
        
                        predictions = reasign_hmm_states(fit_data, predictions)
                        
            if trace_index == 0:
                plt.plot(fit_data)
                plt.plot(predictions)
                plt.show()
                    
        except:
            print(traceback.format_exc())
                    
        combined_predictions.append(predictions)
        
    return combined_predictions




with open('simulatedev.pickle', 'rb') as handle:
    trans_mat, trace_dict, matrics = pickle.load(handle)
    
    
    
traces = []
labels = []

for trace_data in trace_dict:
    
    fit_data = np.array(trace_data["E"])

    traces.append(fit_data)
    labels.append(trace_data["label"])
    
traces = traces[:50]

# plt.plot(traces[0])
# plt.show()
    
hmm_models = detect_hmm(traces)    
    

    
    
    
    
# dataset = traces
    
    
# n_states = 2
# n_init = 10
# hmm_package = "Pomegranate"
# hmm_mode="algl"
# n_iter=1000
# min_length=2
# max_transitions=10


# if hmm_mode.lower() == "all":
#     concat_traces = True
# else:
#     concat_traces = False

# print("Fitting HMM Model(s)...")

# hmm_models = {}


# for trace_index, fit_data in enumerate(dataset):
    
#     if type(fit_data) != list:
#         fit_data = np.expand_dims(fit_data, axis=1)
#         dataset[trace_index] = fit_data
            
# if concat_traces == False:
    
#     for trace_index, fit_data in enumerate(dataset):
        
#         if hmm_package == "Pomegranate":
#             model = pg_fit_hmm(fit_data, n_states, n_iter, n_init)
#         elif hmm_package == "HMM Learn":
#             model = hmmlearn_fit_hmm(fit_data, n_states, n_iter, n_init)

#         hmm_models[trace_index] = model
# else:

#     if hmm_package == "Pomegranate":
#         model = pg_fit_hmm(dataset, n_states)
#     elif hmm_package == "HMM Learn":
#         lengths = [len(trace) for trace in dataset]
#         dataset = np.concatenate(dataset, axis=0)

#         model = hmmlearn_fit_hmm(dataset, n_states, lengths=lengths)

#     if model != None:
#         for trace_index in np.arange(len(dataset)):
#             hmm_models[trace_index] = model
    
    
    
    
    
    
    


