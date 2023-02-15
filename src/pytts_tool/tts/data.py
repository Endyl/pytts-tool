from collections import namedtuple, defaultdict
import json
import mimetypes
import os, os.path
from urllib.parse import urlparse
import time
from typing import Any, Union, ClassVar, Final

import requests
import tomli, tomli_w
from tqdm import tqdm

#region: keys
#region: save_keys
KEY_SAVE_NAME = 'SaveName'
KEY_EPOCH_TIME = 'EpochTime'
KEY_DATE = 'Date'
KEY_VERSION_NUMBER = 'VersionNumber'
KEY_GAME_MODE = 'GameMode'
KEY_GAME_TYPE = 'GameType'
KEY_GAME_COMPLEXITY = 'GameComplexity'
KEY_PLAYING_TIME = 'PlayingTime'
KEY_PLAYER_COUNTS = 'PlayerCounts'
KEY_TAGS = 'Tags'
KEY_GRAVITY = 'Gravity'
KEY_PLAY_AREA = 'PlayArea'
KEY_TABLE = 'Table'
KEY_SKY = 'Sky'
KEY_SKY_URL = 'SkyURL'
KEY_NOTE = 'Note'
KEY_GRID = 'Grid'
KEY_COMPONENT_TAGS = 'ComponentTags'
KEY_TURNS = 'Turns'
KEY_DECAL_PALLET = 'DecalPallet'
KEY_TABLE_URL = 'TableURL'
KEY_RULES = 'Rules'
KEY_TAB_STATES = 'TabStates'
KEY_CAMERA_STATES = 'CameraStates'
KEY_SNAP_POINTS = 'SnapPoints'
KEY_LUA_SCRIPT_STATE = 'LuaScriptState'
KEY_OBJECT_STATES = 'ObjectStates'
KEY_HANDS = 'Hands'
KEY_LIGHTING = 'Lighting'
KEY_MUSIC_PLAYER = 'MusicPlayer'
KEY_TAG_STATES = 'TagStates'
KEY_LUA_SCRIPT = 'LuaScript'
KEY_XML_UI = 'XmlUI'
#endregion: save_keys

#region: object_keys
KEY_ATTACHED_SNAP_POINTS = 'AttachedSnapPoints'
KEY_AUTORAISE = 'Autoraise'
KEY_COLOR_DIFFUSE = 'ColorDiffuse'
KEY_CUSTOM_ASSETBUNDLE = 'CustomAssetbundle'
KEY_CUSTOM_DECK = 'CustomDeck'
KEY_CUSTOM_IMAGE = 'CustomImage'
KEY_CUSTOM_MESH = 'CustomMesh'
KEY_DECK_IDS = 'DeckIDs'
KEY_DESCRIPTION = 'Description'
KEY_GM_NOTES = 'GMNotes'
KEY_GRID_PROJECTION = 'GridProjection'
KEY_GUID = 'GUID'
KEY_HIDDEN_WHEN_FACE_DOWN = 'HiddenWhenFaceDown'
KEY_IGNORE_FOW = 'IgnoreFoW'
KEY_LOCKED = 'Locked'
KEY_MATERIAL_INDEX = 'MaterialIndex'
KEY_MESH_INDEX = 'MeshIndex'
KEY_NAME = 'Name'
KEY_NICKNAME = 'Nickname'
KEY_NUMBER = 'Number'
KEY_SIDEWAYS_CARD = 'SidewaysCard'
KEY_SNAP = 'Snap'
KEY_STATES = 'States'
KEY_STICKY = 'Sticky'
KEY_TOOLTIP = 'Tooltip'
KEY_TRANSFORM = 'Transform'
KEY_CARD_ID = 'CardID'
KEY_BAG = 'Bag'
KEY_COUNTER = 'Counter'
KEY_CUSTOM_PDF = 'CustomPDF'
KEY_DRAG_SELECTABLE = 'DragSelectable'
KEY_HIDE_WHEN_FACE_DOWN = 'HideWhenFaceDown'
KEY_JOINT_HINGE = 'JointHinge'
KEY_LAYOUT_GROUP_SORT_INDEX = 'LayoutGroupSortIndex'
KEY_MEASURE_MOVEMENT = 'MeasureMovement'
KEY_PHYSICS_MATERIAL = 'PhysicsMaterial'
KEY_RIGID_BODY = 'Rigidbody'
KEY_TEXT = 'Text'
KEY_VALUE = 'Value'
KEY_CONTAINED_OBJECTS = 'ContainedObjects'
KEY_ROTATION_VALUES = 'RotationValues'
# Keys from save:
# KEY_GRID = 'Grid'
# KEY_HANDS = 'Hands'
# KEY_LUA_SCRIPT = 'LuaScript'
# KEY_LUA_SCRIPT_STATE = 'LuaScriptState'
# KEY_XML_UI = 'XmlUI'
#endregion: object_keys

