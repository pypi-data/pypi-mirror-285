from __future__ import annotations

from datetime import date, datetime
from pathlib import Path, PurePosixPath
import jinja2

from . import filters as f


def build_jinja_environment(search_path: str | list[Path|str] | None = None) -> jinja2.Environment:
    env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(search_path) if search_path is not None else None,
            autoescape=jinja2.select_autoescape(),
            undefined=jinja2.StrictUndefined,
            enable_async=True,
        )
    env.trim_blocks = True
    env.lstrip_blocks = True

    # Include additional jinja filters
    env.filters.update({
        'flatten_nested': f.flatten_nested_dict,
        'index': f.multi_index,
        'items': f.items,
        'promote_key': f.promote_key,
        'sort_by': f.sort_by,
        'resize': f.resize,
    })
    if search_path:
        assert len(search_path) == 2
        template_path = search_path[-1]
        image_manager = f.AssetManager(
            webserver_root=Path('./_output'),
            asset_path=Path('./_output/static'),
        )
        env.globals['TEMPLATE_DIR'] = str(PurePosixPath(template_path)) + '/'
        env.filters.update({
            'asset': image_manager.build,
            'uri': image_manager.get_uri,
        })
        

    # Include additional jinja globals
    env.globals.update({
        'today': date.today(),
        'now': datetime.now(),
        'str': str,
    })
    return env



