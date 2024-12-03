import json
from pathlib import Path
import re

class TTSSaveBuilder:
    def __init__(self, save_root: Path):
        self.root = save_root

    def read_text(self, path: Path):
        with open(path, 'r') as f:
            return f.read()

    def read_json(self, path: Path):
        with open(path, 'r') as f:
            return json.load(f)

    def read_fields(self, home: Path, data: dict):
        fields_path = home / 'fields'
        if not (fields_path.is_dir() and fields_path.exists()):
            return

        for path in fields_path.iterdir():
            if not path.is_file():
                continue

            if '.json' == path.suffix:
                data[path.stem] = self.read_json(path)
            else:
                data[path.stem] = self.read_text(path)

    def read_script(self, root: Path, home: Path, data: dict):
        script_path = home / 'main.ttslua'
        if script_path.is_file():
            source = self.read_text(script_path)
            data['LuaScript'] = LuaScriptBuilder(root, script_path, source, False).build()

    def read_state(self, home: Path, data: dict):
        # TODO: warn if both?
        state_raw_path = home / 'state.txt'
        if state_raw_path.is_file():
            data['LuaScriptState'] = self.read_text(state_raw_path)

        state_path = home / 'state.json'
        if state_path.is_file():
            data['LuaScriptState'] = json.dumps(self.read_json(state_path))

    def read_ui(self, home: Path, data: dict):

        ui_path = home / 'main.xml'
        if ui_path.is_file():
            data['XmlUI'] = self.read_text(ui_path)

    def read_contents(self, root: Path, home: Path, data: dict, key):
        contents = []

        registry = data.get(key, [])
        for item in registry:
            if isinstance(item, str):
                # Name.GUID reference
                item_home = home / 'objects' / item
                print(f'Adding explicit object: {item_home.name}')
                contents.append(self.build_object(
                    root, item_home, 'ContainedObjects', True, True
                ))
            else:
                # raw object
                print(f'Adding raw object: {item.get("Name", "?")}.{item.get("GUID", "?")}')
                contents.append(item)

        objects_path = home / 'objects'
        if objects_path.is_dir() and objects_path.exists():
            for item_home in objects_path.iterdir():
                if str(item_home.name) in registry:
                    continue
                print(f'Adding implicit object: {item_home.name}')
                contents.append(self.build_object(
                    root, item_home, 'ContainedObjects', True, True
                ))

        if contents:
            data[key] = contents

    def read_children(self, root: Path, home: Path, data: dict):
        children = []

        registry = data.get('ChildObjects', [])
        for item in registry:
            if isinstance(item, str):
                # Name.GUID reference
                item_home = home / 'children' / item
                print(f'Adding explicit child: {item_home.name}')
                children.append(self.build_object(
                    root, item_home, 'ContainedObjects', True, True
                ))
            else:
                # raw object
                print(f'Adding raw child: {item.get("Name", "?")}.{item.get("GUID", "?")}')
                children.append(item)

        children_path = home / 'children'
        if children_path.is_dir() and children_path.exists():
            for item_home in children_path.iterdir():
                if str(item_home.name) in registry:
                    continue
                print(f'Adding implicit child: {item_home.name}')
                children.append(self.build_object(
                    root, item_home, 'ContainedObjects', True, True
                ))

        if children:
            data['ChildObjects'] = children

    def read_object_states(self, root: Path, home: Path, data: dict):
        states = {}

        reg_set = set()
        registry = data.get('States', {}).items()
        for key, item in registry:
            if isinstance(item, str):
                # key.Name.GUID reference
                reg_set.add(item)
                item_home = home / 'states' / f'{key}.{item}'
                print(f'Adding explicit state: {item_home.name}')
                states[key] = self.build_object(
                    root, item_home, 'ContainedObjects', True, True
                )
            else:
                print(f'Adding raw state: {key}.{item.get("Name", "?")}.{item.get("GUID", "?")}')
                states[key] = item

        states_path = home / 'states'
        if states_path.is_dir() and states_path.exists():
            for item_home in states_path.iterdir():
                home_parts = str(item_home.name).split('.')
                key = home_parts[0]
                name = '.'.join(home_parts[1:])
                if name in reg_set:
                    continue
                print(f'Adding implicit state: {name}')
                states[key] = self.build_object(
                    root, item_home, 'ContainedObjects', True, True
                )

        if states:
            data['States'] = states

    def build_object(self, root: Path, home: Path, contents_key, read_children, read_state_objects):
        data = self.read_json(home / 'main.json')
        self.read_fields(home, data)
        self.read_script(root, home, data)
        self.read_state(home, data)
        self.read_ui(home, data)

        if contents_key:
            self.read_contents(root, home, data, contents_key)

        if read_children:
            self.read_children(root, home, data)

        if read_state_objects:
            self.read_object_states(root, home, data)

        return data

    def build_save(self):
        return self.build_object(
            self.root,
            self.root / 'src' / 'save',
            'ObjectStates',
            False,
            False
        )


class LuaScriptBuilder:
    RE_INCLUDE = re.compile(r'^#include\s+(<?(/|!/|~!|).+>?)\s*$')
    RE_WRAPPED = re.compile(r'^<(.*)>$')

    INCLUDE_TYPE = {
        '/': 'absolute',
        '!/': 'fixed',
        '~/': 'home',
    }

    def __init__(self, root: Path, path: Path, source: str, is_relative_anchor):
        self.root = root
        self.path = path
        self.source = source
        self.is_relative_anchor = is_relative_anchor

    def read_text(self, path: Path):
        with open(path, 'r') as f:
            return f.read()

    def get_include_info(self, line_match):
        raw_path = line_match.group(1)
        raw_type = line_match.group(2)

        include_type = self.INCLUDE_TYPE.get(raw_type, 'relative')
        wrapped = True if self.RE_WRAPPED.match(raw_path) else False
        path = raw_path[1:-1] if wrapped else raw_path

        return include_type, path, wrapped

    def build(self):
        result = []
        for line in self.source.splitlines():
            include_match = self.RE_INCLUDE.match(line)
            if not include_match:
                result.append(line)
                continue

            source = None
            include_type, path, wrapped = self.get_include_info(include_match)
            if 'absolute' == include_type:
                ipath = (self.root / 'lib-absolute' / path[1:]).with_suffix('.ttslua')
                source = self.read_text(ipath)
                source = LuaScriptBuilder(self.root, ipath, source, True).build()
            elif 'fixed' == include_type:
                ipath = (self.root / 'lib' / path[2:]).with_suffix('.ttslua')
                source = self.read_text(ipath)
                source = LuaScriptBuilder(self.root, ipath, source, True).build()
            elif 'home' == include_type:
                ipath = (self.root / 'lib-home' / path[2:]).with_suffix('.ttslua')
                source = self.read_text(ipath)
                source = LuaScriptBuilder(self.root, ipath, source, True).build()
            elif 'relative' == include_type:
                if self.is_relative_anchor:
                    ipath = self.path.parent / path
                else:
                    ipath = self.root / 'lib' / path
                ipath = ipath.with_suffix('.ttslua')
                source = self.read_text(ipath)
                source = LuaScriptBuilder(self.root, ipath, source, True).build()
            else:
                print(f'Unknown include type: {include_type}')

            result.append(f'----{line}')
            if source:
                result.append(source if not wrapped else f'do\n\n{source}\n\nend')
            result.append(f'----{line}')

        return '\n'.join(result)
