from dataclasses import dataclass
from enum import IntEnum

from typing_extensions import MutableSequence
from typing_extensions import TypedDict


class FleetType(IntEnum):
    Single = 0
    Carrier = 1
    Surface = 2
    Transport = 3


class FormationType(IntEnum):
    LineAhead = 1
    DoubleLine = 2
    Diamond = 3
    Echelon = 4
    LineAbreast = 5
    Vanguard = 6

    FirstPatrolFormation = 11
    SecondPatrolFormation = 12
    ThirdPatrolFormation = 13
    FourthPatrolFormation = 14


class EquipmentTypes(IntEnum):
    UNKNOWN = 0
    """Default if nothing"""

    MainGunSmall = 1
    """小口径主砲"""

    MainGunMedium = 2
    """中口径主砲"""

    MainGunLarge = 3
    """大口径主砲"""

    SecondaryGun = 4
    """副砲"""

    Torpedo = 5
    """魚雷"""

    CarrierBasedFighter = 6
    """艦上戦闘機"""

    CarrierBasedBomber = 7
    """艦上爆撃機"""

    CarrierBasedTorpedo = 8
    """艦上攻撃機"""

    CarrierBasedRecon = 9
    """艦上偵察機"""

    SeaplaneRecon = 10
    """水上偵察機"""

    SeaplaneBomber = 11
    """水上爆撃機"""

    RadarSmall = 12
    """小型電探"""

    RadarLarge = 13
    """大型電探"""

    Sonar = 14
    """ソナー"""

    DepthCharge = 15
    """爆雷"""

    ExtraArmor = 16
    """追加装甲"""

    Engine = 17
    """機関部強化"""

    AAShell = 18
    """対空強化弾"""

    APShell = 19
    """対艦強化弾"""

    VTFuse = 20
    """VT信管"""

    AAGun = 21
    """対空機銃"""

    MidgetSubmarine = 22
    """特殊潜航艇"""

    DamageControl = 23
    """応急修理要員"""

    LandingCraft = 24
    """上陸用舟艇"""

    Autogyro = 25
    """オートジャイロ"""

    ASPatrol = 26
    """対潜哨戒機"""

    ExtraArmorMedium = 27
    """追加装甲（中型）"""

    ExtraArmorLarge = 28
    """追加装甲（大型）"""

    Searchlight = 29
    """探照灯"""

    TransportContainer = 30
    """簡易輸送部材"""

    RepairFacility = 31
    """艦艇修理施設"""

    SubmarineTorpedo = 32
    """潜水艦魚雷"""

    StarShell = 33
    """照明弾"""

    CommandFacility = 34
    """司令部施設"""

    AviationPersonnel = 35
    """航空要員"""

    AADirector = 36
    """高射装置"""

    Rocket = 37
    """対地装備"""

    MainGunLarge2 = 38
    """大口径主砲(II)"""

    SurfaceShipPersonnel = 39
    """水上艦要員 (lookouts)"""

    """大型ソナー"""
    SonarLarge = 40

    FlyingBoat = 41
    """大型飛行艇"""

    SearchlightLarge = 42
    """大型探照灯"""

    Ration = 43
    """戦闘糧食"""

    Supplies = 44
    """補給物資"""

    SeaplaneFighter = 45
    """水上戦闘機"""

    SpecialAmphibiousTank = 46
    """特型内火艇"""

    LandBasedAttacker = 47
    """陸上攻撃機"""

    Interceptor = 48
    """局地戦闘機"""

    LandBasedRecon = 49
    """陸上偵察機"""

    TransportMaterial = 50
    """輸送機材"""

    SubmarineEquipment = 51
    """潜水艦装備"""

    ArmyInfantry = 52
    """陸戦部隊"""

    HeavyBomber = 53
    """大型陸上機"""

    SurfaceShipEquipment = 54
    """水上艦装備 (smoker)"""

    JetFighter = 56
    """噴式戦闘機"""

    JetBomber = 57
    """噴式戦闘爆撃機"""

    JetTorpedo = 58
    """噴式攻撃機"""

    JetRecon = 59
    """噴式索敵機"""

    RadarLarge2 = 93
    """大型電探(II)"""

    CarrierBasedRecon2 = 94
    """艦上偵察機(II)"""

    SecondaryGun2 = 95
    """副砲(II)"""


