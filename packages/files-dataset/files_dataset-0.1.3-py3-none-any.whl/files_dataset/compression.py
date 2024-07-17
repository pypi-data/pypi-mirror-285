from typing import Iterable

def iterate_tar(path: str) -> Iterable[bytes]:
  import tarfile
  with tarfile.open(path) as tarf:
    for member in tarf.getmembers():
      yield tarf.extractfile(member).read() # type: ignore

def iterate_zip(path: str) -> Iterable[bytes]:
  import zipfile
  with zipfile.ZipFile(path) as zipf:
    for name in zipf.namelist():
      yield zipf.open(name).read()