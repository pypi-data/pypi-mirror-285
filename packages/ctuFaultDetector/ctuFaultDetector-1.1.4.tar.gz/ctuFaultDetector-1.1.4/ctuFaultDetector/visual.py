import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ctuFaultDetector.utils import transform_pd_to_npy
from ctuFaultDetector.metrics.dtw_barycenter import METHODS_LABEL_DICT
import pickle
from scipy.interpolate import interp1d


def draw_roc_from_dict(roc_dict, save_fig = None, title = None, scatter = False):
    """
    Draws ROC curve from the saved ROC dictionary, used to create ROC figures in the thesis.
    Args:
        roc_dict : str - path to the saved dict
        save_fig : None|str - save generated figure if not none - name of the figure
        title : str - title for the ROC plt plot
        scatter : bool - use normal plot if False, else use scatter plot
    """
    def mean_roc(roc_curves, num_points=100):
        mean_fpr = np.linspace(0, 1, num_points)
        interp_tprs = []
        for roc in roc_curves:
            fpr, tpr = roc[1], roc[0]
            interp_func = interp1d(fpr, tpr, kind='linear', fill_value="extrapolate")
            interp_tprs.append(interp_func(mean_fpr))
        mean_tpr = np.mean(interp_tprs, axis=0) 
        return mean_fpr, mean_tpr
    colors = ["red", "green", "blue", "orange", "brown"]
    if isinstance(roc_dict, str):
        with open(roc_dict, "rb") as f:
            total_roc = pickle.load(f)
    elif isinstance(roc_dict, dict):
        total_roc = roc_dict
    aucs = []
    curves = [np.flip(i["ROC"], axis=1) for i in total_roc]
    fpr_m, tpr_m = mean_roc(curves)
    for i in range(len(curves)):
        if scatter:
            plt.scatter(curves[i][1,:], curves[i][0,:], color = colors[i%5], marker="x", s=10)
        else:
            plt.plot(curves[i][1,:], curves[i][0,:], color = "tab:green", alpha = 0.75, label="")

        auc = np.trapz(np.nan_to_num(np.flip(np.append(curves[i][0, :], 0))), np.nan_to_num(np.flip(np.append(curves[i][1, :], 0))))
        aucs.append(auc)
        print(f"AUC is {auc}")
    if scatter:
        pass
    else:
        plt.plot(fpr_m, tpr_m, color = "blue", label="Mean ROC")
    print(f"Mean AUC is: {np.mean(aucs)}")
    plt.plot([0,1], [0,1], color="black", linestyle= "dotted")
    plt.legend(loc="lower right")
    plt.xlim([0,1])
    plt.ylim([0,1])
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.grid()
    if title is not None:
        plt.title(title)
    if save_fig is not None:
        name = str(save_fig) if len(save_fig) > 4 and str(save_fig)[-4:] == ".pdf" else str(save_fig) + ".pdf"
        plt.savefig(name , format='pdf', bbox_inches='tight')
    plt.show()
    return fpr_m, tpr_m

def plot_one_6dim_signal(signal1, avg = None, std = None, sensitivity = None, save_fig = None, anomaly_highlight = False, anomalies = [], anomalies_all = [], real_len = 0):
    """
    Plot a 6-dimensional signal  - used for debugging, testing and figures in the thesis
    Args:
        signal1 : np.ndarray - signal to be plotted
        avg : np.ndarray|None - mean signal to be plotted as well if not None
        std : np.ndarray|None - standard deviation signal for plotting the blue zone if not None
        sensitivity : int - size of the blue zone std deviation multiplier
        save_fig : str|None - name of the figure to be saved in pdf format if not None
        anomaly_highlight : bool - highlight anomalies as in figure 3.2
        anomalies : list - list of anomalies for each dimension
        anomalies_all : list - list of anomalies for all dimensions
        real_len : int = show only part of the signal of length real_len
    Returns:
        None, plots the signal

    """
    fig, ax = plt.subplots(6, 1, figsize=(6.5, 5), sharex=False)
    ylabels = [ "Force x",
                "Force y",
                "Force z",
                "Torque x",
                "Torque y",
                "Torque z"
             ]
    signal_len = np.shape(signal1)[0] if real_len==0 else real_len
    xaxis = np.arange(signal_len)
    for i in range(0, 6):
        if avg is not None:
            upper_bound = avg[:, i] + sensitivity * std[:, i]
            lower_bound = avg[:, i] - sensitivity * std[:, i]
            upper_bound = upper_bound[:signal_len]
            lower_bound = lower_bound[:signal_len]
            ax[i].plot(xaxis, upper_bound, color = "#378CE7")
            ax[i].plot(xaxis, lower_bound, color = "#378CE7")
            ax[i].fill_between(xaxis, lower_bound, upper_bound, color = "#378CE7", alpha = 0.3)
        ax[i].plot(xaxis[:signal_len], signal1[:signal_len, i], color = "black", linewidth = 1)
        ax[i].set_ylabel(ylabels[i])
        if i < 5:
            ax[i].set_xticklabels([])
    ax[5].set_xlabel("Time")
    #fig.suptitle("Sample signal of a process", fontweight="bold", fontsize = 12)
    fig.align_ylabels()
    if anomaly_highlight:
        for i in range(0,6):
            for j in range(len(anomalies)):
                ax[i].axvspan(*anomalies[j], color='red', alpha=0.2)
            for k in range(len(anomalies_all[i])):
                ax[i].axvspan(*anomalies_all[i][k], color='red', alpha = 0.6)
    if save_fig is not None:
        name = str(save_fig) if len(save_fig) > 4 and str(save_fig)[-4:] == ".pdf" else str(save_fig) + ".pdf"
        plt.savefig(name , format='pdf', bbox_inches='tight')
    plt.show()

