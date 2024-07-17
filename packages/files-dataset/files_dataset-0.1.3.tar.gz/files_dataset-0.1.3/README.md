# Files Dataset

> Dead simple standard for storing/loading datasets as files. Supports TAR and ZIP archives.

```bash
pip install files-dataset
```

### Format

A dataset folder looks something like this:

```
my-dataset/
  meta.json
  car-images/
    001.jpg
    002.jpg
    003.jpg
  train-images/
    images.tar
  ...
```

`meta.json`:
```json
{
  "files_dataset": {
    "cars": {
      "archive": "car-images/*.jpg",
      "num_files": 3000 // optionally specify the number of files
    },
    "trains": {
      "archive": "train-images/images.tar",
      "format": "tar",
      "num_files": 10000
    }
  },
  // you can add other stuff if you want to
}
```

### Usage

```python
import files_dataset as fds

ds = fds.Dataset.read('path/to/my-dataset')
num_samples = ds.len('cars', 'trains') # int | None

for x in ds.samples('inputs', 'labels'):
  x['cars'] # the first car image
  x['trains'] # the first train image (extracted from the TAR archive)
```

A common convenience to use is:

```python
import files_dataset as fds

datasets = fds.glob('path/to/datasets/*') # list[fds.Dataset]
for x in fds.chain(datasets, 'trains', 'cars'):
  ...
```

And that's it! Simple.