#region: misc_keys
# Decal
KEY_IMAGE_URL = 'ImageURL'
# CustomDeck
KEY_FACE_URL = 'FaceURL'
KEY_BACK_URL = 'BackURL'
# CustomAssetbundle
KEY_ASSETBUNDLE_URL = 'AssetbundleURL'
KEY_ASSETBUNDLE_SECONDARY_URL = 'AssetbundleSecondaryURL'
# CustomImage
KEY_IMAGE_SECONDARY_URL = 'ImageSecondaryURL'
# CustomMesh
KEY_MESH_URL = 'MeshURL'
KEY_DIFFUSE_URL = 'DiffuseURL'
KEY_NORMAL_URL = 'NormalURL'
KEY_COLLIDER_URL = 'ColliderURL'
# CustomPDF
KEY_PDF_URL = 'PDFUrl'
#endregion: misc_keys

KEY_TO_EXT = {
    KEY_SKY_URL: '.img-x',
    KEY_TABLE_URL: '.img-x',
    KEY_ASSETBUNDLE_URL: '.bin',
    KEY_ASSETBUNDLE_SECONDARY_URL: '.bin',
    KEY_MESH_URL: '.bin',
    KEY_PDF_URL: '.pdf',
    KEY_IMAGE_URL: '.img-x',
    KEY_IMAGE_SECONDARY_URL: '.img-x',
    KEY_DIFFUSE_URL: '.img-x',
    KEY_NORMAL_URL: '.bin-x',
    KEY_COLLIDER_URL: '.bin',
    KEY_FACE_URL: '.img-x',
    KEY_BACK_URL: '.img-x',
}
#endregion: keys


def json_dumps(value):
    return json.dumps(value, ensure_ascii=False, indent='\t')

def toml_dumps(value):
    return tomli_w.dumps(value)

def is_url(value):
    try:
        result = urlparse(value)
        return all((result.scheme, result.netloc))
    except:
        return False


class ResourceRequest:
    MIME_EXT = {} # ?
    RES_LIST = {}
    GUID_MAP = defaultdict(list)

    @classmethod
    def create(cls, guid, files: 'FileExports', get_path, url, ext=None, guess_ext=None) -> 'ResourceRequest':
        if url not in cls.RES_LIST:
            cls.RES_LIST[url] = cls(url, ext, guess_ext)
        res = cls.RES_LIST[url]
        res_path = get_path(res)
        files.add(res_path, res)
        cls.GUID_MAP[url].append([guid, res_path])
        return res

    def __init__(self, url, ext=None, guess_ext=None):
        self.url = url
        self.ext = ext
        self.guess_ext = guess_ext

    def get_ext(self):
        if self.ext:
            return self.ext

        mtype, encoding = mimetypes.guess_type(self.url)
        if mtype is None:
            res = requests.head(self.url)
            mtype = ''
            for hname, hvalue in res.headers.items():
                lhname = str(hname).lower().strip()
                if lhname in ('content-type', 'contenttype'):
                    mtype = hvalue
        self.ext = mimetypes.guess_extension(mtype)

        return self.ext if self.ext is not None else self.guess_ext


    def download(self, path):
        chunk_encoded = False # Change to True if chunk encoded???
        chunk_size = None if chunk_encoded else 8192
        time.sleep(0.1)
        with requests.get(self.url, stream=True) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if (chunk_encoded and chunk) or not chunk_encoded:
                        f.write(chunk)

