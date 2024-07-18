import pandas as pd
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import matplotlib.pyplot as plt


class ann:
    def __init__(self,
                 test_path,
                 feature_names,
                 label_names,
                 train_path='default',
                 hidden_layers='default',
                 epochs='default',
                 solution_functions='default',
                 batch_size='default',
                 activation_function='default',
                 model_loadpath='default',
                 model_savepath='default',
                 criterion='default',
                 optimizer='default',
                 learning_rate='default'):
        self.train_path = train_path
        self.test_path = test_path
        self.feature_names = feature_names
        self.label_names = label_names
        self.hidden_layers = hidden_layers
        self.epochs = epochs
        self.solution_functions = solution_functions
        self.batch_size = batch_size
        self.activation_function = activation_function
        self.model_loadpath = model_loadpath
        self.model_savepath = model_savepath
        self.criterion = criterion
        self.optimizer = optimizer
        self.learning_rate = learning_rate

        self.train_data, self.test_data = self.load_data()
        self.train_loader, self.test_loader = self.create_dataloaders()

        self.model = self.create_model()

    def load_data(self):
        if self.train_path == 'default':
            train_data = pd.read_csv(self.test_path)
        else:
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
        train_features = train_features / train_features_max
        test_features = test_features / train_features_max

        train_labels_max = train_labels.max()
        train_labels = train_labels / train_labels_max

        return (TensorDataset(torch.Tensor(train_features.values), torch.Tensor(train_labels.values)),
                TensorDataset(torch.Tensor(test_features.values), torch.Tensor(test_labels.values)))

    def create_dataloaders(self):
        if self.batch_size == 'default':
            batch_size = self.train_data.tensors[0].shape[0]
        else:
            batch_size = self.batch_size

        train_loader = DataLoader(self.train_data, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(self.test_data, batch_size=batch_size, shuffle=False)
        return train_loader, test_loader

    def create_model(self):
        class NNArch(nn.Module):
            def __init__(self, feature_num, hidden_layers, label_num, activation_function):
                super(NNArch, self).__init__()

                self.layers = nn.ModuleList()

                if activation_function == 'default':
                    self.activation_function = nn.PReLU()
                else:
                    self.activation_function = activation_function

                if hidden_layers == 'default':
                    hidden_layers = [8, 8]
                else:
                    hidden_layers = hidden_layers

                self.layers.append(nn.Linear(feature_num, hidden_layers[0]))

                for i in range(1, len(hidden_layers)):
                    self.layers.append(self.activation_function)
                    self.layers.append(nn.Linear(hidden_layers[i - 1], hidden_layers[i]))

                self.layers.append(nn.Linear(hidden_layers[-1], label_num))

            def forward(self, x):
                for layer in self.layers:
                    x = layer(x)
                return x

        feature_num = self.train_data.tensors[0].shape[1]
        label_num = self.train_data.tensors[1].shape[1]

        return NNArch(feature_num, self.hidden_layers, label_num, self.activation_function)

    def train(self):
        if self.model_loadpath == 'default':
            if self.criterion == 'default':
                criterion = nn.MSELoss()
            else:
                criterion = self.criterion

            if self.learning_rate == 'default':
                learning_rate = 0.01
            else:
                learning_rate = self.learning_rate

            if self.optimizer == 'default':
                optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
            else:
                optimizer = self.optimizer

            if self.epochs == 'default':
                epochs = 5000
            else:
                epochs = self.epochs

            with tqdm(total=epochs, desc='Training Progress', unit='epoch') as epoch_pbar:
                for epoch in range(epochs):
                    total_loss = 0
                    for inputs_train, labels_train in self.train_loader:
                        optimizer.zero_grad()
                        outputs = self.model(inputs_train)
                        loss = criterion(outputs, labels_train.reshape(-1, 1))
                        loss.backward()
                        optimizer.step()
                        total_loss += loss.item()

                    avg_loss = total_loss / len(self.train_loader)
                    epoch_pbar.set_postfix(loss=avg_loss, refresh=True)
                    epoch_pbar.update(1)

            if self.model_savepath != 'default':
                torch.save(self.model.state_dict(), self.model_savepath)
        else:
            state_dict = torch.load(self.model_loadpath)
            self.model.load_state_dict(state_dict)

    def predict(self):
        all_predictions = []
        for inputs_test, labels_test in self.test_loader:
            predictions = self.model(inputs_test)
            all_predictions.append(predictions.detach().numpy())

        y_pre = np.concatenate(all_predictions, axis=0) * (np.array((pd.read_csv(self.train_path)[self.label_names]).astype(float).max()))

        return y_pre

    def test(self):
        all_tests = []
        for inputs_test, labels_test in self.test_loader:
            all_tests.append(labels_test.detach().numpy())

        y_test = np.concatenate(all_tests, axis=0).reshape(-1, 1)

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
