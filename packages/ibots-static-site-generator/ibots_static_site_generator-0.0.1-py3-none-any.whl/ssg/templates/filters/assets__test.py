from pathlib import PurePosixPath
import pytest
from unittest.mock import Mock
from _hashlib import HASH

from . import assets


@pytest.fixture
def manager(tmp_path_factory) -> assets.AssetManager:
    asset_path = tmp_path_factory.mktemp('assets')
    webserver_root = tmp_path_factory.mktemp('output')
    output_path = webserver_root / 'static'
    
    hashfun = Mock(HASH)
    hashfun().hexdigest.return_value = 'ABCDEFGHIJKLMNOPQ'
    

    data_file = asset_path.joinpath('data.file')
    data_file.touch()
    
    copyfun = Mock()
    downloadfun = Mock()
    manager = assets.AssetManager(
        webserver_root=webserver_root, 
        asset_path=output_path, 
        copyfun=copyfun,
        downloadfun=downloadfun,
        hashfun=hashfun,
    )
    return manager


@pytest.mark.asyncio
async def test_asset_creates_hashed_asset_in_assets_dir(tmp_path, manager: assets.AssetManager):
    data_file = tmp_path.joinpath('data.file')    
    data_file.touch()
    output_path = await manager.build(data_file)
    expected_output_path = str(PurePosixPath(manager.asset_path).joinpath('data_ABCDEF.file'))
    assert output_path == expected_output_path
    manager.copyfun.assert_called_once_with(
        str(PurePosixPath(data_file)),
        expected_output_path,
    )
    manager.downloadfun.assert_not_called()


@pytest.mark.asyncio
async def test_downloaded_assets_create_hashed_asset_in_assets_dir_using_url(manager):    
    url = 'http://website.com/dafadflkj/image.jpg'
    output_path = await manager.build(url)
    expected_output_path = str(PurePosixPath(manager.asset_path.joinpath('image_ABCDEF.jpg')))
    assert output_path == expected_output_path
    
    manager.downloadfun.assert_called_once_with(
        url,
        expected_output_path
    )
    manager.copyfun.assert_not_called()

    

@pytest.mark.asyncio
async def test_get_webserver_path_from_built_file(manager):
    filepath = manager.asset_path.joinpath('myfile.png')
    filepath.touch()
    filepath_str = str(PurePosixPath(filepath))
    uri = await manager.get_uri(filepath_str)
    expected_uri = '/static/myfile.png'
    assert uri == expected_uri


