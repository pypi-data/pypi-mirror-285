import asyncio
import dataclasses
import datetime
import enum
import json
import sqlite3

import httpx
from typing_extensions import Any
from typing_extensions import Generator
from typing_extensions import Optional

from .logger import LOGGER
from .path import DATA_DIR
from .types import FitBonusPerEquipment
from .types import KcwikiEquipment
from .types import KcwikiShip
from .types import MasterItem
from .types import MasterShip
from .types import MasterTypeValidator
from .types.const import EquipmentTypes
from .types.equipment_id import EquipmentId
from .types.ship_id import ShipId

DB_FILE_PATH = DATA_DIR / "data.db"


class DataSourceURL(enum.Enum):
    KC_WIKI_EN_JSON_SHIP = (
        r"https://raw.githubusercontent.com/kcwiki/kancolle-data/master/wiki/ship.json"
    )
    KC_WIKI_EN_JSON_EQUIPMENT = r"https://raw.githubusercontent.com/kcwiki/kancolle-data/master/wiki/equipment.json"

    EO_EN_JSON_FIT_BONUS = r"https://raw.githubusercontent.com/ElectronicObserverEN/Data/master/Data/FitBonuses.json"

    NORO6_MASTER_JSON = r"https://firebasestorage.googleapis.com/v0/b/development-74af0.appspot.com/o/master.json"
    NORO6_MASTER_JSON_MEDIA = f"{NORO6_MASTER_JSON}{r'?alt=media'}"

    KC3_TRANSLATION_JSON_ITEMS = (
        r"https://cdn.jsdelivr.net/gh/KC3Kai/kc3-translations@master/data/en/items.json"
    )
    KC3_TRANSLATION_JSON_SHIPS = (
        r"https://cdn.jsdelivr.net/gh/KC3Kai/kc3-translations@master/data/en/ships.json"
    )


def dbConnection():
    return sqlite3.connect(DB_FILE_PATH)


def dbCreate():
    with dbConnection() as conn:
        conn.executescript((DATA_DIR / "db_create.sql").read_text())


def dbDrop():
    with dbConnection() as conn:
        conn.executescript((DATA_DIR / "db_drop.sql").read_text())


def dbVacuum():
    with dbConnection() as conn:
        conn.execute("VACUUM")


def _writeToDB(sourceUrl: DataSourceURL, content: str):
    with dbConnection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO t_{sourceUrl.name.lower()} VALUES (?, ?)",
            [datetime.datetime.now().timestamp(), json.dumps(json.loads(content))],
        )
        LOGGER.debug(f"data insert into db, {cur.lastrowid}")


async def _urlUpdateTask(
    client: httpx.AsyncClient, sourceUrl: DataSourceURL, retryCap: int = 5
):
    retryTimeOut: tuple[float, ...] = (0.5, *(i for i in range(1, retryCap)))

    for retryAttempt in range(retryCap):
        LOGGER.debug(f"fetching {sourceUrl} attempt {retryAttempt}")
        response = await client.get(sourceUrl.value)
        if response.is_success:
            LOGGER.debug(f"{sourceUrl} success")
            _writeToDB(sourceUrl, response.text)
            break

        if response.status_code == 404:
            raise httpx.RequestError(f"{sourceUrl} url return 404")

        await asyncio.sleep(retryTimeOut[retryAttempt])
        LOGGER.debug(f"{sourceUrl} attempt fail {retryAttempt}")


async def _dbUpdate():
    async with httpx.AsyncClient() as client:
        await asyncio.gather(
            _urlUpdateTask(client, DataSourceURL.KC_WIKI_EN_JSON_SHIP),
            _urlUpdateTask(client, DataSourceURL.KC_WIKI_EN_JSON_EQUIPMENT),
            _urlUpdateTask(client, DataSourceURL.EO_EN_JSON_FIT_BONUS),
            _urlUpdateTask(client, DataSourceURL.NORO6_MASTER_JSON_MEDIA),
            _urlUpdateTask(client, DataSourceURL.KC3_TRANSLATION_JSON_ITEMS),
            _urlUpdateTask(client, DataSourceURL.KC3_TRANSLATION_JSON_SHIPS),
        )


def dbUpdate(needBackUp: bool = True):
    _dbBackUp: bytes = b""
    if needBackUp:
        _dbBackUp = DB_FILE_PATH.read_bytes()
    try:
        dbCreate()
        asyncio.run(_dbUpdate())
        dbVacuum()
    except Exception as e:
        LOGGER.error(e)
        LOGGER.info("database will be rollback")
        DB_FILE_PATH.write_bytes(_dbBackUp)


def dbReset(needBackUp: bool = True):
    _dbBackUp: bytes = b""
    if needBackUp:
        _dbBackUp = DB_FILE_PATH.read_bytes()
    try:
        dbDrop()
        dbVacuum()
        dbCreate()
        dbUpdate()
    except Exception as e:
        LOGGER.error(e)
        LOGGER.info("database will be rollback")
        DB_FILE_PATH.write_bytes(_dbBackUp)


