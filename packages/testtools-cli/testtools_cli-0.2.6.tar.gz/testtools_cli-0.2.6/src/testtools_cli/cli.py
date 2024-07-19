import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.logging import RichHandler
from rich.traceback import install
from typing_extensions import Annotated

from testtools_cli.generator.scaffold_checker import ScaffoldChecker
from .generator.scaffold_generator import ScaffoldGenerator, LangType

install(show_locals=True)

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

app = typer.Typer(rich_markup_mode="markdown")

log = logging.getLogger("rich")


@app.command()
def init(
        workdir: Annotated[
            Optional[str],
            typer.Option(
                help="Where you want the scaffolding code to be stored, defaulting to the current directory"
            ),
        ] = None,
        verbose: Annotated[Optional[bool], typer.Option(help="Verbose output")] = False,
) -> None:
    """
    **Init** a testsolar testtool with guide

    Current supported languages:

    - python

    - golang

    - javascript

    - java
    """
    if not verbose:
        log.setLevel(logging.INFO)
        logger.remove()
        logger.add(sys.stdout, level="INFO")

    tool_name = typer.prompt("Name of the test tool?")
    pre_langs = "/".join([e.value for e in LangType])
    lang = LangType(
        typer.prompt(f"The language you want to use for development({pre_langs})?")
    )

    gen = ScaffoldGenerator(lang=lang, testtool_name=tool_name, workdir=workdir)
    gen.generate()


@app.command()
def check(
        workdir: Annotated[
            Optional[str],
            typer.Option(
                help="The test tool dir to check, defaulting to the current directory"
            ),
        ] = None,
        verbose: Annotated[Optional[bool], typer.Option(help="Verbose output")] = False,
) -> None:
    """
    **Check** if the testing tools are effective

    - Check the validity of the testing tool metadata

    - Check the validity of the testing tool scripts
    """
    if not verbose:
        log.setLevel(logging.INFO)
        logger.remove()
        logger.add(sys.stdout, level="INFO")

    working_dir = Path(workdir) if workdir else Path.cwd()
    checker = ScaffoldChecker(working_dir)
    checker.check_test_tool()


def cli_entry() -> None:
    app()


if __name__ == "__main__":
    app()
