import os
import typer
from moveread.ocr import cli, finetuning

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def stderr():
  import sys
  return sys.stderr

app = typer.Typer()


@app.callback()
def main(debug: bool = typer.Option(False, '--debug', help='Enable debug mode')):
  if debug:
    import debugpy
    debugpy.listen(5678)
    print('Waiting for debugger to attach...')
    debugpy.wait_for_client()
    

@app.command('predict')
def predict(
  weights: str = typer.Option(..., '-w', '--weights', help='Path to .weights.h5 file'),
  data: str = typer.Option(..., '-d', '--data', help='Path to tfrecords dataset containing an "image" field'),
  beam_width: int = typer.Option(100, '-b', '--beam-width', help='CTC beam decoding width'),
  top_paths: int = typer.Option(25, '-k', '--top-paths', help='Number of top paths to return'),
  batch_size: int = typer.Option(32, '-s', '--batch-size'),
  verbose: bool = typer.Option(False, '-v', '--verbose'),
  exp: bool = typer.Option(False, '-e', '--exp', help='Whether to exponentiate log-probabilities'),
):
  """Predicts all images into NDJSON format, one sample per line (prints to stdout)"""
  cli.predict(
    weights=weights, data=data, beam_width=beam_width, top_paths=top_paths,
    batch_size=batch_size, logstream=stderr() if verbose else None, exp=exp,
  )

@app.command('evaluate')
def evaluate(
  weights: str = typer.Option(..., '-w', '--weights', help='Path to .weights.h5 file'),
  data: str = typer.Option(..., '-d', '--data', help='Path to tfrecords dataset containing an "image" and "text" field'),
  beam_width: int = typer.Option(100, '-b', '--beam-width', help='CTC beam decoding width'),
  top_paths: list[int] = typer.Option([5, 25], '-k', '--top-paths', help='Top paths for edit distance and accuracy metrics'),
  batch_size: int = typer.Option(32, '-s', '--batch-size'),
  verbose: bool = typer.Option(False, '-v', '--verbose')
):
  """Evaluates the model on the given dataset"""
  cli.evaluate(
    weights=weights, data=data, beam_width=beam_width, top_paths=top_paths,
    batch_size=batch_size, logstream=stderr() if verbose else None
  )

@app.command('finetune')
def finetune(
  train: str = typer.Option(..., '--train', help='Path to training dataset'),
  val: list[str] = typer.Option(..., '--val', help='Paths to validation datasets'),
  weights: str = typer.Option(..., '-w', '--weights', help='Path to initial weights'),
  base_path: str = typer.Option(..., '--base-path', help='Path to save metrics, checkpoints, and hparams'),
  metrics_freq: int = typer.Option(10, '--metrics-freq', help='Frequency to log metrics'),
  epochs: int = typer.Option(20, '--epochs', help='Number of epochs'),
  batch_size: int = typer.Option(32, '--batch-size', help='Batch size'),
  learning_rate: float = typer.Option(5e-4, '--learning-rate', help='Learning rate'),
  weight_decay: float = typer.Option(0.02, '--weight-decay', help='Weight decay'),
  verbose: bool = typer.Option(False, '-v', '--verbose'),
  recursive: bool = typer.Option(False, '-r', '--recursive', help='Whether to recursively search for datasets')
):
  val_datasets = { os.path.basename(v): v for v in val }
  finetuning.run(
    train=train, val=val_datasets, weights=weights, base_path=base_path, epochs=epochs,
    batch_size=batch_size, learning_rate=learning_rate, weight_decay=weight_decay,
    metrics_freq=metrics_freq, logstream=stderr() if verbose else None,
    recursive=recursive
  )
  

@app.command('export')
def export(
  weights: str = typer.Option(..., '-w', '--weights', help='Path to .weights.h5 file'),
  output: str = typer.Option(..., '-o', '--output', help='Output path for the serving model'),
  top_paths: int = typer.Option(25, '-k', '--top-paths', help='Number of top paths to return'),
  beam_width: int = typer.Option(100, '-b', '--beam-width', help='CTC beam decoding width'),
  verbose: bool = typer.Option(False, '-v', '--verbose')
):
  """Exports the model for serving"""
  cli.export_serving(
    weights, output, top_paths=top_paths, beam_width=beam_width,
    logstream=stderr() if verbose else None
  )

records = typer.Typer()
app.add_typer(records, name='records')

# @records.command('boxes')
# def export_boxes(
#   glob: str = typer.Argument(..., help='Glob pattern to match file-datasets'),
#   output: str = typer.Option(..., '-o', '--output', help='Output path for the TFRecords dataset'),
#   recursive: bool = typer.Option(True, '-r', '--recursive', help='Recursively search for file-datasets'),
#   boxes_key: str = typer.Option('boxes', '-b', '--boxes', help='Key to extract boxes from file-datasets'),
#   compression_factor: float = typer.Option(0.4, '-c', '--compression', help='Compression factor to approximate sample size'),
#   min_shards: int = typer.Option(10, '-m', '--min-shards', help='Minimum number of shards (if `min_shard_size` passes)'),
#   min_shard_size: int = typer.Option(100*1024*1024, '-s', '--min-shard-size', help='Minimum size of a shard in bytes'),
#   verbose: bool = typer.Option(False, '-v', '--verbose'),
# ):
#   """Exports a set of boxes `files-dataset`s into a compatible TFRecords dataset
#   - Generates `{output}/{shard}.tfrecord.gz` and `{output}/meta.json`
#   """
#   cli.export_boxes(
#     glob, output=output, recursive=recursive,
#     boxes_key=boxes_key, compression_factor=compression_factor,
#     min_shards=min_shards, min_shard_size=min_shard_size,
#     logstream=stderr() if verbose else None,
#   )

@records.command('samples')
def export_samples(
  glob: str = typer.Argument(..., help='Glob pattern to match file-datasets'),
  output: str = typer.Option(..., '-o', '--output', help='Output path for the TFRecords dataset'),
  recursive: bool = typer.Option(True, '-r', '--recursive', help='Recursively search for file-datasets'),
  boxes_key: str = typer.Option('boxes', '-b', '--boxes', help='Key to extract boxes from file-datasets'),
  labels_key: str = typer.Option('labels', '-l', '--labels', help='Key to extract labels from file-datasets'),
  compression_factor: float = typer.Option(0.4, '-c', '--compression', help='Compression factor to approximate sample size'),
  min_shards: int = typer.Option(10, '-m', '--min-shards', help='Minimum number of shards (if `min_shard_size` passes)'),
  min_shard_size: int = typer.Option(100*1024*1024, '-s', '--min-shard-size', help='Minimum size of a shard in bytes'),
  verbose: bool = typer.Option(False, '-v', '--verbose'),
):
  """Exports a set of samples `ocr-dataset`s into a compatible TFRecords dataset
  - Generates `{output}/{shard}.tfrecord.gz` and `{output}/meta.json`
  """
  cli.export_samples(
    glob, output=output, recursive=recursive,
    boxes_key=boxes_key, labels_key=labels_key, compression_factor=compression_factor,
    min_shards=min_shards, min_shard_size=min_shard_size,
    logstream=stderr() if verbose else None,
  )


if __name__ == '__main__':
  import sys
  import os
  os.chdir('/home/m4rs/mr-github/rnd/ocr/test')
  sys.argv.extend([
    'finetune', '-vw', 'baseline3.weights.h5',
    '--train', 'data/train',
    '--val', 'data/val',
    '--base-path', '.',
    '--metrics-freq', '1',
    '--batch-size', '2'
  ])
  app()