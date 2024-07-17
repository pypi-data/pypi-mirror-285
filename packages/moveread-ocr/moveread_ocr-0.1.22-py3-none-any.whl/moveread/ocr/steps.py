from typing import Sequence, TextIO, Callable, Any
from haskellian import dicts as D
import keras
import tensorflow as tf
from tf.tools import tf_function
import tf.ctc as ctc

def evaluate(
  val_ds: tf.data.Dataset, val_step: Callable[[Any], dict[str, tf.Tensor]],
  *, logstream: TextIO | None = None,
  logfreq: int = 10, n_batches: int | None = None
):
  metrics = []
  for i, batch in enumerate(val_ds):
    m = val_step(batch)
    metrics.append(m)
    if logstream and i % logfreq == logfreq - 1:
      avg = D.aggregate(tf.reduce_mean, metrics)
      avg = D.map(float, avg)
      display = ' - '.join([f'{k}: {v:.3f}' for k, v in avg.items()])
      prog = f'{i+1}/{n_batches}' if n_batches else i+1
      print(f'\r{prog} - {display}\t\t', end='', file=logstream, flush=True)
      
  avg = D.aggregate(tf.reduce_mean, metrics)
  return D.map(float, avg)

def compile_train(model: keras.Model, opt: keras.Optimizer):
  @tf_function
  def train_step(batch):
    x, y = batch
    with tf.GradientTape() as tape:
      z = model(x, training=True)
      loss = tf.clip_by_value(ctc.loss(y, z), 0, 100) # clip to avoid NaNs, shouldn't get over 100 anyway

    grads = tape.gradient(loss, model.trainable_variables)
    opt.apply_gradients(zip(grads, model.trainable_variables)) # type: ignore (idk tbh)
    return loss, z
  
  return train_step

def compile_val(model: keras.Model, *, top_ks: Sequence[int] = [5, 25], max_edit_dist: float = 100):
  """Returns `(evaluate, metrics_step)`"""
  top_paths = max(top_ks, default=1)

  @tf_function
  def metrics_step(y, z):
    paths, _ = ctc.beam_decode(z, top_paths=top_paths)
    return {
      'accuracy': ctc.preds_accuracy(y, paths[:1]),
      'edit_distance': tf.clip_by_value(ctc.preds_edit_distance(y, paths[:1]), 0, max_edit_dist),
    } | {
      f'accuracy{k}': ctc.preds_accuracy(y, paths[:k]) for k in top_ks
    } | {
      f'edit_distance{k}': tf.clip_by_value(ctc.preds_edit_distance(y, paths[:k]), 0, max_edit_dist) for k in top_ks
    }
  
  @tf_function
  def val_step(batch):
    x, y = batch
    z = model(x, training=False)
    return metrics_step(y, z) | {'loss': tf.reduce_mean(ctc.loss(y, z)) }
  
  return val_step, metrics_step