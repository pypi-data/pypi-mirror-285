from typing import NamedTuple
from jaxtyping import Float, Shaped
import keras
import tensorflow as tf
import tf.ctc as ctc
from .data import parse_base64
from .postprocess import decode_labels

class PreprocessBase64(keras.Layer):
  def call(self, b64imgs: Shaped[tf.Tensor, 'batch']):
    return tf.map_fn(
      parse_base64, b64imgs,
      fn_output_signature=tf.TensorSpec(shape=(256, 64, 1), dtype=tf.float32) # type: ignore
    )
  
class PredsProbs(NamedTuple):
  preds: Shaped[tf.Tensor, 'batch top_paths']
  logprobs: Float[tf.Tensor, 'batch top_paths']

class PostprocessCTC(keras.Layer):
  def __init__(
    self, num2char: keras.layers.StringLookup, *,
    beam_width: int = 100, top_paths: int = 100
  ):
    super().__init__()
    self.num2char = num2char
    self.beam_width = beam_width
    self.top_paths = top_paths

  def call(self, logits: Float[tf.Tensor, 'batch len classes']):
    paths, logps = ctc.beam_decode(logits, beam_width=self.beam_width, top_paths=self.top_paths)
    preds = [decode_labels(p, self.num2char) for p in paths]
    samplewise_preds = tf.transpose(tf.stack(preds))
    return PredsProbs(preds=samplewise_preds, logprobs=logps)
  
  
def ServingModel(
  model: keras.Model, num2char: keras.layers.StringLookup,
  *, beam_width: int = 100, top_paths: int = 25
):
  """Full-pipeline model, with pre/post processing included in the graph
  - `model :: Uint8[tf.Tensor, "width height 1"] -> Float[tf.Tensor, "batch maxlen vocabsize"]`
  - Returns `pipeline_model :: Base64String[tf.Tensor, "batch"] -> PredsProbs`
  """
  b64img = keras.layers.Input(shape=(), dtype=tf.string, name="b64_images")
  x = PreprocessBase64()(b64img)
  z = model(x)
  y = PostprocessCTC(num2char, beam_width=beam_width, top_paths=top_paths)(z)
  return keras.Model(inputs=b64img, outputs=y)