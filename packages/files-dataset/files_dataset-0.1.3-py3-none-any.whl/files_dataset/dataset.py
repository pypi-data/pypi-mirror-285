from typing import Mapping, Iterable, TypeVar, TextIO
from dataclasses import dataclass
from glob import glob as _glob
import os
from haskellian import iter as I, dicts as D, Iter
from .meta import MetaJson, Archive

K = TypeVar('K', bound=str)

@dataclass
class Dataset:

  base_path: str
  archives: Mapping[str, Archive]

  @staticmethod
  def read(base: str) -> 'Dataset':
    """Reads a daataset at `{path}/meta.json`. Throws if not found."""
    with open(os.path.join(base, 'meta.json')) as f:
      meta = MetaJson.model_validate_json(f.read())
    return Dataset(base, meta.files_dataset)
  
  @staticmethod
  def at(base: str) -> 'Dataset':
    """Reads or creates a new dataset at `{path}/meta.json`"""
    try:
      return Dataset.read(base)
    except:
      return Dataset(base, {})
  
  def archive(self, key: str) -> Archive | None:
    """Metadata of a given archive"""
    if (archive := self.archives.get(key)) is not None:
      output = archive.model_copy()
      output.archive = os.path.join(self.base_path, archive.archive)
      return output
    return None
  
  @I.lift
  def iterate(self, key: str) -> Iterable[bytes]:
    """Iterate an archive's images"""
    if (archive := self.archive(key)) is not None:
      if archive.format == 'zip':
        from .compression import iterate_zip
        files = _glob(archive.archive)
        for file in files:
          yield from iterate_zip(file)
      elif archive.format == 'tar':
        from .compression import iterate_tar
        files = _glob(archive.archive)
        for file in files:
          yield from iterate_tar(file)
      else:
        files = _glob(archive.archive)
        for file in files:
          with open(file, 'rb') as f:
            yield f.read()

  def samples(self, *keys: K) -> Iter[Mapping[K, bytes]]:
    """Iterate all samples of `keys`. If no `keys` are provided, iterates all files."""
    keys = keys or list(self.archives.keys()) # type: ignore
    return D.zip({
      k: self.iterate(k)
      for k in keys
    })

  def __iter__(self):
    return iter(self.samples())

  def len(self, *keys: str) -> int | None:
    """Returns the minimum length of `keys` (or all files, if not provided). Returns `None` if some length is unspecified, or if some key is not found"""
    keys = keys or list(self.archives.keys()) # type: ignore
    lens = [self._len(k) for k in keys]
    if None in lens:
      return None
    return min(lens) # type: ignore

  def _len(self, key: str) -> int | None:
    file = self.archive(key)
    return file and file.num_files
  

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

def chain(datasets: Iterable[Dataset], *keys: K) -> Iter[Mapping[K, bytes]]:
  """Chain multiple datasets into a single generator"""
  return I.flatten([ds.samples(*keys) for ds in datasets])

def len(datasets: Iterable[Dataset], *keys: str) -> int | None:
  """Total length of `keys` in all datasets. (Count as 0 if undefined)"""
  return sum((l for ds in datasets if (l := ds.len(*keys)) is not None))