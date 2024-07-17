from typing import Mapping, Sequence
import string
from haskellian import iter as I
from jaxtyping import Shaped, UInt8, Float
import tensorflow as tf

VOCABULARY = string.ascii_letters + '12345678' + '-='

def decode_base64(img: Shaped[tf.Tensor, '']) -> UInt8[tf.Tensor, 'h w 1']:
  dec = tf.io.decode_base64(img)
  return tf.io.decode_png(dec, channels=1) # type: ignore

def parse_img(mat, width: int = 256, height: int = 64, *, already_gray: bool = False) -> Float[tf.Tensor, '256 64 1']:
  gray = tf.image.rgb_to_grayscale(mat) if not already_gray else mat
  neg = 255 - gray # type: ignore
  resized = tf.image.resize_with_pad(neg, height, width) # always pads to 0. I want pad = 255 (white). So, I negate the image before and after!
  unneg = 255 - resized
  transposed = tf.transpose(unneg, perm=[1, 0, 2])
  flipped = tf.image.flip_left_right(transposed)
  normalized = tf.cast(flipped, tf.float32) / 255. # type: ignore
  return normalized

def parse_base64(img: Shaped[tf.Tensor, '']) -> Float[tf.Tensor, '256 64 1']:
  return parse_img(decode_base64(img), already_gray=True)

def unflip_img(img: Shaped[tf.Tensor, "w h _"]) -> Shaped[tf.Tensor, "h w _"]:
  """Undo transposition + left-to-right flip (done for training), so that the image is nicely displayed"""
  return tf.transpose(tf.image.flip_left_right(img), [1, 0, 2])

def parse_sample(sample: tuple[bytes, str], char2num: Mapping[str, int]):
  import pure_cv as vc
  img, label = sample
  x = parse_img(vc.decode(img)) # type: ignore
  y = [char2num[c] for c in label.strip()]
  return x, y

def collate_batch(batch: tuple[tuple[tf.Tensor, Sequence[int]], ...]):
  imgs, labs = I.unzip(batch)
  return tf.stack(imgs), tf.ragged.stack(labs).to_sparse() # type: ignore