# EquipmentTypes: TypeAlias = int | EquipmentTypeEnum
# EquipmentTypes: TypeAlias = EquipmentTypeEnum


class AIR_STATE(IntEnum):
    KAKUHO = 0
    YUSEN = 1
    KINKO = 2
    RESSEI = 3
    SOSHITSU = 4
    NONE = 5


class SUPPORT_TYPE(IntEnum):
    SHELLING = 0
    AIRSTRIKE = 1
    ANTI_SUBMARINE = 2
    LONG_RANGE_TORPEDO = 3
    NOT_FOUNDED_DD = 4
    NONE = 5


@dataclass(slots=True)
class AirStatus:
    text: str
    value: AIR_STATE
    color: str


AIR_STATUS = (
    AirStatus("確保", AIR_STATE.KAKUHO, "green"),
    AirStatus("優勢", AIR_STATE.YUSEN, "light-green"),
    AirStatus("拮抗", AIR_STATE.KINKO, "yellow"),
    AirStatus("劣勢", AIR_STATE.RESSEI, "deep-orange"),
    AirStatus("喪失", AIR_STATE.SOSHITSU, "red"),
    AirStatus("不発", AIR_STATE.NONE, "secondary"),
)

PLANE_TYPES = {
    EquipmentTypes.CarrierBasedFighter,
    EquipmentTypes.CarrierBasedBomber,
    EquipmentTypes.CarrierBasedTorpedo,
    EquipmentTypes.CarrierBasedRecon,
    EquipmentTypes.SeaplaneRecon,
    EquipmentTypes.SeaplaneBomber,
    EquipmentTypes.Autogyro,
    EquipmentTypes.ASPatrol,
    EquipmentTypes.FlyingBoat,
    EquipmentTypes.SeaplaneFighter,
    EquipmentTypes.LandBasedAttacker,
    EquipmentTypes.Interceptor,
    EquipmentTypes.LandBasedRecon,
    EquipmentTypes.HeavyBomber,
    EquipmentTypes.JetBomber,
}

CB_PLANE_TYPES = {
    EquipmentTypes.CarrierBasedFighter,
    EquipmentTypes.CarrierBasedBomber,
    EquipmentTypes.CarrierBasedTorpedo,
    EquipmentTypes.CarrierBasedRecon,
    EquipmentTypes.JetBomber,
}

SB_PLANE_TYPES = {
    EquipmentTypes.SeaplaneRecon,
    EquipmentTypes.SeaplaneBomber,
    EquipmentTypes.FlyingBoat,
    EquipmentTypes.SeaplaneFighter,
}

AB_PLANE_TYPES = {
    EquipmentTypes.LandBasedAttacker,
    EquipmentTypes.Interceptor,
    EquipmentTypes.LandBasedRecon,
    EquipmentTypes.HeavyBomber,
}

FIGHTERS = {
    EquipmentTypes.CarrierBasedFighter,
    EquipmentTypes.SeaplaneFighter,
    EquipmentTypes.JetFighter,
}

ATTACKERS = {
    EquipmentTypes.CarrierBasedBomber,
    EquipmentTypes.CarrierBasedTorpedo,
    EquipmentTypes.SeaplaneBomber,
    EquipmentTypes.LandBasedAttacker,
    EquipmentTypes.HeavyBomber,
    EquipmentTypes.JetBomber,
}

ASW_PLANES = {
    EquipmentTypes.Autogyro,
    EquipmentTypes.ASPatrol,
}

RECONNAISSANCES = {
    EquipmentTypes.CarrierBasedRecon,
    EquipmentTypes.SeaplaneRecon,
    EquipmentTypes.FlyingBoat,
    EquipmentTypes.LandBasedRecon,
}

