#tensorboard --logdir lightning_logs
from sklearn.model_selection import train_test_split
import torch
import pandas as pd
import numpy as np
import pytorch_lightning as pl
from tqdm.auto import tqdm
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from multiprocessing import cpu_count
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger
from torchmetrics import Accuracy

class signalsDataModule(pl.LightningDataModule):
    """
    Datamodule (based on the Datamodule from pytorch lightning)
    for easier model manipulation
    """
    def __init__(self, train_signals, batch_size, test_signals = [], val_ratio = 0.2) -> None:
        """
        Constructor
        Args:
            train_signals : [(np.ndarray, bool)] - list of tuples in the form (signal, label) - contains training and validation dataset for the model
            batch_size : int - batch size
            test_signals : [(np.ndarray, bool)] or empty - specific train signals if we want to use the .test() built-in method
            val_ratio : float - validation/train split ratio
        """
        super().__init__()
        self.train_signals, self.val_signals = train_test_split(train_signals, test_size = val_ratio)
        self.test_signals = test_signals
        self.batch_size = batch_size
    
    def setup(self, stage = None):
        """
        Sets up the train and validation signals dataset
        Args:
            None
        Returns:
            None
        """
        self.train_dataset = signalDataset(self.train_signals)
        self.val_dataset = signalDataset(self.val_signals)
        self.test_dataset = signalDataset(self.test_signals)
    
    def train_dataloader(self):
        """
        Sets up the train dataloader
        Args:
            None
        Returns:
            None
        """
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=cpu_count(),
            persistent_workers=True
        )
    def val_dataloader(self):
        """
        Sets up the train dataloader
        Args:
            None
        Returns:
            None
        """
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=cpu_count(),
            persistent_workers=True
        )
    def test_dataloader(self):
        """
        Sets up the train dataloader
        Args:
            None
        Returns:
            None
        """
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=cpu_count()
        )
class signalDataset(Dataset):
    """
        Creates a datased used by the dataloaders
    """
    def __init__(self, signals) -> None:
        self.signals = signals
    def __len__(self):
        return len(self.signals)
    def __getitem__(self, index):
        signal, label = self.signals[index]
        return dict(
            signal = torch.Tensor(signal.to_numpy()),
            label = torch.tensor(label).long()
        )
    
class LSTMModule(nn.Module):
    """
    This module implements the LSTM-based predictor
    """
    def __init__(self, n_features, n_classes, n_hidden=256, n_layers = 3) -> None:
        """
            n_features : int - dimensionality of the input signal (in the case of our signals 6)
            n_classes  : int - number of output classes
            n_hidden : int - size of the hidden state vector
            n_layers : int - number of LSTM layers
        """
        super().__init__()
        self.n_hidden = n_hidden

        self.ltsm = nn.LSTM(input_size = n_features,
                            hidden_size = n_hidden,
                            num_layers = n_layers,
                            batch_first = True,
                            dropout = 0.75)
        self.classifier = nn.Linear(n_hidden, n_classes)
    
    def forward(self, resampled_signal):
        """
        Returns a result of the forward pass of the network
        Args:
            resampled_signal : torch.Tensor - singal to be put through the forward pass
        Returns:
            torch.Tensor - output of the classifier
        """
        self.ltsm.flatten_parameters()
        _, (hidden, _) = self.ltsm(resampled_signal)
        out = hidden[-1]
        sigm = nn.Sigmoid()
        out_ = sigm(out)
        return self.classifier(out_)


