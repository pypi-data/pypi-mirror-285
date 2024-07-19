import argparse
import json
import logging
import sys
from dataclasses import dataclass
from io import TextIOWrapper

from typing_extensions import Sequence

from . import database
from .logger import LOGGER
from .services.preprocessor.process import Process
from .services.translator.translator import Translator
from .services.translator.translator import TranslatorBuilder
from .types import Convert


def argumentParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kanclatex",
        description="a tool generate latex from AirDefense Calculator",
    )

    parser.add_argument(
        "-n",
        "--noro",
        metavar="fleet.json",
        type=argparse.FileType("r"),
        help="path to the fleet json.",
    )

    parser.add_argument(
        "-t",
        "--template",
        metavar="template.tex",
        type=argparse.FileType("r"),
        help="path to the template latex file.",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="output.tex",
        type=argparse.FileType("w"),
        help="path to the output latex file. If not specific the result will be display to stdout.",
    )

    parser.add_argument(
        "--update",
        action="store_true",
        help="update ship, equipment and fit bonus.",
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="reset the database. Old record will be missing.",
    )

    parser.add_argument("--debug", action="store_true", help="enable debug message")

    parser.add_argument(
        "-tse",
        "--translation-ships-en",
        metavar="translation_ships_en.json",
        type=argparse.FileType("r"),
        help="path to the json of english translation for ships",
    )

    parser.add_argument(
        "-tee",
        "--translation-equipments-en",
        metavar="translation_equipment_en.json",
        type=argparse.FileType("r"),
        help="path to the json of english translation for equipments",
    )

    return parser


@dataclass(slots=True)
class Args:
    noro: TextIOWrapper | None
    template: TextIOWrapper | None
    output: TextIOWrapper | None
    update: bool
    reset: bool
    debug: bool
    translation_ships_en: TextIOWrapper | None
    translation_equipments_en: TextIOWrapper | None


_SUCCESS = 0
_ERROR = 1


def main(argv: Sequence[str] | None = None):

    parser = argumentParser()
    _parsedResult = parser.parse_args(argv)
    args = Args(**vars(_parsedResult))

    if args.debug:
        LOGGER.setLevel(logging.DEBUG)
        setattr(_parsedResult, "debug", False)

    LOGGER.debug(f"{args = }")

    if all(not v for v in vars(_parsedResult).values()):
        parser.print_help()

    if args.reset:
        try:
            database.dbReset()
        except Exception as e:
            LOGGER.fatal(e)
            sys.exit(_ERROR)

    if args.update:
        try:
            database.dbUpdate()
        except Exception as e:
            LOGGER.fatal(e)
            sys.exit(_ERROR)

    if args.noro and args.template:

        fleetInfo = Convert.loadDeckBuilderToFleetInfo(args.noro.read())

        if fleetInfo is None:
            LOGGER.fatal("fleetInfo is None")
            sys.exit(_ERROR)

        _transactor = Translator(
            builder=TranslatorBuilder(
                (
                    json.loads(args.translation_ships_en.read())
                    if args.translation_ships_en is not None
                    else dict()
                ),
                (
                    json.loads(args.translation_equipments_en.read())
                    if args.translation_equipments_en is not None
                    else dict()
                ),
            )
        )

        p = Process(fleetInfo, args.template, _transactor)
        result = p.process()
        if args.output and not p.errorCount:
            args.output.write(result.getvalue())
        elif not p.errorCount:
            print(result.getvalue())

    elif args.noro and args.template is None:
        LOGGER.info("Please provide a template.")
        sys.exit(_ERROR)
    elif args.noro is None and args.template:
        LOGGER.info("Please provide a deck builder json.")
        sys.exit(_ERROR)

    sys.exit(_SUCCESS)
