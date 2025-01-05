"""
Project Structure

build/
imports/  # to store savegame.json?
src/
    lib/
    lib-absolute/
    lib-home/
    save/
        assets/
        fields/
        objects/
            Name.GUID/
                assets/
                children/
                    Name.GUID/
                        ...
                fields/
                objects/
                    Name.GUID/
                        ...
                states/
                    key.Name.GUID/
                        ...
                main.json
                main.ttslua
                main.xml
                state.[json|txt]
        guid-map.json
        main.json
        main.ttslua
        main.xml
        state.[json|txt]
"""
from __future__ import annotations

import json
import logging
import mimetypes
import os.path
from pathlib import Path
import re
import time
from typing import Generator, Any
from urllib.parse import urlparse, quote as urlquote
from collections import defaultdict

from .structured import SaveKeys, ObjectKeys, MiscKeys

import requests
from tqdm import tqdm

logger = logging.getLogger('pytts_tool')

def is_string_field_empty(value: Any) -> bool:
    return not (value and str(value).strip())

def pathify_url(value: str):
    return urlquote(value, safe='').replace('~', '%7E')

def pathify_url_tts(value: str):
    chars = (':', '/', '.', '-')
    for ch in chars:
        value = value.replace(ch, '')
    return value

def is_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        result = urlparse(value.strip())
        if all([result.scheme, result.netloc]):
            return True
        else:
            if value.startswith('http'):
                print('what?', value)
            return False
    except ValueError:
        return False


def export_urls(vfs: ExportVFS, guid: str, path: Path, key: str, value: Any):
    if is_url(value):
        vfs.add_resource(guid, path, key, value)
    elif isinstance(value, dict):
        for vkey, vvalue in value.items():
            export_urls(vfs, guid, path, f'{key}.{vkey}', vvalue)
    elif isinstance(value, list):
        for index, vvalue in enumerate(value):
            export_urls(vfs, guid, path, f'{key}.{index}', vvalue)

def guess_ext(url, fix_ext, guess='.unk.bin'):
    if fix_ext:
        return fix_ext

    mtype, encoding = mimetypes.guess_type(url)
    if mtype is None:
        ct_headers = ('content-type', 'contenttype')
        res = requests.head(url)
        mtype = ''
        for hname, hvalue in res.headers.items():
            lhname = str(hname).lower().strip()
            if lhname in ct_headers:
                mtype = hvalue

    ext = mimetypes.guess_extension(mtype)
    return ext if ext is not None else guess



def lookahead(iterable, flag_for_last=True) -> Generator[tuple[bool, Any], Any, Any]:
    flag_all = not flag_for_last
    flag_for_last = not flag_all

    # wrap iterator around iterable
    iterator = iter(iterable)

    # fetch and cache first value, if any
    try:
        result = next(iterator)
    except StopIteration:
        return

    # loop through remaining items, return then update cached value
    for value in iterator:
        yield flag_all, result
        result = value

    # end of loop, yield last value
    yield flag_for_last, result


