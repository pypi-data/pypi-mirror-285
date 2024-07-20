import itertools
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import seaborn as sns
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from pandas import DataFrame
from torch.utils.data import DataLoader, Dataset
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support,
                             confusion_matrix)
from sklearn.model_selection import (KFold, StratifiedKFold, GroupKFold,
                                     GridSearchCV, train_test_split)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.utils import shuffle
from sys import stdout
from tqdm import trange


OUTER_K = 5
INNER_K = 3

# Standard machine learning parameters
MAX_ITER = 250000  # for support vector classifier
C_LIST = [1e-3, 1e-2, 1e-1, 1e0]
N_NEIGHBORS_LIST = list(range(1, 10))

# Deep learning parameters
PATIENCE = 5  # for early stopping


def machine_learn(nirs, labels, groups, model, normalize=None,
                  random_state=None, output_folder='./outputs'):
    """
    Perform nested k-fold cross-validation for standard machine learning models
    producing metrics and confusion matrices. The models include linear
    discriminant analysis (LDA), support vector classifier (SVC) with grid
    search for the regularization parameter (inner cross-validation), and
    k-nearest neighbors (kNN) with grid search for the number of neighbors
    (inner cross-validation).

    Parameters
    ----------
    nirs : array of shape (n_epochs, n_channels, n_times)
        Processed NIRS data.

    labels : array of integers
        List of labels matching the NIRS data.

    groups : array of integers | None
        List of subject ID matching the epochs to perfrom a group k-fold
        cross-validation. If ``None``, performs a stratified k-fold
        cross-validation instead.

    model : string
        Standard machine learning to use. Either ``'lda'`` for a linear
        discriminant analysis, ``'svc'`` for a linear support vector
        classifier or ``'knn'`` for a k-nearest neighbors classifier.

    normalize : tuple of integers | None
        Axes on which to normalize data before feeding to the model with
        min-max scaling based on the train set for each iteration of the outer
        cross-validation. For example (0, 2) to normalize across epochs and
        time. Defaults to ``None`` for no normalization.

    random_state : integer | None
        Controls the shuffling applied to data. Pass an integer for
        reproducible output across multiple function calls. Defaults to
        ``None`` for not setting the seed.

    output_folder : string
        Path to the directory into which the figures will be saved. Defaults to
        ``'./outputs'``.

    Returns
    -------
    accuracies : array of floats
        List of accuracies on the test sets (one for each iteration of the
        outer cross-validation).

    all_hps : list of floats | list of None
        List of regularization parameters for the SVC or a list of None for the
        LDA (one for each iteration of the outer cross-validation).

    additional_metrics : list of tuples
        List of tuples of metrics composed of (precision, recall, F1 score) on
        the outer cross-validation (one tuple for each iteration of the outer
        cross-validation). This uses the ``precision_recall_fscore_support``
        function from scikit-learn with ``average='weighted'``, ``y_true`` and
        ``y_pred`` being the true and the predictions on the specific iteration
        of the outer cross-validation.
    """
    print(f'Machine learning: {model}')

    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    # K-fold cross-validator
    if groups is None:
        out_kf = StratifiedKFold(n_splits=OUTER_K)
        in_kf = StratifiedKFold(n_splits=INNER_K)
    else:
        out_kf = GroupKFold(n_splits=OUTER_K)
        in_kf = GroupKFold(n_splits=INNER_K)
    all_y_true = []
    all_y_pred = []
    accuracies = []
    additional_metrics = []
    all_hps = []
    out_split = out_kf.split(nirs, labels, groups)
    for k, out_idx in enumerate(out_split):
        print(f'    FOLD #{k}')
        nirs_train, nirs_test = nirs[out_idx[0]], nirs[out_idx[1]]
        labels_train, labels_test = labels[out_idx[0]], labels[out_idx[1]]

        if groups is None:
            groups_train = None
            nirs_train, labels_train = shuffle(
                nirs_train, labels_train, random_state=random_state)
        else:
            groups_train = groups[out_idx[0]]
            nirs_train, labels_train, groups_train = shuffle(
                nirs_train, labels_train, groups_train,
                random_state=random_state)

        all_y_true += labels_test.tolist()

        # Min-max scaling
        if normalize:
            maxs = nirs_train.max(axis=normalize, keepdims=True)
            mins = nirs_train.min(axis=normalize, keepdims=True)
            nirs_train = (nirs_train - mins) / (maxs - mins)
            nirs_test = (nirs_test - mins) / (maxs - mins)

        nirs_train = nirs_train.reshape(len(nirs_train), -1)
        nirs_test = nirs_test.reshape(len(nirs_test), -1)

        in_split = in_kf.split(nirs_train, labels_train, groups_train)

        # LDA
        if model == 'lda':
            lda = LinearDiscriminantAnalysis()
            lda.fit(nirs_train, labels_train)
            y_pred = lda.predict(nirs_test).tolist()
            all_hps.append(None)

        # SVC
        elif model == 'svc':
            parameters = {'C': C_LIST}
            svc = LinearSVC(max_iter=MAX_ITER, dual='auto')
            clf = GridSearchCV(svc, parameters, scoring='accuracy',
                               cv=in_split)
            clf.fit(nirs_train, labels_train)
            y_pred = clf.predict(nirs_test).tolist()
            all_hps.append(clf.best_params_['C'])

        # kNN
        elif model == 'knn':
            parameters = {'n_neighbors': N_NEIGHBORS_LIST}
            knn = KNeighborsClassifier()
            clf = GridSearchCV(knn, parameters, scoring='accuracy',
                               cv=in_split)
            clf.fit(nirs_train, labels_train)
            y_pred = clf.predict(nirs_test).tolist()
            all_hps.append(clf.best_params_['n_neighbors'])

        # Metrics
        accuracies.append(accuracy_score(labels_test, y_pred))
        prfs = precision_recall_fscore_support(labels_test, y_pred,
                                               average='weighted')
        additional_metrics.append(prfs[:-1])
        all_y_pred += y_pred

    # Figures
    cm = confusion_matrix(all_y_true, all_y_pred, normalize='true')
    sns.heatmap(cm, annot=True, cmap='crest', vmin=0.1, vmax=0.8)
    plt.xlabel('Predicted')
    plt.ylabel('Ground truth')
    plt.savefig(f'{output_folder}/confusion_matrix.png')
    plt.close()

    accuracies = np.array(accuracies)

    return accuracies, all_hps, additional_metrics


