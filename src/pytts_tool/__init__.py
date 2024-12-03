import json
import os.path

import click
from pydantic import ValidationError
import tomli

from .tts.data import TTSSave

def read_conf(config_path):
    with open(config_path, 'rb') as f:
        conf = tomli.load(f)
        for path_key, path in conf['PATHS'].items():
            conf['PATHS'][path_key] = str(path).format(**conf['PATHS_BASE'])
        return conf

def format_path(conf, path):
    return path.format(**conf['PATHS_BASE'], **conf['PATHS'])

def extract_save(path_to_save, path_to_project, do_backup=False):
    tts_save = TTSSave.from_save(path_to_save, do_backup=do_backup)
    tts_save.export_as_project(path_to_project, os.path.join(path_to_project, 'lib'))


@click.group('pytts_tool')
def pytts_tool():
    pass

@pytts_tool.command('extract')
@click.option('-s', '--save', default=None)
@click.option('-o', '--output', default=None)
@click.option('-c', '--config', default='pytts.toml')
@click.option('-b', '--backup', 'do_backup', is_flag=True, default=False)
def pytts_extract(save, output, config, do_backup):
    conf = read_conf(config)
    conf_save = format_path(conf, conf.get('EXTRACT_SAVE', ''))
    conf_out = format_path(conf, conf.get('EXTRACT_OUT', ''))

    save = save or conf_save
    output = output or conf_out
    extract_save(save, output, do_backup)

@pytts_tool.command('gentypes')
def pytts_gentypes():
    from .tts.type_extract import Types
    def extract_types(types, o):
        name = o['Name']
        if name not in types:
            types[name] = []

        new_keys = set(o.keys())
        types[name] = list(set(types[name]) | new_keys)
        types['#all'] |= new_keys
        if types['#common'] is None:
            types['#common'] = new_keys
        else:
            types['#common'] &= new_keys


        if 'ContainedObjects' in o:
            for c in o['ContainedObjects']:
                extract_types(types, c)

    with open('000-data/testing/TFMARS_vVERSION.json', 'r') as f:
        data = json.load(f)

    t = Types()
    t.extract_save(data)
    print(json.dumps(t.serialize(), indent=2))
    """
    types = {
        '#all': set(),
        '#common': None,
    }
    for o in data['ObjectStates']:
        extract_types(types, o)

    for k in (set(types.keys()) - set(['#all', '#common'])):
        types[f'{k}-unique'] = list(set(types[k]) - types['#common'])
    types['#all'] = list(types['#all'])
    types['#common'] = list(types['#common'])
    print(json.dumps(types, indent=2))
    """


@pytts_tool.command('extract2')
def pytts_extract_2():
    from pathlib import Path
    from .tts.structured import TTSSave, get_known_fields
    from .tts.exporter import TTSSaveExporter, ExportVFS
    TEST_FILES = {
        'TFMARS': '000-data/testing/TFMARS_vVERSION.json',
        'SZUV': '000-data/Saves/szuv.json',
    }
    with open(TEST_FILES['SZUV'], 'r') as f:
        data = json.load(f)

    try:
        save = TTSSave.model_validate(data)

        vfs = ExportVFS(Path('out'), Path('out'))
        exporter = TTSSaveExporter(save.model_dump(exclude_unset=True), vfs)
        exporter.export_as_project()
        vfs.write_files()

    except ValidationError as ex:
        print('Save validation error:')
        print(ex)


@pytts_tool.command('build')
def pytts_build():
    from pathlib import Path
    from .tts.builder import TTSSaveBuilder
    builder = TTSSaveBuilder(Path('out'))
    data = builder.build_save()
    with open('000-data/build/szuv.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