@dataclasses.dataclass(slots=True)
class _DBQueryWrapper:
    conn: sqlite3.Connection = dataclasses.field(init=False)

    def __post_init__(self):
        self.conn = dbConnection()

    def QueryShipByIdFromKcWikiEn(self, id: ShipId) -> Optional[KcwikiShip]:
        queryFilePath = DATA_DIR / "kcwiki/query_ship_by_id.sql"

        result: tuple[Any] | None = self.conn.execute(
            queryFilePath.read_text(), [id]
        ).fetchone()

        if result is not None:
            return KcwikiShip.model_validate_json(result[0])

        LOGGER.debug(f"QueryKcWikiEnShipById({id=}), {result=}")

        return None

    def QueryShipByNameJapaneseFromKcWikiEn(self, name: str) -> Optional[KcwikiShip]:
        queryFilePath = DATA_DIR / "kcwiki/query_ship_by_name_japanese.sql"

        result: tuple[Any] | None = self.conn.execute(
            queryFilePath.read_text(), [name]
        ).fetchone()

        if result is not None:
            return KcwikiShip.model_validate_json(result[0])

        LOGGER.debug(f"QueryKcWikiEnShipById({name=}), {result=}")

        return None

    def QueryEquipmentByIdFromKcWikiEn(
        self, id: EquipmentId
    ) -> Optional[KcwikiEquipment]:
        queryFilePath = DATA_DIR / "kcwiki/query_equipment_by_id.sql"

        result: tuple[Any] | None = self.conn.execute(
            queryFilePath.read_text(), [id]
        ).fetchone()

        if result is not None:
            return KcwikiEquipment.model_validate_json(result[0])

        LOGGER.debug(f"QueryKcWikiEnEquipmentById({id=}), {result=}")

        return None

    def QueryEquipmentByNameJapaneseFromKcWikiEn(
        self, name: str
    ) -> Optional[KcwikiEquipment]:
        queryFilePath = DATA_DIR / "kcwiki/query_equipment_by_name_japanese.sql"

        result: tuple[Any] | None = self.conn.execute(
            queryFilePath.read_text(), [name]
        ).fetchone()

        if result is not None:
            return KcwikiEquipment.model_validate_json(result[0])

        LOGGER.debug(f"QueryKcWikiEnEquipmentById({name=}), {result=}")

        return None

    def QueryFitBonusAllFromEOEn(self) -> Generator[FitBonusPerEquipment, None, None]:
        queryFilePath = DATA_DIR / "eo/query_fit_bonus_all.sql"

        cur = self.conn.cursor()
        cur.execute(queryFilePath.read_text())
        for c in cur:
            yield FitBonusPerEquipment.model_validate_json(*c)

    def QueryFitBonusByEquipmentIdFromEOEn(
        self, id: EquipmentId
    ) -> Optional[list[FitBonusPerEquipment]]:

        queryFilePath = DATA_DIR / "eo/query_fit_bonus_by_equipment_id.sql"

        result: list[tuple[Any]] | None = self.conn.execute(
            queryFilePath.read_text(), [id]
        ).fetchall()

        if result:
            return [FitBonusPerEquipment.model_validate_json(i[0]) for i in result]

        return None

    def QueryFitBonusByEquipmentTypeFromEOEn(
        self, equType: EquipmentTypes | int
    ) -> Optional[list[FitBonusPerEquipment]]:

        queryFilePath = DATA_DIR / "eo/query_fit_bonus_by_equipment_id.sql"

        result: list[tuple[Any]] | None = self.conn.execute(
            queryFilePath.read_text(), [equType]
        ).fetchall()

        if result:
            return [FitBonusPerEquipment.model_validate_json(i[0]) for i in result]

        return None

    def QueryMasterShipByIdFromNoro6Media(self, id: int) -> Optional[MasterShip]:

        queryFilePath = DATA_DIR / "noro6/query_master_ship_by_id.sql"

        result: tuple[Any] | None = self.conn.execute(
            queryFilePath.read_text(), [id]
        ).fetchone()

        if result:
            return MasterTypeValidator.MasterShip(*result)

        return None

    def QueryMasterEquipmentByIdFromNoro6Media(self, id: int) -> Optional[MasterItem]:

        queryFilePath = DATA_DIR / "noro6/query_master_equipment_by_id.sql"

        result: tuple[Any] | None = self.conn.execute(
            queryFilePath.read_text(), [id]
        ).fetchone()

        if result:
            return MasterTypeValidator.MasterItem(*result)

        return None

    def QueryShipNameEnByKeyFromKc3(self, key: str) -> Optional[str]:
        queryFilePath = DATA_DIR / "kc3/query_ship_name_en_by_key.sql"

        result: tuple[Any] | None = self.conn.execute(
            queryFilePath.read_text(), [key]
        ).fetchone()

        if result and isinstance(result[0], str):
            return result[0]

        return None

    def QueryEquipmentNameEnByKeyFromKc3(self, key: str) -> Optional[str]:
        queryFilePath = DATA_DIR / "kc3/query_equipment_name_en_by_key.sql"

        result: tuple[Any] | None = self.conn.execute(
            queryFilePath.read_text(), [key]
        ).fetchone()

        if result and isinstance(result[0], str):
            return result[0]

        return None


DATABASE = _DBQueryWrapper()
