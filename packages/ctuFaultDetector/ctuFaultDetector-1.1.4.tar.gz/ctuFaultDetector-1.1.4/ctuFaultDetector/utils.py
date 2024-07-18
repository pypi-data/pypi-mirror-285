import numpy as np
import pandas as pd
from torch import Tensor

def transform_pd_to_npy(dataframe):
    """
    Function that performs pd->np conversion
    Args:
        dataframe : pd.DataFrame|np.ndarray - object to be converted
    Returns:
        np.ndarray - outcome as numpy array
    """
    return dataframe.to_numpy() if isinstance(dataframe, pd.DataFrame) else dataframe

def transform_pd_to_tensor(dataframe):
    """
    Function that performs pd->torch conversion
    Args:
        dataframe : pd.DataFrame|torch.Tensor - object to be converted
    Returns:
        torch.Tensor - outcome as numpy array
    """
    return Tensor(dataframe.to_numpy()) if isinstance(dataframe, pd.DataFrame) else dataframe

def set_signals_to_same_length(signal1, signal2):
    """
    Pad the shorter signal with zeros to the same length
    Args:
        signal1, signal2 : np.ndarray - signals
    Returns
        signal1_, signal2_ : np.ndarray - elongated signals of the same length
    """
    signal1_len = np.shape(signal1)[0]
    signal2_len = np.shape(signal2)[0]
    signal1_, signal2_ = signal1, signal2
    if signal1_len > signal2_len:
        signal2_ = np.pad(signal2, ((0, signal1_len - signal2_len), (0, 0)), 'constant')
    elif signal1_len < signal2_len:
        signal1_ = np.pad(signal1, ((0, signal2_len - signal1_len), (0, 0)), 'constant')
    return signal1_, signal2_


def incremental_mean_update(cur_mean, new_sample, n_samples):
    """
    Computes the incremental mean update as in the equation (3) in section 3.1.2 from the thesis
    Args:
        cur_mean : np.ndarray - mean signal
        new_sample : np.ndarray - new signal to learn from
        n_samples : int - number of samples from which the classifier was trained
    Returns:
        np.ndarray - updated mean signal
    """
    n_samples = n_samples if n_samples > 0 else 1
    if cur_mean is None:
        return new_sample
    new_mean = cur_mean + (new_sample - cur_mean)/n_samples
    return transform_pd_to_npy(new_mean)

def incremental_variance_update(cur_variance, new_sample, n_samples, cur_mean, new_mean):
    """
    Computes the incremental variance update as in the equation (4) in section 3.1.2 from the thesis
    Args:
        cur_variance : np.ndarray - standard deviation signal
        new_sample : np.ndarray - new signal to learn from
        n_samples : int - number of samples from which the classifier was trained
        cur_mean : np.ndarray - mean signal - before the last mean update
        new_mean : np.ndarray - updated mean from the last mean update
    Returns:
        np.ndarray - updated standard deviation signal
    """
    n_samples = n_samples if n_samples > 0 else 1
    if cur_variance is None:
        return np.zeros_like(cur_mean)
    new_var = np.sqrt((n_samples * cur_variance**2 + (new_sample - cur_mean) * (new_sample - new_mean))/n_samples)
    return transform_pd_to_npy(new_var)

def load_data(path : str, id_name : str = 'meas_id', id : list[int] | None = None,
              feature_column_start : int = 3, resampling_fcn = None,
              supervised : bool = True):
    """
    Function that loads data from the csv dataset, and returns the loaded signals in the form of [(signal, label), ...] list of tuples
    it is possible to load signals from certain days.
    Args:
        path : str - path to the csv dataset
        id_name : str - key name of the column in which the day of the measurement is stored
        id : list[int] - list of numbers = days to select (1 : Original signals, 2 : 29.2.2024, 3 : 07.03.2024, 4 : 11.03.2024, 5 : 14.03.2024, 6 : 18.04.2024)
        feature_column_start - start of the real values of the signals in csv (for our file does not need to be changed)
        resampling_fcn : func - function to alter the grouping 
        supervised : bool - option to add None as the label value when selecting an unsupervised dataset
    Returns:
        sequences : [(np.ndarray, bool), ...] - [(signal, label), ...] list of tuples
    """
    sequences : list = []
    raw_sequence = pd.read_csv(path)
    if id is not None:
        raw_sequence = raw_sequence[raw_sequence[id_name].isin(id)]
    FEATURE_COLUMNS = raw_sequence.columns.to_list()[feature_column_start:]
    for _, group in raw_sequence.groupby("idx"):
        sequence_features = group[FEATURE_COLUMNS] if resampling_fcn is None else resampling_fcn(group[FEATURE_COLUMNS])
        label = list(set(group["label"]))[0] if supervised else None
        sequences.append((sequence_features, label))
    return sequences

def get_n_th_fold(dataset, fold_idx, fold_size = 56, small_train = False, report =False):
    """
    Performs the n-th fold of k-fold crossvalidation
    Args:
        dataset - samples to make the fold from
        fold_idx : int from [1,k] interval - fold index
        fold_size : int - size of each fold
        small_train : bool - do the inverse crossvalidation
    Returns:
        train_set : list - training set for the fold_idx fold
        test_set : list - testing set for the fold_idx fold
    """
    indices = np.arange(fold_size)
    indices += (fold_idx * fold_size)
    if report:
        print(f"Test: {indices}")
    if not small_train:
        train_set = [sig for i, sig in enumerate(dataset) if i not in indices]
        test_set = [sig for i, sig in enumerate(dataset) if i in indices]
    else:
        train_set = [sig for i, sig in enumerate(dataset) if i in indices]
        test_set = [sig for i, sig in enumerate(dataset) if i not in indices]
    return train_set, test_set

def get_swich_points(arr):
    """
    Returns the points where anomalies begin and end for n-sigma method - just a helper function for visualization.
    Args :
        arr : np.ndarray - signal
    Returns:
        ret : np.ndarray - anomaly swich points
    """
    arr = np.array(arr)
    padded_arr = np.pad(arr, (1, 1), mode='constant', constant_values=0)
    diffs = np.diff(padded_arr.astype(bool).astype(int))
    start_indices = np.where(diffs == 1)[0]
    end_indices = np.where(diffs == -1)[0]
    ret = np.array([start_indices, end_indices]).T
    return ret