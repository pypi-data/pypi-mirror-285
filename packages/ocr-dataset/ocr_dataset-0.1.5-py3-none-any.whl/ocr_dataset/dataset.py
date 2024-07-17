from typing_extensions import Iterable, TextIO
from dataclasses import dataclass
from haskellian import Iter, iter as I
import lines_dataset as lds
import files_dataset as fds

class MetaJson(lds.MetaJson, fds.MetaJson):
  @classmethod
  def new_tar(cls, num_samples: int, *, images: str = 'images', labels: str = 'labels'):
    return cls(files_dataset={
      images: fds.Archive(archive=f'{images}.tar', format='tar', num_files=num_samples)
    }, lines_dataset={
      labels: lds.File(file=f'{labels}.txt', num_lines=num_samples)
    })
  
@dataclass
class Dataset:

  base_path: str
  images: fds.Dataset
  labels: lds.Dataset

  @staticmethod
  def read(base: str) -> 'Dataset':
    """Reads a dataset from `{base}/meta.json`. Throws if it doesn't exist."""
    return Dataset(
      base_path=base,
      labels=lds.Dataset.read(base),
      images=fds.Dataset.read(base),
    )
  
  @staticmethod
  def at(base: str) -> 'Dataset':
    """Reads or creates an empty dataset at `{base}/meta.json`."""
    return Dataset(
      base_path=base,
      labels=lds.Dataset.at(base),
      images=fds.Dataset.at(base),
    )
  
  @I.lift
  def samples(self, images_key: str = 'images', labels_key: str = 'labels') -> Iterable[tuple[bytes, str]]:
    return zip(self.images.iterate(images_key), self.labels.iterate(labels_key))
  
  def __iter__(self):
    return self.samples()
  
  def len(self, images_key: str = 'images', labels_key: str = 'labels') -> int | None:
    images_len = self.images.len(images_key)
    labels_len = self.labels.len(labels_key)
    if images_len is not None and labels_len is not None:
      return min(images_len, labels_len)

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

def chain(datasets: Iterable[Dataset], images_key: str = 'images', labels_key: str = 'labels') -> Iter[tuple[bytes, str]]:
  """Chain multiple datasets into a single one."""
  return I.flatten([ds.samples(images_key, labels_key) for ds in datasets])

def len(datasets: Iterable[Dataset], images_key: str = 'images', labels_key: str = 'labels') -> int | None:
  """Total length of `keys` in all datasets. (Count as 0 if undefined)"""
  return sum((l for ds in datasets if (l := ds.len(images_key, labels_key)) is not None))