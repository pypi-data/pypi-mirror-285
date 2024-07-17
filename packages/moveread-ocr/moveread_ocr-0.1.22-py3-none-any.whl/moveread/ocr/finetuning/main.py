from typing_extensions import TypedDict, Unpack, TextIO, Sequence, Mapping
import os
import json
from haskellian import iter as I
import numpy as np
import keras
import demetric as dm
from checkptr import Checkpointer
import moveread.ocr as mo

class HParams(TypedDict):
  learning_rate: float
  weight_decay: float
  batch_size: int

def create_run(base_path: str, hparams: HParams):
  logger = dm.Metrics.new(os.path.join(base_path, 'metrics'), overwrite=True)
  checkpt = Checkpointer.keras(os.path.join(base_path, 'checkpoints'))
  with open(os.path.join(base_path, 'hparams.json'), 'w') as f:
    json.dump(hparams, f, indent=2)

  return logger, checkpt

def run(
  *, train: str, val: Mapping[str, str], weights: str, base_path: str, epochs: int,
  logstream: TextIO | None = None, metrics_freq: int = 10,
  recursive: bool = False, **hparams: Unpack[HParams]
):
  
  if logstream:
    print('Loading model...', file=logstream)
  model, char2num, _ = mo.load_model(weights)
  
  if logstream:
    print('Loading datasets...', file=logstream)

  train_ds, train_n = mo.records.read_dataset(train, mode='shuffle', batch_size=hparams['batch_size'], char2num=char2num, recursive=recursive)
  train_ds = train_ds.shuffle(100)

  val_datasets = {}
  for name, path in val.items():
    val_ds, n_samples = mo.records.read_dataset(path, mode=None, batch_size=hparams['batch_size'], char2num=char2num, recursive=recursive)
    val_datasets[name] = (val_ds, n_samples and n_samples//hparams['batch_size'])

  opt = keras.optimizers.Adam(learning_rate=hparams['learning_rate'], weight_decay=hparams['weight_decay'])
  
  if logstream:
    print(f'Creating run at "{base_path}"...', file=logstream)
  logger, checkpt = create_run(base_path, hparams)
  if logstream:
    print('Starting finetuning with hyperparameters:', hparams, file=logstream)
  history = mo.finetuning.loop(
    model, train_ds, val_datasets=val_datasets, opt=opt, logger=logger, checkpt=checkpt, epochs=epochs,
    logstream=logstream, metrics_freq=metrics_freq, n_batches=train_n and train_n//hparams['batch_size'],
  )
  if logstream:
    print('Training finished', file=logstream)
  
  if logstream:
    for metric in history[0].keys():
      metrics = list(I.pluck(history, metric))
      best_epoch: int = np.argmax(metrics) if 'accuracy' in metric else np.argmin(metrics) # type: ignore
      print(f'Best {metric} at epoch {best_epoch}: {metrics[best_epoch]}', file=logstream)