AB_ATTACKERS = {
    EquipmentTypes.LandBasedAttacker,
    EquipmentTypes.HeavyBomber,
}

AB_ATTACKERS_LARGE = {
    EquipmentTypes.HeavyBomber,
}

ROCKET = {
    350,
    351,
    352,
}

BAKUSEN = {
    60,
    154,
    219,
    447,
    487,
}

LATE_MODEL_TORPEDO = {
    213,
    214,
    383,
    441,
    443,
    457,
    461,
    512,
}

ENABLED_LAND_BASE_ATTACK = {
    64,
    148,
    233,
    277,
    305,
    306,
    319,
    320,
    391,
    392,
    420,
    421,
    474,
}

ENABLED_ASW_SUPPORT = {7, 8, 10, 11, 45, 41, 25, 26}

STRICT_DEPTH_CHARGE = {
    226,
    227,
    378,
    439,
    488,
}


class _SpecialGroup(TypedDict):
    key: str
    text: str
    item: MutableSequence[int]


SPECIAL_GROUP: list[_SpecialGroup] = []


PROF_LEVEL_BORDER = (0, 10, 25, 40, 55, 70, 85, 100, 120)


class SpEffectItemKind(IntEnum):
    SeaColoredRibbon = 1
    WhiteSash = 2


class ShipType(IntEnum):
    DE = 1
    DD = 2
    CL = 3
    CLT = 4
    CA = 5
    CAV = 6
    CVL = 7
    FBB = 8
    BB = 9
    BBV = 10
    CV = 11
    BBB = 12
    SS = 13
    SSV = 14
    AO_2 = 15
    AV = 16
    LHA = 17
    CVB = 18
    AR = 19
    AS = 20
    CT = 21
    AO = 22


JPN = {
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    49,
    50,
    51,
    52,
    53,
    54,
    56,
    59,
    60,
    62,
    66,
    71,
    72,
    74,
    75,
    76,
    77,
    85,
    86,
    90,
    94,
    97,
    100,
    101,
    103,
    104,
    109,
    111,
    115,
    117,
    119,
    120,
    123,
    126,
    127,
}

USA = {
    65,
    69,
    83,
    84,
    87,
    91,
    93,
    95,
    99,
    102,
    105,
    106,
    107,
    110,
    114,
    116,
    118,
    121,
    122,
    125,
}

ITA = {58, 61, 64, 68, 80, 92, 113, 124}

GBR = {67, 78, 82, 88, 108, 112}

DEU = {47, 48, 55, 57, 63}

FRA = {70, 79}

RUS = {73, 81}

SWE = {89}

AUS = {96}

NLD = {98}


class CountryType(IntEnum):
    JPN = 1
    DEU = 2
    ITA = 3
    USA = 4
    GBR = 5
    FRA = 6
    # RUS=?
    # SWE=?
    # NLD=?
    AUS = 10


CountryTable: dict[CountryType | int, set[int]] = {
    CountryType.JPN: JPN,
    CountryType.DEU: DEU,
    CountryType.ITA: ITA,
    CountryType.USA: USA,
    CountryType.GBR: GBR,
    CountryType.FRA: FRA,
    CountryType.AUS: AUS,
}


@dataclass(slots=True)
class Formation:
    text: str
    value: int
    correction: float


FORMATIONS = (
    Formation("単縦陣", FormationType.LineAhead, 1.0),
    Formation("複縦陣", FormationType.DoubleLine, 1.2),
    Formation("輪形陣", FormationType.Diamond, 1.6),
    Formation("梯形陣", FormationType.Echelon, 1.0),
    Formation("単横陣", FormationType.LineAbreast, 1.0),
    Formation("警戒陣", FormationType.Vanguard, 1.1),
    Formation("第一警戒", FormationType.FirstPatrolFormation, 1.1),
    Formation("第二警戒", FormationType.SecondPatrolFormation, 1.0),
    Formation("第三警戒", FormationType.ThirdPatrolFormation, 1.5),
    Formation("第四警戒", FormationType.FourthPatrolFormation, 1.0),
)


