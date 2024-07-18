from jaxtyping import Int, Shaped, Float
import tensorflow as tf
import keras
import tf.ctc as ctc
from haskellian import iter as I
import numpy as np
StringLookup = keras.layers.StringLookup

def remove_blanks(path: tf.Tensor, blank: int = 0) -> tf.RaggedTensor:
  """Remove zeros from `path` across the last dimension"""
  mask = tf.not_equal(path, blank)
  return tf.ragged.boolean_mask(path, mask)

def decode_labels(labels: Int[tf.SparseTensor | tf.Tensor, "batch maxlen"], num2char: StringLookup) -> Shaped[tf.Tensor, "batch"]:
  """Converts an encoded label/prediction back into a string tensor"""
  dense = tf.sparse.to_dense(labels) if isinstance(labels, tf.SparseTensor) else labels
  chars = num2char(remove_blanks(dense))
  return tf.strings.reduce_join(chars, axis=-1)

def stringify_labels(labels: Int[tf.SparseTensor, "batch maxlen"], num2char: StringLookup) -> list[str]:
  """Converts an encoded label/prediction back into a string tensor"""
  tensor = decode_labels(labels, num2char)
  return [s.decode() for s in tensor.numpy()]

def ctc_distrib(
  logits: Float[tf.Tensor, "batch maxlen num_classes"],
  num2char: StringLookup, *,
  beam_width: int = 100, top_paths: int = 25,
  exp: bool = False
) -> list[list[tuple[str, float]]]:
  preds, probs = ctc.beam_decode(logits, beam_width=beam_width, top_paths=top_paths)
  decoded = [stringify_labels(p, num2char) for p in preds]
  samplewise_preds = I.transpose_ragged(decoded)
  return [
    list(zip(sample_preds, [float(np.exp(p) if exp else p) for p in sample_probs]))
    for sample_preds, sample_probs in zip(samplewise_preds, probs.numpy())
  ]