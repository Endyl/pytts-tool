"""
TODO:
- color strings
"""
from __future__ import annotations
from enum import StrEnum
from typing import Annotated, Literal, Optional, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

# ===================================================================== Utils #
def get_known_fields():
    import inspect

    result = set()

    for name, value in globals().items():
        if not (inspect.isclass(value) and issubclass(value, TTSBaseModel)):
            continue
        if not (name == 'TTSSave' or name.endswith('Object')):
            continue

        result |= set(value.model_fields.keys())

    return sorted(list(result))

# ==================================================================== Global #
class SaveKeys(StrEnum):
    SAVE_NAME = 'SaveName'
    EPOCH_TIME = 'EpochTime'
    DATE = 'Date'
    VERSION_NUMBER = 'VersionNumber'
    GAME_MODE = 'GameMode'
    GAME_TYPE = 'GameType'
    GAME_COMPLEXITY = 'GameComplexity'
    PLAYING_TIME = 'PlayingTime'
    PLAYER_COUNTS = 'PlayerCounts'
    TAGS = 'Tags'
    GRAVITY = 'Gravity'
    PLAY_AREA = 'PlayArea'
    TABLE = 'Table'
    SKY = 'Sky'
    SKY_URL = 'SkyURL'
    NOTE = 'Note'
    GRID = 'Grid'
    COMPONENT_TAGS = 'ComponentTags'
    TURNS = 'Turns'
    DECAL_PALLET = 'DecalPallet'
    TABLE_URL = 'TableURL'
    RULES = 'Rules'
    TAB_STATES = 'TabStates'
    CAMERA_STATES = 'CameraStates'
    SNAP_POINTS = 'SnapPoints'
    LUA_SCRIPT_STATE = 'LuaScriptState'
    OBJECT_STATES = 'ObjectStates'
    HANDS = 'Hands'
    LIGHTING = 'Lighting'
    MUSIC_PLAYER = 'MusicPlayer'
    TAG_STATES = 'TagStates'
    LUA_SCRIPT = 'LuaScript'
    XML_UI = 'XmlUI'

class ObjectKeys(StrEnum):
    ATTACHED_SNAP_POINTS = 'AttachedSnapPoints'
    AUTORAISE = 'Autoraise'
    COLOR_DIFFUSE = 'ColorDiffuse'
    CUSTOM_ASSETBUNDLE = 'CustomAssetbundle'
    CUSTOM_DECK = 'CustomDeck'
    CUSTOM_IMAGE = 'CustomImage'
    CUSTOM_MESH = 'CustomMesh'
    DECK_IDS = 'DeckIDs'
    DESCRIPTION = 'Description'
    GM_NOTES = 'GMNotes'
    GRID_PROJECTION = 'GridProjection'
    GUID = 'GUID'
    HIDDEN_WHEN_FACE_DOWN = 'HiddenWhenFaceDown'
    IGNORE_FOW = 'IgnoreFoW'
    LOCKED = 'Locked'
    MATERIAL_INDEX = 'MaterialIndex'
    MESH_INDEX = 'MeshIndex'
    NAME = 'Name'
    NICKNAME = 'Nickname'
    NUMBER = 'Number'
    SIDEWAYS_CARD = 'SidewaysCard'
    SNAP = 'Snap'
    STATES = 'States'
    STICKY = 'Sticky'
    TOOLTIP = 'Tooltip'
    TRANSFORM = 'Transform'
    CARD_ID = 'CardID'
    BAG = 'Bag'
    COUNTER = 'Counter'
    CUSTOM_PDF = 'CustomPDF'
    DRAG_SELECTABLE = 'DragSelectable'
    HIDE_WHEN_FACE_DOWN = 'HideWhenFaceDown'
    JOINT_HINGE = 'JointHinge'
    LAYOUT_GROUP_SORT_INDEX = 'LayoutGroupSortIndex'
    MEASURE_MOVEMENT = 'MeasureMovement'
    PHYSICS_MATERIAL = 'PhysicsMaterial'
    RIGID_BODY = 'Rigidbody'
    TEXT = 'Text'
    VALUE = 'Value'
    CONTAINED_OBJECTS = 'ContainedObjects'
    ROTATION_VALUES = 'RotationValues'
    GRID = 'Grid'
    HANDS = 'Hands'
    LUA_SCRIPT = 'LuaScript'
    LUA_SCRIPT_STATE = 'LuaScriptState'
    XML_UI = 'XmlUI'

