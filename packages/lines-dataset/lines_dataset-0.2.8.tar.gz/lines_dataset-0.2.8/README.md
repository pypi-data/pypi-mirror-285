# Lines Dataset

> Dead simple standard for storing/loading datasets as lines of text. Supports zstd compression.

```bash
pip install lines-dataset
```

### Format

A dataset folder looks like this:

```
my-dataset/
  meta.json
  my-inputs.txt
  my-compressed-labels.txt.zst
  other-labels.txt.zst
  ...
```

`meta.json`:
```json
{
  "lines_dataset": {
    "inputs": {
      "file": "my-inputs.txt",
      "num_lines": 3000 // optionally specify the number of lines
    },
    "labels": {
      "file": "my-compressed-labels.txt.zst",
      "compression": "zstd",
      "num_lines": 3000
    },
    "other-labels": {
      "file": "other-labels.txt.zst",
      "compression": "zstd",
      "num_lines": 2000 // not all files need to have the same number of lines, as long as samples match line by line. The shortest file will determine the length of the dataset.
    },
  },
  // you can add other stuff if you want to
}
```

### Usage

```python
import lines_dataset as lds

ds = lds.Dataset.read('path/to/my-dataset')
num_samples = ds.len('inputs', 'labels') # int | None

for x in ds.samples('inputs', 'labels'):
  x['inputs'] # "the first line of inputs.txt\n"
  x['labels'] # "the decompressed first line of labels.txt.zst\n"
```

A common convenience to use is:

```python
import lines_dataset as lds

datasets = lds.glob('path/to/datasets/*') # list[lds.Dataset]
for x in lds.chain(datasets, 'inputs', 'labels'):
  ...
```

And that's it! Simple.