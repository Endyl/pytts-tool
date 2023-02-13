import json
import mimetypes
import os, os.path
from urllib.parse import urlparse
import time

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
#endregion: misc_keys

KEY_TO_EXT = {
    KEY_SKY_URL: '.jpg',
    KEY_TABLE_URL: '.jpg',
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

    @classmethod
    def create(cls, files, get_path, url, ext=None, guess_ext=None):
        if url not in cls.RES_LIST:
            cls.RES_LIST[url] = cls(url, ext, guess_ext)
        res = cls.RES_LIST[url]
        files[get_path(res)] = res

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

    def __init__(self, data: dict, *args, **kwargs):
        self.data = data

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
            return TTSSave(json.load(savefile), *args, **kwargs)

    def __init__(self, data, *args, do_backup=False, **kwargs):
        super().__init__(data, *args, **kwargs)
        self.do_backup = do_backup

    def export_as_project(self, path):
        export_files = {
            self.FILE_MAIN: {},
        }

        # Export fields
        for c_key, c_value in self.iterate_data():
            if c_key not in self.KEYS_ALL:
                print(f'Unknown key: {c_key}')
            self.export(c_key, c_value, export_files)

        # Write exported files
        file_progress = tqdm(export_files.items())
        for fpath, fcontent in file_progress:
            full_path = os.path.join(path, fpath)
            file_progress.set_description(f'Export: {full_path}')
            path_parts = os.path.split(full_path)
            os.makedirs(path_parts[0], exist_ok=True)
            fname = os.path.splitext(path_parts[1])

            if isinstance(fcontent, ResourceRequest):
                if not os.path.isfile(full_path):
                    fcontent.download(full_path)
            else:
                with open(full_path, 'w') as f:
                    if '.json' == fname[1]:
                        json.dump(fcontent, f, ensure_ascii=False, indent='\t')
                    else:
                        f.write(str(fcontent))

    # ------------------------------------------------------ Field Exporters ###
    def export(self, key, value, files):
        exporter = getattr(self, f'export__{key}', self.export_raw)
        return exporter(key, value, files)

    def export_raw(self, key, value, files):
        if key in self.KEYS_AS_EXTERNAL:
            files[f'{self.FILE_EXTERNAL}/{key}.json'] = value
        else:
            if self.do_backup and is_url(value):
                resource = ResourceRequest(value, guess_ext=KEY_TO_EXT.get(key, None))
                files[f'{self.FILE_BACKUP}/{key}{resource.get_ext()}'] = resource
            files[self.FILE_MAIN][key] = value

    def export__DecalPallet(self, key, value, files):
        if self.do_backup and value:
            for i, decal in enumerate(value):
                decal_url = decal.get(KEY_IMAGE_URL, None)
                if decal_url and is_url(decal_url):
                    resource = ResourceRequest(decal_url, guess_ext='.png')
                    files[f'{self.FILE_BACKUP}/{key}-{i}{resource.get_ext()}'] = resource
        self.export_raw(key, value, files)

    def export__LuaScript(self, key, value, files):
        files[self.FILE_LUA] = value

    def export__XmlUI(self, key, value, files):
        files[self.FILE_XML] = value

    def export__LuaScriptState(self, key, value, files):
        if type(value) is str:
            files[self.FILE_LUA_STATE_RAW] = value
        else:
            files[self.FILE_LUA_STATE] = json_dumps(value)

    def export__ObjectStates(self, key, value, files):
        files[self.FILE_MAIN][key] = []
        for obj_data in value:
            save_obj = TTSSaveObject(obj_data, self, self.FILE_OBJECTS)
            save_obj.export_as_project(files)
            files[self.FILE_MAIN][key].append(save_obj.folder_name)



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

    def __init__(self, data, save: TTSSave, path, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        self.save = save
        self.data = data
        self.path = f'{path}/{self.folder_name}'
        self.do_backup = save.do_backup

    @property
    def guid(self):
        return self.data.get(KEY_GUID, 'ffffff')

    @property
    def name(self):
        return self.data.get(KEY_NAME, 'UNKNOWN')

    @property
    def folder_name(self):
        return f'{self.name}.{self.guid}'

    def export_as_project(self, files):
        files[self.get_path(self.FILE_MAIN)] = {}
        for c_key, c_value in self.iterate_data():
            if c_key not in self.KEYS_ALL:
                print(f'Unknown key: {c_key}')
            self.export(c_key, c_value, files)

    # ------------------------------------------------------ Field Exporters ###
    def get_path(self, path):
        return f'{self.path}/{path}'

    def get_ext_path(self, key):
        return self.get_path(f'{self.FILE_EXTERNAL}/{key}.json')

    def get_backup_path(self, key, res: ResourceRequest, is_root=False):
        root_path = f'{self.FILE_BACKUP}/{key}{res.get_ext()}'
        return root_path if is_root else self.get_path(root_path)



    def export(self, key, value, files):
        exporter = getattr(self, f'export__{key}', self.export_raw)
        return exporter(key, value, files)

    def export_raw(self, key, value, files):
        if key in self.KEYS_AS_EXTERNAL:
            files[self.get_ext_path(key)] = value
        else:
            if self.do_backup and is_url(value):
                resource = ResourceRequest(value, guess_ext=KEY_TO_EXT.get(key, None))
                files[self.get_backup_path(key, resource)] = resource
            files[self.get_path(self.FILE_MAIN)][key] = value

    def export__States(self, key, value, files):
        files[self.get_path(self.FILE_MAIN)][key] = {}
        for state_key, state_data in value.items():
            save_obj = TTSSaveObject(state_data, self.save, self.get_path(self.FILE_STATES))
            save_obj.export_as_project(files)
            files[self.get_path(self.FILE_MAIN)][key][state_key] = save_obj.folder_name

    def export__ContainedObjects(self, key, value, files):
        files[self.get_path(self.FILE_MAIN)][key] = []
        for obj_data in value:
            save_obj = TTSSaveObject(obj_data, self.save, self.get_path(self.FILE_OBJECTS))
            save_obj.export_as_project(files)
            files[self.get_path(self.FILE_MAIN)][key].append(save_obj.folder_name)

    def export__CustomDeck(self, key, value, files):
        self.export_raw(key, value, files)
        if not value:
            return
        for deckId, deck in value.items():
            if not (self.do_backup and deck):
                continue
            assets = (
                (deck.get(KEY_FACE_URL, None), f'{key}-{deckId}-{KEY_FACE_URL}'),
                (deck.get(KEY_BACK_URL, None), f'{key}-{deckId}-{KEY_BACK_URL}'),
            )
            for asset in assets:
                if not is_url(asset[0]):
                    continue
                ResourceRequest.create(
                    files, lambda res: self.get_backup_path(asset[1], res, True),
                    asset[0], guess_ext=KEY_TO_EXT.get(key, None)
                )
                #resource = ResourceRequest(asset[0], guess_ext=KEY_TO_EXT.get(key, None))
                #files[self.get_backup_path(asset[1], resource, True)] = resource