def plot_6dim_signal_dataset(signal_dataset, save_fig = None):
    """
    Function for plotting the whole dataset, used for getting a general information about the dataset
    Args:
        signal_dataset : [(np.ndarray, bool), ...] - list of tuples (signal, label)
        save_fig : None|str - name of the figure to be saved in pdf figure if not None
    Returns:
        None, plots the dataset plot
    """
    fig, ax = plt.subplots(6, 1, figsize=(6.5, 5), sharex=True)
    ylabels = [ "Force x",
                "Force y",
                "Force z",
                "Torque x",
                "Torque y",
                "Torque z"
             ]
    for signal in signal_dataset:
        xaxis = np.arange(np.shape(signal[0])[0])
        color = "blue" if not signal[1] else "red"
        sig = transform_pd_to_npy(signal[0])
        for i in range(0, 6):
            ax[i].plot(xaxis, sig[ : , i], color = color, linewidth = 1)
            ax[i].set_ylabel(ylabels[i])
            if i < 5:
                ax[i].set_xticklabels([])
        ax[5].set_xlabel("Time")
        #fig.suptitle("Sample signal of a process", fontweight="bold", fontsize = 12)
        fig.align_ylabels()
    if save_fig is not None:
        name = str(save_fig) if len(save_fig) > 4 and str(save_fig)[-4:] == ".pdf" else str(save_fig) + ".pdf"
        plt.savefig(name , format='pdf', bbox_inches='tight')
    plt.show()

def plot_samples(correct_points, wrong_points, method = [1, 5], title = "", correct_idx = [], anom_idx = [], save_fig1 = "samples"):
    """
    Plots the feature vectors in memory of a feature classifier
    Args:
        correct_points : np.ndarray|list - feature vectors from non-anomalous processes
        wrong_points : np.ndarray|list - feature vectors from anomalous processes
        method : [int, int] - features of the signal, see ctuFaultDetector.metrics.dtw_barycenter.method.get_distance function
    """
    scatter_if_not_empty(correct_points, color="blue", marker="+")
    scatter_if_not_empty(wrong_points, color="red", marker="x")
    plt.grid(True)
    plt.xlabel(METHODS_LABEL_DICT[method[0]])
    plt.ylabel(METHODS_LABEL_DICT[method[1]])
    plt.title(title)
    plt.legend(["Successfull process",
                "Failed process",
                "Barycenter distance",
                "Euclidean barycenter distance"], loc="lower right")
    plt.xlim([0, 50000])
    plt.ylim([0, 5000])
    if correct_idx:
        for i, label in enumerate(correct_idx):
            plt.annotate(label+1, (correct_points[i]))
    if anom_idx:
        for i, label in enumerate(anom_idx):
            plt.annotate(label+1, (wrong_points[i]))
    if save_fig1 is not None:
        name = str(save_fig1) if len(save_fig1) > 4 and str(save_fig1)[-4:] == ".pdf" else str(save_fig1) + ".pdf"
        plt.savefig(name , format='pdf', bbox_inches='tight')
    plt.show()

def scatter_if_not_empty(points, color, marker):
    """
    If "points" is not empty, creates a scatter chart of them
    Args:
        points : list (can be empty) - points to be scattered
        color : str from plt colors - color of the points
        marker : str from plt markers - marker used for points
    Returns:
        None, scatters the points.
    """
    if points:
        if np.shape(points)[0] != 2:
            points = np.array(points).T
        if points is not None:
            plt.scatter(*points, color=color, marker=marker)