class _DatasetFromNumPy(Dataset):
    """
    Dataset loader from NumPy arrays for PyTorch.
    """

    def __init__(self, x, y):
        self.x = torch.from_numpy(x)
        self.y = torch.from_numpy(y)

    def __getitem__(self, index):
        return self.x[index], self.y[index]

    def __len__(self):
        return len(self.x)


class _ANNClassifier(nn.Module):

    def __init__(self, n_classes):
        super(_ANNClassifier, self).__init__()
        self.fc1 = nn.Linear(12, 8)
        self.fc2 = nn.Linear(8, 4)
        self.fc3 = nn.Linear(4, n_classes)

    def forward(self, x):
        batch_size = x.size(0)
        x = x.view(batch_size, -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class _CNNClassifier(nn.Module):

    def __init__(self, n_classes):
        super(_CNNClassifier, self).__init__()
        self.conv1 = nn.Conv1d(4, 4, kernel_size=10, stride=2)  # tempo conv
        self.pool1 = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(4, 4, kernel_size=5, stride=2)  # tempo conv
        self.pool2 = nn.MaxPool1d(2)
        self.fc1 = nn.Linear(20, 10)
        self.fc2 = nn.Linear(10, n_classes)

    def forward(self, x):
        batch_size = x.size(0)
        x = F.relu(self.conv1(x))
        x = self.pool1(x)
        x = F.relu(self.conv2(x))
        x = self.pool2(x)
        x = x.view(batch_size, -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


class _LSTMClassifier(nn.Module):

    def __init__(self, n_classes):
        super(_LSTMClassifier, self).__init__()
        self.unit_size = 20  # number of timepoints for each elt of the seq
        self.hidden_size = 36
        input_size = self.unit_size * 4  # number of timepoints x 4 channels
        self.lstm = nn.LSTM(input_size, self.hidden_size, batch_first=True)
        self.fc1 = nn.Linear(self.hidden_size, 16)
        self.fc2 = nn.Linear(16, n_classes)

    def forward(self, x):
        # Reshape
        r = x.size(-1) % self.unit_size
        if r > 0:
            x = x[:, :, :-r]  # crop to fit unit size
        x = x.reshape(x.size(0), 4, -1, self.unit_size)  # (b, ch, seq, tpts)
        x = x.permute(0, 2, 1, 3)  # (b, seq, ch, tpts)
        x = x.reshape(x.size(0), x.size(1), -1).double()

        # Initialise hidden and cell states
        h0 = torch.zeros(1, x.size(0), self.hidden_size).double().to(x.device)
        c0 = torch.zeros(1, x.size(0), self.hidden_size).double().to(x.device)

        # Feed to model
        x, _ = self.lstm(x, (h0, c0))
        x = x[:, -1, :]  # last output of the sequence
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def _train_dl(nirs_train, labels_train, clf, batch_size, lr, max_epoch,
              early_stop, random_state, device):
    """
    Train a deep learning classifier with PyTorch.
    """
    # Load data
    if early_stop:
        split = train_test_split(nirs_train, labels_train, shuffle=True,
                                 train_size=0.80, stratify=labels_train,
                                 random_state=random_state)
        nirs_train, labels_train = split[0], split[2]
        nirs_val, labels_val = split[1], split[3]
        dataset_val = _DatasetFromNumPy(nirs_val, labels_val)
        val_loader = DataLoader(dataset=dataset_val, batch_size=1,
                                shuffle=False)
    dataset_train = _DatasetFromNumPy(nirs_train, labels_train)
    train_loader = DataLoader(dataset=dataset_train, batch_size=batch_size,
                              shuffle=True)

    # Instantiate model and hyperparameters
    device_count = torch.cuda.device_count()
    if device_count > 1:
        clf = nn.DataParallel(clf)  # use multiple GPUs
    clf.to(device)
    criterion = nn.CrossEntropyLoss()  # LogSoftmax() & NLLLoss()
    optimizer = optim.Adam(clf.parameters(), lr=lr)
    # scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=25, gamma=0.5)

    train_losses = []
    train_accuracies = []
    val_losses = []
    val_accuracies = []
    bf = "    > Model training: {l_bar}{bar}| Epoch {n_fmt}/{total_fmt}"
    disable = False
    if not stdout.isatty():
        try:
            __IPYTHON__
        except NameError:
            disable = True
    pbar = trange(
        max_epoch, bar_format=bf, leave=False, disable=disable, ascii=True)
    for epoch in pbar:
        # Train
        clf.train()
        running_loss = 0.0
        correct = 0.0
        total = 0.0
        for i, data in enumerate(train_loader):
            # Get the inputs
            x, y = data[0].to(device), data[1].to(device)

            # Zero the parameter gradients
            optimizer.zero_grad()

            # Forward
            outputs = clf(x)
            _, predicted = torch.max(outputs.data, 1)
            loss = criterion(outputs, y)

            # Backward & optimize
            loss.backward()
            optimizer.step()

            # Get statistics
            running_loss += loss.item()
            total += y.size(0)
            correct += (predicted == y).sum()
            correct = int(correct)
        train_losses.append(running_loss / (i+1))
        train_accuracies.append(correct / total)

        # if epoch % 5 == 0:
        #     print(f'Loss: {train_losses[-1]}, '
        #           f'Accuracy: {train_accuracies[-1]}')

        if early_stop:
            # Validate
            clf.eval()
            with torch.no_grad():
                running_loss = 0.0
                correct = 0.0
                total = 0.0
                for i, data in enumerate(val_loader):
                    x, y = data[0].to(device), data[1].to(device)
                    outputs = clf(x)
                    _, predicted = torch.max(outputs.data, 1)
                    loss = criterion(outputs, y)
                    running_loss += loss.item()
                    total += y.size(0)
                    correct += (predicted == y).sum()
                    correct = int(correct)
                val_losses.append(running_loss / (i+1))
                val_accuracies.append(correct / total)
                last_sorted = sorted(val_losses[-PATIENCE:])
                if epoch >= PATIENCE and val_losses[-PATIENCE:] == last_sorted:
                    print(f'    > Early stopping after {epoch+1} epochs')
                    break
        # scheduler.step()

    if device_count > 1:
        clf = clf.module

    results = {'train_losses': train_losses,
               'train_accuracies': train_accuracies,
               'val_losses': val_losses,
               'val_accuracies': val_accuracies}
    return clf, results


def _test_dl(nirs_test, labels_test, clf, device):
    """
    Test a deep learning classifier with PyTorch.
    """
    # Load data sets
    dataset_test = _DatasetFromNumPy(nirs_test, labels_test)
    test_loader = DataLoader(dataset=dataset_test, batch_size=1,
                             shuffle=False)

    if torch.cuda.device_count() > 1:
        clf = nn.DataParallel(clf)  # use multiple GPUs
    clf.to(device)
    criterion = nn.CrossEntropyLoss()  # LogSoftmax() & NLLLoss()

    # Test
    clf.eval()
    with torch.no_grad():
        y_true = []
        y_pred = []
        correct = 0.0
        total = 0.0
        running_loss = 0.0
        for i, data in enumerate(test_loader):
            x, y = data[0].to(device), data[1].to(device)
            outputs = clf(x)
            _, predicted = torch.max(outputs.data, 1)
            total += y.size(0)
            correct += (predicted == y).sum()
            correct = int(correct)
            y_true.append(y.item())
            y_pred.append(predicted.item())
            loss = criterion(outputs, y)
            running_loss += loss.item()
        results = {'test_loss': running_loss / (i+1),
                   'test_accuracy': correct / total,
                   'y_true': y_true, 'y_pred': y_pred}
    return results


def deep_learn(nirs, labels, groups, model_class, normalize=None,
               batch_sizes=[4, 8, 16, 32, 64],
               lrs=[1e-5, 1e-4, 1e-3, 1e-2, 1e-1], max_epoch=100,
               random_state=None, output_folder='./outputs'):
    """
    Perform nested k-fold cross-validation for a deep learning model. Produces
    loss graph, accuracy graph and confusion matrice. This is made with early
    stopping (with a validation set of 20 %) once the model has been fine tuned
    on the inner loop of the nested k-fold cross-validation. The number of
    classes is deduced from the number of unique labels.

    Parameters
    ----------
    nirs : array of shape (n_epochs, n_channels, n_times)
        Processed NIRS data.

    labels : array of integers
        List of labels matching the NIRS data.

    groups : array of integers | None
        List of subject ID matching the epochs to perfrom a group k-fold
        cross-validation. If ``None``, performs a stratified k-fold
        cross-validation instead.

    model_class : string | PyTorch nn.Module class
        The PyTorch model class to use. If a string, can be either ``'ann'``,
        ``'cnn'`` or ``'lstm'``. If a PyTorch ``nn.Module`` class, the
        ``__init__()`` method must accept the number of classes as a parameter,
        and this needs to be the number of output neurons.

    normalize : tuple of integers | None
        Axes on which to normalize data before feeding to the model with
        min-max scaling based on the train set for each iteration of the outer
        cross-validation. For example (0, 2) to normalize across epochs and
        time. Defaults to ``None`` for no normalization.

    batch_sizes : list of integers
        List of batch sizes to test for fine-tuning.

    lrs : list of floats
        List of learning rates to test for fine-tuning.

    max_epoch : integer
        Maximum number of epochs possible for training. Defaults to ``100``.

    random_state : integer | None
        Controls the shuffling applied to data and random model initialization.
        Pass an integer for reproducible output across multiple function calls.
        Defaults to ``None`` for not setting the seed.

    output_folder : string
        Path to the directory into which the figures will be saved. Defaults to
        ``'./outputs'``.

    Returns
    -------
    accuracies : array of floats
        List of accuracies on the test sets (one for each iteration of the
        outer cross-validation).

    all_hps : list of tuples
        List of best hyperparameters (one tuple for each iteration of the outer
        cross-validation). Each tuple will be `(batch size, learning rate)`.

    additional_metrics : list of tuples
        List of tuples of metrics composed of (precision, recall, F1 score) on
        the outer cross-validation (one tuple for each iteration of the outer
        cross-validation). This uses the ``precision_recall_fscore_support``
        function from scikit-learn with ``average='weighted'``, ``y_true`` and
        ``y_pred`` being the true and the predictions on the specific iteration
        of the outer cross-validation.
    """
    if random_state:
        torch.manual_seed(random_state)

    n_classes = len(set(labels))

    # Assign PyTorch model class
    if model_class == 'ann':
        model_class = _ANNClassifier
    elif model_class == 'cnn':
        model_class = _CNNClassifier
    elif model_class == 'lstm':
        model_class = _LSTMClassifier

    print(f'Deep learning: {model_class.__name__}', end=' ')

    # Set device
    if torch.cuda.is_available():
        device = torch.device('cuda:0')
        device_count = torch.cuda.device_count()
        print(f"(using {device_count} GPU{'s' if device_count > 1 else ''})")
    else:
        device = torch.device('cpu')
        print("(using CPU)")

    # Outer split
    if os.path.isfile(f'{output_folder}/split.pickle'):
        print('    Saved k-fold split found, loading it...', end=' ')
        with open(f'{output_folder}/split.pickle', 'rb') as f:
            out_split = pickle.load(f)
        print('Done!')
    else:
        if groups is None:
            out_kf = StratifiedKFold(n_splits=OUTER_K)
        else:
            out_kf = GroupKFold(n_splits=OUTER_K)
        out_split = list(out_kf.split(nirs, labels, groups))

        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        with open(f'{output_folder}/split.pickle', 'wb') as f:
            pickle.dump(out_split, f)

    # Inner split
    if groups is None:
        in_kf = StratifiedKFold(n_splits=INNER_K)
    else:
        in_kf = GroupKFold(n_splits=INNER_K)

    for k, out_idx in enumerate(out_split):
        print(f'    Training outer fold #{k}')
        nirs_train = nirs[out_idx[0]]
        labels_train = labels[out_idx[0]]

        if groups is None:
            groups_train = None
            nirs_train, labels_train = shuffle(
                nirs_train, labels_train, random_state=random_state)
        else:
            groups_train = groups[out_idx[0]]
            nirs_train, labels_train, groups_train = shuffle(
                nirs_train, labels_train, groups_train,
                random_state=random_state)

        # Min-max scaling
        if normalize:
            maxs = nirs_train.max(axis=normalize, keepdims=True)
            mins = nirs_train.min(axis=normalize, keepdims=True)
            nirs_train = (nirs_train - mins) / (maxs - mins)

        if os.path.isfile(f'{output_folder}/model_k{k}.pt'):
            print('    > Classifier checkpoint found, skipping training')
        else:
            # Train classifier for each combination of hyperparameters
            hp_list = list(itertools.product(batch_sizes, lrs))
            if len(hp_list) > 1:
                print('    > Hyperparameter selection')
                in_accuracies = [[] for _ in hp_list]
                for i, hp in enumerate(hp_list):
                    batch_size, lr = hp[0], hp[1]
                    in_split = in_kf.split(nirs_train, labels_train,
                                           groups_train)
                    for in_idx in in_split:
                        nirs_in_train = nirs_train[in_idx[0]]
                        labels_in_train = labels_train[in_idx[0]]
                        nirs_val = nirs_train[in_idx[1]]
                        labels_val = labels_train[in_idx[1]]

                        clf = model_class(n_classes).double()
                        clf, _ = _train_dl(nirs_in_train, labels_in_train,
                                           clf, batch_size, lr, max_epoch,
                                           False, random_state, device)
                        results = _test_dl(nirs_val, labels_val, clf, device)
                        in_accuracies[i].append(results['test_accuracy'])

                # Get best hyperparameters
                in_average_accuracies = np.mean(in_accuracies, axis=1)
                index_best = np.argmax(in_average_accuracies)
                best_hps = hp_list[index_best]
            else:
                best_hps = (batch_sizes[0], lrs[0])

            # Retrain with best hyperparameters
            clf = model_class(n_classes).double()
            clf, results = _train_dl(nirs_train, labels_train,
                                     clf, best_hps[0], best_hps[1], max_epoch,
                                     True, random_state, device)

            # Save trained model and training results
            clf.cpu()
            torch.save(clf.state_dict(), f'{output_folder}/model_k{k}.pt')
            with open(f'{output_folder}/hps_k{k}.pickle', 'wb') as f:
                pickle.dump(best_hps, f)
            with open(f'{output_folder}/results_k{k}.pickle', 'wb') as f:
                pickle.dump(results, f)

            # Plot outer fold loss graph
            _, ax = plt.subplots(figsize=(12, 6))
            epochs = [epoch for epoch in range(len(results['train_losses']))]
            dict_losses = {'Epoch': epochs,
                           'Training': results['train_losses'],
                           'Validation': results['val_losses']}
            df_losses = DataFrame(dict_losses)
            df_losses = df_losses.melt(
                id_vars=['Epoch'], value_vars=['Training', 'Validation'],
                var_name='Condition', value_name='Loss')
            sns.lineplot(ax=ax, data=df_losses, y='Loss', x='Epoch',
                         hue='Condition', estimator=None)
            plt.savefig(f'{output_folder}/k{k}_graph.png',
                        bbox_inches='tight')
            plt.close()

    all_ks, all_epochs = [], []
    all_train_losses, all_val_losses = [], []
    all_train_accuracies, all_val_accuracies = [], []
    all_y_true, all_y_pred = [], []
    accuracies, all_hps, additional_metrics = [], [], []
    for k, out_idx in enumerate(out_split):
        print(f'    Testing outer fold #{k}')
        nirs_train, nirs_test = nirs[out_idx[0]], nirs[out_idx[1]]
        labels_test = labels[out_idx[1]]

        # Min-max scaling of test set using training set only to avoid leakage
        if normalize:
            maxs = nirs_train.max(axis=normalize, keepdims=True)
            mins = nirs_train.min(axis=normalize, keepdims=True)
            nirs_test = (nirs_test - mins) / (maxs - mins)

        # Load trained model, hyperparameters and training results
        clf = model_class(n_classes).double()
        clf.load_state_dict(torch.load(f'{output_folder}/model_k{k}.pt'))
        with open(f'{output_folder}/hps_k{k}.pickle', 'rb') as f:
            best_hps = pickle.load(f)
        with open(f'{output_folder}/results_k{k}.pickle', 'rb') as f:
            results = pickle.load(f)

        # Append training details
        all_hps.append(best_hps)
        all_ks += [k for _ in results['train_losses']]
        all_epochs += [epoch for epoch in range(len(results['train_losses']))]
        all_train_losses += results['train_losses']
        all_val_losses += results['val_losses']
        all_train_accuracies += results['train_accuracies']
        all_val_accuracies += results['val_accuracies']

        # Test model
        results = _test_dl(nirs_test, labels_test, clf, device)
        all_y_true += results['y_true']
        all_y_pred += results['y_pred']
        accuracies.append(results['test_accuracy'])
        prfs = precision_recall_fscore_support(
            results['y_true'], results['y_pred'], average='weighted')
        additional_metrics.append(prfs[:-1])

    # Plot all loss and accuracy graphs
    _, axes = plt.subplots(ncols=2, figsize=(16, 6))
    dict_losses = {'k': all_ks, 'Epoch': all_epochs,
                   'Training': all_train_losses,
                   'Validation': all_val_losses}
    df_losses = DataFrame(dict_losses)
    df_losses = df_losses.melt(id_vars=['k', 'Epoch'],
                               value_vars=['Training', 'Validation'],
                               var_name='Condition', value_name='Loss')
    sns.lineplot(ax=axes[0], data=df_losses, y='Loss', x='Epoch',
                 hue='Condition', units='k', estimator=None)
    dict_accuracies = {'k': all_ks, 'Epoch': all_epochs,
                       'Training': all_train_accuracies,
                       'Validation': all_val_accuracies}
    df_accuracies = DataFrame(dict_accuracies)
    df_accuracies = df_accuracies.melt(id_vars=['k', 'Epoch'],
                                       value_vars=['Training', 'Validation'],
                                       var_name='Condition',
                                       value_name='Accuracy')
    sns.lineplot(ax=axes[1], data=df_accuracies, y='Accuracy', x='Epoch',
                 hue='Condition', units='k', estimator=None)
    plt.savefig(f'{output_folder}/graphs.png', bbox_inches='tight')
    plt.show()
    plt.close()

    # Figures
    cm = confusion_matrix(all_y_true, all_y_pred, normalize='true')
    sns.heatmap(cm, annot=True, cmap='crest', vmin=0.1, vmax=0.8)
    plt.xlabel('Predicted')
    plt.ylabel('Ground truth')
    plt.savefig(f'{output_folder}/confusion_matrix.png')
    plt.close()

    accuracies = np.array(accuracies)

    return accuracies, all_hps, additional_metrics


def _train_encdec(x_train, y_train, encoder, decoder, batch_size, lr,
                  max_epoch, early_stop, random_state, device):
    """
    Train a deep learning encoder-decoder with PyTorch.
    """
    # Load data
    if early_stop:
        split = train_test_split(x_train, y_train, shuffle=True,
                                 train_size=0.80, random_state=random_state)
        x_train, y_train = split[0], split[2]
        x_val, y_val = split[1], split[3]
        dataset_val = _DatasetFromNumPy(x_val, y_val)
        val_loader = DataLoader(dataset=dataset_val, batch_size=1,
                                shuffle=False)
    dataset_train = _DatasetFromNumPy(x_train, y_train)
    train_loader = DataLoader(dataset=dataset_train, batch_size=batch_size,
                              shuffle=True)

    # Instantiate model and hyperparameters
    device_count = torch.cuda.device_count()
    if device_count > 1:  # use multiple GPUs
        encoder = nn.DataParallel(encoder)
        decoder = nn.DataParallel(decoder)
    encoder.to(device)
    decoder.to(device)
    criterion = nn.MSELoss()
    params = list(encoder.parameters()) + list(decoder.parameters())
    optimizer = optim.Adam(params, lr=lr)

    train_losses = []
    val_losses = []
    bf = "    > Model training: {l_bar}{bar}| Epoch {n_fmt}/{total_fmt}"
    disable = False
    if not stdout.isatty():
        try:
            __IPYTHON__
        except NameError:
            disable = True
    pbar = trange(
        max_epoch, bar_format=bf, leave=False, disable=disable, ascii=True)
    for epoch in pbar:
        # Train
        encoder.train()
        decoder.train()
        running_loss = 0.0
        for i, data in enumerate(train_loader):
            # Get the inputs
            x, y = data[0].to(device), data[1].to(device)

            # Zero the parameter gradients
            optimizer.zero_grad()

            # Forward
            features = encoder(x)
            outputs = decoder(features)
            loss = criterion(outputs, y)

            # Backward & optimize
            loss.backward()
            optimizer.step()

            # Get statistics
            running_loss += loss.item()
        train_losses.append(running_loss / (i+1))

        # if epoch % 5 == 0:
        #     print(f'Loss: {train_losses[-1]}')

        if early_stop:
            # Validate
            encoder.eval()
            decoder.eval()
            with torch.no_grad():
                running_loss = 0.0
                for i, data in enumerate(val_loader):
                    x, y = data[0].to(device), data[1].to(device)
                    features = encoder(x)
                    outputs = decoder(features)
                    loss = criterion(outputs, y)
                    running_loss += loss.item()
                val_losses.append(running_loss / (i+1))
                last_sorted = sorted(val_losses[-PATIENCE:])
                if epoch >= PATIENCE and val_losses[-PATIENCE:] == last_sorted:
                    print(f'    > Early stopping after {epoch+1} epochs')
                    break

    if device_count > 1:
        encoder = encoder.module
        decoder = decoder.module

    results = {'train_losses': train_losses,
               'val_losses': val_losses}
    return encoder, decoder, results


def _test_encdec(x_test, y_test, encoder, decoder, device):
    """
    Test a deep learning encoder-decoder with PyTorch.
    """
    # Load data sets
    dataset_test = _DatasetFromNumPy(x_test, y_test)
    test_loader = DataLoader(dataset=dataset_test, batch_size=1,
                             shuffle=False)

    if torch.cuda.device_count() > 1:  # use multiple GPUs
        encoder = nn.DataParallel(encoder)
        decoder = nn.DataParallel(decoder)
    encoder.to(device)
    decoder.to(device)
    criterion = nn.MSELoss()

    # Test
    encoder.eval()
    decoder.eval()
    with torch.no_grad():
        running_loss = 0.0
        for i, data in enumerate(test_loader):
            x, y = data[0].to(device), data[1].to(device)
            features = encoder(x)
            outputs = decoder(features)
            loss = criterion(outputs, y)
            running_loss += loss.item()

        results = {'test_loss': running_loss / (i+1)}
    return results


def _proxy_selec(nirs_train, targets_train, groups_train, enc_class, dec_class,
                 batch_sizes, lrs, max_epoch, random_state, output_folder):
    """
    Train and fine-tune encoder-decoder.
    """
    # Set device
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    if random_state:
        torch.manual_seed(random_state)

    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    if groups_train is None:
        in_kf = KFold(n_splits=INNER_K)
    else:
        in_kf = GroupKFold(n_splits=INNER_K)

    # Encoder-decoder fine-tuning
    hp_list = list(itertools.product(batch_sizes, lrs))
    if len(hp_list) > 1:
        print('    > Hyperparameter selection')
        in_losses = [[] for _ in hp_list]
        for i, hp in enumerate(hp_list):
            batch_size, lr = hp[0], hp[1]
            in_split = in_kf.split(nirs_train, targets_train, groups_train)
            for in_idx in in_split:
                nirs_in_train = nirs_train[in_idx[0]]
                targets_in_train = targets_train[in_idx[0]]
                nirs_val = nirs_train[in_idx[1]]
                targets_val = targets_train[in_idx[1]]

                encoder = enc_class().double()
                decoder = dec_class().double()
                encoder, decoder, _ = _train_encdec(
                    nirs_in_train, targets_in_train, encoder, decoder,
                    batch_size, lr, max_epoch, False, random_state, device)

                results = _test_encdec(nirs_val, targets_val, encoder, decoder,
                                       device)
                in_losses[i].append(results['test_loss'])

        # Get best hyperparameters
        in_average_losses = np.mean(in_losses, axis=1)
        index_best = np.argmin(in_average_losses)
        best_hps = hp_list[index_best]
    else:
        best_hps = (batch_sizes[0], lrs[0])

    # Retrain with best hyperparameters
    encoder = enc_class().double()
    decoder = dec_class().double()
    encoder, decoder, results = _train_encdec(
        nirs_train, targets_train, encoder, decoder,
        best_hps[0], best_hps[1], max_epoch, True, random_state, device)

    # Save trained model and training results
    encoder.cpu()
    decoder.cpu()
    torch.save(encoder.state_dict(), f'{output_folder}/encoder.pt')
    torch.save(decoder.state_dict(), f'{output_folder}/decoder.pt')
    with open(f'{output_folder}/hps.pickle', 'wb') as f:
        pickle.dump(best_hps, f)
    with open(f'{output_folder}/results.pickle', 'wb') as f:
        pickle.dump(results, f)

    # Plot loss graph
    _, ax = plt.subplots(figsize=(12, 6))
    epochs = [epoch for epoch in range(len(results['train_losses']))]
    dict_losses = {'Epoch': epochs,
                   'Training': results['train_losses'],
                   'Validation': results['val_losses']}
    df_losses = DataFrame(dict_losses)
    df_losses = df_losses.melt(id_vars=['Epoch'],
                               value_vars=['Training', 'Validation'],
                               var_name='Condition', value_name='Loss')
    sns.lineplot(ax=ax, data=df_losses, y='Loss', x='Epoch',
                 hue='Condition', estimator=None)
    plt.savefig(f'{output_folder}/graph.png', bbox_inches='tight')
    plt.close()

    return encoder, decoder


def deep_transfer_learn(nirs, labels, groups, enc_class, dec_class,
                        model_class, normalize=None,
                        batch_sizes=[4, 8, 16, 32, 64],
                        lrs=[1e-5, 1e-4, 1e-3, 1e-2, 1e-1], max_epoch=100,
                        random_state=None, output_folder='./outputs'):
    """
    Perform nested k-fold cross-validation for a deep transfer learning model.
    Produces loss graphs, accuracy graph and confusion matrice. This is made
    with early stopping (with a validation set of 20 %) once the model has been
    fine tuned on the inner loop of the nested k-fold cross-validation. The
    number of classes is deduced from the number of unique labels.

    Parameters
    ----------
    nirs : array of shape (n_epochs, n_channels, n_times)
        Processed NIRS data.

    labels : array of integers
        List of labels matching the NIRS data. Must include values 8 for all
        the unlabeled segments this should be performed by `process_epochs`.

    groups : array of integers | None
        List of subject ID matching the epochs to perfrom a group k-fold
        cross-validation. If ``None``, performs a stratified k-fold
        cross-validation instead.

    enc_class : PyTorch nn.Module class
        The PyTorch encoder class to use for each Hb channel type.

    dec_class : PyTorch nn.Module class
        The PyTorch decoder class to use for each Hb channel type.

    model_class : PyTorch nn.Module class
        The PyTorch classifier class to use for the overall classification
        containing the Hb encoders. The ``__init__()`` method must accept the
        number of classes, an encoder for HbO and an encoder for HbR as
        parameters. The number of classes needs to be the number of output
        neurons.

    normalize : tuple of integers | None
        Axes on which to normalize data before feeding to the model with
        min-max scaling based on the train set for each iteration of the outer
        cross-validation. For example (0, 2) to normalize across epochs and
        time. Defaults to ``None`` for no normalization.

    batch_sizes : list of integers
        List of batch sizes to test for fine-tuning.

    lrs : list of floats
        List of learning rates to test for fine-tuning.

    max_epoch : integer
        Maximum number of epochs possible for training. Defaults to ``100``.

    random_state : integer | None
        Controls the shuffling applied to data and random model initialization.
        Pass an integer for reproducible output across multiple function calls.
        Defaults to ``None`` for not setting the seed.

    output_folder : string
        Path to the directory into which the figures will be saved. Defaults to
        ``'./outputs'``.

    Returns
    -------
    accuracies : array of floats
        List of accuracies for the overall classifier on the test sets (one for
        each iteration of the outer cross-validation).

    all_hps : list of tuples
        List of best hyperparameters for the overall classifier (one tuple for
        each iteration of the outer cross-validation). Each tuple will be
        `(batch size, learning rate)`.

    additional_metrics : list of tuples
        List of tuples of metrics composed of (precision, recall, F1 score) on
        the outer cross-validation (one tuple for each iteration of the outer
        cross-validation). This uses the ``precision_recall_fscore_support``
        function from scikit-learn with ``average='weighted'``, ``y_true`` and
        ``y_pred`` being the true and the predictions on the specific iteration
        of the outer cross-validation.

    :meta private:
    """
    if random_state:
        torch.manual_seed(random_state)

    print(f'Labels: {set(labels)}')
    if 8 in set(labels):
        n_classes = len(set(labels)) - 1  # minus unlabelled
    else:
        n_classes = len(set(labels))

    print(f'Deep transfer learning: {enc_class.__name__}/'
          f'{dec_class.__name__}-{model_class.__name__}', end=' ')

    # Set device
    if torch.cuda.is_available():
        device = torch.device('cuda:0')
        device_count = torch.cuda.device_count()
        print(f"(using {device_count} GPU{'s' if device_count > 1 else ''})")
    else:
        device = torch.device('cpu')
        print("(using CPU)")

    # Get index to split channel types
    mid_idx = nirs.shape[1] / 2
    if mid_idx.is_integer():
        mid_idx = int(mid_idx)

    # Outer split
    if os.path.isfile(f'{output_folder}/split.pickle'):
        print('    Saved k-fold split found, loading it...', end=' ')
        with open(f'{output_folder}/split.pickle', 'rb') as f:
            out_split = pickle.load(f)
        print('Done!')
    else:
        if groups is None:
            out_kf = StratifiedKFold(n_splits=OUTER_K)
        else:
            out_kf = GroupKFold(n_splits=OUTER_K)
        out_split = list(out_kf.split(nirs, labels, groups))

        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        with open(f'{output_folder}/split.pickle', 'wb') as f:
            pickle.dump(out_split, f)

    # Inner split
    if groups is None:
        in_kf = StratifiedKFold(n_splits=INNER_K)
    else:
        in_kf = GroupKFold(n_splits=INNER_K)

    for k, out_idx in enumerate(out_split):
        print(f'    Training outer fold #{k}')
        nirs_train = nirs[out_idx[0]]
        labels_train = labels[out_idx[0]]

        if groups is None:
            groups_train = None
            nirs_train, labels_train = shuffle(
                nirs_train, labels_train, random_state=random_state)
        else:
            groups_train = groups[out_idx[0]]
            nirs_train, labels_train, groups_train = shuffle(
                nirs_train, labels_train, groups_train,
                random_state=random_state)

        # Min-max scaling
        if normalize:
            maxs = nirs_train.max(axis=normalize, keepdims=True)
            mins = nirs_train.min(axis=normalize, keepdims=True)
            nirs_train = (nirs_train - mins) / (maxs - mins)

        # Train and optimise self-supervised models
        nirs_train_hbo = nirs_train[:, mid_idx:, :]
        nirs_train_hbr = nirs_train[:, :mid_idx, :]
        # HbO -> HbR
        if os.path.isfile(f'{output_folder}/k{k}/hbo/encoder.pt'):
            print('    > HbO encoder checkpoint found, loading it...', end=' ')
            enc_hbo = enc_class().double()
            enc_hbo.load_state_dict(
                torch.load(f'{output_folder}/k{k}/hbo/encoder.pt'))
            print('Done!')
        else:
            enc_hbo, _ = _proxy_selec(
                nirs_train_hbo, nirs_train_hbr, groups_train,
                enc_class, dec_class, batch_sizes=batch_sizes, lrs=lrs,
                max_epoch=max_epoch, random_state=random_state,
                output_folder=f'{output_folder}/k{k}/hbo')
        # HbR -> HbO
        if os.path.isfile(f'{output_folder}/k{k}/hbr/encoder.pt'):
            print('    > HbR encoder checkpoint found, loading it...', end=' ')
            enc_hbr = enc_class().double()
            enc_hbr.load_state_dict(
                torch.load(f'{output_folder}/k{k}/hbr/encoder.pt'))
            print('Done!')
        else:
            enc_hbr, _ = _proxy_selec(
                nirs_train_hbr, nirs_train_hbo, groups_train,
                enc_class, dec_class, batch_sizes=batch_sizes, lrs=lrs,
                max_epoch=max_epoch, random_state=random_state,
                output_folder=f'{output_folder}/k{k}/hbr')

        if os.path.isfile(f'{output_folder}/k{k}/clf.pt'):
            print('    > Classifier checkpoint found, skipping training')
        else:
            # Train classifier for each combination of hyperparameters
            hp_list = list(itertools.product(batch_sizes, lrs))
            if len(hp_list) > 1:
                print('    > Hyperparameter selection')
                in_accuracies = [[] for _ in hp_list]
                for i, hp in enumerate(hp_list):
                    batch_size, lr = hp[0], hp[1]
                    in_split = in_kf.split(nirs_train, labels_train,
                                           groups_train)
                    for in_idx in in_split:
                        nirs_in_train = nirs_train[in_idx[0]]
                        labels_in_train = labels_train[in_idx[0]]
                        nirs_val = nirs_train[in_idx[1]]
                        labels_val = labels_train[in_idx[1]]

                        # Remove unlabelled examples
                        idx_in_train = np.where(np.array(labels_in_train) != 8)
                        labels_in_train = labels_in_train[idx_in_train]
                        nirs_in_train = nirs_in_train[idx_in_train]
                        idx_val = np.where(np.array(labels_val) != 8)
                        labels_val = labels_val[idx_val]
                        nirs_val = nirs_val[idx_val]

                        clf = model_class(n_classes, enc_hbo, enc_hbr).double()
                        clf, _ = _train_dl(nirs_in_train, labels_in_train,
                                           clf, batch_size, lr, max_epoch,
                                           False, random_state, device)
                        results = _test_dl(nirs_val, labels_val, clf, device)
                        in_accuracies[i].append(results['test_accuracy'])

                # Get best hyperparameters
                in_average_accuracies = np.mean(in_accuracies, axis=1)
                index_max = np.argmax(in_average_accuracies)
                best_hps = hp_list[index_max]
            else:
                best_hps = (batch_sizes[0], lrs[0])

            # Retrain with best hyperparameters
            idx_train = np.where(np.array(labels_train) != 8)
            labels_train = labels_train[idx_train]
            nirs_train = nirs_train[idx_train]
            clf = model_class(n_classes, enc_hbo, enc_hbr).double()
            clf, results = _train_dl(nirs_train, labels_train,
                                     clf, best_hps[0], best_hps[1], max_epoch,
                                     True, random_state, device)

            # Save trained model and training results
            clf.cpu()
            torch.save(clf.state_dict(), f'{output_folder}/k{k}/clf.pt')
            with open(f'{output_folder}/k{k}/hps.pickle', 'wb') as f:
                pickle.dump(best_hps, f)
            with open(f'{output_folder}/k{k}/results.pickle', 'wb') as f:
                pickle.dump(results, f)

            # Plot outer fold loss graph
            _, ax = plt.subplots(figsize=(12, 6))
            epochs = [epoch for epoch in range(len(results['train_losses']))]
            dict_losses = {'Epoch': epochs,
                           'Training': results['train_losses'],
                           'Validation': results['val_losses']}
            df_losses = DataFrame(dict_losses)
            df_losses = df_losses.melt(
                id_vars=['Epoch'], value_vars=['Training', 'Validation'],
                var_name='Condition', value_name='Loss')
            sns.lineplot(ax=ax, data=df_losses, y='Loss', x='Epoch',
                         hue='Condition', estimator=None)
            plt.savefig(f'{output_folder}/k{k}/clf_graph.png',
                        bbox_inches='tight')
            plt.close()

    all_ks, all_epochs = [], []
    all_train_losses, all_val_losses = [], []
    all_train_accuracies, all_val_accuracies = [], []
    all_y_true, all_y_pred = [], []
    accuracies, all_hps, additional_metrics = [], [], []
    for k, out_idx in enumerate(out_split):
        print(f'    Testing outer fold #{k}')
        nirs_train, nirs_test = nirs[out_idx[0]], nirs[out_idx[1]]
        labels_test = labels[out_idx[1]]

        # Min-max scaling of test set using training set only to avoid leakage
        if normalize:
            maxs = nirs_train.max(axis=normalize, keepdims=True)
            mins = nirs_train.min(axis=normalize, keepdims=True)
            nirs_test = (nirs_test - mins) / (maxs - mins)

        # Load trained model, hyperparameters and training results
        enc_hbo = enc_class().double()
        enc_hbr = enc_class().double()
        enc_hbo.load_state_dict(
            torch.load(f'{output_folder}/k{k}/hbo/encoder.pt'))
        enc_hbr.load_state_dict(
            torch.load(f'{output_folder}/k{k}/hbr/encoder.pt'))
        clf = model_class(n_classes, enc_hbo, enc_hbr).double()
        clf.load_state_dict(torch.load(f'{output_folder}/k{k}/clf.pt'))
        with open(f'{output_folder}/k{k}/hps.pickle', 'rb') as f:
            best_hps = pickle.load(f)
        with open(f'{output_folder}/k{k}/results.pickle', 'rb') as f:
            results = pickle.load(f)

        # Append training details
        all_hps.append(best_hps)
        all_ks += [k for _ in results['train_losses']]
        all_epochs += [epoch for epoch in range(len(results['train_losses']))]
        all_train_losses += results['train_losses']
        all_val_losses += results['val_losses']
        all_train_accuracies += results['train_accuracies']
        all_val_accuracies += results['val_accuracies']

        # Test model
        idx_test = np.where(np.array(labels_test) != 8)
        labels_test = labels_test[idx_test]
        nirs_test = nirs_test[idx_test]
        results = _test_dl(nirs_test, labels_test, clf, device)
        all_y_true += results['y_true']
        all_y_pred += results['y_pred']
        accuracies.append(results['test_accuracy'])
        prfs = precision_recall_fscore_support(
            results['y_true'], results['y_pred'], average='weighted')
        additional_metrics.append(prfs[:-1])

    # Plot all loss and accuracy graphs
    _, axes = plt.subplots(ncols=2, figsize=(16, 6))
    dict_losses = {'k': all_ks, 'Epoch': all_epochs,
                   'Training': all_train_losses,
                   'Validation': all_val_losses}
    df_losses = DataFrame(dict_losses)
    df_losses = df_losses.melt(id_vars=['k', 'Epoch'],
                               value_vars=['Training', 'Validation'],
                               var_name='Condition', value_name='Loss')
    sns.lineplot(ax=axes[0], data=df_losses, y='Loss', x='Epoch',
                 hue='Condition', units='k', estimator=None)
    dict_accuracies = {'k': all_ks, 'Epoch': all_epochs,
                       'Training': all_train_accuracies,
                       'Validation': all_val_accuracies}
    df_accuracies = DataFrame(dict_accuracies)
    df_accuracies = df_accuracies.melt(id_vars=['k', 'Epoch'],
                                       value_vars=['Training', 'Validation'],
                                       var_name='Condition',
                                       value_name='Accuracy')
    sns.lineplot(ax=axes[1], data=df_accuracies, y='Accuracy', x='Epoch',
                 hue='Condition', units='k', estimator=None)
    plt.savefig(f'{output_folder}/graphs.png', bbox_inches='tight')
    plt.show()
    plt.close()

    # Figures
    cm = confusion_matrix(all_y_true, all_y_pred, normalize='true')
    sns.heatmap(cm, annot=True, cmap='crest', vmin=0.1, vmax=0.8)
    plt.xlabel('Predicted')
    plt.ylabel('Ground truth')
    plt.savefig(f'{output_folder}/confusion_matrix.png')
    plt.close()

    accuracies = np.array(accuracies)

    return accuracies, all_hps, additional_metrics
