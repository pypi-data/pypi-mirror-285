import aioshutil
from aiopath import AsyncPath


from pathlib import Path


async def copy(src: Path, target: Path, skip_if_exists: bool = True) -> None:

    if skip_if_exists and Path(target).exists():
        print(f'Skipping Copying: {src}')
        return

    print(f"Copying: {src}")
    if Path(src).is_dir():

        await aioshutil.copytree(src, target, dirs_exist_ok=True)
        return

    await AsyncPath(target).parent.mkdir(parents=True, exist_ok=True)
    await aioshutil.copy2(src=src, dst=target)


async def write_textfile(path, text) -> None:
    apath = AsyncPath(path)
    await apath.parent.mkdir(parents=True, exist_ok=True)
    await apath.write_text(text)