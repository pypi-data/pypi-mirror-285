import os
import typer
import lines_dataset as lds

app = typer.Typer()

@app.callback()
def callback():
  """Export, list and iterate lines-datasets"""


@app.command()
def add(
  base_path: str = typer.Argument(None, help='The base path of the dataset. Defaults to .'),
  key: str = typer.Option(..., '-k', '--key', help='Key of the new file'),
  file: str = typer.Option(None, '-f', '--file', help='Path to the file. Defaults to `{key}.txt` or `{key}.txt.zst`'),
  zstd: bool = typer.Option(False, '-z', '--zstd', help='Is the file compressed with zstd?'),
  lines: int = typer.Option(None, '-l', '--lines', help='Number of lines in the file'),
):
  """Add an entry to a `meta.json`. Creates the file if needed."""
  base_path = base_path or '.'
  try:
    with open(os.path.join(base_path, 'meta.json')) as f:
      meta = lds.MetaJson.model_validate_json(f.read())
  except:
    os.makedirs(base_path, exist_ok=True)
    meta = lds.MetaJson(lines_dataset={})

  file = file or f'{key}.txt' + ('.zst' if zstd else '')
  entry = lds.File(file=file, num_lines=lines, compression='zstd' if zstd else None)
  meta.lines_dataset = {**meta.lines_dataset, key: entry}
  with open(os.path.join(base_path, 'meta.json'), 'w') as f:
    f.write(meta.model_dump_json(indent=2))

