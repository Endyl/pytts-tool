import datetime as dt
import json
import logging
from pathlib import Path
import os.path

import click
from epylogging import BaseSQLiteHandler, LogField
from pydantic import ValidationError
import tomli

from .tts.data import TTSSave

logger = logging.getLogger('pytts_tool')

class AllFieldsSQLiteHandler(BaseSQLiteHandler):
    def __init__(self, *args, db_uri: str, **kwargs):
        log_fields = [
            self.LF_CREATED,
            self.LF_MSECS,
            self.LF_LEVEL,
            self.LF_LEVEL_NAME,
            self.LF_NAME,
            LogField('user', 'INTEGER', 'user'),
            self.LF_MESSAGE,
            self.LF_EXC_INFO_TEXT,
            self.LF_STACK_INFO,
            self.LF_PATH_NAME,
            self.LF_FILE_NAME,
            self.LF_MODULE,
            self.LF_FUNC_NAME,
            self.LF_LINE,
            self.LF_PROCESS,
            self.LF_PROCESS_NAME,
            self.LF_THREAD,
            self.LF_THREAD_NAME,
            self.LF_TASK_NAME,

            #self.LF_ARGS,
            #self.LF_ASCTIME,
            #self.LF_EXC_INFO,
            #self.LF_MSG,
            #self.LF_RELATIVE_CREATED,
        ]
        super().__init__(*args, db_uri=db_uri, log_fields=log_fields, **kwargs)


    def create_log_index(self, conn):
        with conn:
            indexes = (
                ('logtime', '(created)'),
                ('logtimeprec', '(created, msecs)'),
                ('loglevelnum', '(level)'),
                ('loglevelname', '(level_name)'),
                ('logname', '(name)'),
            )
            for i in indexes:
                conn.execute(
                    f'CREATE INDEX IF NOT EXISTS {i[0]} ON "log" {i[1]}'
                )


    def format_time(self, v):
        return dt.datetime.fromtimestamp(
            v, tz=dt.timezone.utc
        ).isoformat()


    def format_exc_info(self, v):
        if v:
            return logging._defaultFormatter.formatException(v)  # type: ignore
        else:
            return None

def param_to_path(ctx, param, value) -> Path:
    return Path(value)

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

def setup_logging():
    from epylogging import dictConfig
    CONF = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "basic": {
                "format": f"[%(asctime)s] [%(levelname)s|%(module)s|L%(lineno)d]: %(message)s\n{80*'='}",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
            "jsonl": {
                "()": "epylogging.JSONLineFormatter",
                "fmt_keys": {
                    "level": "levelname",
                    "message": "message",
                    "timestamp": "timestamp",
                    "logger": "name",
                    "module": "module",
                    "function": "funcName",
                    "line": "lineno",
                    "thread_name": "threadName",
                },
            },
        },

        "handlers": {
            "basic_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "when": "midnight",
                "backupCount": 5,
                "filename": "/media/slemmer/HDD002-4TB/000-storage/project/me/pytts-tool/logs/pytts-tool-logs.txt",
                "formatter": "basic",
            },
            "json_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "when": "midnight",
                "backupCount": 5,
                "filename": "/media/slemmer/HDD002-4TB/000-storage/project/me/pytts-tool/logs/pytts-tool-logs.jsonl",
                "formatter": "jsonl",
            },
            "sqlite": {
                "()": "pytts_tool.AllFieldsSQLiteHandler",
                "db_uri": "file:/media/slemmer/HDD002-4TB/000-storage/project/me/pytts-tool/logs/pytts-tool-logs.sqlite",
            },
            "queue_handler": {
                "class": "epylogging.PreservingQueueHandler",
                "respect_handler_level": True,
                "handlers": [
                    "basic_file",
                    "json_file",
                    "sqlite",
                ],
            },
        },

        "loggers": {
            "root": {
                "level": "DEBUG",
                "handlers": ["queue_handler"],
            },
        },
    }
    dictConfig(CONF)



@click.group('pytts_tool', invoke_without_command=True)
@click.pass_context
def pytts_tool(ctx):
    setup_logging()
    logger.debug('pytts-tool started')

@pytts_tool.command('extract')
@click.option('-s', '--save', 'savefile_path',
    type=click.Path(exists=True),
    required=True,
    prompt='Save file',
    default='imports/save.json',
    callback=param_to_path)
@click.option('-e', '--export', 'fs_root',
    type=click.Path(exists=True),
    required=True,
    prompt='Export root',
    default='.',
    callback=param_to_path)
@click.option('-l', '--lib', 'lib_root',
    type=click.Path(exists=True),
    required=True,
    prompt='Lib root',
    default='src',
    callback=param_to_path)
def pytts_extract(savefile_path: Path, fs_root: Path, lib_root: Path):
    from .tts.structured import TTSSave, get_known_fields
    from .tts.exporter import TTSSaveExporter, ExportVFS

    with open(savefile_path, 'r') as f:
        data = json.load(f)

    try:
        save = TTSSave.model_validate(data)

        vfs = ExportVFS(fs_root, lib_root)
        exporter = TTSSaveExporter(save.model_dump(exclude_unset=True), vfs)
        exporter.export_as_project()
        vfs.write_files()

    except ValidationError as ex:
        print('Save validation error:')
        print(ex)


# ============================================================= Tmp / Testing #
@pytts_tool.command('extract-old')
@click.option('-s', '--save', default=None)
@click.option('-o', '--output', default=None)
@click.option('-c', '--config', default='pytts.toml')
@click.option('-b', '--backup', 'do_backup', is_flag=True, default=False)
def pytts_extract_old(save, output, config, do_backup):
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
