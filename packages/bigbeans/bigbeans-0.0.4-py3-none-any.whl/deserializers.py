import numpy as np
import pandas as pd
import json


def _deserialize(path, file_format):
    """
    Deserialize the object from a file
    """
    if file_format == 'pkl':
        df: pd.DataFrame = pd.read_pickle(path)
        data = df.filter(like='data_')
        target = df.filter(like='target_')
        data.columns = data.columns.str.replace('data_', '')
        target.columns = target.columns.str.replace('target_', '')
        return data, target
    elif file_format == 'npz':
        npzfile = np.load(path, allow_pickle=True)
        return npzfile['data'], npzfile['target']
    else:
        raise ValueError('Unsupported format')


def deserialize_file(data_file, metadata_file):
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
        extension = metadata['format']
        return _deserialize(data_file, extension)
