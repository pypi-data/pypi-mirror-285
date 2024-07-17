from typing import Mapping, Literal
from pydantic import BaseModel, ConfigDict

class File(BaseModel):
  file: str
  compression: Literal['zstd'] | None = None
  num_lines: int | None = None

Meta = Mapping[str, File]

class MetaJson(BaseModel):
  model_config = ConfigDict(extra='allow')
  lines_dataset: Meta