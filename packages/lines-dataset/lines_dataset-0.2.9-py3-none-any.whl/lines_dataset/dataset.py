from typing_extensions import Iterable, Mapping, TypeVar, LiteralString, TextIO
from dataclasses import dataclass
import os
from haskellian import Iter, iter as I, dicts as D
from .meta import MetaJson, File

K = TypeVar('K', bound=LiteralString)

@dataclass
class Dataset(Iterable[Mapping[str, str]]):

  base_path: str
  files: Mapping[str, File]

  @staticmethod
  def read(base: str) -> 'Dataset':
    """Reads a daataset at `{path}/meta.json`. Throws if not found."""
    meta = MetaJson.read(os.path.join(base, 'meta.json'))
    return Dataset(base, meta.lines_dataset)
  
  @staticmethod
  def at(base: str) -> 'Dataset':
    """Reads or creates a new dataset at `{path}/meta.json`"""
    try:
      return Dataset.read(base)
    except:
      return Dataset(base, {})
  
  def file(self, key: str) -> File | None:
    """Metadata of a given file"""
    if key in self.files:
      file = self.files[key]
      output = file.model_copy()
      output.file = os.path.join(self.base_path, file.file)
      return output
    return None
  
  @I.lift
  def iterate(self, key: str) -> Iterable[str]:
    """Iterate lines of a single file."""
    file = self.file(key)
    if file:
      if file.compression == 'zstd':
        from .compression import iterate
        for line in iterate(file.file):
          yield line.rstrip('\n')
      else:
        with open(file.file) as f:
          for line in f:
            yield line.rstrip('\n')

  def samples(self, *keys: K) -> Iter[Mapping[K, str]]:
    """Iterate all samples of `keys`. If no `keys` are provided, iterates all files."""
    keys = keys or list(self.files.keys()) # type: ignore
    return D.zip({
      k: self.iterate(k)
      for k in keys
    })

  def __iter__(self):
    return iter(self.samples())

  def len(self, *keys: str) -> int | None:
    """Returns the minimum length of `keys` (or all files, if not provided). Returns `None` if some length is unspecified, or if some key is not found"""
    keys = keys or list(self.files.keys()) # type: ignore
    lens = [self._len(k) for k in keys]
    if None in lens:
      return None
    return min(lens) # type: ignore

  def _len(self, key: str) -> int | None:
    file = self.file(key)
    return file and file.num_lines
  

def glob(glob: str, *, recursive: bool = False, err_stream: TextIO | None = None) -> list[Dataset]:
  """Read all datasets that match a glob pattern."""
  from glob import glob as _glob
  datasets = []
  for p in sorted(_glob(glob, recursive=recursive)):
    try:
      datasets.append(Dataset.read(p))
    except Exception as e:
      if err_stream:
        print(f'Error reading dataset at {p}:', e, file=err_stream)
  return datasets

def chain(datasets: Iterable[Dataset], *keys: K) -> Iter[Mapping[K, str]]:
  """Chain multiple datasets into a single one."""
  return I.flatten([ds.samples(*keys) for ds in datasets])

def len(datasets: Iterable[Dataset], *keys: str) -> int | None:
  """Total length of `keys` in all datasets. (Count as 0 if undefined)"""
  return sum((l for ds in datasets if (l := ds.len(*keys)) is not None))