from typing import Mapping, Literal
from pydantic import BaseModel, ConfigDict

class File(BaseModel):
  file: str
  compression: Literal['zstd'] | None = None
  num_lines: int | None = None

Meta = Mapping[str, File]

class MetaJson(BaseModel):
  model_config = ConfigDict(extra='allow')
  lines_dataset: Meta = {}

  @classmethod
  def read(cls, path: str):
    """Reads a json at `path`. Throws if it doesn't exist or is invalid."""
    with open(path) as f:
      return cls.model_validate_json(f.read())
    
  @classmethod
  def at(cls, path: str):
    """Reads from `path` or returns an empty dataset"""
    try:
      return cls.read(path)
    except:
      return cls()
    
  def dump(self, path: str):
    with open(path, 'w') as f:
      f.write(self.model_dump_json(indent=2))