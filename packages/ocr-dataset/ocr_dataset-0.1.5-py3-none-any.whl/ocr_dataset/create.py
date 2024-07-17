from typing import Sequence
import os
import fs
import files_dataset as fds
import lines_dataset as lds
from .dataset import MetaJson

def create_tar(
  base_path: str,
  samples: Sequence[tuple[bytes, str]], *,
  images_name: str = 'images',
  labels_name: str = 'labels',
  images_ext: str = 'jpg',
):
  os.makedirs(base_path, exist_ok=True)
  meta_path = os.path.join(base_path, 'meta.json')
  meta = MetaJson.at(meta_path)
  meta.files_dataset = {
    **meta.files_dataset,
    images_name: fds.Archive(archive=f'{images_name}.tar', format='tar', num_files=len(samples))
  }
  meta.lines_dataset = {
    **meta.lines_dataset,
    labels_name: lds.File(file=f'{labels_name}.txt', num_lines=len(samples))
  }
  meta.dump(meta_path)

  imgs, labs = zip(*samples)
  
  num_digits = len(str(len(samples)))
  files = [(f'{i:0{num_digits}}.{images_ext}', img) for i, img in enumerate(imgs)]
  fs.create_tarfile(files, f'{base_path}/{images_name}.tar')

  with open(f'{base_path}/{labels_name}.txt', 'w') as f:
    f.write('\n'.join(labs) + '\n')