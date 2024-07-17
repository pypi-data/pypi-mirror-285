import sys
import numpy as np
import orjson
import typer
from haskellian import promise as P
import files_dataset as fds
import tf.serving as tfs

app = typer.Typer()

@app.callback()
def callback():
  ...


@app.command()
@P.run
async def predict(
  files_dataset: str = typer.Argument(..., help='Path to the files-dataset to predict'),
  endpoint: str = typer.Option('/v1/models/baseline:predict', '-e', '--endpoint', help='TFServing endpoint'),
  host: str = typer.Option('http://localhost', '--host', help='TFServing host'),
  port: int = typer.Option(8501, '--port', help='TFServing port'),
  batch_size: int = typer.Option(32, '-b', '--batch-size', help='Batch size for predictions'),
  key: str = typer.Option('image', '-k', '--key', help='Files-dataset key for the images'),
  verbose: bool = typer.Option(False, '-v', '--verbose', help='Verbose mode'),
  exponentiate: bool = typer.Option(False, '--exp', help='Whether to exponentiate the logprobabilities'),
):
  """Predict images from a `files-dataset` using a TFServing endpoint."""
  ds = fds.Dataset.read(files_dataset)
  len = ds.len(key)
  n_batches = len and int(np.ceil(len / batch_size))
  for i, batch in ds.iterate(key).batch(batch_size).enumerate():
    if verbose:
      print(f'Predicting [{i+1}/{n_batches}] ...', file=sys.stderr)
    batch64 = list(map(tfs.encode64, batch))
    e = await tfs.predict(batch64, host=host, port=port, endpoint=endpoint)
    if e.tag == 'left':
      if verbose:
        print(file=sys.stderr)
      print('ERROR:', e.value, file=sys.stderr)
    else:
      for p in e.value:
        probs = np.exp(p.logprobs).tolist() if exponentiate else p.logprobs
        obj = list(zip(p.preds, probs))
        sys.stdout.buffer.write(orjson.dumps(obj) + b'\n')
  if verbose:
    print(file=sys.stderr)