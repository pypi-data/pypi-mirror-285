import pandas as pd
import numpy as np
from sklearn.svm import SVR
import matplotlib.pyplot as plt
from joblib import dump, load
import os


class svr:
    def __init__(self,
                 train_path,
                 test_path,
                 feature_names,
                 label_names,
                 solution_functions='default',
                 model_loadpath='default',
                 model_savepath='default',
                 kernel='default',
                 degree='default',
                 gamma='default',
                 coef0='default',
                 tol='default',
                 C='default',
                 epsilon='default',
                 shrinking='default',
                 cache_size='default',
                 verbose='default',
                 max_iter='default'):
        self.train_path = train_path
        self.test_path = test_path
        self.feature_names = feature_names
        self.label_names = label_names
        self.solution_functions = solution_functions if solution_functions != 'default' else None
        self.model_loadpath = model_loadpath if model_loadpath != 'default' else None
        self.model_savepath = model_savepath if model_savepath != 'default' else None
        self.kernel = kernel if kernel != 'default' else 'linear'
        self.degree = degree if degree != 'default' else 3
        self.gamma = gamma if gamma != 'default' else 'scale'
        self.coef0 = coef0 if coef0 != 'default' else 0.0
        self.tol = tol if tol != 'default' else 0.001
        self.C = C if C != 'default' else 1.0
        self.epsilon = epsilon if epsilon != 'default' else 0.1
        self.shrinking = shrinking if shrinking != 'default' else True
        self.cache_size = cache_size if cache_size != 'default' else 200
        self.verbose = verbose if verbose != 'default' else False
        self.max_iter = max_iter if max_iter != 'default' else -1

        self.train_features, self.train_labels, self.test_features, self.test_labels = self.load_data()
        self.model = self.create_model()

    def load_data(self):
        train_data = pd.read_csv(self.train_path)
        test_data = pd.read_csv(self.test_path)

        train_features = train_data[self.feature_names].astype(float)
        train_labels = train_data[self.label_names].astype(float)

        test_features = test_data[self.feature_names].astype(float)
        test_labels = test_data[self.label_names].astype(float)

        if self.solution_functions is not None:
            for i, solution in enumerate(self.solution_functions):
                train_features[f'solutions_{i}'] = solution(train_features)
                test_features[f'solutions_{i}'] = solution(test_features)

        train_features_max = train_features.max()
        train_features = np.array(train_features / train_features_max)
        test_features = np.array(test_features / train_features_max)

        train_labels = np.array(train_labels).ravel()
        test_labels = np.array(test_labels).ravel()

        return train_features, train_labels, test_features, test_labels

    def create_model(self):
        if self.model_loadpath is None:
            return SVR(kernel=self.kernel,
                       degree=self.degree,
                       gamma=self.gamma,
                       coef0=self.coef0,
                       tol=self.tol,
                       C=self.C,
                       epsilon=self.epsilon,
                       shrinking=self.shrinking,
                       cache_size=self.cache_size,
                       verbose=self.verbose,
                       max_iter=self.max_iter)
        else:
            if os.path.exists(self.model_loadpath):
                return load(self.model_loadpath)
            else:
                raise FileNotFoundError(f"No model found at {self.model_loadpath}")

    def train(self):
        if self.model_loadpath is None:
            self.model.fit(self.train_features, self.train_labels)

            if self.model_savepath is not None:
                dump(self.model, self.model_savepath)
        else:
            if os.path.exists(self.model_loadpath):
                self.model = load(self.model_loadpath)
            else:
                raise FileNotFoundError(f"No model found at {self.model_loadpath}")

    def predict(self):
        y_pre = self.model.predict(self.test_features)
        y_pre = y_pre.reshape(-1, 1)
        return y_pre

    def test(self):
        y_test = self.test_labels.reshape(-1, 1)
        return y_test

    def plot_results(self, y_test, y_pre):
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        plt.figure(figsize=(4, 3))
        plt.rc('font', family='Times New Roman', size=12)
        plt.subplots_adjust(left=0.16, bottom=0.16, top=0.95, right=0.95)
        plt.plot(y_test, y_test, linewidth=1, color='grey', alpha=0.7, zorder=1)
        plt.scatter(y_test, y_pre, s=0.5, color='lightcoral', alpha=1, zorder=2)
        plt.xlabel("Test")
        plt.ylabel("Prediction")
        plt.show()
