"""
TODO:
- color strings
"""
from __future__ import annotations

from typing import Annotated, Literal, Optional, Union
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

# ==================================================================== Global #
class TTSRGBColor(BaseModel):
    model_config = ConfigDict(extra='forbid')

    r: float
    g: float
    b: float


class TTSRGBAColor(TTSRGBColor):
    a: float


class TTSXYZColor(BaseModel):
    model_config = ConfigDict(extra='forbid')

    x: float
    y: float
    z: float


class TTSCoordinate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    x: float
    y: float
    z: float


class TTSRotation(BaseModel):  # 0-360 ?
    model_config = ConfigDict(extra='forbid')

    x: float
    y: float
    z: float


class TTSTransform(BaseModel):
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
class TTSGrid(BaseModel):
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


class TTSLighting(BaseModel):
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


class TTSHandTransform(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Color: str  # colorstring?
    Transform: TTSTransform


class TTSHands(BaseModel):
    model_config = ConfigDict(extra='forbid')

    DisableUnused: bool
    Enable: bool
    Hiding: int

    HandTransforms: list[TTSHandTransform] | None = None


class TTSTurns(BaseModel):
    model_config = ConfigDict(extra='forbid')

    DisableInteractions: bool
    Enable: bool
    PassTurns: bool
    Reverse: bool
    SkipEmpty: bool
    TurnColor: str  # colorstring?
    TurnOrder: list[str]  # colorstrings
    Type: int


class TTSTabState(BaseModel):
    model_config = ConfigDict(extra='forbid')

    body: str
    color: str  # colorstring?
    id: int
    title: str
    visibleColor: TTSRGBColor


class TTSCameraState(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Distance: float
    Position: TTSCoordinate
    Rotation: TTSRotation
    Zoomed: bool


class TTSDecal(BaseModel):
    model_config = ConfigDict(extra='forbid')

    ImageURL: str  # url
    Name: str
    Size: float


class TTSSnapPoint(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Position: TTSCoordinate
    Rotation: TTSRotation
    Tags: Optional[list[str]] = Field(default_factory=list)


# ============================================================== Object Parts #
class TTSBaseCustomImage(BaseModel):
    model_config = ConfigDict(extra='forbid')

    ImageURL: str  # url
    ImageSecondaryURL: str  # url
    ImageScalar: float
    WidthScale: float


class TTSCustomToken(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Thickness: float
    MergeDistancePixels: float
    StandUp: bool = True
    Stackable: bool


class TTSCustomTile(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Type: int
    Thickness: float
    Stackable: bool
    Stretch: bool


class TTSTokenCustomImage(TTSBaseCustomImage):
    CustomToken: TTSCustomToken


class TTSTileCustomImage(TTSBaseCustomImage):
    CustomTile: TTSCustomTile


class TTSCustomDeck(BaseModel):
    model_config = ConfigDict(extra='forbid')

    FaceURL: str  # URL
    BackURL: str  # URL
    NumWidth: int
    NumHeight: int
    BackIsHidden: bool
    UniqueBack: bool
    Type: int | None = None


class TTSDeck(BaseModel):
    pass


class TTSText(BaseModel):
    model_config = ConfigDict(extra='forbid')

    colorstate: TTSRGBColor | None = Field(default=None, validation_alias=AliasChoices('colorstate', 'Colorstate'))
    fontsize: int | float | None = Field(default=None, alias='fontSize')
    Text: str


class TTSJointHinge(BaseModel):
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


class TTSCustomAssetBundle(BaseModel):
    model_config = ConfigDict(extra='forbid')

    AssetbundleURL: str  # URL
    AssetbundleSecondaryURL: str  # URL
    MaterialIndex: int
    TypeIndex: int
    LoopingEffectIndex: int


class TTSPhysicsMaterial(BaseModel):
    model_config = ConfigDict(extra='forbid')

    BounceCombine: int
    Bounciness: float
    DynamicFriction: float
    FrictionCombine: int
    StaticFriction: float


class TTSRigidBody(BaseModel):
    model_config = ConfigDict(extra='forbid')

    AngularDrag: float | None = Field(default=None, validation_alias=AliasChoices('AngularDrag', 'AngularGrag'))
    Drag: float
    Mass: float
    UseGravity: bool


class TTSCustomMesh(BaseModel):
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


class TTSCustomShader(BaseModel):
    model_config = ConfigDict(extra='forbid')

    FresnelStrength: float
    SpecularColor: TTSRGBColor | TTSRGBAColor
    SpecularIntensity: float
    SpecularSharpness: float


class TTSRotationValue(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Value: str
    Rotation: TTSRotation


class TTSBag(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Order: int


class TTSCounter(BaseModel):
    model_config = ConfigDict(extra='forbid')

    value: int


class TTSCustomPDF(BaseModel):
    model_config = ConfigDict(extra='forbid')

    PDFPage: int
    PDFPageOffset: int
    PDFPassword: str
    PDFUrl: str  # URL


class TTSMusicPlayer(BaseModel):
    model_config = ConfigDict(extra='forbid')

    RepeatSong: bool
    PlaylistEntry: int
    CurrentAudioTitle: str
    CurrentAudioURL: str  # URL
    AudioLibrary: list[str]


class TTSComponentTag(BaseModel):
    model_config = ConfigDict(extra='forbid')

    displayed: str
    normalized: str


class TTSComponentTags(BaseModel):
    model_config = ConfigDict(extra='forbid')

    labels: list[TTSComponentTag]


# =================================================================== Objects #
class TTSObjectBase(BaseModel):
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
class TTSSave(BaseModel):
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
