import subprocess

def iterate(path: str):
  try:
    process = subprocess.Popen(['zstdcat', path], stdout=subprocess.PIPE, text=True)
    yield from process.stdout # type: ignore
  except FileNotFoundError:
    raise ValueError('`zstdcat` not found, please run `apt install zstd` to support zstandard decompression')