class ResourceRequest:
    EXT_MAP = {
        SaveKeys.SKY_URL.value: '.img.bin',
        SaveKeys.TABLE_URL.value: '.img.bin',
        MiscKeys.ASSETBUNDLE_URL.value: '.bin',
        MiscKeys.ASSETBUNDLE_SECONDARY_URL.value: '.bin',
        MiscKeys.MESH_URL.value: '.bin',
        MiscKeys.PDF_URL.value: '.pdf',
        MiscKeys.IMAGE_URL.value: '.img.bin',
        MiscKeys.IMAGE_SECONDARY_URL.value: '.img.bin',
        MiscKeys.DIFFUSE_URL.value: '.img.bin',
        MiscKeys.NORMAL_URL.value: '.bin',
        MiscKeys.COLLIDER_URL.value: '.bin',
        MiscKeys.FACE_URL.value: '.img.bin',
        MiscKeys.BACK_URL.value: '.img.bin',
    }

    def __init__(self, url: str, path: Path, item_path: Path, item_key: str, cache_entries: list[str]):
        self.url = url
        self.path = path
        self.item_path = item_path
        self.item_key = item_key
        self.cache_entries = cache_entries

    def get_ext_guess(self):
        key = self.item_key.split('.')[-1]
        return self.EXT_MAP.get(key, '.unk.bin')

    def get_from_cache(self) -> None | Path:
        if not self.cache_entries:
            return None


    def download(self, url, path):
        chunk_encoded = False # Change to True if chunk encoded???
        chunk_size = None if chunk_encoded else 8192
        time.sleep(0.5)
        with requests.get(url, stream=True) as r:
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if (chunk_encoded and chunk) or not chunk_encoded:
                            f.write(chunk)
                logger.debug(f'Downloaded <{url}> to <{path}>')
                return True
            else:
                logger.debug(f'Failed to download <{url}> to <{path}>')
                #r.raise_for_status()
                return False

    def do_download(self, url):
        ext_guess = self.get_ext_guess()
        ext = guess_ext(url, None, ext_guess)
        ext_path = self.path.with_suffix(f'{self.path.suffix}{ext}')
        if ext_path.exists():
            logger.debug(f'Asset already exists: {ext_path}')
            return ext_path

        if self.download(url, ext_path):
            return ext_path

        return None

    def write_file(self):
        ext_path = self.get_from_cache()
        if ext_path:
            return ext_path

        ext_path = self.do_download(self.url)
        if ext_path:
            return ext_path

        akamai_url = urlparse(self.url)
        if not akamai_url.netloc.endswith('.steamusercontent.com'):
            return None

        akamai_url = akamai_url._replace(
            scheme='https',
            netloc='steamusercontent-a.akamaihd.net',
        )
        logger.debug(f'Trying: {akamai_url.geturl()}')
        ext_path = self.do_download(akamai_url.geturl())
        if ext_path:
            return ext_path

        return None


class ExportVFS:
    def __init__(self, fs_root: Path, lib_root: Path):
        self.fs_root = fs_root
        self.lib_root = lib_root

        with open('/media/slemmer/HDD002-4TB/000-storage/project/me/pytts-tool/000-data/cachereg.json') as f:
            self.cache_reg = json.load(f)

        self.files = {}
        self.lib = {}
        self.resources = defaultdict(list)

    def add_lib_file(self, path: Path, content: str):
        if path in self.lib and (content != self.lib[path]):
            logger.debug(f'Mismatched content: {path}')
            return
        self.lib[path] = content

    def add_file(self, path: Path, content: str | list | dict):
        if path in self.files:
            logger.debug(f'Path already exists: <{path}>')
        else:
            self.files[path] = content

    def add_to_file(self, path: Path, *keys: list[str], value):
        if path not in self.files:
            logger.debug(f'Trying to add to missing file: <{path}>: <{keys}>')
            self.add_file(path, {})

        target = self.files[path]
        for is_last, key in lookahead(keys):
            if is_last:
                if key in target:
                    logger.debug(f'Multiple assignment: <{path}: {keys}>')
                target[key] = value
            else:
                if key not in target:
                    logger.debug(f'Creating target path: <{path}: {key} / {keys}>')
                    target[key] = {}
                target = target[key]

    def append_to(self, path: Path, key: str, value):
        if path not in self.files:
            logger.debug(f'Trying to append to missing file: <{path}>: <{key}>')
            self.add_file(path, {})

        target = self.files[path]
        if key not in target:
            logger.debug(f'Append to missing key: <{path}: {key}>')
            target[key] = []
        target[key].append(value)

    def add_resource(self, guid: str, path: Path, key: str, value):
        self.resources[value].append([path, guid, key])

    def write_resource(self, path: Path, content: ResourceRequest):
        # if exists skip (force download?)
        #logger.debug(f'Writing ResourceRequest not implemented: {path}')
        return content.write_file()

    def write_contents(self, path: Path, content):
        with open(path, 'w') as f:
            if '.json' == path.suffix or not isinstance(content, str):
                json.dump(content, f, ensure_ascii=False, indent='\t')
            elif not isinstance(content, str):
                logger.debug(f'Writing non string to non json <{path}> {type(content)}')
                f.write(str(content))
            else:
                f.write(content)

    def write_file(self, path: Path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, ResourceRequest):
            return self.write_resource(path, content)
        else:
            self.write_contents(path, content)
            return path

    def write_assets(self):
        pass

    def write_files(self):
        pbar = tqdm(self.files.items())
        for path, content in pbar:
            cpath = self.fs_root / path
            pbar.set_description(f'Exporting file: {cpath}')
            self.write_file(cpath, content)

        pbar = tqdm(self.lib.items())
        for path, content in pbar:
            cpath = self.lib_root / path
            pbar.set_description(f'Exporting lib: {cpath}')
            self.write_file(cpath, content)

        guid_map = defaultdict(list)
        pbar = tqdm(self.resources.items())
        for url, referers in pbar:
            pbar.set_description(f'Processing:  {url}')
            url_path = pathify_url(url)
            for r in referers:
                guid_map[url_path].append(
                    [str(r[0]), r[2]]
                )
            resource_path = self.fs_root / 'src' / 'save' / 'assets' / url_path
            logger.debug(f'Resource: {resource_path}')
            ext_path = self.write_file(resource_path, ResourceRequest(
                url,
                resource_path,
                r[0],
                r[2],
                self.cache_reg.get(pathify_url_tts(url), None)
            ))
        self.write_file(self.fs_root / 'src' / 'save' / 'guid-map.json', dict(guid_map))




