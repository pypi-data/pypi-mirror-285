from typing import TextIO
import os
import pure_cv as vc
import files_dataset as fds
import ocr_dataset as ods
import tf.records as tfr
import moveread.ocr as mo
import tensorflow as tf

def sample_size(compression_factor: float = 0.4):
  """Approximated sample size in bytes"""
  return 256*64*4*compression_factor

def export_boxes(
  glob: str, output: str, *,
  recursive: bool = True, boxes_key: str = 'boxes',
  compression_factor: float = 0.4, min_shards: int = 10,
  min_shard_size: int = 100*1024*1024, logstream: TextIO | None = None
):
  """Export samples to TFRecords files
  - `glob`: glob pattern to find `ocr-dataset`s
  - `output`: base path of the output dataset. Will generate `{output}/{shard}.tfrecord.gz` and `{output}/meta.json`
  """
  datasets = fds.glob(glob, recursive=recursive)
  samples = fds.chain(datasets, boxes_key)
  n_samples = fds.len(datasets, boxes_key)
  sample_s = sample_size(compression_factor)
  if n_samples:
    min_size = tfr.shard_size(n_samples, sample_s, min_shard_bytes=min_shard_size, min_shards=min_shards)
  else:
    min_size = min_shard_size
  
  meta = tfr.MetaJson(tfrecords_dataset=tfr.Meta(
    files='*.tfrecord.gz', compression='GZIP',
    schema=mo.records.BOX_SCHEMA, # type: ignore
    num_samples=n_samples
  ))
  os.makedirs(output, exist_ok=True)
  with open(os.path.join(output, 'meta.json'), 'w') as f:
    f.write(meta.model_dump_json(indent=2, by_alias=True))

  shard_idx = 0
  def serialize(tup):
    i, sample = tup
    if logstream and i % 10 == 0:
      print(f'\r[{i+1}/{n_samples}] - shard {shard_idx}', end='', flush=True, file=logstream)
    img = sample[boxes_key]
    tensor = mo.parse_img(vc.decode(img))
    return tfr.serialize(mo.records.BOX_SCHEMA, image=tensor)

  os.makedirs(output, exist_ok=True)
  shards = samples.enumerate().map(serialize).shard(min_size, len, lazy=True)
  for shard_idx, shard in enumerate(shards):
    file = os.path.join(output, f'{shard_idx}.tfrecord.gz')
    tfr.write(shard, file, compression='GZIP')

def export_samples(
  glob: str, output: str, *,
  recursive: bool = True, boxes_key: str = 'boxes',
  compression_factor: float = 0.4, min_shards: int = 10,
  min_shard_size: int = 100*1024*1024, logstream: TextIO | None = None
):
  """Export samples to TFRecords files
  - `glob`: glob pattern to find `ocr-dataset`s
  - `output`: base path of the output dataset. Will generate `{output}/{shard}.tfrecord.gz` and `{output}/meta.json`
  """
  datasets = ods.glob(glob, recursive=recursive)
  samples = ods.chain(datasets, boxes_key)
  n_samples = ods.len(datasets, boxes_key)
  sample_s = sample_size(compression_factor)
  if n_samples:
    min_size = tfr.shard_size(n_samples, sample_s, min_shard_bytes=min_shard_size, min_shards=min_shards)
  else:
    min_size = min_shard_size
  
  os.makedirs(output, exist_ok=True)
  meta = tfr.MetaJson(tfrecords_dataset=tfr.Meta(
    files='*.tfrecord.gz', compression='GZIP',
    schema=mo.records.SCHEMA, # type: ignore
    num_samples=n_samples,
  ))
  with open(os.path.join(output, 'meta.json'), 'w') as f:
    f.write(meta.model_dump_json(indent=2, by_alias=True))

  shard_idx = 0
  def serialize(tup):
    i, sample = tup
    if logstream and i % 10 == 0:
      print(f'\r[{i+1}/{n_samples}] - shard {shard_idx}', end='', flush=True, file=logstream)
    img, lab = sample
    tensor = mo.parse_img(vc.decode(img))
    return tfr.serialize(mo.records.SCHEMA, image=tensor, label=tf.constant(lab.strip()))

  shards = samples.enumerate().map(serialize).shard(min_size, len, lazy=True)
  for shard_idx, shard in enumerate(shards):
    file = os.path.join(output, f'{shard_idx}.tfrecord.gz')
    tfr.write(shard, file, compression='GZIP')
