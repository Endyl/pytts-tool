"""
Project Structure

build/
imports/
src/
    assets/
    lib/
    lib-absolute/
    lib-home/
    save/
        children/
        fields/
        objects/
            Name.GUID/
                fields/
                objects/
                main.json
                main.ttslua
                main.xml
        main.json
        main.ttslua
        main.xml
        guid-map.json
"""
from pathlib import Path
from typing import Generator, Any


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
    def __init__(self, data: dict, vfs: ExportVFS):
        self.data = data
        self.vfs = vfs

    def export_as_project(self):
        self.vfs.add_file(Path('src/save/main.ttslua'), {})

        for key, value in self.data:
            pass
