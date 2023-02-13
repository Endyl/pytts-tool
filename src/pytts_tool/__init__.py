import json

import click

from .tts.data import TTSSave

WIN_TTS = '/media/slemmer/ACCC6108CC60CE60/Documents and Settings/Endyl/Dokumentumok/My Games/Tabletop Simulator'
WIN_WORKSHOP = f'{WIN_TTS}/Mods/Workshop'
WIN_SAVES = f'{WIN_TTS}/Saves'

LNX_TTS = '/home/slemmer/.local/share/Tabletop Simulator'
LNX_WORKSHOP = f'{LNX_TTS}/Mods/Workshop'
LNX_SAVES = f'{LNX_TTS}/Saves'

def extract_save(path_to_save, path_to_project, do_backup=False):
    tts_save = TTSSave.from_save(path_to_save, do_backup=do_backup)
    tts_save.export_as_project(path_to_project)


@click.group('pytts_tool')
def pytts_tool():
    pass

@pytts_tool.command('extract')
@click.option('-b', '--backup', 'do_backup', is_flag=True, default=False)
def pytts_extract(do_backup):
    extract_save(f'{WIN_SAVES}/MMGA/Modded/TFMARS_vVERSION.json', './out/mmga', do_backup)

