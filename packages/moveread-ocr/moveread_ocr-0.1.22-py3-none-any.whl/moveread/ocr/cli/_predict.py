from typing import TextIO
import sys
import typer
import tf.records as tfr
import moveread.ocr as mo

def predict(
  *, weights: str, data: str, logstream: TextIO | None = None,
  batch_size: int = 32, beam_width: int = 100, top_paths: int = 25,
  exp: bool = False, labels: bool = False, ordered: bool = False,
  outstream: TextIO = sys.stdout
):

  if logstream:
    print('Predicting...', file=logstream)
    print(f'- Batch size: {batch_size}', file=logstream)
    print(f'- Beam width: {beam_width}', file=logstream)
    print(f'- Top paths: {top_paths}', file=logstream)
    print(f'- Use exp: {exp}', file=logstream)
    print(f'- Labels: {labels}', file=logstream)
    print(f'- Ordered: {ordered}', file=logstream)
    print(f'Loading model from {weights}', file=logstream)

  model, _, num2char = mo.load_model(weights)

  if logstream:
    print(f'Reading dataset from {data}', file=logstream)

  import tensorflow as tf
  dataset = tfr.Dataset.read(data)
  ds = dataset.iterate(batch_size=batch_size, mode='ordered' if ordered else None) \
    .prefetch(tf.data.AUTOTUNE)
  
  if logstream:
    print('Predicting...', file=logstream)
  
  l = dataset.len()
  num_batches = l and l // batch_size
  import orjson
  for i, x in enumerate(ds):
    if labels and not 'label' in x:
      raise typer.BadParameter('Labels are not available in the dataset')
    if logstream:
      print(f'\r{i+1}/{num_batches or "UNK"}', end='', flush=True, file=logstream)
    z = model(x['image'], training=False)
    top_preds = mo.ctc_distrib(z, num2char, beam_width=beam_width, top_paths=top_paths, exp=exp)
    for j, preds in enumerate(top_preds):
      json = orjson.dumps(preds)
      if labels:
        lab = x['label'][j].numpy()
        out = lab + b'\t' + json
      else:
        out = json
      outstream.buffer.write(out + b'\n')