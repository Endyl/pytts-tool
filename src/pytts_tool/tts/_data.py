import json
from typing import Any, Union, ClassVar, Final

from attrs import define, field, asdict, fields, Attribute

# ====================================================================== Utils #
def attrs_iterator():
    pass

def should_export_field_as_file(field: Attribute):
    return field.metadata.get('as_file', False)

def get_field_exporter(instance: object, field: Attribute):
    return getattr(
        instance, f'export_field__{field.name}',
        getattr(instance, 'export_field')
    )

# ============================================================= TTS Data Model #
@define
class TTSVector:
    x: float
    y: float
    z: float



@define
class TTSColor:
    r: float
    g: float
    b: float
    a: float = field(default=1)
    name: str = field(default=None, kw_only=True)

    White: 'ClassVar[TTSColor]'
    Brown: 'ClassVar[TTSColor]'
    Red: 'ClassVar[TTSColor]'
    Orange: 'ClassVar[TTSColor]'
    Yellow: 'ClassVar[TTSColor]'
    Green: 'ClassVar[TTSColor]'
    Teal: 'ClassVar[TTSColor]'
    Blue: 'ClassVar[TTSColor]'
    Purple: 'ClassVar[TTSColor]'
    Pink: 'ClassVar[TTSColor]'
    Grey: 'ClassVar[TTSColor]'
    Black: 'ClassVar[TTSColor]'

    @classmethod
    def add(cls, name, values):
        setattr(cls, name, cls(*values, name=name))

    def as_name(self):
        if not self.name:
            raise AttributeError('No color name specified')
        return self.name

    def as_dict(self):
        return {
            'r': self.r,
            'g': self.g,
            'b': self.b,
            'a': self.a,
        }

TTSColor.add('White', (1, 1, 1,))
TTSColor.add('Brown', (0.443, 0.231, 0.09,))
TTSColor.add('Red', (0.856, 0.1, 0.094,))
TTSColor.add('Orange', (0.956, 0.392, 0.113,))
TTSColor.add('Yellow', (0.905, 0.898, 0.172,))
TTSColor.add('Green', (0.192, 0.701, 0.168,))
TTSColor.add('Teal', (0.129, 0.694, 0.607,))
TTSColor.add('Blue', (0.118, 0.53, 1,))
TTSColor.add('Purple', (0.627, 0.125, 0.941,))
TTSColor.add('Pink', (0.96, 0.439, 0.807,))
TTSColor.add('Grey', (0.5, 0.5, 0.5,))
TTSColor.add('Black', (0.25, 0.25, 0.25,))



@define
class TTSAssetbundle:
    pass



@define(kw_only=True)
class TTSSaveGrid:
    Type: int
    Lines: bool
    Color: Union[dict, TTSColor]
    Opacity: float
    ThickLines: bool
    Snapping: bool
    Offset: bool
    BothSnapping: bool
    xSize: float
    ySize: float
    PosOffset: Union[dict, TTSVector]

@define(kw_only=True)
class TTSSaveHands:
    Enable: bool = field(default=True)
    DisableUnused: bool = field(default=False)
    Hiding: int = field(default=0)

@define(kw_only=True)
class TTSSaveLighting:
    LightIntensity: float
    LightColor: Union[dict, TTSColor]
    AmbientIntensity: float
    AmbientType: int
    AmbientSkyColor: Union[dict, TTSColor]
    AmbientEquatorColor: Union[dict, TTSColor]
    AmbientGroundColor: Union[dict, TTSColor]
    ReflectionIntensity: float
    LutIndex: int
    LutContribution: float
    LutURL: str

@define(kw_only=True)
class TTSSaveTurns:
    Enable: bool
    Type: int
    TurnOrder: list[str]
    Reverse: bool
    SkipEmpty: bool
    DisableInteractions: bool
    PassTurns: bool
    TurnColor: str



@define(kw_only=True)
class TTSSaveObject:
    AttachedSnapPoints: list
    Autoraise: bool
    ColorDiffuse: dict
    CustomAssetbundle: Union[dict, TTSAssetbundle]
    CustomDeck: dict
    CustomImage: dict
    CustomMesh: dict
    DeckIDs: list
    Description: str
    GMNotes: str
    Grid: bool
    GridProjection: bool
    GUID: str
    Hands: bool
    HiddenWhenFaceDown: bool
    IgnoreFoW: bool
    Locked: bool
    LuaScript: str
    LuaScriptState: str
    MaterialIndex: int
    MeshIndex: int
    Name: str
    Nickname: str
    Number: int
    SidewaysCard: bool
    Snap: bool
    States: dict
    Sticky: bool
    Tooltip: bool
    Transform: dict
    XmlUI: str

    CardID: int
    ContainedObjects: list



@define(kw_only=True)
class TTSSave:
    SaveName: str
    EpochTime: int = field(kw_only=True, default=0)
    Date: str
    VersionNumber: str
    GameMode: str
    GameType: str = field(kw_only=True, default='')
    GameComplexity: str = field(kw_only=True, default='')
    PlayingTime: list[int] = field(kw_only=True, factory=lambda: [0])
    PlayerCounts: list[int] = field(kw_only=True, factory=lambda: [1])
    Tags: list = field(kw_only=True, factory=list)
    Gravity: float
    PlayArea: float
    Table: str
    Sky: str
    SkyURL: str
    Note: str
    Grid: Union[dict, TTSSaveGrid]
    ComponentTags: dict = field(kw_only=True, factory=dict)
    Turns: Union[dict, TTSSaveTurns]
    DecalPallet: list
    TableURL: str
    Rules: str
    TabStates: dict
    CameraStates: dict
    SnapPoints: list

    LuaScriptState: str = field(kw_only=True, metadata={'as_file': True})
    ObjectStates: list[Union[dict, TTSSaveObject]] = field(kw_only=True, metadata={'as_file': True})
    Hands: Union[dict, TTSSaveHands]
    Lighting: Union[dict, TTSSaveLighting]
    MusicPlayer: dict = field(kw_only=True, factory=dict)
    TagStates: dict = field(kw_only=True, factory=dict)
    LuaScript: str = field(kw_only=True, metadata={'as_file': True})
    XmlUI: str = field(kw_only=True, metadata={'as_file': True})

    @classmethod
    def from_save(cls, path) -> 'TTSSave':
        with open(path, 'r') as savefile:
            return TTSSave(**json.load(savefile))

    @classmethod
    def from_project(cls, path) -> 'TTSSave':
        return TTSSave(**{})

    @classmethod
    def export_as_save(cls, path):
        pass

    def export_as_project(self, path):
        export_dict = {}
        export_files = {}

        att: Attribute
        for att in fields(self.__class__): # type: ignore
            value = getattr(self, att.name)
            if should_export_field_as_file(att):
                pass
            else:
                export_dict[att.name] = getattr(self, att.name)

    def serialize(self):
        pass
