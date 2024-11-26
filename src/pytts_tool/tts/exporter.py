"""
Project Structure

build/
imports/
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
import os.path
from pathlib import Path
import re
from typing import Generator, Any

from .structured import SaveKeys, ObjectKeys, MiscKeys

def is_string_field_empty(value: Any) -> bool:
    return not (value and str(value).strip())

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


class ExportVFS:
    def __init__(self, fs_root: Path, lib_root: Path):
        self.fs_root = fs_root
        self.lib_root = lib_root

        self.files = {}
        self.lib = {}

    def add_lib_file(self, path: Path, content: str):
        if path in self.lib and (content != self.lib[path]):
            print(f'Mismatched content: {path}')
            return
        self.lib[path] = content

    def add_file(self, path: Path, content: str | list | dict):
        if path in self.files:
            print(f'Path already exists: <{path}>')
        else:
            self.files[path] = content

    def add_to_file(self, path: Path, *keys: list[str], value):
        if path not in self.files:
            print(f'Trying to add to missing file: <{path}>: <{keys}>')
            self.add_file(path, {})

        target = self.files[path]
        for is_last, key in lookahead(keys):
            if is_last:
                if key in target:
                    print(f'Multiple assignment: <{path}: {keys}>')
                target[key] = value
            else:
                if key not in target:
                    print(f'Creating target path: <{path}: {key} / {keys}>')
                    target[key] = {}
                target = target[key]

    def append_to(self, path: Path, key: str, value):
        if path not in self.files:
            print(f'Trying to append to missing file: <{path}>: <{key}>')
            self.add_file(path, {})

        target = self.files[path]
        if key not in target:
            print(f'Append to missing key: <{path}: {key}>')
            target[key] = []
        target[key].append(value)


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
        if 'absolute' == include_type:
            return path
        elif 'fixed' == include_type:
            return path[2:]
        elif 'home' == include_type:
            return path
        elif 'relative' == include_type:
            if 'main.ttslua' == self.key:
                return path
            else:
                return os.path.normpath(Path(self.key).parent / path)
        else:
            print(f'Unknown include type: {include_type} [{path}]')

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
            print(f'Unknown file type [{self.file_type}]: {self.key}')
