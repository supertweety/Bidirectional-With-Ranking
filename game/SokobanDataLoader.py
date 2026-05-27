import torch
import numpy as np
import lightning as L
from torch.utils.data import DataLoader, Subset

from game.getData import get_data, get_paths
class SokobanDataModule(L.LightningDataModule):
    def __init__(self, data_dir: str = "path/to/dir", path_dir: str = "path/to/path_dir", batch_size: int = 32):
        super().__init__()
        self.state_dir = data_dir
        self.path_dir = path_dir
        self.batch_size = batch_size

    def setup(self, stage: str):
        states = get_data()
        paths = get_paths()
        train_size = int(0.8 * len(states))
        val_size = int(0.1 * len(states))
        test_size = len(states) - train_size - val_size

        # 1. Create shuffled indices
        indices = list(range(len(states)))
        np.random.shuffle(indices)

        # 2. Calculate split points
        train_split = int(0.8 * len(states))
        val_split = int(0.9 * len(states))

        # 3. Create subsets
        train_indices = indices[:train_split]
        val_indices = indices[train_split:val_split]
        test_indices = indices[val_split:]

        train_set = Subset(states, train_indices)
        val_set = Subset(states, val_indices)
        test_set = Subset(states, test_indices)

    def train_dataloader(self):
        return DataLoader(self.mnist_train, batch_size=self.batch_size)

    def val_dataloader(self):
        return DataLoader(self.mnist_val, batch_size=self.batch_size)

    def test_dataloader(self):
        return DataLoader(self.mnist_test, batch_size=self.batch_size)

    def predict_dataloader(self):
        return DataLoader(self.mnist_predict, batch_size=self.batch_size)