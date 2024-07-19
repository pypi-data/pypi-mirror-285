from src.testtools_cli.generator.scaffold_generator import ScaffoldGenerator, LangType


def test_create_pytest_scaffold() -> None:
    gen = ScaffoldGenerator(lang=LangType.Python, testtool_name="pytest", workdir="/tmp/tool/pytest")
    gen.generate()
