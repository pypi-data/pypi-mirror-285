from typing import Literal
import tensorflow as tf
import keras
import tf.records as tfr
import moveread.ocr as mo

def valid_labels(labels, vocab: str, maxlen: int = 10, minlen: int = 2):
  or_ = '|'.join(vocab)
  vocab_regex = f'^({or_})+$'
  vocab_ok = tf.strings.regex_full_match(labels, vocab_regex)
  short_enough = tf.strings.length(labels) <= maxlen
  long_enough = tf.strings.length(labels) >= minlen
  return vocab_ok and short_enough and long_enough

def parse_labels(labels, char2num: keras.layers.StringLookup, vocab: str):
  oov_regex = f'[^{vocab}]'
  clean = tf.strings.regex_replace(labels, oov_regex, '')
  split = tf.strings.unicode_split(clean, 'UTF-8')
  tf.assert_greater(tf.size(split), 0)
  y: tf.RaggedTensor = char2num(split)
  return y.to_sparse()

def read_dataset(
  glob: str, *, batch_size: int = 32, char2num: keras.layers.StringLookup,
  mode: Literal['shuffle', 'ordered', 'deterministic'] | None = 'deterministic',
  recursive: bool = False
):
  def parse_batch(x, char2num):
    return x['image'], parse_labels(x['label'], char2num, vocab=mo.VOCABULARY)
  
  datasets = tfr.glob(glob, recursive=recursive)
  ds = tfr.concat(datasets, mode=mode, batch_size=batch_size) \
    .map(lambda x: parse_batch(x, char2num)) \
    .prefetch(tf.data.AUTOTUNE) \
    .cache()
  
  return ds, tfr.len(datasets)