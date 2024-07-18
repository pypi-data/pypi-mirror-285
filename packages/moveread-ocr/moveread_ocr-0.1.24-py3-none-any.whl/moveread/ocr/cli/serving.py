from typing import TextIO
import moveread.ocr as mo

def export_serving(
  weights: str, output: str, *,
  top_paths: int = 25, beam_width: int = 100,
  logstream: TextIO | None = None
):
  if logstream:
    print(f'Loading model from "{weights}"', file=logstream)
  model, _, num2char = mo.load_model(weights)
  if logstream:
    print('Compiling pipeline model', file=logstream)
  pipeline = mo.ServingModel(model, num2char, top_paths=top_paths, beam_width=beam_width)
  if logstream:
    print(f'Exporting serving model to "{output}"', file=logstream)
  pipeline.export(output)