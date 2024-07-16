from pathlib import Path, PurePosixPath

from PIL import Image


def resize(path: str | Path, width: int, height: int) -> str:
    with Image.open(path) as img:
        img2 = img.resize((width, height))
    target_path = Path(path).with_stem(Path(path).stem + f'_{width}x{height}')
    img2.save(target_path)
    return str(PurePosixPath(target_path))