import json

import click
import tomli

from .tts.data import TTSSave

def read_conf():
    with open('pytts.toml', 'rb') as f:
        conf = tomli.load(f)
        for path_key, path in conf['PATHS'].items():
            conf['PATHS'][path_key] = str(path).format(**conf['PATHS_BASE'])
        return conf

def format_path(conf, path):
    return path.format(**conf['PATHS_BASE'], **conf['PATHS'])

def extract_save(path_to_save, path_to_project, do_backup=False):
    tts_save = TTSSave.from_save(path_to_save, do_backup=do_backup)
    tts_save.export_as_project(path_to_project)


@click.group('pytts_tool')
def pytts_tool():
    pass

@pytts_tool.command('extract')
@click.option('-s', '--save', default=None)
@click.option('-o', '--output', default=None)
@click.option('-b', '--backup', 'do_backup', is_flag=True, default=False)
def pytts_extract(save, output, do_backup):
    conf = read_conf()
    conf_save = format_path(conf, conf.get('EXTRACT_SAVE', ''))
    conf_out = format_path(conf, conf.get('EXTRACT_OUT', ''))

    save = save or conf_save
    output = output or conf_out
    extract_save(save, output, do_backup)

