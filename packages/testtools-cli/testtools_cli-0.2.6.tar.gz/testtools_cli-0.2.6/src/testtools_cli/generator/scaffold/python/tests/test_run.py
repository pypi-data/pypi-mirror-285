import io
from pathlib import Path

from testsolar_testtool_sdk.pipe_reader import read_test_result
from testsolar_testtool_sdk.model.testresult import ResultType, LogLevel

from src.run import run_testcases_from_args

testdata_dir: str = str(Path(__file__).parent.absolute().joinpath("testdata"))


def test_run_testcases_from_args():
    pipe_io = io.BytesIO()
    run_testcases_from_args(
        args=["run.py", Path.joinpath(Path(testdata_dir), "entry.json")],
        workspace=testdata_dir,
        pipe_io=pipe_io,
    )

    pipe_io.seek(0)
    re = read_test_result(pipe_io)

    assert re.Test.Name == "a/b/c?d"
    assert re.ResultType == ResultType.RUNNING
    assert len(re.Steps) == 0
    assert re.StartTime
    assert not re.EndTime

    re = read_test_result(pipe_io)
    assert re.Test.Name == "a/b/c?d"
    assert re.ResultType == ResultType.SUCCEED
    assert re.StartTime
    assert re.EndTime
    assert len(re.Steps) == 1
    assert re.Steps[0].ResultType == ResultType.SUCCEED
    assert re.Steps[0].Title == "a/b/c?d"
    assert len(re.Steps[0].Logs) == 1
    assert re.Steps[0].Logs[0].Level == LogLevel.INFO
    assert re.Steps[0].Logs[0].Content == "Test Output"
