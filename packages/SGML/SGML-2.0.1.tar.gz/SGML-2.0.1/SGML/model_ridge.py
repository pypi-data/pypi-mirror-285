import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from joblib import dump, load


class ridge:
    def __init__(self,
                 train_path,
                 test_path,
                 feature_names,
                 label_names,
                 solution_functions='default',
                 model_loadpath='default',
                 model_savepath='default',
                 alpha='default',
                 fit_intercept='default',
                 copy_X='default',
                 max_iter='default',
                 tol='default',
                 solver='default',
                 positive='default',
                 random_state='default'):
        self.train_path = train_path
        self.test_path = test_path
        self.feature_names = feature_names
        self.label_names = label_names
        self.solution_functions = solution_functions
        self.model_loadpath = model_loadpath
        self.model_savepath = model_savepath
        self.alpha = alpha
        self.fit_intercept = fit_intercept
        self.copy_X = copy_X
        self.max_iter = max_iter
        self.tol = tol
        self.solver = solver
        self.positive = positive
        self.random_state = random_state

        self.train_features, self.train_labels, self.test_features, self.test_labels = self.load_data()
        self.model = self.create_model()

    def load_data(self):
        train_data = pd.read_csv(self.train_path)
        test_data = pd.read_csv(self.test_path)

        train_features = train_data[self.feature_names].astype(float)
        train_labels = train_data[self.label_names].astype(float)

        test_features = test_data[self.feature_names].astype(float)
        test_labels = test_data[self.label_names].astype(float)

        if self.solution_functions != 'default':
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
        if self.alpha == 'default':
            alpha = 1
        else:
            alpha = self.alpha

        if self.fit_intercept == 'default':
            fit_intercept = True
        else:
            fit_intercept = self.fit_intercept

        if self.copy_X == 'default':
            copy_X = True
        else:
            copy_X = self.copy_X

        if self.tol == 'default':
            tol = 0.0001
        else:
            tol = self.tol

        if self.solver == 'default':
            solver = 'auto'
        else:
            solver = self.solver

        if self.positive == 'default':
            positive = False
        else:
            positive = self.positive

        return Ridge(alpha=alpha, fit_intercept=fit_intercept, copy_X=copy_X,
                     tol=tol, solver=solver, positive=positive)

    def train(self):
        if self.model_loadpath == 'default':
            self.model.fit(self.train_features, self.train_labels)

            if self.model_savepath != 'default':
                dump(self.model, self.model_savepath)
        else:
            self.model = load(self.model_loadpath)

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
