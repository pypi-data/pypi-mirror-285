from pathlib import PurePosixPath

import numpy as np
from PIL import Image

from . import images

def test_image_resize(tmp_path):

    im = Image.fromarray(np.zeros((120, 240, 3), np.uint8))
    im.save(tmp_path / 'image.jpg')

    fpath = str(PurePosixPath(tmp_path / 'image.jpg'))
    fpath_out = images.resize(fpath, 60, 120)
    assert fpath_out == str(PurePosixPath(tmp_path / 'image_60x120.jpg'))