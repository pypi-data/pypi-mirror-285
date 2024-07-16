from __future__ import annotations

from dataclasses import dataclass
import hashlib
import shutil
from typing import Callable
import typing
import urllib.request
from pathlib import Path, PurePosixPath
from aiopath import AsyncPath
if typing.TYPE_CHECKING:
    from _hashlib import HASH


@dataclass(frozen=True)
class AssetManager:
    webserver_root: Path
    asset_path: Path
    copyfun: Callable[[str, str], None] = shutil.copyfile
    downloadfun: Callable[[str, str], None] = urllib.request.urlretrieve
    hashfun: Callable[[bytes], HASH] = hashlib.md5

    def __post_init__(self):
        if not self.asset_path.is_relative_to(self.webserver_root):
            raise ValueError("asset_path must be inside webserver_path")
        self.asset_path.mkdir(parents=True, exist_ok=True)

    async def build(self, path: str | Path) -> str:
        is_url = str(path).startswith('http')
        if is_url:
            to_hash = path.encode()
        else:
            to_hash = await AsyncPath(path).read_bytes()        
        hash_str = self.hashfun(to_hash).hexdigest()[:6]
        fname_out = Path(path).with_stem(Path(path).stem + '_' + hash_str).name

        save_path = self.asset_path.joinpath(fname_out)
        save_path_str = str(PurePosixPath(save_path))
        if save_path.exists():
            return save_path_str
        savefun = self.downloadfun if is_url else self.copyfun
        src = str(path if is_url else PurePosixPath(path))
        savefun(src, save_path_str)
        return save_path_str
    
    async def get_uri(self, path: str | Path) -> str:
        path_str = str(PurePosixPath(path))
        assert await AsyncPath(path).exists(), path_str
        assert Path(path).is_relative_to(self.webserver_root), path_str
        webserver_path = Path(path).relative_to(self.webserver_root)
        return '/' + str(PurePosixPath(webserver_path))


    