@dataclass(slots=True)
class Support:
    text: str
    value: SUPPORT_TYPE


SUPPORTS: tuple[Support, ...] = (
    Support("支援射撃", SUPPORT_TYPE.SHELLING),
    Support("航空支援", SUPPORT_TYPE.AIRSTRIKE),
    Support("対潜支援哨戒", SUPPORT_TYPE.ANTI_SUBMARINE),
    Support("支援長距離雷撃", SUPPORT_TYPE.LONG_RANGE_TORPEDO),
    Support("支援不可(要駆逐2)", SUPPORT_TYPE.NOT_FOUNDED_DD),
    Support("不発", SUPPORT_TYPE.NONE),
)


@dataclass(slots=True)
class AvoidType:
    text: str
    value: int
    c1: float
    c2: float
    c3: float
    c4: float


MANUAL_AVOID = 99

EXPAND_SLOT_INDEX = 99

AVOID_TYPE = (
    AvoidType("なし", 0, 1, 1, 1, 1),
    AvoidType("弱", 1, 0.6, 1, 1, 1),
    AvoidType("中", 2, 0.6, 0.7, 0.6, 1),
    AvoidType("強", 3, 0.5, 0.7, 0.4, 0.5),
    AvoidType("超", 4, 0.5, 0.5, 0.4, 0.5),
    AvoidType("任意", MANUAL_AVOID, 1, 1, 1, 1),
)

ANTI_AIR_CUT_IN_PRIORITIES: tuple[int, ...] = (
    38,
    39,
    40,
    42,
    41,
    10,
    43,
    46,
    11,
    25,
    1,
    34,
    44,
    26,
    4,
    2,
    35,
    36,
    27,
    45,
    19,
    21,
    29,
    16,
    14,
    3,
    5,
    6,
    28,
    37,
    33,
    30,
    8,
    13,
    15,
    7,
    20,
    24,
    32,
    12,
    31,
    47,
    17,
    18,
    22,
    9,
    23,
)


class AntiAirCutInItem(TypedDict):
    id: int
    text: str
    rateBonus: float
    c1: int
    c2: int
    rate: int
    remarks: str