class TTSSaveExporter:
    EXTERNAL = (
        SaveKeys.GRID,
        SaveKeys.LIGHTING,
        SaveKeys.HANDS,
        SaveKeys.TURNS,
        SaveKeys.TAB_STATES,
        SaveKeys.CAMERA_STATES,
        SaveKeys.DECAL_PALLET,
        SaveKeys.COMPONENT_TAGS,
    )

    def __init__(self, data: dict, vfs: ExportVFS):
        self.data = data
        self.vfs = vfs

    def export_as_project(self):
        path = Path('src/save/main.json')

        # Export save file
        self.vfs.add_file(path, {})

        for key, value in self.data.items():
            self.export(path, key, value)


    def export(self, path: Path, key: str, value):
        exporter = getattr(self, f'export__{key}', self.export_raw)
        exporter(path, key, value)

    def export_raw(self, path: Path, key, value):
        export_urls(self.vfs, 'root', path, key, value)
        if key in self.EXTERNAL:
            self.vfs.add_file(path.parent / 'fields' / f'{key}.json', value)
        else:
            self.vfs.add_to_file(path, key, value=value)

    def export__LuaScript(self, path: Path, key, value):
        if is_string_field_empty(value):
            self.export_raw(path, key, value)
        else:
            lse = LuaScriptExtractor(self.vfs, 'file', path.parent / 'main.ttslua', value)
            lse.extract()
            #self.vfs.add_file(path.parent / 'main.ttslua', value)

    def export__LuaScriptState(self, path: Path, key, value):
        if is_string_field_empty(value):
            self.export_raw(path, key, value)
        elif isinstance(value, str):
            self.vfs.add_file(path.parent / 'state.txt', value)
        else:
            self.vfs.add_file(path.parent / 'state.json', value)

    def export__ObjectStates(self, path: Path, key, value):
        self.vfs.add_to_file(path, key, value=[])
        for object_data in value:
            save_object = TTSSaveObjectExporter(object_data, self.vfs, path.parent / 'objects')
            self.vfs.append_to(path, key, save_object.folder_name)
            save_object.export_as_project()

    def export__XmlUI(self, path: Path, key, value):
        if is_string_field_empty(value):
            self.export_raw(path, key, value)
        else:
            self.vfs.add_file(path.parent / 'main.xml', value)