ExportPathInfo = namedtuple('ExportPathInfo', ('path', 'full', 'dir', 'name', 'ext'))
class FileExports:
    def __init__(self, base_path):
        self.files = {}
        self.base_path = base_path

    def add(self, path, content):
        self.files[path] = content

    def add_to(self, path, key, value):
        if not path in self.files:
            print(f'Adding to missing dict file: {path}')
            self.add(path, {})
        if key in self.files[path]:
            print(f'Multiple assignment [{path}: {key}]')
        self.files[path][key] = value


    def add_to2(self, path, key, key2, value):
        if not path in self.files:
            print(f'Adding to missing dict file: {path}')
            self.add(path, {})
        if not key in self.files[path]:
            print(f'Adding to missing dict key [{path}: {key}.{key2}]')
        if key2 in self.files[path][key]:
            print(f'Multiple assignment [{path}: {key}.{key2}]')
        self.files[path][key][key2] = value

    def append_to(self, path, key, value):
        if not path in self.files:
            print(f'Appending to key in missing file [{path}: {key}]')
            self.add(path, {})
        if not key in self.files[path]:
            print(f'Appending to missing key in file [{path}: {key}]')
            self.files[path][key] = []
        self.files[path][key].append(value)

    def get_path_info(self, fpath) -> ExportPathInfo:
        full_path = os.path.join(self.base_path, fpath)
        path_parts = os.path.split(full_path)
        return ExportPathInfo(
            fpath,
            full_path,
            path_parts[0],
            *os.path.splitext(path_parts[1])
        )

    def export_file(self, pinfo: ExportPathInfo, content):
        with open(pinfo.full, 'w') as f:
            if '.json' == pinfo.ext:
                json.dump(content, f, ensure_ascii=False, indent='\t')
            else:
                f.write(str(content))

    def export_resource(self, pinfo: ExportPathInfo, res: ResourceRequest):
        if os.path.isfile(pinfo.full):
            return
        res.download(pinfo.full)

    def export_all(self):
        pbar = tqdm(self.files.items())
        for fpath, fcontent in pbar:
            pinfo = self.get_path_info(fpath)
            pbar.set_description(f'Exporting: {pinfo.full}')
            os.makedirs(pinfo.dir, exist_ok=True)

            if isinstance(fcontent, ResourceRequest):
                self.export_resource(pinfo, fcontent)
            else:
                self.export_file(pinfo, fcontent)




class TTSBase:
    KEYS_ALL = ()
    KEYS_AS_EXTERNAL = ()

    FILE_EXTERNAL = 'core'
    FILE_LUA_LIB = 'lib'
    FILE_BACKUP = 'bin'
    FILE_STATES = 'states'
    FILE_OBJECTS = 'objects'

    FILE_MAIN = 'main.json'
    FILE_LUA = 'main.ttslua'
    FILE_LUA_STATE = 'state.json'
    FILE_LUA_STATE_RAW = 'state.txt'
    FILE_XML = 'main.xml'

    def __init__(
            self,
            data: dict,
            root: Union['TTSSave', None]=None,
            parent: Union['TTSSave', 'TTSSaveObject', None]=None,
            base_path: str='',
            *args,
            do_backup=False,
            **kwargs):
        self.data = data
        self.root = root
        self.parent = parent
        self.base_path = base_path
        self.do_backup = root.do_backup if root else do_backup
        self.files: Union[FileExports, None] = None

    def get_path(self, *path):
        return os.path.join(self.base_path, *path)

    def get_ext_path(self, key):
        return self.get_path(self.FILE_EXTERNAL, f'{key}.json')

    def get_backup_path(self, key, res: ResourceRequest, is_root=False):
        root_path = os.path.join(self.FILE_BACKUP, f'{key}{res.get_ext()}')
        return root_path if is_root else self.get_path(root_path)

    def iterate_data(self):
        for key in self.KEYS_ALL:
            if key in self.data:
                yield key, self.data[key]

        remaining = set(self.data.keys()) - set(self.KEYS_ALL)
        for key in remaining:
            yield key, self.data[key]