class MiscKeys(StrEnum):# Decal
    IMAGE_URL = 'ImageURL'
    # CustomDeck
    FACE_URL = 'FaceURL'
    BACK_URL = 'BackURL'
    # CustomAssetbundle
    ASSETBUNDLE_URL = 'AssetbundleURL'
    ASSETBUNDLE_SECONDARY_URL = 'AssetbundleSecondaryURL'
    # CustomImage
    IMAGE_SECONDARY_URL = 'ImageSecondaryURL'
    # CustomMesh
    MESH_URL = 'MeshURL'
    DIFFUSE_URL = 'DiffuseURL'
    NORMAL_URL = 'NormalURL'
    COLLIDER_URL = 'ColliderURL'
    # CustomPDF
    PDF_URL = 'PDFUrl'


class TTSBaseModel(BaseModel):
    pass

class TTSRGBColor(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    r: float
    g: float
    b: float


class TTSRGBAColor(TTSRGBColor):
    a: float


class TTSXYZColor(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    x: float
    y: float
    z: float


class TTSCoordinate(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    x: float
    y: float
    z: float


class TTSRotation(TTSBaseModel):  # 0-360 ?
    model_config = ConfigDict(extra='forbid')

    x: float
    y: float
    z: float


class TTSTransform(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    posX: float
    posY: float
    posZ: float
    rotX: float
    rotY: float
    rotZ: float
    scaleX: float
    scaleY: float
    scaleZ: float


# ================================================================ Save Parts #
class TTSGrid(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    BothSnapping: bool
    Color: TTSRGBColor
    Lines: bool
    Offset: bool
    Opacity: float
    PosOffset: TTSCoordinate
    Snapping: bool
    ThickLines: bool
    Type: int
    xSize: float
    ySize: float


class TTSLighting(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    AmbientEquatorColor: TTSRGBColor
    AmbientGroundColor: TTSRGBColor
    AmbientIntensity: float
    AmbientSkyColor: TTSRGBColor
    AmbientType: int
    LightColor: TTSRGBColor
    LightIntensity: float
    LutContribution: float
    LutIndex: int
    LutURL: str  # url
    ReflectionIntensity: float


class TTSHandTransform(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    Color: str  # colorstring?
    Transform: TTSTransform


class TTSHands(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    DisableUnused: bool
    Enable: bool
    Hiding: int

    HandTransforms: list[TTSHandTransform] | None = None


class TTSTurns(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    DisableInteractions: bool
    Enable: bool
    PassTurns: bool
    Reverse: bool
    SkipEmpty: bool
    TurnColor: str  # colorstring?
    TurnOrder: list[str]  # colorstrings
    Type: int


class TTSTabState(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    body: str
    color: str  # colorstring?
    id: int
    title: str
    visibleColor: TTSRGBColor


class TTSCameraState(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    Distance: float
    Position: TTSCoordinate
    Rotation: TTSRotation
    Zoomed: bool


class TTSDecal(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    ImageURL: str  # url
    Name: str
    Size: float


class TTSSnapPoint(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    Position: TTSCoordinate
    Rotation: TTSRotation
    Tags: Optional[list[str]] = Field(default_factory=list)


# ============================================================== Object Parts #
class TTSBaseCustomImage(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    ImageURL: str  # url
    ImageSecondaryURL: str  # url
    ImageScalar: float
    WidthScale: float


class TTSCustomToken(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    Thickness: float
    MergeDistancePixels: float
    StandUp: bool = True
    Stackable: bool


class TTSCustomTile(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    Type: int
    Thickness: float
    Stackable: bool
    Stretch: bool


class TTSTokenCustomImage(TTSBaseCustomImage):
    CustomToken: TTSCustomToken


class TTSTileCustomImage(TTSBaseCustomImage):
    CustomTile: TTSCustomTile


class TTSCustomDeck(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    FaceURL: str  # URL
    BackURL: str  # URL
    NumWidth: int
    NumHeight: int
    BackIsHidden: bool
    UniqueBack: bool
    Type: int | None = None


class TTSDeck(TTSBaseModel):
    pass


class TTSText(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    colorstate: TTSRGBColor | None = Field(default=None, validation_alias=AliasChoices('colorstate', 'Colorstate'))
    fontsize: int | float | None = Field(default=None, alias='fontSize')
    Text: str


class TTSJointHinge(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    Anchor: dict
    Axis: dict
    BreakForce: str
    BreakTorgue: str
    ConnectedAnchor: dict
    ConnectedBodyGUID: str  # GUID
    EnableCollision: bool
    Limits: dict
    Motor: dict
    Spring: dict
    UseLimits: bool
    UseMotor: bool
    UseSpring: bool


class TTSCustomAssetBundle(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    AssetbundleURL: str  # URL
    AssetbundleSecondaryURL: str  # URL
    MaterialIndex: int
    TypeIndex: int
    LoopingEffectIndex: int


class TTSPhysicsMaterial(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    BounceCombine: int
    Bounciness: float
    DynamicFriction: float
    FrictionCombine: int
    StaticFriction: float


class TTSRigidBody(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    AngularDrag: float | None = Field(default=None, validation_alias=AliasChoices('AngularDrag', 'AngularGrag'))
    Drag: float
    Mass: float
    UseGravity: bool


class TTSCustomMesh(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    CastShadows: bool
    ColliderURL: str  # URL
    Convex: bool
    CustomShader: TTSCustomShader | None = None
    DiffuseURL: str  # URL
    MaterialIndex: int
    MeshURL: str  # URL
    NormalURL: str  # URL
    TypeIndex: int


class TTSCustomShader(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    FresnelStrength: float
    SpecularColor: TTSRGBColor | TTSRGBAColor
    SpecularIntensity: float
    SpecularSharpness: float


class TTSRotationValue(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    Value: str
    Rotation: TTSRotation


class TTSBag(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    Order: int


class TTSCounter(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    value: int


class TTSCustomPDF(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    PDFPage: int
    PDFPageOffset: int
    PDFPassword: str
    PDFUrl: str  # URL


class TTSMusicPlayer(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    RepeatSong: bool
    PlaylistEntry: int
    CurrentAudioTitle: str
    CurrentAudioURL: str  # URL
    AudioLibrary: list[str]


class TTSComponentTag(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    displayed: str
    normalized: str


class TTSComponentTags(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    labels: list[TTSComponentTag]


# =================================================================== Objects #
class TTSObjectBase(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    Description: str
    GMNotes: str
    GUID: str
    Nickname: str
    Tags: list[str] | None = None
    LayoutGroupSortIndex: int | None = None
    Value: int | None = None

    AttachedSnapPoints: list[TTSSnapPoint] | None = None
    ColorDiffuse: TTSRGBColor | TTSRGBAColor | TTSXYZColor
    Transform: TTSTransform

    Autoraise: bool
    DragSelectable: bool = True
    Grid: bool
    GridProjection: bool
    Hands: bool = True
    HideWhenFaceDown: bool = True
    IgnoreFoW: bool
    Locked: bool
    MeasureMovement: bool = False
    Snap: bool
    Sticky: bool
    Tooltip: bool

    XmlUI: str
    LuaScript: str
    LuaScriptState: str


class TTS3DTextObject(TTSObjectBase):
    Name: Literal['3DText']
    Text: TTSText


class TTSBlockSquareObject(TTSObjectBase):
    Name: Literal['BlockSquare']


class TTSCardObject(TTSObjectBase):
    Name: Literal['Card']
    CardID: int
    CustomDeck: dict[int, TTSCustomDeck] | None = None
    PhysicsMaterial: TTSPhysicsMaterial | None = None
    RigidBody: TTSRigidBody | None = Field(default=None, validation_alias=AliasChoices('RigidBody', 'Rigidbody'))
    SidewaysCard: bool
    ContainedObjects: list[TTSCardObject] | None = None


class TTSDeckObject(TTSObjectBase):
    Name: Literal['Deck']
    CustomDeck: dict[int, TTSCustomDeck]
    DeckIDs: list[int]
    SidewaysCard: bool
    ContainedObjects: list[TTSCardObject]


class TTSCustomAssetBundleObject(TTSObjectBase):
    Name: Literal['Custom_Assetbundle']
    CustomAssetbundle: TTSCustomAssetBundle
    JointHinge: TTSJointHinge | None = None


class TTSCustomModelInfiniteBagObject(TTSObjectBase):
    Name: Literal['Custom_Model_Infinite_Bag']
    CustomMesh: TTSCustomMesh
    MaterialIndex: int
    MeshIndex: int
    PhysicsMaterial: TTSPhysicsMaterial | None = None
    RigidBody: TTSRigidBody | None = Field(default=None, alias='Rigidbody')
    ContainedObjects: list[TTSObject]


class TTSCustomTileObject(TTSObjectBase):
    Name: Literal['Custom_Tile']
    CustomImage: TTSTileCustomImage
    PhysicsMaterial: TTSPhysicsMaterial | None = None
    RigidBody: TTSRigidBody | None = Field(default=None, alias='Rigidbody')
    RotationValues: list[TTSRotationValue] | None = None
    States: dict[int, TTSCustomTileObject] | None = None


class TTSCustomTokenObject(TTSObjectBase):
    Name: Literal['Custom_Token']
    CustomImage: TTSTokenCustomImage
    States: dict[int, TTSCustomTokenObject] | None = None
    ChildObjects: list[TTSObject] | None = None  # Attached objects?


class TTSCustomModelBagObject(TTSObjectBase):
    Name: Literal['Custom_Model_Bag']
    Bag: TTSBag | None = None
    CustomMesh: TTSCustomMesh
    MaterialIndex: int
    MeshIndex: int
    Number: int | None = None
    ContainedObjects: list[TTSObject] | None = None


class TTSChineseCheckersPieceObject(TTSObjectBase):
    Name: Literal['Chinese_Checkers_Piece']
    MaterialIndex: int


class TTSCustomModelObject(TTSObjectBase):
    Name: Literal['Custom_Model']
    CustomMesh: TTSCustomMesh
    PhysicsMaterial: TTSPhysicsMaterial | None = None
    RigidBody: TTSRigidBody | None = Field(default=None, alias='Rigidbody')
    States: dict[int, TTSCustomModelObject] | None = None


class TTSDeckCustomObject(TTSObjectBase):
    Name: Literal['DeckCustom']
    CustomDeck: dict[int, TTSCustomDeck]
    DeckIDs: list[int]
    SidewaysCard: bool
    ContainedObjects: list[TTSCardObject]


class TTSScriptingTriggerObject(TTSObjectBase):
    Name: Literal['ScriptingTrigger']


class TTSCounterObject(TTSObjectBase):
    Name: Literal['Counter']
    Counter: TTSCounter | None = None


class TTSCustomAssetbundleBagObject(TTSObjectBase):
    Name: Literal['Custom_Assetbundle_Bag']
    CustomAssetbundle: TTSCustomAssetBundle
    MaterialIndex: int
    MeshIndex: int
    ContainedObjects: list[TTSObject] | None = None


class TTSCustomPDFObject(TTSObjectBase):
    Name: Literal['Custom_PDF']
    CustomPDF: TTSCustomPDF


class TTSInfiniteBagObject(TTSObjectBase):
    Name: Literal['Infinite_Bag']
    MaterialIndex: int
    MeshIndex: int
    ContainedObjects: list[TTSObject] | None = None


class TTSCardCustomObject(TTSObjectBase):
    Name: Literal['CardCustom']
    CardID: int
    CustomDeck: dict[int, TTSCustomDeck] | None = None
    SidewaysCard: bool


class TTSGoGamePieceBlackObject(TTSObjectBase):
    Name: Literal['go_game_piece_black']


class TTSPlayerPawnObject(TTSObjectBase):
    Name: Literal['PlayerPawn']
    MaterialIndex: int


class TTSHandTriggerObject(TTSObjectBase):
    Name: Literal['HandTrigger']
    FogColor: str  # colorstring?


class TTSBagObject(TTSObjectBase):
    Name: Literal['Bag']
    Bag: TTSBag
    MaterialIndex: int
    MeshIndex: int
    ContainedObjects: list[TTSObject] | None = None


TTSObject = Annotated[
    Union[
        TTS3DTextObject,
        TTSBlockSquareObject,
        TTSCardObject,
        TTSDeckObject,
        TTSCustomAssetBundleObject,
        TTSCustomModelInfiniteBagObject,
        TTSCustomTileObject,
        TTSCustomTokenObject,
        TTSCustomModelBagObject,
        TTSChineseCheckersPieceObject,
        TTSCustomModelObject,
        TTSDeckCustomObject,
        TTSScriptingTriggerObject,
        TTSCounterObject,
        TTSCustomAssetbundleBagObject,
        TTSCustomPDFObject,
        TTSInfiniteBagObject,
        TTSCardCustomObject,
        TTSGoGamePieceBlackObject,
        TTSPlayerPawnObject,
        TTSHandTriggerObject,
        TTSBagObject,
    ],
    Field(discriminator='Name')
]


# ================================================================== SaveFile #
class TTSSave(TTSBaseModel):
    model_config = ConfigDict(extra='forbid')

    CameraStates: list[None | TTSCameraState] | None = None
    ComponentTags: Optional[TTSComponentTags] = None
    Date: str  # 4/4/2020 6:45:12 PM
    DecalPallet: list[TTSDecal]
    EpochTime: int | None = None
    GameComplexity: str | None = None
    GameMode: str
    GameType: str | None = None
    Gravity: float
    Grid: TTSGrid
    Hands: TTSHands
    Lighting: TTSLighting
    LuaScript: str
    LuaScriptState: str
    MusicPlayer: TTSMusicPlayer | None = None
    Note: str
    PlayArea: float
    PlayerCounts: int | list[int] | None = None
    PlayingTime: int | list[int] | None = None
    Rules: str | None = None
    SaveName: str
    Sky: str
    SkyURL: str  # url
    SnapPoints: list[TTSSnapPoint] | None = None
    TabStates: dict[str, TTSTabState]
    Table: str
    TableURL: str | None = None  # url
    Tags: Optional[list[str]] = None
    Turns: TTSTurns
    VersionNumber: str
    XmlUI: str

    ObjectStates: list[TTSObject]
