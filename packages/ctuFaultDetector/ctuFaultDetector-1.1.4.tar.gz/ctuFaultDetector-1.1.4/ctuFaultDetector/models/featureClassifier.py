from tslearn.barycenters import euclidean_barycenter, dtw_barycenter_averaging
from tslearn.utils import to_time_series_dataset
from scipy.stats import chi2
import numpy as np
import pandas as pd
import pickle
import time
from datetime import datetime
from ctuFaultDetector.metrics.dtw_barycenter import compute_dtw_dists, get_distance
from ctuFaultDetector.visual import plot_samples, plot_one_6dim_signal
from ctuFaultDetector.support.my_k_means import classify_kmeans, get_cluster_params, GaussianClassifier
from ctuFaultDetector.utils import transform_pd_to_npy, set_signals_to_same_length


class featureClassifier():
    """
    Model that represents the distance-based feature classifier method.
    """
    def __init__(self, n_clusters = None, method = [1,5]) -> None:
        """
        Constructor of the method
        Args:
            n_clusters : None | int - number of clusters (should k-means algorithm be applied)
            method : list[int] - method of computing the features (see ctuFaultDetector.metrics.dtw_barycenter.method.get_distance function)
        Returns:
            None
        """
        self.barycenter_dtw = None
        self.barycenter_euclid = None
        self.classifier = None
        self.n_clusters = n_clusters
        self.method = method
        self.dtw_error = None
        self.euclid_error = None
        self.learn_from_signal = False
        self.magnitude = 0
        self.error_magnitude = 0
        self.c_samples = []
        self.w_samples = []
        self.update_barycenters = False
        self.human_mode = False
        self.confidence_interval_update = 10
        self.true_thresh = 0

    def freeze(self):
        """
        Disables continual learning (freezes the model)
        Args:
            None
        Returns:
            None
        """
        self.learn_from_signal = False
        self.update_barycenters = False
        print("INFO: Learning is freezed.")
    
    def unfreeze(self, bar_update = False):
        """
        Enables continual learning.
        Args:
            bar_update : bool - enable also barycenter update
        Returns:
            None
        """
        self.learn_from_signal = True
        if bar_update:
            self.update_barycenters = True
        print("INFO: Learning is unfreezed.")
    
    def enable_human_mode(self):
        """
        Enable console human labeling of the outcome when using continual learning
        Args:
            None
        Returns:
            None
        """
        self.human_mode = True
        print("INFO: Human mode enabled!")

    def disable_human_mode(self):
        """
        Disable human labeling of the outcome when using continual learning
        Args:
            None
        Returns:
            None
        """
        self.human_mode = False
        print("INFO: Human mode disabled!")
    
    def set_true_thresh(self, value):
        """
        Manualy adjust the value of signals to be defaultly labeled as true (practical thing since very short signals may be distorted)
        Args:
            value : int - a threshold for a length of the signal any signals shorter will during the online evaluation predicted as non-anomalous
        Returns:
            None
        """
        self.true_thresh = value
        print(f"The True threshold set to {self.true_thresh}")

    def offline_fit(self, training_signals, n_clusters = 1, method = [1, 5], vis = False, objective = "TPR", value = 0.95):
        """
        Default training method for supervised training the classifier to classify whole signals
        Args:
            training_signals : [(np.ndarray, bool)] - list of tuples in the form (signal, label) - training dataset for the model
            n_clusters : int - default number of k for k-means
            method : list[int] - method of computing the features (see ctuFaultDetector.metrics.dtw_barycenter.method.get_distance function)
            vis : bool - enable visualisation (matplotlib plots) of the training process (show feature vectors)
            objective : str from ["TPR", "TNR", "ACC", "sACC"] - criterion for the anomaly threshold to be optimised on the training dataset
            value : float|None - value of the selected criterion may be None for ACC or sACC
        """
        self.method = method
        correct_signals_np_array = [transform_pd_to_npy(sample[0]) for sample in training_signals if sample[1] == False]
        wrong_signals_np_array = [transform_pd_to_npy(sample[0]) for sample in training_signals if sample[1] == True]
        training_set = to_time_series_dataset(correct_signals_np_array)
        self.barycenter_dtw = [dtw_barycenter_averaging(training_set)]
        self.barycenter_euclid = [euclidean_barycenter(training_set)]
        self.n_clusters = n_clusters
        self.method = method
        self.magnitude = len(correct_signals_np_array)
        c, w, b, eb = compute_dtw_dists(correct_signals_np_array,
                                        wrong_signals_np_array,
                                        self.barycenter_dtw,
                                        self.barycenter_euclid,
                                        method = method)
        if vis:
            correct_signals_indices = [i for i in range(len(training_signals)) if training_signals[i][1] == False]
            anom_signals_indices = [i for i in range(len(training_signals)) if training_signals[i][1] == True]
            plot_samples(c, w, b, eb, method)
        self.c_samples = c
        self.w_samples = w
        data_to_fit = np.array(c)
        centroids, clusters = classify_kmeans(data_to_fit, n_clusters)
        cluster_params = get_cluster_params(centroids, data_to_fit, clusters)
        self.classifier = GaussianClassifier(cluster_params)
        self.classifier.set_confidence_interval(c, w, metric = objective, value = value)

    def online_fit(self, training_signals, train_size = 20):
        """
        Default training method for training the classifier to classify partial signals. The training_signals set should be whole signals.
        Args:
            training_signals : [(np.ndarray, bool)] - list of tuples in the form (signal, label) - training dataset for the model
            train_size : int - number of training signals to train on
        """
         
        if self.barycenter_dtw is None or self.barycenter_euclid is None:
            print("WARN: Classifier is not trained!")
            return
        correct_signals_np_array = [transform_pd_to_npy(sample[0]) for sample in training_signals if sample[1] == False]
        selected = np.random.choice(np.arange(len(correct_signals_np_array)), min(len(correct_signals_np_array), train_size))
        selected_sigs = [sig for i, sig in enumerate(correct_signals_np_array) if i in selected]
        
        self.error_magnitude = len(selected_sigs)
        training_set = to_time_series_dataset(selected_sigs)
        n_sig, sig_len, n_dim = np.shape(training_set)
        errors_dtw, errors_euclid = [], []
        for i, sig in enumerate(selected_sigs):
            print(f"Computing signal {i+1} out of {len(selected_sigs)}")
            cur_ts_dtw = np.zeros(sig_len)
            cur_ts_euclid = np.zeros(sig_len)
            for endtime in range(1, sig_len):
                (cur_ts_dtw[endtime], cur_ts_euclid[endtime]), _ = self.return_distance_to_closest(sig[:endtime, :], partial=True)
            errors_dtw.append(cur_ts_dtw)
            errors_euclid.append(cur_ts_euclid)
        print("Done computing")
        dtw_err_ = to_time_series_dataset([i/max(i) for i in errors_dtw])
        euclid_err_ = to_time_series_dataset([i/max(i) for i in errors_euclid])
        self.dtw_error = euclidean_barycenter(dtw_err_)
        self.euclid_error = euclidean_barycenter(euclid_err_)

    def unsupervised_fit(self, training_signals, method=[1,5], vis=False, objective = "ACC", value = 0.95, n_clusters = 1, success_ratio = 0.9):
        """
        Default training method for unsupervised training the classifier to classify whole signals
        Args:
            training_signals : [(np.ndarray, bool)] - list of tuples in the form (signal, label) - training dataset for the model
            method : list[int] - method of computing the features (see ctuFaultDetector.metrics.dtw_barycenter.method.get_distance function)
            vis : bool - enable visualisation (matplotlib plots) of the training process (show feature vectors)
            objective : str from ["TPR", "TNR", "ACC", "sACC"] - criterion for the anomaly threshold to be optimised on the training dataset
            value : float|None - value of the selected criterion may be None for ACC or sACC
            n_clusters : int - default number of k for k-means
            success_ratio : float from [0,1] interval - ratio of the successfuly executed signals in the training dataset estimation
        Returns:
            new_training_set : [(np.ndarray, bool)] - list of tuples in the form (signal, label) - training dataset labeled by the classifier.
        """
        self.method = method
        signals = [transform_pd_to_npy(sample[0]) for sample in training_signals]
        training_set = to_time_series_dataset(signals)
        self.barycenter_dtw = [dtw_barycenter_averaging(training_set)]
        self.barycenter_euclid = [euclidean_barycenter(training_set)]
        self.n_clusters = n_clusters
        self.method = method
        print("INFO: Barycenters computed. (1/4)")
        c, _, _, _ = compute_dtw_dists(signals,
                                        [],
                                        self.barycenter_dtw,
                                        self.barycenter_euclid,
                                        method = method)
        print("INFO: Feature vectors computed. (2/4)")
        distances = [np.sum(np.array(i)**2) for i in c]
        point_dist_indices = np.argsort(distances)
        anom_breakpoint_index = int(success_ratio*len(c))
        successfull_processes_indices = point_dist_indices[:anom_breakpoint_index]
        print("INFO: Anomalous feature vectors removed. (3/4)")
        new_training_set = [(process, False) if i in successfull_processes_indices else (process, True) for i, process in enumerate(signals)]
        self.offline_fit(new_training_set, self.n_clusters, self.method, vis, objective, value)
        print("INFO: Classifier is trained. (4/4)")
        return new_training_set
    
    def unsupervised_online_fit(self, training_signals, online_train_ratio, success_ratio):
        """
        Default training method for unsupervised training the classifier to classify paritial signals
        Args:
            training_signals : [(np.ndarray, bool)] - list of tuples in the form (signal, label) - training dataset for the model
            online_train_ratio : int - ratio of non-anomalous training signals from the training dataset to train on
            success_ratio : float from [0,1] interval - ratio of the successfuly executed signals in the training dataset estimation
        Returns:
            None
        """
        new_training_set = self.unsupervised_fit(training_signals, success_ratio=success_ratio)
        correct_signals = [sig for sig in new_training_set if sig[1] == False]
        number_of_signals_to_train_on = int(online_train_ratio*len(correct_signals))
        self.online_fit(correct_signals[:number_of_signals_to_train_on])
    
    def retrain_classifier(self, metric = "ACC", value = 0.95, n_steps = 100, confidence_intervals = [0.8, 1], report_result = True):
        """
        Changes the objective (criterion of the classifier) without computing new barycenters.
        Args:
            metric : str from ["TPR", "TNR", "ACC", "sACC"] - criterion for the anomaly threshold to be optimised on the training dataset
            value : float|None - value of the selected criterion may be None for ACC or sACC
            n_steps : int - number of steps in the search of confidence interval
        Returns:
            None
        """
        print(self.c_samples)
        self.classifier.set_confidence_interval(self.c_samples, self.w_samples, metric = metric, value = value, n_steps=n_steps, report_result = report_result, confidence_intervals=confidence_intervals)
        #self.show_samples()
    
    def __repr__(self) -> str:
        return f"""
        Feature Classifier:
            Number of clusters: {self.n_clusters}
            Confidence treshhold: {None if self.classifier is None else self.classifier.confidence_threshold}
            Number of dtw barycenters: {len(self.barycenter_dtw)}
            Number of euclidean barycenters: {len(self.barycenter_euclid)}
            """

    def return_distance_to_closest(self, signal, partial = False, return_args = False):
        """
        Returns distance to the closest barycenter (outputs the feature vector)
        Args:
            signal : np.ndarray - signal to be examined
            partial : bool - True if the signal is partial else False
        Returns:
            dist : list[int] - smallest feature vector
            args : list[int] - argmin of the feature vector
        """
        if not partial:
            min_len = min([np.shape(i)[0] for i in self.barycenter_euclid])
            signal = signal[:min_len, :]
            dist = np.array([min([get_distance(signal, i, self.method[0]) for i in self.barycenter_dtw]),
                    min([get_distance(signal, i[:min_len, :], self.method[1]) for i in self.barycenter_euclid])])
            args = np.array([np.argmin([get_distance(signal, i, self.method[0]) for i in self.barycenter_dtw]),
                    np.argmin([get_distance(signal, i[:min_len, :], self.method[1]) for i in self.barycenter_euclid])])
        else:
            signal_len = np.shape(signal)[0]
            dist = np.array([min([get_distance(signal, i[:min(signal_len, np.shape(i)[0]), :], self.method[0]) for i in self.barycenter_dtw]),
                    min([get_distance(signal, i[:min(signal_len, np.shape(i)[0]), :], self.method[1]) for i in self.barycenter_euclid])])
            args = np.array([np.argmin([get_distance(signal, i[:min(signal_len, np.shape(i)[0]), :], self.method[0]) for i in self.barycenter_dtw]),
                    np.argmin([get_distance(signal, i[:min(signal_len, np.shape(i)[0]), :], self.method[1]) for i in self.barycenter_euclid])])
        return dist, args
    
    def show_barycenters_dtw(self):
        """
        Plots all the barycenter model parameters of the trained model
        Args:
            None
        Returns:
            None
        """
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(6, 1, figsize=(6.5, 5), sharex=True)
        xaxis = np.arange(1013)
        bars = [*self.barycenter_dtw, *self.barycenter_euclid]
        for bar in bars:
            for i in range(0, 6):
                ax[i].plot(xaxis, bar[:, i], linewidth = 1)
                if i < 5:
                    ax[i].set_xticklabels([])
        ax[5].set_xlabel("Time")
        plt.show()

    def show_samples(self):
        """
        Show the current feature vectors in memory of the classifier
        Args:
            None
        Returns:
            None
        """
        plot_samples(self.c_samples, self.w_samples, self.barycenter_dtw, self.barycenter_euclid)#, correct_idx=[i for i in range(len(self.c_samples))], anom_idx=[i for i in range(len(self.w_samples))])
    
    def predict_partial_signal(self, signal_, time_coef = 1):
        """
        Predicts partial signal using the data-stream trained model
        Args:
            signal_ : np.ndarray - signal part, or whole signal
            time_coef : float - a multiplier of the method to make the prediction either more benevolent or more strict.
        Returns:
            is_anomaly : bool - True if the signal is anomalous else False
        """
        signal = transform_pd_to_npy(signal_)
        if self.classifier is not None:
            signal_len = np.shape(signal)[0]
            if signal_len < self.true_thresh:
                return False
            compensation_coefficients = np.array([self.dtw_error[min(signal_len, len(self.dtw_error)-1)], self.euclid_error[min(signal_len, len(self.euclid_error)-1)]])
            signal_metrics, barycenter_args = self.return_distance_to_closest(signal, partial = True)
            signal_metrics =  signal_metrics * (1/compensation_coefficients).T * time_coef
            is_anomaly = not self.classifier.classify(signal_metrics)
            return is_anomaly
        else:
            print("ERROR: Cannot predict, classifier is not trained yet!")

    def predict(self, signal, vis = False, objective = "TPR", value = 0.95):
        """
        Predicts a full signal
        Args:
            signal : np.ndarray - signal to be predicted
            vis : bool - show visualisation of the prediction
            objective : str - criterion to optimise from if continual learning is applied
            value : float from [0,1] interval - value of the objective used for continual learning
        Returns:
            is_anomaly : bool - True if the signal is anomalous else False
        """
        def softmax(x):

            e_x = np.exp(x - np.max(x))
            return e_x / e_x.sum(axis=0)
        signal_ = transform_pd_to_npy(signal)
        if self.classifier is not None:
            signal_metrics, barycenter_args = self.return_distance_to_closest(signal_)
            is_anomaly = not self.classifier.classify(signal_metrics)
            if self.human_mode:
                truth_q = ['t', '1', 'true', 'True', 'c', 'correct', 'Correct']
                human_evaluation = input("Enter the process evaluation: ")
                is_anomaly = human_evaluation not in truth_q
                anom_str = "anomalous" if is_anomaly else "successfully executed process"
                confirmation = input(f"The sample is {anom_str}. Write 'YES' to confirm")
                is_anomaly = is_anomaly if confirmation == 'YES' else not is_anomaly
            if self.learn_from_signal:
                if not is_anomaly:
                    self.c_samples.append(signal_metrics)
                else:
                    self.w_samples.append(signal_metrics)
                if self.update_barycenters and not is_anomaly:
                    min_len = min([np.shape(i)[0] for i in self.barycenter_euclid])
                    new_ds_dtw = to_time_series_dataset([self.barycenter_dtw[barycenter_args[0]], signal_])
                    new_ds_euclid = to_time_series_dataset([self.barycenter_euclid[barycenter_args[1]], signal_[:min_len, :]])
                    weights = softmax(np.array([self.magnitude, 1]))
                    self.barycenter_dtw[barycenter_args[0]] = dtw_barycenter_averaging(new_ds_dtw, weights = weights)
                    self.barycenter_euclid[barycenter_args[1]] = euclidean_barycenter(new_ds_euclid, weights = weights)
                self.magnitude += 1
                if self.magnitude % self.confidence_interval_update == 0:
                    self.classifier.set_confidence_interval(self.c_samples, self.w_samples, metric = objective, value = value, report_result=False)
                if vis:
                    plot_samples(self.c_samples, self.w_samples, self.barycenter_dtw, self.barycenter_euclid, correct_idx=[i for i in range(1, len(self.c_samples)+1)], anom_idx=[i for i in range(1, len(self.w_samples)+1)])
            return is_anomaly
        else:
            print("ERROR: Cannot predict, classifier is not trained yet!")

    
    def save_params(self, name, dirpath = "./model_params/"):
        """
        Save the model to a pickle file.
        Args:
            name : str - name of the file to save the model
            dirpath : str - path to the directory where the file is saved
        """
        path = dirpath + (name if len(name) > 4 and name[-4:] == ".pkl" else name + ".pkl")
        with open(path, 'wb') as f:
            pickle.dump(self, f)



    def load_params(self, path):
        """
        Loads a model saved by save_params method in a pickle format.
        Args:
            path : str - path to the model
        Returns:
            None
        """
        with open(path, 'rb') as f:
            loaded_object : featureClassifier = pickle.load(f)
        self.barycenter_dtw = loaded_object.barycenter_dtw
        self.barycenter_euclid = loaded_object.barycenter_euclid
        self.classifier = loaded_object.classifier
        self.method = loaded_object.method
        self.n_clusters = loaded_object.n_clusters
        self.dtw_error = loaded_object.dtw_error
        self.euclid_error = loaded_object.euclid_error

