import numpy as np

from scipy.stats import linregress


def process_epochs(mne_epochs, tmax=None, tslide=None, sort=False,
                   reject_criteria=None):
    """
    Perform processing on epochs including baseline cropping, bad epoch
    removal, label extraction and  unit conversion.

    Parameters
    ----------
    mne_epochs : MNE Epochs object
        MNE epochs of filtered data with associated labels. Subject IDs are
        contained in the ``metadata`` property.

    tmax : float | None
        End time of selection in seconds. Defaults to ``None`` to keep the
        initial end time.

    tslide : float | None
        Size of the sliding window in seconds. Will crop the epochs if ``tmax``
        is not a multiple of ``tslide``. Defaults to ``None`` for no window
        sliding.

    sort : boolean
        Whether to sort channels by type (all HbO, all HbR). Defaults to
        ``False`` for no sorting.

    reject_criteria : list of floats | None
        List of the 2 peak-to-peak rejection thresholds for HbO and HbR
        channels respectively in uM. Defaults to ``None`` for no rejection.

    Returns
    -------
    nirs : array of shape (n_epochs, n_channels, n_times)
        Processed NIRS data in uM.

    labels : array of integer
        List of labels.

    groups : array of integer
        List of subject ID matching the epochs.
    """
    # Process epochs
    epochs = mne_epochs.copy()
    epochs.baseline = None
    epochs.crop(tmin=0, tmax=tmax)
    if reject_criteria is not None:
        reject = {'hbo': reject_criteria[0]*1e-6,
                  'hbr': reject_criteria[1]*1e-6}
        epochs.drop_bad(reject=reject)

    # Extract data
    labels = epochs.events[:, 2] - 1  # start at 0
    try:
        groups = epochs.metadata['Subject_ID'].to_numpy() - 1  # start at 0
    except TypeError:
        groups = None
    nirs_epochs = epochs.pick('fnirs')
    if sort:
        hbo_chs = epochs.copy().pick('hbo').ch_names
        hbr_chs = epochs.copy().pick('hbr').ch_names
        nirs_epochs.reorder_channels(hbo_chs + hbr_chs)
    nirs = nirs_epochs.get_data(copy=True)
    nirs *= 1e6  # convert from M to uM

    # Create sliding window
    if tslide is not None:
        sliding_size = int(tslide * nirs_epochs.info['sfreq'])
        r = nirs.shape[-1] % sliding_size
        if r > 0:
            nirs = nirs[:, :, :-r]  # crop to fit window size
        nirs = nirs.reshape(nirs.shape[0], nirs.shape[1], -1, sliding_size)
        labels = labels.repeat(nirs.shape[2])
        if groups:
            groups = groups.repeat(nirs.shape[2])
        nirs = nirs.swapaxes(1, 2)
        nirs = nirs.reshape(-1, nirs.shape[2], nirs.shape[3])

    print(f'Dataset shape: {nirs.shape}')

    return nirs, labels, groups


def extract_features(nirs, feature_list):
    """
    Perform feature extraction on NIRS data.

    Parameters
    ----------
    nirs : array of shape (n_epochs, n_channels, n_times)
        Processed NIRS data.

    feature_list : list of strings
        List of features to extract. The list can include ``'mean'`` for the
        mean along the time axis, ``'std'`` for standard deviation along the
        time axis and ``'slope'`` for the slope of the linear regression along
        the time axis.

    Returns
    -------
    nirs_features : array of shape (n_epochs, n_channels, n_features)
        Features extracted from NIRS data.
    """
    nirs_features = []
    for feature in feature_list:
        if feature == 'mean':
            nirs_feature = np.mean(nirs, axis=-1, keepdims=True)
        elif feature == 'std':
            nirs_feature = np.std(nirs, axis=-1, keepdims=True)
        elif feature == 'slope':
            x = range(nirs.shape[-1])
            nirs_feature = []
            for epoch in nirs:
                ep_slopes = []
                for channel in epoch:
                    ep_slopes.append(linregress(x, channel).slope)
                nirs_feature.append(ep_slopes)
            nirs_feature = np.expand_dims(nirs_feature, -1)
        nirs_features.append(nirs_feature)

    nirs_features = np.concatenate(nirs_features, axis=-1)

    return nirs_features