class lstmClassifier(pl.LightningModule):
    def __init__(self, n_features, n_classes, n_hidden_lstm = 256) -> None:
        super().__init__()
        self.model = LSTMModule(n_features, n_classes, n_hidden = n_hidden_lstm)
        self.criterion = nn.CrossEntropyLoss()
        self.accuracy = Accuracy(task="multiclass", num_classes=2)
    
    def forward(self, signal, labels = None):
        """
        Implements pl.LightningModule based forward loop
        Args:
            signal : torch.Tensor - signal to be predicted
        Returns:
            loss
            output
        """
        output = self.model(signal)
        loss = 0
        if labels is not None:
            loss = self.criterion(output, labels)
        return loss, output
    
    def predict(self, signal):
        """
        Default prediction method
        Args:
            signal : np.ndarray - signal to be predicted
        Returns:
            bool - True if anomaly else False
        """
        def resample_ts(ts):
            return ts[600:900:2]
        self.freeze()
        signal_ = resample_ts(signal)
        if isinstance(signal, pd.DataFrame):
            signal_ = torch.Tensor(signal_.to_numpy())
        elif isinstance(signal, np.ndarray):
            signal_ = torch.Tensor(signal_)
        elif isinstance(signal, torch.Tensor):
            signal_ = signal
        else:
            print("WARN: Unknown input type, aborting process.")
            return
        _, out = self.forward(signal_.unsqueeze(dim=0))
        self.unfreeze()
        return bool(torch.argmax(out, dim=1).item())
    
    def train_classifier(self, train_data : tuple[pd.DataFrame, bool], N_EPOCHS : int, BATCH_SIZE : int = 54, val_ratio = 0.2, weighted_loss = True, weight = 1):
        """
        Default method to train the classifier.
        Args:
            train_data  - training dataset
            N_EPOCHS : int - number of training epochs
            BATCH_SIZE : int - batch size
            val_ratio : 0.2 - validation step ratio
            weighted_loss : boll - use weighted loss
            weight : float - weight of the weighted loss if 1 the positive predictions are the same importance as negative predictions with regards to their
                representation within the training dataset.
        Returns:
            None
        """
        if weighted_loss:
            print("INFO: Setting weighted loss.")
            n_bad = np.sum([i[1] for i in train_data])
            n_good = len(train_data) - n_bad
            weights = 1. / torch.tensor([weight * n_good, n_bad])
            class_weights = (weights / weights.sum())
            class_weights = class_weights * 1/min(class_weights)
            self.criterion = nn.CrossEntropyLoss(weight=class_weights)
            print(f"INFO: Weighted loss set to {class_weights}")
        def resample_ts(ts):
            return ts[600:900:2]
        print("INFO: Preprocessing training data!")
        train_data_m = []
        for sig, label in train_data:
            train_data_m.append((resample_ts(sig), label))
        
        data_module = signalsDataModule(train_data_m, BATCH_SIZE, val_ratio=val_ratio)
        checkpoint_callback = ModelCheckpoint(
        dirpath = "./ctuFaultDetector/model_params/",
        filename="best_model",
        save_top_k = 1,
        verbose=True,
        monitor="validation_loss",
        mode="min"
        )

        logger = TensorBoardLogger("lightning_logs", name="signal_prediction")
        trainer = pl.Trainer(
        logger=logger,
        num_sanity_val_steps=2,
        enable_checkpointing=True,
        callbacks = [checkpoint_callback],
        max_epochs = N_EPOCHS
        )

        trainer.fit(self, data_module)
        
        

    def training_step(self, batch):
        """
        Defines the training step of the network
        Args:
            batch - training batch
        Returns:
            dict - training loss, training accuracy report
        """
        signals = batch["signal"]
        labels = batch["label"]
        loss, outputs = self(signals, labels)
        predictions = torch.argmax(outputs, dim=1)
        step_accuracy = self.accuracy(predictions, labels)

        self.log("train_loss", loss, prog_bar = True, logger = True)
        self.log("train_accuracy", step_accuracy, prog_bar = True, logger = True)
        return {"loss": loss, "accuracy" : step_accuracy}
    
    def validation_step(self, batch):
        """
        Defines the validation step of the network
        Args:
            batch - validation batch
        Returns:
            dict - validation loss, validation accuracy report
        """
        signals = batch["signal"]
        labels = batch["label"]
        loss, outputs = self(signals, labels)
        predictions = torch.argmax(outputs, dim=1)
        step_accuracy = self.accuracy(predictions, labels)

        self.log("validation_loss", loss, prog_bar = True, logger = True)
        self.log("validation_accuracy", step_accuracy, prog_bar = True, logger = True)
        return {"loss": loss, "accuracy" : step_accuracy}
    
    def testing_step(self, batch):
        """
        Defines the testing step of the network
        Args:
            batch - testing batch
        Returns:
            dict - testing loss, testing accuracy report
        """
        signals = batch["signal"]
        labels = batch["label"]
        loss, outputs = self(signals, labels)
        predictions = torch.argmax(outputs, dim=1)
        step_accuracy = self.accuracy(predictions, labels)

        self.log("test_loss", loss, prog_bar = True, logger = True)
        self.log("test_accuracy", step_accuracy, prog_bar = True, logger = True)
        return {"loss": loss, "accuracy" : step_accuracy}
    
    
    def configure_optimizers(self):
        """
        configures optimizers (method based in pl.LightningModule)
        """
        return optim.Adam(self.parameters(), lr = 0.001)
    
