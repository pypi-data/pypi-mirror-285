import math
from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field

from typing_extensions import Optional
from typing_extensions import Sequence

from ... import const
from ...const import AvoidType
from ...const import Formation
from ..interface import ShipBase
from .anti_air_cut_in import AntiAirCutIn


@dataclass(slots=True)
class ShootDownStatus:
    antiAirWeightList: list[float]
    rateDownList: list[float]
    fixDownList: list[float]
    minimumDownList: list[float]


@dataclass(slots=True)
class ShootDownInfo:
    ship: InitVar[Sequence[ShipBase]]
    isEnemy: InitVar[bool]
    isUnion: InitVar[bool]
    antiAirCutIn: InitVar[AntiAirCutIn]
    _border: InitVar[float]
    formation: InitVar[Optional[Formation]]
    isAirRaid: InitVar[bool] = False

    shootDownStatusList: list[ShootDownStatus] = field(init=False)
    border: float = field(init=False)
    maxRange: int = field(init=False)

    def __post_init__(
        self,
        ships: Sequence[ShipBase],
        isEnemy: bool,
        isUnion: bool,
        antiAirCutIn: AntiAirCutIn,
        _border: float,
        formation: Optional[Formation] = None,
        isAirRaid: bool = False,
    ) -> None:
        if formation is not None:
            self.shootDownStatusList = ShootDownInfo.getStage2(
                ships, isEnemy, isUnion, formation, antiAirCutIn, isAirRaid
            )
        else:
            self.shootDownStatusList = ShootDownInfo.getStage2(
                ships, isEnemy, isUnion, const.FORMATIONS[0], antiAirCutIn, isAirRaid
            )

        self.maxRange = len(ships)
        self.border = _border

    @staticmethod
    def getStage2(
        ships: Sequence[ShipBase],
        isEnemy: bool,
        isUnion: bool,
        formation: Formation,
        cutIn: AntiAirCutIn,
        isAirRaid: Optional[bool] = None,
        avoid: Optional[AvoidType] = None,
    ) -> list[ShootDownStatus]:
        """stage2撃墜数テーブルを返却"""

        stage2: list[ShootDownStatus] = []
        shipCount = len(ships)
        if shipCount == 0:
            # 全てが0のデータ
            stage2 = [ShootDownStatus([0], [0], [0], [0]) for _ in const.AVOID_TYPE]
            return stage2

        stage2 = [ShootDownStatus([], [], [], []) for _ in const.AVOID_TYPE]
        # 陣形補正
        aj1 = formation.correction

        # 艦隊防空ボーナス合計
        sumAntiAirBonus = 0
        sumAntiAirBonus = sum(
            ship.antiAirBonus + ship.itemBonusStatus.antiAir for ship in ships
        )
        sumAntiAirBonus = math.floor(sumAntiAirBonus)
        # 艦隊防空 => 陣形補正 * 各艦の艦隊対空ボーナス合計
        fleetAntiAir = sumAntiAirBonus * aj1
        # 対空CI変動ボーナス
        cutInBonus1 = cutIn.rateCorr
        # 対空CI固定ボーナスA 敵側かつ不発なら0
        cutInBonusA = 0 if isEnemy and cutIn.id == 0 else cutIn.fixCorrA
        # 対空CI固定ボーナスB
        cutInBonusB = cutIn.fixCorrB

        for ship in ships:
            sumAntiAirWeight = 0
            sumItemAntiAir = 0

            # この艦娘の装備各値の合計
            for shipItem in ship.items:
                # 装備加重対空値の加算
                sumAntiAirWeight += shipItem.antiAirWeight
                # 装備対空値の加算
                sumItemAntiAir += shipItem.data.antiAir

            # 補強増設の分を加算
            sumAntiAirWeight += ship.exItem.antiAirWeight
            sumItemAntiAir += ship.exItem.data.antiAir

            # 装備フィットボーナス(対空)
            itemBonusAntiAir = ship.itemBonusStatus.antiAir

            # 連合艦隊補正
            unionFactor = 1.0
            if isUnion and ship.isEscort:
                unionFactor = 0.48
            elif isUnion and not ship.isEscort:
                unionFactor = 0.8
                if isAirRaid:
                    unionFactor = 0.72

            # 敵味方航空戦補正(味方:0.8, 敵:0.75)
            aerialCorr = 0.75 if isEnemy else 0.8

            # 各回避補正毎にテーブルを作成
            for j, avoidObj in enumerate(const.AVOID_TYPE):
                # 対空射撃回避補正取得
                avoid1 = avoidObj.c1
                avoid2 = avoidObj.c2
                # 対空CI補正Aに掛かると思われる係数 加重対空補正と同等？
                # => 違いました。5 / 8 / 12種に対して、弱で0 中で1 強、超で3
                # 出典 https://x.com/Divinity_123/status/1721218795878879635
                avoid3 = avoidObj.c3
                # 対空CI補正Bに掛かると思われる係数
                # => 上の結果を踏まえ少なくとも 5 / 8 / 12種の結果は合うように調整
                avoid4 = avoidObj.c4

                if (j == len(const.AVOID_TYPE) - 1) and (avoid is not None):
                    # 任意の射撃回避補正値を置き換え
                    avoid1 = avoid.c1
                    avoid2 = avoid.c2
                    avoid3 = avoid.c3
                    avoid4 = avoid.c4

                # 艦船加重対空値
                antiAirWeight: int = 0
                if isEnemy:
                    # 艦船加重対空値(敵側式) => int((int(sqrt(素対空 + 装備対空)) + Σ(装備対空値 * 装備倍率)) * 対空射撃回避補正)
                    antiAirWeight = math.floor(
                        math.floor(
                            math.floor(math.sqrt(ship.antiAir + sumItemAntiAir))
                            + sumAntiAirWeight
                        )
                        * avoid1
                    )
                else:
                    # 艦船加重対空値(味方側式) => int(((素対空 / 2 + Σ(装備対空値 * 装備倍率)) + 装備対空ボーナス * 0.75?) * 対空射撃回避補正)
                    antiAirWeight = math.floor(
                        (
                            math.floor(
                                ship.antiAir / 2
                                + sumAntiAirWeight
                                + itemBonusAntiAir * 0.75
                            )
                        )
                        * avoid1
                    )
                # 加重対空格納
                stage2[j].antiAirWeightList.append(antiAirWeight)

                # 艦隊防空補正 => int(艦隊防空 * 対空射撃回避補正(艦隊防空ボーナス))
                fleetAA = math.floor(fleetAntiAir * avoid2)
                # 最終艦隊防空 => int(int(艦隊防空) / ブラウザ版補正(味方:1.3 敵1.0))
                fleetAABonus = math.floor(fleetAA / 1 if isEnemy else 1.3)

                # 割合撃墜 => int(0.02 * 0.25 * 機数[あとで] * 艦船加重対空値 * 連合補正)
                stage2[j].rateDownList.append(0.02 * 0.25 * antiAirWeight * unionFactor)
                # 固定撃墜 => int((加重対空値 + int(艦隊防空補正)) * 基本定数(0.25) * 敵味方航空戦補正 * 連合補正 * 対空CI変動ボーナス)
                stage2[j].fixDownList.append(
                    math.floor(
                        math.floor(antiAirWeight + math.floor(fleetAABonus))
                        * 0.25
                        * aerialCorr
                        * unionFactor
                        * cutInBonus1
                    )
                )

                # 最低保証 => int(対空CI固定ボーナスA * 対空射撃補正A + 対空CI固定ボーナスB * 対空射撃補正B)
                minimum = cutInBonusA * avoid3 + cutInBonusB * avoid4
                # 最低保証
                stage2[j].minimumDownList.append(minimum)

        return stage2

    @staticmethod
    def getAntiAirCutIn(ship: ShipBase) -> list[AntiAirCutIn]:
        cutInIds: list[int] = []
        # 装備一覧
        items = [*ship.items, ship.exItem]
        (
            kokakuCount,
            specialKijuCount,
            specialKokakuCount,
            antiAirRadarCount,
            koshaCount,
            kijuCount,
        ) = (
            ship.kokakuCount,
            ship.specialKijuCount,
            ship.specialKokakuCount,
            ship.antiAirRadarCount,
            ship.koshaCount,
            ship.kijuCount,
        )
        # 艦型
        type2 = ship.data.type2
        # 艦娘id
        shipId = ship.data.id
        # 高角砲の数
        allKokaku = kokakuCount + specialKokakuCount
        # 高角砲の有無
        hasKokaku = allKokaku > 0
        # 三式弾の有無
        hasSanshiki = any(v.data.apiTypeId == 18 for v in items)

        if type2 == 54:
            # 秋月型
            # 電探
            hasRadar = any(v.data.iconTypeId == 11 for v in items)
            # 1種 (高角砲2, 電探)
            if allKokaku >= 2 and hasRadar:
                cutInIds.append(1)
            # 2種 (高角砲, 電探)
            if hasKokaku and hasRadar:
                cutInIds.append(2)
            # 3種 (高角砲2) 共存なし
            if allKokaku >= 2:
                cutInIds.append(3)
        elif shipId == 428:
            # 摩耶様改二
            # 10種 (高角砲, 特殊機銃, 対空電探)
            if hasKokaku and specialKijuCount and antiAirRadarCount:
                cutInIds.append(10)
            # 11種 (高角砲, 特殊機銃)
            if hasKokaku and specialKijuCount:
                cutInIds.append(11)
        elif shipId == 141:
            # 五十鈴改二
            # 14種 (高角砲, 対空機銃, 対空電探)
            if hasKokaku and (kijuCount or specialKijuCount) and antiAirRadarCount:
                cutInIds.append(14)
            # 15種 (高角砲, 対空機銃)
            if hasKokaku and (kijuCount or specialKijuCount):
                cutInIds.append(15)
        elif shipId == 470 or shipId == 622:
            # 霞改二乙 夕張改二
            # 16種 (高角砲, 対空機銃, 対空電探)
            if hasKokaku and (kijuCount or specialKijuCount) and antiAirRadarCount:
                cutInIds.append(16)
            # 17種 (高角砲, 対空機銃)
            if shipId == 470 and hasKokaku and (kijuCount or specialKijuCount):
                cutInIds.append(17)
        elif shipId == 418:
            # 皐月改二
            # 18種 (特殊機銃)
            if specialKijuCount:
                cutInIds.append(18)
        elif shipId == 487:
            # 鬼怒改二
            # 19種 (よわ高角砲, 特殊機銃)
            if kokakuCount > 0 and specialKijuCount:
                cutInIds.append(19)
            # 20種 (特殊機銃)
            if specialKijuCount:
                cutInIds.append(20)
        elif shipId == 488:
            # 由良改二
            # 21種 (高角砲, 対空電探)
            if hasKokaku and antiAirRadarCount:
                cutInIds.append(21)
        elif shipId == 548:
            # 文月改二
            # 22種 (特殊機銃)
            if specialKijuCount:
                cutInIds.append(22)
        elif shipId == 329 or shipId == 530:
            # UIT-25 伊504
            # 23種 (通常機銃)
            if kijuCount:
                cutInIds.append(23)
        elif shipId == 478:
            # 龍田改二
            # 24種 (高角砲, 通常機銃)
            if allKokaku and kijuCount:
                cutInIds.append(24)
        elif shipId in {82, 88, 553, 554}:
            # 伊勢型改 / 改二
            # 25種 (噴進砲改二, 対空電探, 三式弾)
            if (
                antiAirRadarCount
                and hasSanshiki
                and any(v.data.id == 274 for v in items)
            ):
                cutInIds.append(25)
            # 28種 (噴進砲改二, 対空電探)
            if antiAirRadarCount and any(v.data.id == 274 for v in items):
                cutInIds.append(28)
        elif shipId == 148:
            # 武蔵改
            # 28種 (噴進砲改二, 対空電探)
            if antiAirRadarCount and any(v.data.id == 274 for v in items):
                cutInIds.append(28)
        elif type2 == 52:
            # 大淀
            # 27種 (10cm改+増設 対空電探)
            if (
                antiAirRadarCount
                and any(v.data.id == 274 for v in items)
                and any(v.data.id == 275 for v in items)
            ):
                cutInIds.append(27)
        elif shipId == 557 or shipId == 558:
            # 磯風乙改 / 浜風乙改
            # 29種 (高角砲, 対空電探)
            if hasKokaku and antiAirRadarCount:
                cutInIds.append(29)
        elif shipId == 477:
            # 天龍改二
            # 24種 (高角砲, 通常機銃)
            if allKokaku and kijuCount:
                cutInIds.append(24)
            # 30種 (高角砲3)
            if allKokaku >= 3:
                cutInIds.append(30)
            # 31種 (高角砲2)
            if allKokaku >= 2:
                cutInIds.append(31)
        elif shipId == 579 or shipId == 630:
            # Gotland改以降
            # 30種 (高角砲3)
            if allKokaku >= 3:
                cutInIds.append(30)
            # 33種 (高角砲, 素対空値4以上の機銃)
            if hasKokaku and any(
                v.data.apiTypeId == 21 and v.data.antiAir >= 4 for v in items
            ):
                cutInIds.append(33)
        elif type2 in const.GBR or type2 == 6 and ship.data.version >= 2:
            # 英国艦艇 / 金剛型改二以降
            # 32種 (16inch Mk.I三連装砲改+FCR type284, QF 2ポンド8連装ポンポン砲)
            if any(v.data.id == 300 for v in items) and any(
                v.data.id == 191 for v in items
            ):
                cutInIds.append(32)
            # 32種 (20連装7inch UP Rocket Launchers, QF 2ポンド8連装ポンポン砲)
            if any(v.data.id == 301 for v in items) and any(
                v.data.id == 191 for v in items
            ):
                cutInIds.append(32)
            # 32種 (20連装7inch UP Rocket Launchers, 20連装7inch UP Rocket Launchers)
            if len(tuple(v for v in items if v.data.id == 301)) >= 2:
                cutInIds.append(32)
        elif type2 == 91:
            # Fletcher級
            hasGFCSMk37 = any(v.data.id == 307 for v in items)
            # 34種 (5inch単装砲 Mk.30改+GFCS Mk.37, 5inch単装砲 Mk.30改+GFCS Mk.37)
            if len(tuple(v for v in items if v.data.id == 308)) >= 2:
                cutInIds.append(34)
            # 35種 (5inch単装砲 Mk.30改+GFCS Mk.37, 5inch単装砲 Mk.30 / 改)
            if any(v.data.id == 308 for v in items) and any(
                v.data.id == 284 or v.data.id == 313 for v in items
            ):
                cutInIds.append(35)
            # 36種 (5inch単装砲 Mk.30 / 改 2種, GFCS Mk.37)
            if (
                len(tuple(v for v in items if v.data.id == 284 or v.data.id == 313))
                >= 2
                and hasGFCSMk37
            ):
                cutInIds.append(36)
            # 37種 (5inch単装砲 Mk.30改 2種)
            if len(tuple(v for v in items if v.data.id == 313)) >= 2:
                cutInIds.append(37)
        elif type2 == 99:
            # Atlanta級

            GFCS5inchCount = len(tuple(v for v in items if v.data.id == 363))
            normal5inchCount = len(tuple(v for v in items if v.data.id == 362))
            # 38種 (GFCS Mk.37+5inch連装両用砲(集中配備) x2)
            if GFCS5inchCount >= 2:
                cutInIds.append(38)
            # 39種 (GFCS Mk.37+5inch連装両用砲(集中配備) と 5inch連装両用砲(集中配備) の両方が存在)
            if GFCS5inchCount and normal5inchCount:
                cutInIds.append(39)
            # 40種 (GFCS Mk.37+5inch連装両用砲(集中配備) or 5inch連装両用砲(集中配備) の合計が2 + GFCS Mk.37)
            if (GFCS5inchCount + normal5inchCount) >= 2 and any(
                v.data.id == 307 for v in items
            ):
                cutInIds.append(40)
            # 41種 (GFCS Mk.37+5inch連装両用砲(集中配備) or 5inch連装両用砲(集中配備) の合計が2)
            if (GFCS5inchCount + normal5inchCount) >= 2:
                cutInIds.append(41)
        elif shipId in {546, 911, 916}:
            # 大和型改二
            hasYamatoRadar = any(v.data.id == 142 or v.data.id == 460 for v in items)
            hasMore6AAkiju = any(
                v.data.apiTypeId == 21 and v.data.antiAir for v in items
            )
            syuchu10cmCount = len(tuple(v for v in items if v.data.id == 464))
            # 26種 (大和型改二, 10cm改+増設, 対空電探)
            if antiAirRadarCount and any(v.data.id == 275 for v in items):
                cutInIds.append(26)
            # 28種 (噴進砲改二, 対空電探)
            if (
                shipId == 546
                and antiAirRadarCount
                and any(v.data.id == 274 for v in items)
            ):
                cutInIds.append(28)
            # 42種（大和電探 + 10cm高角砲集中配備 * 2 + 素対空値6以上の機銃）
            if hasYamatoRadar and syuchu10cmCount >= 2 and hasMore6AAkiju:
                cutInIds.append(42)
            # 43種（大和電探 + 10cm高角砲集中配備 * 2）
            if hasYamatoRadar and syuchu10cmCount >= 2:
                cutInIds.append(43)
            # 44種（大和電探 + 10cm高角砲集中配備 + 素対空値6以上の機銃）
            if hasYamatoRadar and syuchu10cmCount and hasMore6AAkiju:
                cutInIds.append(44)
            # 45種（大和電探 + 10cm高角砲集中配備）
            if hasYamatoRadar and syuchu10cmCount:
                cutInIds.append(45)
        elif shipId == 593:
            # 榛名改二乙
            # 46種 (35.6改三 or 改四, 対空電探, 特殊機銃)
            if (
                specialKijuCount
                and antiAirRadarCount
                and any(v.data.id == 502 or v.data.id == 503 for v in items)
            ):
                cutInIds.append(46)
        elif type2 == 23 and ship.data.antiAir >= 70:
            # 白露型対空70以上
            # 春雨砲所持
            harusameGunCount = len(tuple(v for v in items if v.data.id == 529))
            # 25mm対空機銃増備
            has25mmAAGun = any(v.data.id == 505 for v in items)
            # 対空4以上の電探所持
            hasSPAntiAirRadar = any(
                (v.data.apiTypeId == 12 or v.data.apiTypeId == 13)
                and v.data.antiAir >= 4
                for v in items
            )
            if harusameGunCount >= 2 or (
                harusameGunCount and (hasSPAntiAirRadar or has25mmAAGun)
            ):
                cutInIds.append(47)

        # 汎用
        # 全ての水上艦 => 判定できないが必須装備が潜水艦を弾ける
        # 戦艦 航空戦艦 => 判定できないが大口径主砲を積めるのが戦艦だけ

        # 4種 (大口径, 三式弾, 高射装置, 対空電探)
        if (
            any(v.data.apiTypeId == 3 for v in items)
            and hasSanshiki
            and koshaCount
            and antiAirRadarCount
        ):
            cutInIds.append(4)
        # 5種 (特殊高角砲2, 対空電探, 秋月型以外)
        if specialKokakuCount >= 2 and antiAirRadarCount and type2 != 54:
            cutInIds.append(5)
        # 6種 (大口径, 三式弾, 高射装置)
        if any(v.data.apiTypeId == 3 for v in items) and hasSanshiki and koshaCount:
            cutInIds.append(6)
        # 7種 (高角砲, 高射装置, 対空電探, 秋月型以外)
        if hasKokaku and koshaCount and antiAirRadarCount and type2 != 54:
            cutInIds.append(7)
        # 8種 (特殊高角砲, 対空電探, 秋月型以外)
        if specialKokakuCount and antiAirRadarCount and type2 != 54:
            cutInIds.append(8)
        # 9種 (高角砲, 高射装置)
        if hasKokaku and koshaCount:
            cutInIds.append(9)
        # 12種 (特殊機銃, 素対空値3以上の機銃, 対空電探)
        if (
            specialKijuCount
            and len(
                tuple(
                    v for v in items if v.data.apiTypeId == 21 and v.data.antiAir >= 3
                )
            )
            >= 2
            and antiAirRadarCount
        ):
            cutInIds.append(12)
        # 13種 (特殊機銃, 特殊高角砲, 対空電探, 摩耶改二以外)
        if (
            specialKijuCount
            and specialKokakuCount
            and antiAirRadarCount
            and shipId != 428
        ):
            cutInIds.append(13)

        antiAirCutIns: list[AntiAirCutIn] = []
        for cutinId in cutInIds:
            cutIn = (
                _result[0]
                if (
                    _result := tuple(
                        v
                        for v in const.ANTI_AIR_CUTIN
                        if (_id := v.get("id", -1)) > -1 and _id == cutinId
                    )
                )
                and len(_result) == 1
                else None
            )
            if cutIn is None:
                continue

            rate = cutIn.get("rate", 0) / 101
            antiAirCutIns.append(
                AntiAirCutIn(
                    cutIn.get("id", 0),
                    cutIn.get("rateBonus", 1),
                    cutIn.get("c1", 1),
                    cutIn.get("c2", 0),
                    rate,
                )
            )

        return antiAirCutIns
