import logging
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from solar_registry.service.testtool import get_testtool_by_file_path

log = logging.getLogger("rich")


class LeftToDos(BaseModel):
    file: Path
    line: int
    content: str


class ScaffoldChecker:
    def __init__(self, workdir: Optional[Path] = None):
        self.workdir = workdir or Path.cwd()

    def check_test_tool(self) -> None:
        """
        检查文件中的TODO，并输出到控制台提示用户还有多少个需要
        """
        self.check_test_tool_yaml()
        self.show_todos()

    def check_test_tool_yaml(self) -> None:
        yaml_file = Path(self.workdir / "testtool.yaml")
        log.info(f"Checking testtool yaml file: {yaml_file}")
        get_testtool_by_file_path(yaml_file)

    def show_todos(self) -> None:
        results: list[LeftToDos] = []
        for dirpath, dirnames, filenames in os.walk(self.workdir):
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]

            # 检查filenames里面有没有TODO
            for filename in filenames:
                file_to_check = Path(dirpath) / filename
                results.extend(self._get_todos(file_to_check))

        if results:
            log.warning(f"You still have {len(results)} TODOs.Please fix these todos below:")
            for result in results:
                log.warning(f"  {result.file}:{result.line}:\t\t{result.content}")

    def _get_todos(self, file_to_check: Path) -> list[LeftToDos]:
        if file_to_check.name.startswith("."):
            return []

        results: list[LeftToDos] = []
        # noinspection PyBroadException
        try:
            content = file_to_check.read_text(encoding="utf-8")
            for i, line_content in enumerate(content.splitlines()):
                if "__TODO__" in line_content:
                    results.append(LeftToDos(file=file_to_check, line=i + 1, content=line_content))
            return results
        except Exception:
            return []
