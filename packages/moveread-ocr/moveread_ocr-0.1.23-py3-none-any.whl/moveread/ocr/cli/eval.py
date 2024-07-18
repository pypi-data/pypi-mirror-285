from typing import TextIO, Sequence
import moveread.ocr as mo

def evaluate(
  *, weights: str, data: str, logstream: TextIO | None = None,
  batch_size: int = 32, beam_width: int = 100,
  top_paths: Sequence[int] = [5, 25]
):
  if logstream:
    print('Evaluating...', file=logstream)
    print(f'- Batch size: {batch_size}', file=logstream)
    print(f'- Beam width: {beam_width}', file=logstream)
    print(f'- Top paths: {top_paths}', file=logstream)
    print(f'Loading model from {weights}', file=logstream)

  model, char2num, _ = mo.load_model(weights)

  if logstream:
    print(f'Reading dataset from {data}', file=logstream)

  ds, n_samples = mo.records.read_dataset(data, batch_size=batch_size, char2num=char2num, mode=None)
  
  if logstream:
    print('Compiling loop...', file=logstream)
  val_step, _ = mo.compile_val(model)

  metrics = mo.evaluate(ds, val_step, logstream=logstream, n_batches=n_samples and n_samples // batch_size)
  import orjson
  import sys
  sys.stdout.buffer.write(orjson.dumps(metrics) + b'\n')