from sklearn.cluster import KMeans
from scipy.stats import multivariate_normal, chi2
import warnings
import numpy as np
from numpy.linalg import inv

def classify_kmeans(data, n_clusters):
    """
    Function that performs the Kmeans clustering algorithm and returns the means and
    labels of given points

    Args:
        data : list[]
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        classifier_class = KMeans(n_clusters=n_clusters, n_init=10)
        classifier_class.fit(data)
        centroids = classifier_class.cluster_centers_
        labels = classifier_class.labels_
        clusters = [[i for i, x in enumerate(labels) if x == num] for num in range(max(labels) + 1)]
        return centroids, clusters

def get_cluster_params(means, points, labels):
    if not isinstance(points, np.ndarray):
            points = np.array(points)
    clusters_params = [(means[i], np.cov(points[labels[i]].T)) for i in range(len(means))]
    return clusters_params

def upscale(array):
    return array[np.newaxis, :] if len(np.shape(array)) < 2 else array

class GaussianClassifier():
    def __init__(self, cluster_params, confidence = 0.95) -> None:
        self.cluster_params = cluster_params
        self.confidence_threshold = confidence
    
    def set_confidence_threshold(self, value):
        self.confidence_threshold = value

    def set_confidence_interval(self, data_c, data_w, metric = "ACC", value = 1, n_steps=100, report_result = True, confidence_intervals = [0.8, 1]):
        if value is None:
            value = 1
        confidence_intervals : np.ndarray = np.linspace(confidence_intervals[0], confidence_intervals[1], n_steps)
        score_data : np.ndarray = np.zeros((n_steps, 4))
        data = [*data_c, *data_w]
        ground_truths : list[bool] = [*[False for _ in range(len(data_c))],
                                      *[True for _ in range(len(data_w))]]
        for i, interval in enumerate(confidence_intervals):
            self.confidence_threshold : float = interval
            classifications : list[bool] = [not self.classify(sample) for sample in data]

            #score data key:
            #score_data[i, :] = True positives, True Negatives, False Positives, False Negatives


            score_data[i, 0] = np.sum(np.logical_and(classifications, 
                                                     ground_truths)) # TP
            score_data[i, 1] = np.sum(np.logical_and(np.logical_not(classifications), np.logical_not(ground_truths))) #TN
            score_data[i, 2] = np.sum(np.logical_and(classifications, np.logical_not(ground_truths))) #FP
            score_data[i, 3] = np.sum(np.logical_and(np.logical_not(classifications), ground_truths)) #FN
        accuracy = np.sum(score_data[:, :2], axis=1)/len(data)
        tpr = score_data[:, 0]/(score_data[:, 0] + score_data[:, 3] + 0.0001)
        tnr = score_data[:, 1]/(score_data[:, 1] + score_data[:, 2] + 0.0001)
        skewed_accuracy = (value * tpr + tnr)/ (value + 1)
        if metric not in ["TPR", "TNR", "ACC", "sACC"]:
            print(f"WARN: Invalid metric {str(metric)}, aborting calculation of confidence interval!")
            self.confidence_threshold = 0.95
            print(confidence_intervals)
            classifications : list[bool] = [not self.classify(sample) for sample in data]
            print(np.sum(np.logical_and(classifications, 
                      ground_truths)) )# TP)
            print(np.sum(np.logical_and(np.logical_not(classifications), np.logical_not(ground_truths))))
            print(np.sum(np.logical_and(classifications, np.logical_not(ground_truths)))) #FP)
            print(np.sum(np.logical_and(np.logical_not(classifications), ground_truths))) #FN)

            return
        if metric == "TPR":
            max_idx = np.argmax(np.sum(score_data[:, :2], axis=1)*(tpr >= value))
        elif metric == "TNR":
            max_idx = np.argmax(np.sum(score_data[:, :2], axis=1)*(tnr >= value))
        elif metric == "ACC":
            max_idx = np.argmax(accuracy)
        elif metric == "sACC":
            max_idx = np.argmax(skewed_accuracy)
        self.confidence_threshold = confidence_intervals[max_idx]
        print("Setting: ",max_idx, confidence_intervals[max_idx])

        if report_result:
            print(f"""Metrics of the classifier are:
              Accuracy: {accuracy[max_idx]}
              True positive rate: {tpr[max_idx]}
              True negative rate: {tnr[max_idx]}
              Confidence treshold: {self.confidence_threshold}
              """)
        return

    def classify_to_cluster(self, sample):
        if not isinstance(sample, np.ndarray):
            sample = np.array(sample)
        probs = np.zeros(len(self.cluster_params))
        for i in range(len(self.cluster_params)):
            mu, covar = self.cluster_params[i]
            mu = upscale(mu)
            n_dim = len(mu)
            
            chi2value = chi2.ppf(self.confidence_threshold, df = n_dim)
            difference_vector = sample - mu
            difference_vector = upscale(difference_vector)
            mahalonobis_distance = difference_vector @ inv(covar) @ difference_vector.T
            probs[i] = mahalonobis_distance <= chi2value
        return probs
    
    def classify(self, sample):
        """!!!!RETURNS TRUE IF NOT ANOMALY"""
        return np.sum(self.classify_to_cluster(sample)) > 0

    def __repr__(self):
        return f"""Gaussian classifier, params: {self.cluster_params}"""