ANTI_AIR_CUTIN: tuple[AntiAirCutInItem, ...] = (
    {
        "id": 0,
        "text": "不発",
        "rateBonus": 1,
        "c1": 1,
        "c2": 0,
        "rate": 100,
        "remarks": "",
    },
    {
        "id": 1,
        "text": "1種",
        "rateBonus": 1.7,
        "c1": 3,
        "c2": 5,
        "rate": 65,
        "remarks": "秋月型",
    },
    {
        "id": 2,
        "text": "2種",
        "rateBonus": 1.7,
        "c1": 3,
        "c2": 4,
        "rate": 55,
        "remarks": "秋月型",
    },
    {
        "id": 3,
        "text": "3種",
        "rateBonus": 1.6,
        "c1": 2,
        "c2": 3,
        "rate": 50,
        "remarks": "秋月型",
    },
    {
        "id": 4,
        "text": "4種",
        "rateBonus": 1.5,
        "c1": 5,
        "c2": 2,
        "rate": 52,
        "remarks": "戦艦",
    },
    {
        "id": 5,
        "text": "5種",
        "rateBonus": 1.5,
        "c1": 2,
        "c2": 3,
        "rate": 50,
        "remarks": "汎用",
    },
    {
        "id": 6,
        "text": "6種",
        "rateBonus": 1.45,
        "c1": 4,
        "c2": 1,
        "rate": 40,
        "remarks": "戦艦",
    },
    {
        "id": 7,
        "text": "7種",
        "rateBonus": 1.35,
        "c1": 2,
        "c2": 2,
        "rate": 45,
        "remarks": "汎用",
    },
    {
        "id": 8,
        "text": "8種",
        "rateBonus": 1.4,
        "c1": 2,
        "c2": 3,
        "rate": 50,
        "remarks": "汎用",
    },
    {
        "id": 9,
        "text": "9種",
        "rateBonus": 1.3,
        "c1": 1,
        "c2": 2,
        "rate": 40,
        "remarks": "汎用",
    },
    {
        "id": 10,
        "text": "10種",
        "rateBonus": 1.65,
        "c1": 3,
        "c2": 6,
        "rate": 60,
        "remarks": "摩耶改二",
    },
    {
        "id": 11,
        "text": "11種",
        "rateBonus": 1.5,
        "c1": 2,
        "c2": 5,
        "rate": 55,
        "remarks": "摩耶改二",
    },
    {
        "id": 12,
        "text": "12種",
        "rateBonus": 1.25,
        "c1": 1,
        "c2": 3,
        "rate": 45,
        "remarks": "汎用",
    },
    {
        "id": 13,
        "text": "13種",
        "rateBonus": 1.35,
        "c1": 1,
        "c2": 4,
        "rate": 35,
        "remarks": "汎用",
    },
    {
        "id": 14,
        "text": "14種",
        "rateBonus": 1.45,
        "c1": 4,
        "c2": 1,
        "rate": 63,
        "remarks": "五十鈴改二",
    },
    {
        "id": 15,
        "text": "15種",
        "rateBonus": 1.3,
        "c1": 3,
        "c2": 1,
        "rate": 54,
        "remarks": "五十鈴改二",
    },
    {
        "id": 16,
        "text": "16種",
        "rateBonus": 1.4,
        "c1": 4,
        "c2": 1,
        "rate": 62,
        "remarks": "霞改二乙 / 夕張改二",
    },
    {
        "id": 17,
        "text": "17種",
        "rateBonus": 1.25,
        "c1": 2,
        "c2": 1,
        "rate": 57,
        "remarks": "霞改二乙",
    },
    {
        "id": 18,
        "text": "18種",
        "rateBonus": 1.2,
        "c1": 2,
        "c2": 1,
        "rate": 59,
        "remarks": "皐月改二",
    },
    {
        "id": 19,
        "text": "19種",
        "rateBonus": 1.45,
        "c1": 5,
        "c2": 1,
        "rate": 60,
        "remarks": "鬼怒改二",
    },
    {
        "id": 20,
        "text": "20種",
        "rateBonus": 1.25,
        "c1": 3,
        "c2": 1,
        "rate": 65,
        "remarks": "鬼怒改二",
    },
    {
        "id": 21,
        "text": "21種",
        "rateBonus": 1.45,
        "c1": 5,
        "c2": 1,
        "rate": 60,
        "remarks": "由良改二",
    },
    {
        "id": 22,
        "text": "22種",
        "rateBonus": 1.2,
        "c1": 2,
        "c2": 1,
        "rate": 65,
        "remarks": "文月改二",
    },
    {
        "id": 23,
        "text": "23種",
        "rateBonus": 1.05,
        "c1": 1,
        "c2": 1,
        "rate": 80,
        "remarks": "UIT-25 / 伊504",
    },
    {
        "id": 24,
        "text": "24種",
        "rateBonus": 1.25,
        "c1": 3,
        "c2": 1,
        "rate": 62,
        "remarks": "天龍型改二",
    },
    {
        "id": 25,
        "text": "25種",
        "rateBonus": 1.55,
        "c1": 7,
        "c2": 1,
        "rate": 60,
        "remarks": "伊勢型",
    },
    {
        "id": 26,
        "text": "26種",
        "rateBonus": 1.4,
        "c1": 6,
        "c2": 1,
        "rate": 60,
        "remarks": "武蔵改二",
    },
    {
        "id": 27,
        "text": "27種",
        "rateBonus": 1.55,
        "c1": 5,
        "c2": 1,
        "rate": 55,
        "remarks": "大淀",
    },
    {
        "id": 28,
        "text": "28種",
        "rateBonus": 1.4,
        "c1": 4,
        "c2": 1,
        "rate": 56,
        "remarks": "伊勢型 / 武蔵",
    },
    {
        "id": 29,
        "text": "29種",
        "rateBonus": 1.55,
        "c1": 5,
        "c2": 1,
        "rate": 60,
        "remarks": "磯風乙改 / 浜風乙改",
    },
    {
        "id": 30,
        "text": "30種",
        "rateBonus": 1.3,
        "c1": 3,
        "c2": 1,
        "rate": 50,
        "remarks": "天龍改二",
    },
    {
        "id": 31,
        "text": "31種",
        "rateBonus": 1.25,
        "c1": 2,
        "c2": 1,
        "rate": 50,
        "remarks": "天龍改二",
    },
    {
        "id": 32,
        "text": "32種",
        "rateBonus": 1.2,
        "c1": 3,
        "c2": 1,
        "rate": 60,
        "remarks": "金剛型改二 / 英艦",
    },
    {
        "id": 33,
        "text": "33種",
        "rateBonus": 1.35,
        "c1": 3,
        "c2": 1,
        "rate": 42,
        "remarks": "Gotland",
    },
    {
        "id": 34,
        "text": "34種",
        "rateBonus": 1.6,
        "c1": 7,
        "c2": 1,
        "rate": 56,
        "remarks": "Fletcher級",
    },
    {
        "id": 35,
        "text": "35種",
        "rateBonus": 1.55,
        "c1": 6,
        "c2": 1,
        "rate": 55,
        "remarks": "Fletcher級",
    },
    {
        "id": 36,
        "text": "36種",
        "rateBonus": 1.55,
        "c1": 6,
        "c2": 1,
        "rate": 50,
        "remarks": "Fletcher級",
    },
    {
        "id": 37,
        "text": "37種",
        "rateBonus": 1.45,
        "c1": 2,
        "c2": 3,
        "rate": 44,
        "remarks": "Fletcher級",
    },
    {
        "id": 38,
        "text": "38種",
        "rateBonus": 1.85,
        "c1": 6,
        "c2": 5,
        "rate": 60,
        "remarks": "Atlanta",
    },
    {
        "id": 39,
        "text": "39種",
        "rateBonus": 1.7,
        "c1": 6,
        "c2": 5,
        "rate": 60,
        "remarks": "Atlanta",
    },
    {
        "id": 40,
        "text": "40種",
        "rateBonus": 1.7,
        "c1": 6,
        "c2": 5,
        "rate": 60,
        "remarks": "Atlanta",
    },
    {
        "id": 41,
        "text": "41種",
        "rateBonus": 1.65,
        "c1": 5,
        "c2": 5,
        "rate": 60,
        "remarks": "Atlanta",
    },
    {
        "id": 42,
        "text": "42種",
        "rateBonus": 1.65,
        "c1": 10,
        "c2": 1,
        "rate": 65,
        "remarks": "大和型改二",
    },
    {
        "id": 43,
        "text": "43種",
        "rateBonus": 1.6,
        "c1": 8,
        "c2": 1,
        "rate": 60,
        "remarks": "大和型改二",
    },
    {
        "id": 44,
        "text": "44種",
        "rateBonus": 1.6,
        "c1": 6,
        "c2": 1,
        "rate": 55,
        "remarks": "大和型改二",
    },
    {
        "id": 45,
        "text": "45種",
        "rateBonus": 1.55,
        "c1": 5,
        "c2": 1,
        "rate": 50,
        "remarks": "大和型改二",
    },
    {
        "id": 46,
        "text": "46種",
        "rateBonus": 1.55,
        "c1": 8,
        "c2": 1,
        "rate": 50,
        "remarks": "榛名改二乙",
    },
    {
        "id": 47,
        "text": "47種",
        "rateBonus": 1.3,
        "c1": 2,
        "c2": 1,
        "rate": 70,
        "remarks": "白露型改二",
    },
)