class TTSSaveObjectExporter:
    EXTERNAL = ()

    def __init__(self, data: dict, vfs: ExportVFS, path: Path, folder_prefix=''):
        self.data = data
        self.vfs = vfs
        self.path = path
        self.folder_prefix = folder_prefix

    @property
    def guid(self):
        return self.data.get(ObjectKeys.GUID, 'ffffff')

    @property
    def name(self):
        return self.data.get(ObjectKeys.NAME, 'UNKNOWN')

    @property
    def raw_folder_name(self):
        return f'{self.name}.{self.guid}'

    @property
    def folder_name(self):
        result = f'{self.name}.{self.guid}'
        return f'{self.folder_prefix}.{result}' if self.folder_prefix else result


    def export_as_project(self):
        path = self.path / self.folder_name / 'main.json'

        # Export save file
        self.vfs.add_file(path, {})

        for key, value in self.data.items():
            self.export(path, key, value)


    def export(self, path: Path, key: str, value):
        exporter = getattr(self, f'export__{key}', self.export_raw)
        exporter(path, key, value)

    def export_raw(self, path: Path, key, value):
        export_urls(self.vfs, self.data.get('GUID', 'unknown'), path, key, value)
        if key in self.EXTERNAL:
            self.vfs.add_file(path.parent / 'fields' / f'{key}.json', value)
        else:
            self.vfs.add_to_file(path, key, value=value)

    def export__ChildObjects(self, path: Path, key, value):
        self.vfs.add_to_file(path, key, value=[])
        for object_data in value:
            save_object = TTSSaveObjectExporter(object_data, self.vfs, path.parent / 'children')
            self.vfs.append_to(path, key, save_object.folder_name)
            save_object.export_as_project()

    def export__ContainedObjects(self, path: Path, key, value):
        self.vfs.add_to_file(path, key, value=[])
        for object_data in value:
            save_object = TTSSaveObjectExporter(object_data, self.vfs, path.parent / 'objects')
            self.vfs.append_to(path, key, save_object.folder_name)
            save_object.export_as_project()

    def export__LuaScript(self, path: Path, key, value):
        if is_string_field_empty(value):
            self.export_raw(path, key, value)
        else:
            lse = LuaScriptExtractor(self.vfs, 'file', path.parent / 'main.ttslua', value)
            lse.extract()
            #self.vfs.add_file(path.parent / 'main.ttslua', value)

    def export__LuaScriptState(self, path: Path, key, value):
        if is_string_field_empty(value):
            self.export_raw(path, key, value)
        elif isinstance(value, str):
            self.vfs.add_file(path.parent / 'state.txt', value)
        else:
            self.vfs.add_file(path.parent / 'state.json', value)

    def export__States(self, path: Path, key, value):
        self.vfs.add_to_file(path, key, value={})
        for state_key, state_data in value.items():
            state_obj = TTSSaveObjectExporter(state_data, self.vfs, path.parent / 'states', state_key)
            state_obj.export_as_project()
            self.vfs.add_to_file(path, key, state_key, value=state_obj.raw_folder_name)

    def export__XmlUI(self, path: Path, key, value):
        if is_string_field_empty(value):
            self.export_raw(path, key, value)
        else:
            self.vfs.add_file(path.parent / 'main.xml', value)


class StringLineIterator:
    def __init__(self, a_string):
        if a_string is None or a_string is False:
            self.lines = []
        else:
            self.lines = a_string.splitlines()

        self.len = len(self.lines)
        self.index = 0

    def next(self):
        if self.len <= self.index:
            return None

        line = self.lines[self.index].rstrip()
        self.index += 1
        return line

