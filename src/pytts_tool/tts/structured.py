"""
TODO:
- color strings
"""
from __future__ import annotations

from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field

# ==================================================================== Global #
class TTSRGBColor(BaseModel):
    model_config = ConfigDict(extra='forbid')

    r: float
    g: float
    b: float


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

    Type: int
    Lines: bool
    Color: TTSRGBColor
    Opacity: float
    ThickLines: bool
    Snapping: bool
    Offset: bool
    BothSnapping: bool
    xSize: float
    ySize: float
    PosOffset: TTSCoordinate


class TTSLighting(BaseModel):
    model_config = ConfigDict(extra='forbid')

    LightIntensity: float
    LightColor: TTSRGBColor
    AmbientIntensity: float
    AmbientType: int
    AmbientSkyColor: TTSRGBColor
    AmbientEquatorColor: TTSRGBColor
    AmbientGroundColor: TTSRGBColor
    ReflectionIntensity: float
    LutIndex: int
    LutContribution: float
    LutURL: str  # url


class TTSHandTransform(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Color: str  # colorstring?
    Transform: TTSTransform


class TTSHands(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Enable: bool
    DisableUnused: bool
    Hiding: int
    HandTransforms: list[TTSHandTransform]


class TTSTurns(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Enable: bool
    Type: int
    TurnOrder: list[str]  # colorstrings
    Reverse: bool
    SkipEmpty: bool
    DisableInteractions: bool
    PassTurns: bool
    TurnColor: str  # colorstring?


class TTSTabState(BaseModel):
    model_config = ConfigDict(extra='forbid')

    title: str
    body: str
    color: str  # colorstring?
    visibleColor: TTSRGBColor
    id: int


class TTSCameraState(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Position: TTSCoordinate
    Rotation: TTSRotation
    Distance: float
    Zoomed: bool


class TTSDecal(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Name: str
    ImageURL: str  # url
    Size: float


class TTSSnapPoint(BaseModel):
    model_config = ConfigDict(extra='forbid')

    Position: TTSCoordinate
    Rotation: TTSRotation
    Tags: Optional[list[str]] = Field(default_factory=list)


# ============================================================== Object Parts #
class TTSBaseCustomImage(BaseModel):
    ImageURL: str  # url
    ImageSecondaryURL: str  # url
    ImageScalar: float
    WidthScale: float


class TTSCustomToken(BaseModel):
    Thickness: float
    MergeDistancePixels: float
    StandUp: bool
    Stackable: bool


class TTSCustomTile(BaseModel):
    Type: int
    Thickness: float
    Stackable: bool
    Stretch: bool


class TTSTokenCustomImage(TTSBaseCustomImage):
    CustomToken: TTSCustomToken


class TTSTileCustomImage(TTSBaseCustomImage):
    CustomTile: TTSCustomTile


class TTSDeck(BaseModel):
    pass


# =================================================================== Objects #
class TTSObjectBase(BaseModel):
    GUID: str
    Name: str  # enum?
    Nickname: str
    Description: str
    GMNotes: str

    ColorDiffuse: TTSRGBColor
    Transform: TTSTransform

    Grid: bool
    Snap: bool
    Sticky: bool
    Tooltip: bool
    IgnoreFoW: bool
    Locked: bool
    GridProjection: bool
    Autoraise: bool

    XmlUI: str
    LuaScript: str
    LuaScriptState: str


class TTSObject(BaseModel):
    model_config = ConfigDict(extra='forbid')

    GUID: str
    Name: str  # enum?
    Transform: TTSTransform
    Nickname: str
    Description: str
    GMNotes: str
    ColorDiffuse: TTSRGBColor
    LayoutGroupSortIndex: int
    Locked: bool
    Grid: bool
    Snap: bool
    IgnoreFoW: bool
    MeasureMovement: bool
    DragSelectable: bool
    Autoraise: bool
    Sticky: bool
    Tooltip: bool
    GridProjection: bool
    Hands: bool
    AttachedSnapPoints: Optional[list[TTSSnapPoint]] = Field(default_factory=list)
    LuaScript: str
    LuaScriptState: str
    XmlUI: str
    ContainedObjects: Optional[list[TTSObject]] = Field(default_factory=list)


class TTSDeckObject(TTSObject):
    model_config = ConfigDict(extra='forbid')

    HideWhenFaceDown: bool
    SidewaysCard: bool
    DeckIDs: list[int]
    CustomDeck: dict[str, TTSDeck]


# ================================================================== SaveFile #
class TTSSave(BaseModel):
    model_config = ConfigDict(extra='forbid')

    SaveName: str
    GameMode: str
    Gravity: float
    PlayArea: float
    Date: str  # 4/4/2020 6:45:12 PM
    Table: str
    TableURL: str  # url
    Sky: str
    SkyURL: str  # url
    Note: str
    Rules: str
    XmlUI: str
    LuaScript: str
    LuaScriptState: str
    Grid: TTSGrid
    Lighting: TTSLighting
    Hands: TTSHands
    Turns: TTSTurns
    TabStates: dict[str, TTSTabState]
    CameraStates: list[None | TTSCameraState]
    DecalPallet: list[TTSDecal]
    ObjectStates: list[TTSObject | TTSDeckObject]
    SnapPoints: list[TTSSnapPoint]
    VersionNumber: str
