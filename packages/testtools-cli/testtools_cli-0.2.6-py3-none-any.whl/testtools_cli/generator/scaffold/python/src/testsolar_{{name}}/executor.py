from datetime import datetime
from pathlib import Path
from time import sleep
from typing import List

from loguru import logger
from testsolar_testtool_sdk.model.param import EntryParam
from testsolar_testtool_sdk.model.test import TestCase
from testsolar_testtool_sdk.model.testresult import (
    TestResult,
    ResultType,
    TestCaseStep,
    TestCaseLog,
    LogLevel,
)
from testsolar_testtool_sdk.reporter import FileReporter


def run_testcases(entry: EntryParam) -> None:
    reporter = FileReporter(Path(entry.FileReportPath))

    logger.info(f"running testcase in workdir [{entry.ProjectPath}]")

    cases = [TestCase(Name="a/b/c?d")]

    for case in cases:
        run_single_case(case, reporter)


def run_single_case(case: TestCase, reporter: FileReporter) -> None:
    logger.info(f"Running case {case.Name}")

    start_time = datetime.now()
    tr = TestResult(
        Test=case,
        StartTime=start_time,
        ResultType=ResultType.RUNNING,
        Message="",
    )
    reporter.report_case_result(tr)

    sleep(1)
    step_logs: List[TestCaseLog] = [
        TestCaseLog(Time=datetime.now(), Level=LogLevel.INFO, Content="Test Output")
    ]

    logger.info(f"Finished running case {case.Name}")

    tr_result: ResultType = ResultType.SUCCEED
    tr.ResultType = tr_result
    tr.Steps.append(
        TestCaseStep(
            Title=case.Name,
            StartTime=start_time,
            ResultType=tr_result,
            EndTime=datetime.now(),
            Logs=step_logs,
        )
    )
    tr.EndTime = datetime.now()

    reporter.report_case_result(tr)
