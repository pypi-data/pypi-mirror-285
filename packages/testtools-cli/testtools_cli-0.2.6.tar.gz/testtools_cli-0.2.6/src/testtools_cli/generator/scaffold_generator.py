import logging
import os
from enum import Enum
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader
from jinja2.nativetypes import NativeEnvironment

from .scaffold_checker import ScaffoldChecker

log = logging.getLogger("rich")


class LangType(str, Enum):
    Python = "python"
    Golang = "golang"
    Java = "java"
    Javascript = "javascript"


class ScaffoldGenerator:
    def __init__(self, lang: LangType, testtool_name: str, workdir: Optional[str]) -> None:
        self.lang = lang
        self.testtool_name = testtool_name
        self.workdir = workdir or os.getcwd()
        self.native_env = NativeEnvironment()

    def generate(self) -> None:
        if self.lang == LangType.Python:
            self.generate_scaffold(language_name=LangType.Python.value)

    def generate_scaffold(self, language_name: str) -> None:
        scaffold_dir = Path(__file__).parent / "scaffold" / language_name
        env = Environment(loader=FileSystemLoader(scaffold_dir))

        for dirpath, dirnames, filenames in os.walk(scaffold_dir):
            # 计算模板文件的相对目录
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            relative_dir = os.path.relpath(dirpath, scaffold_dir)

            # dirnames是目录，不用管
            # 仅处理当前目录下的filenames即可
            for filename in filenames:
                if filename.endswith(".pyc"):
                    continue
                relative_file = Path(relative_dir) / filename

                path_template = self.native_env.from_string(str(relative_file))
                dest_path = Path(self.workdir) / path_template.render(name=self.testtool_name)

                Path(dest_path).parent.mkdir(parents=True, exist_ok=True)

                log.info(f"Generating scaffold file [{dest_path}]")
                with open(dest_path, "w", encoding="utf-8") as file_out:
                    log.debug(f"  From template file [{relative_file}]")
                    log.debug(f"  Into dest file [{dest_path}]")
                    template = env.get_template(str(relative_file))
                    content = template.render(name=self.testtool_name)
                    file_out.write(content)

        logging.info(f"✅ Generated {language_name} scaffold done.")

        checker = ScaffoldChecker(workdir=Path(self.workdir))
        checker.check_test_tool()