class LuaScriptExtractor:
    RE_INCLUDE = re.compile(r'^----#include\s+(<?(/|!/|~!|).+>?)\s*$')
    RE_WRAPPED = re.compile(r'^<(.*)>$')

    RE_ABSOLUTE = re.compile(r'^#include\s+(/.+)\s*$')
    RE_ABSOLUTE_WRAPPED = re.compile(r'^#include\s+<(/.+)>\s*$')
    RE_RELATIVE = re.compile(r'^#include\s+([^~/!].+)\s*$')
    RE_RELATIVE_WRAPPED = re.compile(r'^#include\s+<([^~/!].+)>\s*$')
    RE_FIXED = re.compile(r'^#include\s+(!/.+)\s*$')
    RE_FIXED_WRAPPED = re.compile(r'^#include\s+<(!/.+)>\s*$')
    RE_HOME = re.compile(r'^#include\s+(~/.+)\s*$')
    RE_HOME_FIXED = re.compile(r'^#include\s+<(~/.+)>\s*$')

    INCLUDE_TYPE = {
        '/': 'absolute',
        '!/': 'fixed',
        '~/': 'home',
    }

    # #include /absolute/path
    # Setting: USER_FOLDER/Documents/Tabletop Simulator
    # #include relative/path (first relative to setting, then to included file)
    # #include !/path (always relative to setting)
    # #include ~/path (relative to user home)
    # enclose path in <> to enclose contents in do ... end, so strip do ... end?
    def __init__(self, files: ExportVFS, file_type, key, src, marker = None):
        self.files = files
        self.file_type = file_type
        self.key = key
        self.iterator = src if isinstance(src, StringLineIterator) else StringLineIterator(src)
        self.marker = marker

    def get_include_info(self, line_match):
        raw_path = line_match.group(1)
        raw_type = line_match.group(2)

        include_type = self.INCLUDE_TYPE.get(raw_type, 'relative')
        wrapped = True if self.RE_WRAPPED.match(raw_path) else False
        path = raw_path[1:-1] if wrapped else raw_path

        return include_type, path, wrapped

    def get_include_path(self, include_type, path):
        #logger.debug(f'Check include type: {include_type} / {self.key} / {path}')
        if 'absolute' == include_type:
            return Path('lib-absolute') / path[1:]
        elif 'fixed' == include_type:
            return Path('lib') / path[2:]
        elif 'home' == include_type:
            return Path('lib-home') / path[2:]
        elif 'relative' == include_type:
            if 'main.ttslua' == self.key.name:
                # including from object LuaScript
                return Path('lib') / path
            else:
                return os.path.normpath(Path(self.key).parent / path)
        else:
            logger.debug(f'Unknown include type: {include_type} [{path}]')

    def process_line(self, contents, line):
        line_match = self.RE_INCLUDE.match(line)
        #print(line)
        if line_match:
            include_type, path, wrapped = self.get_include_info(line_match)
            if path == self.marker:
                #print(f'end of {path}')
                # end of included file
                return False
            else:
                # process included file
                include_path = self.get_include_path(include_type, path)
                #print(f'Extract include: {include_path}')
                lse = LuaScriptExtractor(
                    self.files,
                    'lib',
                    include_path,
                    self.iterator,
                    path,
                )
                lse.extract()
                ipath = f'<{path}>' if wrapped else path
                contents.append(f'#include {ipath}')
                return True
        else:
            contents.append(line)
            return True

    def extract(self):
        contents = []
        while True:
            line = self.iterator.next()
            if line is None:
                break
            if not self.process_line(contents, line):
                break

        if 'file' == self.file_type:
            self.files.add_file(Path(f'{self.key}'), '\n'.join(contents))
            pass
        elif 'lib' == self.file_type:
            self.files.add_lib_file(Path(f'{self.key}.ttslua'), '\n'.join(contents))
        else:
            logger.debug(f'Unknown file type [{self.file_type}]: {self.key}')
