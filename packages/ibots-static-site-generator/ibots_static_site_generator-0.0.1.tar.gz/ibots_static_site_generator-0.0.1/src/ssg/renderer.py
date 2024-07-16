from __future__ import annotations

import asyncio
from collections import defaultdict
from pathlib import Path, PurePosixPath

from aiopath import AsyncPath
import jinja2

from .utils import copy, write_textfile
from .data_directory import extract_global_data, text_to_data
from .templates.jinja_renderer import build_jinja_environment



async def run_render_pipeline():
    
    # Copy Static Files
    await asyncio.gather(
        copy('./shared/static', './_output/static'),
        copy('./theme/assets', './_output/assets'),
    )

    # Read Shared Data (no templating allowed)
    global_data = extract_global_data(base_path='./data')
    stats_data = extract_global_data(base_path='./stats')
    
    # Read site-wide data
    env = build_jinja_environment()
    shared_data = await read_and_render_yaml_dir(base_dir='./shared/data', env=env, data=global_data, stats=stats_data)
    
    # Walk through each 'pages' directory and render the pages found inside
    async for page_path in AsyncPath('./pages').glob('**/[!_]*.md'):
        if page_path.parent.name.startswith('_'):
            continue

        print(f'Rendering: {page_path}')

        subpages_data = defaultdict(dict)
        async for subpage_path in page_path.parent.glob('[!_]*/[!_]*.md'):
            subpage_data = await read_and_render_page_data('./pages', subpage_path, data=global_data, site=shared_data, stats=stats_data)
            subpages_data[subpage_data['type']][subpage_data['id']] = subpage_data
        subpages_data = dict(subpages_data)
        

        # Render HTML Template
        env = build_jinja_environment(['./shared/templates', page_path.parent])
        template = env.get_template('template.html')
        page_data = await read_and_render_page_data('./pages', page_path, data=global_data, site=shared_data, stats=stats_data)
        page_html = await template.render_async(
            data=global_data, 
            site=shared_data, 
            page=page_data,
            subpages=subpages_data,
            stats=stats_data,
        )

        output_path = Path('./_output').joinpath(page_data['url'])
        await write_textfile(path=output_path, text=page_html)



def url_from_path(basedir, page_path: Path):
    url_path = page_path.relative_to(basedir).with_suffix('.html')
    if Path(page_path).with_suffix('').is_dir():
        url_path = url_path.with_suffix('').joinpath('index.html')
    url = str(PurePosixPath(url_path))
    return url


async def read_and_render_page_data(basedir, page_path, **render_data):
    page_text = (await page_path.read_text()).strip()
    env = build_jinja_environment()
    if page_text.startswith('---'):
        _, templated_yaml_text, md_text = page_text.split('---')
        template = env.from_string(templated_yaml_text)
        yaml_text = await template.render_async(**render_data)
        yaml_data = text_to_data(yaml_text, format='yaml')
    else:
        yaml_data = {}
        md_text = page_text

    md_html = text_to_data(md_text, 'md')                
    page_data = yaml_data
    page_data['content'] = md_html
    page_data['url'] = url_from_path(basedir, page_path)
    page_data['id'] = page_path.stem
    page_data['type'] = page_path.parent.name
    return page_data



async def read_and_render_yaml_dir(base_dir: str | Path, env: jinja2.Environment, **render_data):
    data = {}
    async for path in AsyncPath(base_dir).glob('*.yaml'):
        text = await AsyncPath(path).read_text()
        template = env.from_string(text)
        text_to_load = await template.render_async(**render_data)
        data[path.stem] = text_to_data(text_to_load, format='yaml')
    return data


            









        
 