# ------------------------------------------------------------------ TTS Save ##
class TTSSave(TTSBase):
    KEYS_ALL = (
        KEY_SAVE_NAME,
        KEY_EPOCH_TIME,
        KEY_DATE,
        KEY_VERSION_NUMBER,
        KEY_GAME_MODE,
        KEY_GAME_TYPE,
        KEY_GAME_COMPLEXITY,
        KEY_PLAYING_TIME,
        KEY_PLAYER_COUNTS,
        KEY_TAGS,
        KEY_GRAVITY,
        KEY_PLAY_AREA,
        KEY_TABLE,
        KEY_SKY,
        KEY_SKY_URL,
        KEY_NOTE,
        KEY_GRID,
        KEY_COMPONENT_TAGS,
        KEY_TURNS,
        KEY_DECAL_PALLET,
        KEY_TABLE_URL,
        KEY_RULES,
        KEY_TAB_STATES,
        KEY_CAMERA_STATES,
        KEY_SNAP_POINTS,
        KEY_LUA_SCRIPT_STATE,
        KEY_OBJECT_STATES,
        KEY_HANDS,
        KEY_LIGHTING,
        KEY_MUSIC_PLAYER,
        KEY_TAG_STATES,
        KEY_LUA_SCRIPT,
        KEY_XML_UI,
    )
    KEYS_AS_EXTERNAL = (
        KEY_GRID,
        KEY_LIGHTING,
        KEY_HANDS,
        KEY_TURNS,
        KEY_TAB_STATES,
        KEY_CAMERA_STATES,
        KEY_DECAL_PALLET,
    )

    @classmethod
    def from_save(cls, path, *args, **kwargs) -> 'TTSSave':
        with open(path, 'r') as savefile:
            return TTSSave(json.load(savefile), None, None, '', *args, **kwargs)

    def export_as_project(self, export_path):
        self.files = FileExports(export_path)
        self.files.add(self.FILE_MAIN, {})

        # Export fields
        for c_key, c_value in self.iterate_data():
            if c_key not in self.KEYS_ALL:
                print(f'Unknown key: {c_key}')
            self.export(c_key, c_value, self.files)
        if self.do_backup:
            self.files.add(self.get_path(self.FILE_BACKUP, '__GUID_MAP__.json'), dict(ResourceRequest.GUID_MAP))

        # Write exported files
        self.files.export_all()

    # ------------------------------------------------------ Field Exporters ###
    def export(self, key, value, files: FileExports):
        exporter = getattr(self, f'export__{key}', self.export_raw)
        return exporter(key, value, files)

    def export_raw(self, key, value, files: FileExports):
        if key in self.KEYS_AS_EXTERNAL:
            files.add(self.get_ext_path(key), value)
        else:
            if self.do_backup and is_url(value):
                ResourceRequest.create(
                    '_save_', files, lambda res: self.get_backup_path(key, res, True),
                    value, guess_ext=KEY_TO_EXT.get(key, None)
                )
            files.add_to(self.get_path(self.FILE_MAIN), key, value)

    def export__DecalPallet(self, key, value, files):
        if self.do_backup and value:
            for i, decal in enumerate(value):
                decal_url = decal.get(KEY_IMAGE_URL, None)
                if decal_url and is_url(decal_url):
                    ResourceRequest.create(
                        '_save_', files, lambda res: self.get_backup_path(f'{key}/{i}', res, True),
                        decal_url, guess_ext=KEY_TO_EXT.get(key, None)
                    )
        self.export_raw(key, value, files)

    def export__LuaScript(self, key, value, files: FileExports):
        if value and str(value).strip():
            files.add(self.get_path(self.FILE_LUA), value)
        else:
            self.export_raw(key, value, files)

    def export__XmlUI(self, key, value, files: FileExports):
        if value and str(value).strip():
            files.add(self.get_path(self.FILE_XML), value)
        else:
            self.export_raw(key, value, files)

    def export__LuaScriptState(self, key, value, files: FileExports):
        if not (value and str(value).strip()):
            self.export_raw(key, value, files)
            return
        if type(value) is str:
            files.add(self.get_path(self.FILE_LUA_STATE_RAW), value)
        else:
            files.add(self.get_path(self.FILE_LUA_STATE), json_dumps(value))

    def export__ObjectStates(self, key, value, files: FileExports):
        files.add_to(self.get_path(self.FILE_MAIN), key, [])
        for obj_data in value:
            save_obj = TTSSaveObject(obj_data, self, self, self.FILE_OBJECTS)
            save_obj.export_as_project(files)
            files.append_to(self.get_path(self.FILE_MAIN), key, save_obj.folder_name)



