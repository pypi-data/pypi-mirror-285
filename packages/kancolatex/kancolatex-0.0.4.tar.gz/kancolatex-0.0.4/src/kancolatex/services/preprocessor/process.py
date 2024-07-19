from dataclasses import dataclass
from dataclasses import field
from io import StringIO
from io import TextIOWrapper
from string import Formatter

from pydantic import BaseModel
from pydantic import ValidationError
from typing_extensions import Optional
from typing_extensions import Sequence

from ...logger import LOGGER
from ...types.noro6 import FleetInfo
from ..translator.translator import Translator
from .macro import MacroValueType
from .macro import OrderTranslate
from .macro import PreDefineMacro
from .macro import attrAccess
from .macro import isValidMacro


class _DefineConfig(BaseModel):
    overwrite: Optional[bool] = False
    name: str
    template: str
    param: Optional[Sequence[str]] = None


@dataclass(slots=True)
class Process:
    fleetInfo: FleetInfo
    template: TextIOWrapper

    _preDefineMacro: PreDefineMacro = field(init=False)
    translator: Optional[Translator] = None

    result: StringIO = field(default_factory=StringIO)
    errorCount: int = 0

    _defineMode: bool = False
    _preProcessMode: bool = False
    _defineTable: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self._preDefineMacro = PreDefineMacro(
            self.fleetInfo,
            self.translator if self.translator else Translator(builder=None),
        )
        self._defineTable.update(self._preDefineMacro.latexLoopUp)

        self._custom_DefineConfigValue()

        LOGGER.debug(f"{self._defineTable = }")
        LOGGER.debug(f"{tuple(sorted(self._defineTable)) = }")

    def process(self) -> StringIO:
        result = StringIO()

        for lineNum, line in enumerate(self.template, 1):
            workingLine = line
            lineStriped = line.strip()

            if self._setDefineMode(lineNum, lineStriped):
                result.write(workingLine)
                continue
            if self._setProcessMode(lineNum, lineStriped):
                result.write(workingLine)
                continue

            if self._defineMode:
                newDefine = self._parseDefineConfig(lineNum, lineStriped)
                LOGGER.debug(newDefine)
                if newDefine is not None:
                    self._eval_DefineConfigParams(newDefine)

            if self._preProcessMode:
                workingLine, mid, other = line.partition("%")
                for k, v in self._defineTable.items():
                    workingLine = workingLine.replace(k, v)

                if mid:
                    workingLine = "".join((workingLine, mid, other))

            result.write(workingLine)

        result.seek(0)
        return result

    def _setDefineMode(self, lineNumber: int, line: str) -> bool:
        line = line.lower()
        shouldSkip = False
        if line.find("%") != 0:
            return shouldSkip

        if line.find("KancoLaTeX:define:begin".lower()) > 0 and not self._defineMode:
            if self._preProcessMode:
                self.errorCount += 1
                LOGGER.error(
                    f'{lineNumber = } found "KancoLaTeX:define:begin" while in preprocess mode! FAIL ENTER define mode'
                )
            else:
                self._defineMode = True
                LOGGER.debug(
                    f"{lineNumber = } KancoLaTeX:define:begin, Enter define mode"
                )

            shouldSkip = True

        elif line.find("KancoLaTeX:define:end".lower()) > 0 and self._defineMode:
            self._defineMode = False
            LOGGER.debug(f"{lineNumber = } KancoLaTeX:define:end, Exit define mode")

            shouldSkip = True

        return shouldSkip

    def _setProcessMode(self, lineNumber: int, line: str) -> bool:
        line = line.lower()
        shouldSkip = False
        if line.find("%") != 0:
            return shouldSkip

        if line.find("KancoLaTeX:preprocess:begin".lower()) > 0:
            if not self._preProcessMode:
                if self._defineMode:
                    self.errorCount += 1
                    LOGGER.error(
                        f'{lineNumber = } found "KancoLaTeX:preprocess:begin" while in define mode! FAIL ENTER preprocess mode'
                    )
                else:
                    self._preProcessMode = True
                    LOGGER.debug(
                        f"{lineNumber = } KancoLaTeX:preprocess:begin, Enter preprocess mode"
                    )

            shouldSkip = True

        elif line.find("KancoLaTeX:preprocess:end".lower()) > 0:
            if self._preProcessMode:
                self._preProcessMode = False
                LOGGER.debug(
                    f"{lineNumber = } KancoLaTeX:preprocess:end, Exit preprocess mode"
                )

            shouldSkip = True

        return shouldSkip

    def _parseDefineConfig(self, lineNumber: int, line: str) -> _DefineConfig | None:
        if line.find("%") != 0 or len(line) < 1:
            return None

        line = line[1:]

        try:
            result = _DefineConfig.model_validate_json(line)
        except ValidationError as e:
            LOGGER.error(f"{lineNumber = } FAIL to parse define config")
            LOGGER.error(e)
            self.errorCount += 1
            return None

        return result

    def _eval_DefineConfigParams(self, defineConfig: _DefineConfig) -> bool:
        if (
            existDefineEval := self._defineTable.get(defineConfig.name, None)
        ) is not None:
            LOGGER.warning(
                f"OVERWRITE EXIST DEFINE: {defineConfig.name} already exist define as {existDefineEval!r}"
            )

        evalResult: str = ""
        if defineConfig.param is None:
            evalResult = defineConfig.template
        elif len(
            tuple(
                v for v in Formatter().parse(defineConfig.template) if v[1] is not None
            )
        ) != len(defineConfig.param):
            LOGGER.error(
                f"number of {defineConfig.template!r} slot does not match number of param {defineConfig.param!r}"
            )
            return False
        else:
            _evadedParam: list[str] = []
            for i, v in enumerate(defineConfig.param):
                LOGGER.debug(f"{i = }, {v = }, {isValidMacro(v) = }")
                _macro = isValidMacro(v)
                if _macro is not None:
                    _macroResult: str = ""
                    if _macro.type == MacroValueType.MNEMONIC:
                        _macroResult = self._preDefineMacro.macroLookUp.get(
                            _macro.value, ""
                        )
                        LOGGER.debug(f"{_macroResult = }")
                    elif not (_macroResult := attrAccess(self.fleetInfo, _macro)):
                        LOGGER.warning(f"macro: {v!r} return empty result!")

                    LOGGER.debug(f"{_macroResult = }")
                    _evadedParam.append(_macroResult)
                else:
                    LOGGER.warning(
                        f"Invalid param {v!r}, {defineConfig.name!r} WILL NOT eval!"
                    )
                    _evadedParam.append(v)

            evalResult = defineConfig.template.format(*_evadedParam)

        self._defineTable[defineConfig.name] = evalResult
        LOGGER.debug(f"{defineConfig.name = }")
        LOGGER.debug(f"{self._defineTable[defineConfig.name] = }")
        return True

    def _custom_DefineConfigValue(self):
        for shipPos in OrderTranslate.shipName(tuple):
            self._eval_DefineConfigParams(
                _DefineConfig(
                    name="".join((r"\kk", shipPos, "{}")),
                    template="".join((r"\kl", shipPos, r"{{{0}, {1}, {2}, {3}}}")),
                    param=(
                        f"<SHIP_{shipPos}_ID>",
                        f"<SHIP_{shipPos}_NAME_EN>",
                        f"<SHIP_{shipPos}_LEVEL>",
                        f"<SHIP_{shipPos}_DISPLAYSTATUS_LUCK>",
                    ),
                )
            )

            for equipmentPos in OrderTranslate.equipmentName(tuple):
                if equipmentPos == "X":
                    self._eval_DefineConfigParams(
                        _DefineConfig(
                            name="".join((r"\kk", shipPos, equipmentPos)),
                            template="".join(
                                (
                                    r"\kl",
                                    shipPos,
                                    equipmentPos,
                                    r"{{{0}, {1}, {2}, {3}, {4}}}",
                                )
                            ),
                            param=(
                                f"<SHIP_{shipPos}_EQUIPMENT_{equipmentPos}_EQUIPPED>",
                                f"<SHIP_{shipPos}_EQUIPMENT_{equipmentPos}_ICONID>",
                                f"<SHIP_{shipPos}_EQUIPMENT_{equipmentPos}_NAME_EN>",
                                f"<SHIP_{shipPos}_EQUIPMENT_{equipmentPos}_REMODEL>",
                                f"<SHIP_{shipPos}_EQUIPMENT_{equipmentPos}_ID>",
                            ),
                        )
                    )

                    continue

                self._eval_DefineConfigParams(
                    _DefineConfig(
                        name="".join((r"\kk", shipPos, equipmentPos)),
                        template="".join(
                            (
                                r"\kl",
                                shipPos,
                                equipmentPos,
                                r"{{{0}, {1}, {2}, {3}, {4}, {5}}}",
                            )
                        ),
                        param=(
                            f"<SHIP_{shipPos}_SLOT_{equipmentPos}>",
                            f"<SHIP_{shipPos}_EQUIPMENT_{equipmentPos}_ICONID>",
                            f"<SHIP_{shipPos}_EQUIPMENT_{equipmentPos}_NAME_EN>",
                            f"<SHIP_{shipPos}_EQUIPMENT_{equipmentPos}_REMODEL>",
                            f"<SHIP_{shipPos}_EQUIPMENT_{equipmentPos}_LEVEL_ALT>",
                            f"<SHIP_{shipPos}_EQUIPMENT_{equipmentPos}_ID>",
                        ),
                    )
                )
