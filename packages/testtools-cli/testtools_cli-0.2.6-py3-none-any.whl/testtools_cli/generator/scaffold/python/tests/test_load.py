import io
from pathlib import Path

from src.load import collect_testcases_from_args
from testsolar_testtool_sdk.pipe_reader import read_load_result

testdata_dir: str = str(Path(__file__).parent.absolute().joinpath("testdata"))


def test_collect_testcases_from_args():
    pipe_io = io.BytesIO()
    collect_testcases_from_args(
        args=["load.py", Path.joinpath(Path(testdata_dir), "entry.json")],
        workspace=testdata_dir,
        pipe_io=pipe_io,
    )

    pipe_io.seek(0)
    re = read_load_result(pipe_io)

    assert len(re.Tests) == 1

    assert re.Tests[0].Name == "a/b/c?d"

    assert len(re.LoadErrors) == 1
    assert re.LoadErrors[0].name == "load xxx.py failed"
    assert re.LoadErrors[0].message == "backtrace here"