# ----------------------------------------------------------- TTS Save Object ##
class TTSSaveObject(TTSBase):
    KEYS_ALL = (
        KEY_GUID,
        KEY_NAME,
        KEY_NICKNAME,
        KEY_DESCRIPTION,
        KEY_TOOLTIP,
        KEY_GM_NOTES,
        KEY_VALUE,
        KEY_NUMBER,
        KEY_STICKY,
        KEY_LOCKED,
        KEY_AUTORAISE,
        KEY_HANDS,
        KEY_IGNORE_FOW,
        KEY_HIDDEN_WHEN_FACE_DOWN,
        KEY_HIDE_WHEN_FACE_DOWN,
        KEY_SIDEWAYS_CARD,
        KEY_DRAG_SELECTABLE,
        KEY_SNAP,
        KEY_GRID,
        KEY_GRID_PROJECTION,
        KEY_LAYOUT_GROUP_SORT_INDEX,
        KEY_MEASURE_MOVEMENT,

        KEY_CARD_ID,
        KEY_DECK_IDS,
        KEY_CUSTOM_DECK,

        KEY_TEXT,
        KEY_COUNTER,

        KEY_MATERIAL_INDEX,
        KEY_MESH_INDEX,
        KEY_CUSTOM_ASSETBUNDLE,
        KEY_CUSTOM_MESH,
        KEY_PHYSICS_MATERIAL,
        KEY_RIGID_BODY,

        KEY_CUSTOM_PDF,
        KEY_CUSTOM_IMAGE,
        KEY_BAG,
        KEY_JOINT_HINGE,

        KEY_COLOR_DIFFUSE,
        KEY_TRANSFORM,
        KEY_ATTACHED_SNAP_POINTS,
        KEY_ROTATION_VALUES,
        KEY_STATES,
        KEY_CONTAINED_OBJECTS,
        KEY_XML_UI,
        KEY_LUA_SCRIPT_STATE,
        KEY_LUA_SCRIPT,
    )

    KEYS_AS_EXTERNAL = ()


    def __init__(
            self,
            data: dict,
            root: Union['TTSSave', None]=None,
            parent: Union['TTSSave', 'TTSSaveObject', None]=None,
            base_path: str='',
            *args,
            do_backup=False,
            **kwargs):
        super().__init__(data, root, parent, base_path, *args, do_backup=do_backup, **kwargs)
        self.base_path = f'{base_path}/{self.folder_name}'

    @property
    def guid(self):
        return self.data.get(KEY_GUID, 'ffffff')

    @property
    def name(self):
        return self.data.get(KEY_NAME, 'UNKNOWN')

    @property
    def folder_name(self):
        return f'{self.name}.{self.guid}'

    def export_as_project(self, files: FileExports):
        files.add(self.get_path(self.FILE_MAIN), {})
        for c_key, c_value in self.iterate_data():
            if c_key not in self.KEYS_ALL:
                print(f'Unknown key: {c_key}')
            self.export(c_key, c_value, files)

    # ------------------------------------------------------ Field Exporters ###
    def export(self, key, value, files: FileExports):
        exporter = getattr(self, f'export__{key}', self.export_raw)
        return exporter(key, value, files)

    def export_raw(self, key, value, files: FileExports):
        if key in self.KEYS_AS_EXTERNAL:
            files.add(self.get_ext_path(key), value)
        else:
            if self.do_backup and is_url(value):
                ResourceRequest.create(
                    self.guid, files, lambda res: self.get_backup_path(key, res, False),
                    value, guess_ext=KEY_TO_EXT.get(key, None)
                )
            files.add_to(self.get_path(self.FILE_MAIN), key, value)

    def export__States(self, key, value, files: FileExports):
        files.add_to(self.get_path(self.FILE_MAIN), key, {})
        for state_key, state_data in value.items():
            save_obj = TTSSaveObject(state_data, self.root, self, self.get_path(self.FILE_STATES))
            save_obj.export_as_project(files)
            files.add_to2(self.get_path(self.FILE_MAIN), key, state_key, save_obj.folder_name)

    def export__ContainedObjects(self, key, value, files: FileExports):
        files.add_to(self.get_path(self.FILE_MAIN), key, [])
        for obj_data in value:
            save_obj = TTSSaveObject(obj_data, self.root, self, self.get_path(self.FILE_OBJECTS))
            save_obj.export_as_project(files)
            files.append_to(self.get_path(self.FILE_MAIN), key, save_obj.folder_name)

    def export__CustomDeck(self, key, value, files: FileExports):
        self.export_raw(key, value, files)
        if not value:
            return
        for deckId, deck in value.items():
            if not (self.do_backup and deck):
                continue
            assets = (
                (deck.get(KEY_FACE_URL, None), f'{key}/{deckId}-{KEY_FACE_URL}'),
                (deck.get(KEY_BACK_URL, None), f'{key}/{deckId}-{KEY_BACK_URL}'),
            )
            for asset in assets:
                if not is_url(asset[0]):
                    continue
                ResourceRequest.create(
                    self.guid, files, lambda res: self.get_backup_path(asset[1], res, True),
                    asset[0], guess_ext=KEY_TO_EXT.get(key, None)
                )

    def export__CustomAssetbundle(self, key, value, files: FileExports):
        self.export_raw(key, value, files)
        if not (self.do_backup and value):
            return
        assets = (
            (value.get(KEY_ASSETBUNDLE_URL, None), f'{key}/{KEY_ASSETBUNDLE_URL}'),
            (value.get(KEY_ASSETBUNDLE_SECONDARY_URL, None), f'{key}/{KEY_ASSETBUNDLE_SECONDARY_URL}'),
        )
        for asset in assets:
            if not is_url(asset[0]):
                continue
            ResourceRequest.create(
                self.guid, files, lambda res: self.get_backup_path(asset[1], res, False),
                asset[0], guess_ext=KEY_TO_EXT.get(key, None)
            )

    def export__CustomImage(self, key, value, files: FileExports):
        self.export_raw(key, value, files)
        if not (self.do_backup and value):
            return
        assets = (
            (value.get(KEY_IMAGE_URL, None), f'{key}/{KEY_IMAGE_URL}'),
            (value.get(KEY_IMAGE_SECONDARY_URL, None), f'{key}/{KEY_IMAGE_SECONDARY_URL}'),
        )
        for asset in assets:
            if not is_url(asset[0]):
                continue
            ResourceRequest.create(
                self.guid, files, lambda res: self.get_backup_path(asset[1], res, False),
                asset[0], guess_ext=KEY_TO_EXT.get(key, None)
            )

    def export__CustomMesh(self, key, value, files: FileExports):
        self.export_raw(key, value, files)
        if not (self.do_backup and value):
            return
        assets = (
            (value.get(KEY_MESH_URL, None), f'{key}/{KEY_MESH_URL}'),
            (value.get(KEY_DIFFUSE_URL, None), f'{key}/{KEY_DIFFUSE_URL}'),
            (value.get(KEY_NORMAL_URL, None), f'{key}/{KEY_NORMAL_URL}'),
            (value.get(KEY_COLLIDER_URL, None), f'{key}/{KEY_COLLIDER_URL}'),
        )
        for asset in assets:
            if not is_url(asset[0]):
                continue
            ResourceRequest.create(
                self.guid, files, lambda res: self.get_backup_path(asset[1], res, False),
                asset[0], guess_ext=KEY_TO_EXT.get(key, None)
            )

    def export__CustomPDF(self, key, value, files: FileExports):
        self.export_raw(key, value, files)
        if not (self.do_backup and value):
            return
        assets = (
            (value.get(KEY_PDF_URL, None), f'{key}/{KEY_PDF_URL}'),
        )
        for asset in assets:
            if not is_url(asset[0]):
                continue
            ResourceRequest.create(
                self.guid, files, lambda res: self.get_backup_path(asset[1], res, False),
                asset[0], guess_ext=KEY_TO_EXT.get(key, None)
            )

    def export__LuaScript(self, key, value, files: FileExports):
        if value and str(value).strip():
            files.add(self.get_path(self.FILE_LUA), value)
        else:
            self.export_raw(key, value, files)

    def export__XmlUI(self, key, value, files: FileExports):
        if value and str(value).strip():
            files.add(self.get_path(self.FILE_XML), value)
        else:
            self.export_raw(key, value, files)

    def export__LuaScriptState(self, key, value, files: FileExports):
        if not (value and str(value).strip()):
            self.export_raw(key, value, files)
            return
        if type(value) is str:
            files.add(self.get_path(self.FILE_LUA_STATE_RAW), value)
        else:
            files.add(self.get_path(self.FILE_LUA_STATE), json_dumps(value))

class StringLineIterator(object):
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

class LuaScriptExtractor():
    # #include /absolute/path
    # Setting: USER_FOLDER/Documents/Tabletop Simulator
    # #include relative/path (first relative to setting, then to included file)
    # #include !/path (always relative to setting)
    # enclose path in <> to enclose contents in do ... end, so strip do ... end?
    pass

