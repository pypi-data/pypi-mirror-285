# Copyright 2023 Inductor, Inc.
"""Functionality for test suite execution tasks."""

from concurrent import futures
import contextlib
import datetime
from typing import Dict, Generator, Iterator, List, Literal, NamedTuple, Optional, Union

import inquirer
import rich
from rich import progress
import typer

from inductor import config
from inductor.backend_client import backend_client, wire_model
from inductor.data_model import data_model
from inductor.execution import execution, quality_measure_execution


@contextlib.contextmanager
def _disable_logger_decorator():
    """Disable the inductor.logger decorator within this context manager.

    Disable the inductor.logger decorator by setting
    `execution.logger_decorator_enabled` to False. On exit, restore the
    original value of `execution.logger_decorator_enabled`.
    """
    orig_logger_decorator_enabled = execution.logger_decorator_enabled
    try:
        execution.logger_decorator_enabled = False
        yield
    finally:
        execution.logger_decorator_enabled = orig_logger_decorator_enabled


class _ExecuteTestCaseReturn(NamedTuple):
    """Return type of `execute_test_case`.

    See `execute_test_case`'s docstring (below) for
    descriptions of fields.
    """
    execution_details: wire_model.ExecutionDetails
    invalid_quality_measures: List[Dict[str, Union[
        int, str, wire_model.QualityMeasureExecutionDetails]]]
    stdout_stderr: str


def execute_test_case(
    llm_program_fully_qualified_name: str,
    test_case: data_model.TestCase,
    quality_measures_with_metadata: Optional[List[
        data_model.QualityMeasureWithMetadata]] = None,
    hparams: Optional[Dict[str, Union[str, int, float]]] = None,
    mode: Literal["CLI", "PLAYGROUND"] = "CLI",
    suppress_stdout_stderr: bool = True
) -> _ExecuteTestCaseReturn:
    """Run a test case and evaluate its quality measures.

    Args:
        llm_program_fully_qualified_name: Fully qualified name of LLM program.
        test_case: Test case.
        quality_measures_with_metadata: List of quality measures with ID.
        hparams: Mapping from hyperparameter names to values.
        mode: Execution mode.
        suppress_stdout_stderr: Whether to suppress stdout and stderr output.
    
    Returns:
        Named tuple with the following fields:
            execution_details: ExecutionDetails object.
            invalid_quality_measures: List of invalid quality measures. Each
                invalid quality measure is a Dictionary with the following keys:
                    "id": ID of quality measure.
                    "name": Name of quality measure.
                    "execution_details": QualityMeasureExecutionDetails object.
            stdout_stderr: Combined stdout and stderr output, if
                suppress_stdout_stderr is False. Otherwise, an empty string.
    """
    started_at = datetime.datetime.now(datetime.timezone.utc)

    llm_program_stdout = None
    llm_program_stderr = None
    stdout_stderr = ""
    llm_program_error = None
    llm_program_output = None
    # Note: we use backslashes to split the `with` clause immediately below,
    # rather than enclosing in parentheses, because enclosing in parentheses
    # apparently causes a SyntaxError when running in Python 3.8.
    # pylint: disable-next=protected-access
    with execution.capture_stdout_stderr(
        suppress=suppress_stdout_stderr) as captured_streams, \
        execution.capture_logged_values() as logged_values, \
        _disable_logger_decorator(), \
        execution.set_hparams(hparams or {}):
        try:
            # Run the LLM program.
            llm_program_output = data_model.LazyCallable(
                llm_program_fully_qualified_name
            )(**test_case.inputs)
            if isinstance(llm_program_output, Iterator):
                llm_program_output = list(llm_program_output)
                if all(isinstance(value, str) for value in llm_program_output):
                    llm_program_output = "".join(llm_program_output)

        except Exception as error:  # pylint: disable=broad-except
            llm_program_error = str(error)

        llm_program_stdout = captured_streams.stdout.getvalue()
        llm_program_stderr = captured_streams.stderr.getvalue()
        stdout_stderr = captured_streams.suppressed.getvalue()

    ended_at = datetime.datetime.now(datetime.timezone.utc)

    # If the LLM program completed without error, run the executable quality
    # measures.
    if llm_program_error is None and quality_measures_with_metadata:
        quality_measure_execution_result = (
            quality_measure_execution.execute_quality_measures(
                test_case=test_case,
                llm_program_output=llm_program_output,
                quality_measures_with_metadata=quality_measures_with_metadata
            ))
        direct_evaluations = (
            quality_measure_execution_result.direct_evaluations)
        invalid_quality_measures = (
            quality_measure_execution_result.invalid_quality_measures)
        stdout_stderr += (
            quality_measure_execution_result.stdout_stderr)
    else:
        direct_evaluations = []
        invalid_quality_measures = []

    execution_details = wire_model.ExecutionDetails(
        mode=mode,
        inputs=test_case.inputs,
        hparams=hparams or None,
        output=llm_program_output,
        error=llm_program_error,
        stdout=llm_program_stdout,
        stderr=llm_program_stderr,
        execution_time_secs=(ended_at - started_at).total_seconds(),
        started_at=started_at,
        ended_at=ended_at,
        logged_values=logged_values or None,
        direct_evaluations=direct_evaluations or None)

    return _ExecuteTestCaseReturn(
        execution_details=execution_details,
        invalid_quality_measures=invalid_quality_measures,
        stdout_stderr=stdout_stderr)


@contextlib.contextmanager
def _manage_run_requests(
    test_suite: data_model.TestSuite,
    auth_access_token: str
) -> Generator[wire_model.CreateTestSuiteRunResponse, None, None]:
    """Send requests to the server to manage the creation/completion of a run.
    
    Send a request to the server to create a test suite run. Then, yield the
    response, which contains test suite run metadata. On exit, send a request
    to the server to mark the test suite run as complete.

    Args:
        test_suite: Test suite.
        auth_access_token: Auth0 access token.

    Yields:
        CreateTestSuiteRunResponse object.
    """
    test_suite_run = test_suite._get_run_request()  # pylint: disable=protected-access
    test_suite_run_metadata = backend_client.create_test_suite_run(
        test_suite_run, auth_access_token)
    try:
        yield test_suite_run_metadata
    finally:
        backend_client.complete_test_suite_run(
            wire_model.CompleteTestSuiteRunRequest(
                test_suite_run_id=
                    test_suite_run_metadata.test_suite_run_id,
                ended_at=
                    datetime.datetime.now(datetime.timezone.utc)),
            auth_access_token)


class _ExecuteTestSuiteTestCaseReturn(NamedTuple):
    """Return type of `_execute_test_suite_test_case`.

    See `_execute_test_suite_test_case`'s docstring (below)
    for descriptions of fields.
    """
    log_execution_request: wire_model.LogTestCaseExecutionRequest
    invalid_quality_measures: List[Dict[str, Union[
        int, str, wire_model.QualityMeasureExecutionDetails]]]
    stdout_stderr: str


def _execute_test_suite_test_case(
    test_suite_run_id: int,
    test_case_with_metadata: data_model.TestCaseWithMetadata,
    test_case_replica_index: int,
    hparams: Dict[str, Union[str, int, float]],
    llm_program_fully_qualified_name: str,
    quality_measures_with_metadata: List[
        data_model.QualityMeasureWithMetadata],
    auth_access_token: str,
) -> _ExecuteTestSuiteTestCaseReturn:
    """Execute a test suite test case and log the results to the server.
    
    Args:
        test_suite_run_id: ID of test suite run.
        test_case_with_metadata: Test case with metadata.
        test_case_replica_index: Index of test case replica.
        hparams: Mapping from hyperparameter names to values.
        llm_program_fully_qualified_name: Fully qualified name of LLM program.
        quality_measures_with_metadata: List of quality measures with ID.
        auth_access_token: Auth0 access token.
    
    Returns:
        Named tuple with the following fields:
            log_execution_request: LogTestCaseExecutionRequest object.
            invalid_quality_measures: List of invalid quality measures. Each
                invalid quality measure is a Dictionary with the following keys:
                    "id": ID of quality measure.
                    "name": Name of quality measure.
                    "execution_details": QualityMeasureExecutionDetails object.
            stdout_stderr: Combined stdout and stderr output.
    """
    test_case_results = execute_test_case(
        llm_program_fully_qualified_name=llm_program_fully_qualified_name,
        test_case=test_case_with_metadata,
        quality_measures_with_metadata=quality_measures_with_metadata,
        hparams=hparams)

    log_execution_request = wire_model.LogTestCaseExecutionRequest(
        test_suite_run_id=test_suite_run_id,
        test_case_id=test_case_with_metadata.id,
        test_case_replica_index=test_case_replica_index,
        execution_details=test_case_results.execution_details)

    backend_client.log_test_case_execution(
        log_execution_request, auth_access_token)

    return _ExecuteTestSuiteTestCaseReturn(
        log_execution_request=log_execution_request,
        invalid_quality_measures=test_case_results.invalid_quality_measures,
        stdout_stderr=test_case_results.stdout_stderr)


def execute_test_suite(
    test_suite: data_model.TestSuite,
    auth_access_token: str,
    *,
    prompt_open_results: bool = False
) -> wire_model.CreateTestSuiteRunResponse:
    """Execute a test suite.
    
    Execute a test suite while displaying relevant information to the user,
    including a progress bar.
    
    Args:
        test_suite: Test suite to execute.
        auth_access_token: Auth0 access token.
        prompt_open_results: Whether to prompt the user to open the test
            suite run results in a browser.
    
    Returns:
        CreateTestSuiteRunResponse object, containing test suite run metadata.
    """
    # Note: we use backslashes to split the `with` clause immediately below,
    # rather than enclosing in parentheses, because enclosing in parentheses
    # apparently causes a SyntaxError when running in Python 3.8.
    with futures.ProcessPoolExecutor(
            max_workers=test_suite.config.parallelize) as executor, \
        _manage_run_requests(
            test_suite, auth_access_token) as test_suite_run_metadata:

        # Note that `test_suite_run_metadata.test_case_ids` is the IDs
        # of `test_suite.test_cases` followed by the IDs of
        # `test_suite_run_metadata.imported_test_cases`. This ordering
        # needs to be preserved when updating the components with IDs.
        test_cases_with_metadata = data_model.components_with_ids(
            test_suite.test_cases +
            (test_suite_run_metadata.imported_test_cases or []),
            test_suite_run_metadata.test_case_ids,
            data_model.TestCaseWithMetadata)
        quality_measures_with_metadata = data_model.components_with_ids(
            test_suite.quality_measures,
            test_suite_run_metadata.quality_measure_ids,
            data_model.QualityMeasureWithMetadata)

        def pluralize(count: int) -> str:
            return "s" if count != 1 else ""
        rich.print(f"Running {len(test_cases_with_metadata)} test case"
              f"{pluralize(len(test_cases_with_metadata))} "
              f"({test_suite.config.replicas} run"
              f"{pluralize(test_suite.config.replicas)} each) ...")

        test_case_futures = []
        for test_case_replica_index in range(test_suite.config.replicas):
            for hparams in test_suite.hparam_combinations:
                for test_case_with_metadata in test_cases_with_metadata:
                    test_case_futures.append(executor.submit(
                        _execute_test_suite_test_case,
                        test_suite_run_id=
                            test_suite_run_metadata.test_suite_run_id,
                        test_case_with_metadata=test_case_with_metadata,
                        test_case_replica_index=test_case_replica_index,
                        hparams=hparams,
                        llm_program_fully_qualified_name=
                            test_suite.config.llm_program,
                        quality_measures_with_metadata=
                            quality_measures_with_metadata,
                        auth_access_token=auth_access_token
                    ))

        typer.echo(f"Go to {test_suite_run_metadata.url} to view results.")
        if prompt_open_results:
            open_url = inquirer.confirm(
                message="Open in browser?", default=True)
            if open_url:
                typer.launch(test_suite_run_metadata.url)

        # Display progress bar and optionally print test outputs.
        with progress.Progress() as progress_bar:
            progress_task = progress_bar.add_task(
                "Test Cases",
                total=(test_suite.config.replicas *
                        len(test_cases_with_metadata) *
                        len(test_suite.hparam_combinations)))

            for future in futures.as_completed(test_case_futures):
                progress_bar.advance(progress_task)
                test_case_result = future.result()
                test_output = test_case_result.log_execution_request
                invalid_quality_measures = (
                    test_case_result.invalid_quality_measures)
                stdout_stderr = test_case_result.stdout_stderr

                if stdout_stderr:
                    progress_bar.console.print(stdout_stderr)
                if test_output.execution_details.error is not None:
                    progress_bar.console.print(
                        "\n[red][bold][ERROR] Test case execution "
                        "raised an exception.[/bold] The following "
                        "execution will be recorded as FAILED and "
                        "quality measures will not be evaluated:[/red]")
                    progress_bar.console.print(test_output)
                elif config.verbose:
                    progress_bar.console.print(test_output)
                if invalid_quality_measures:
                    progress_bar.console.print(
                        "\n[red][bold][ERROR] One or more quality "
                        "measures raised an exception or returned an "
                        "invalid value.[/bold] The following quality "
                        "measures will not be recorded as part of this "
                        "test case execution:[/red]")
                    progress_bar.console.print(invalid_quality_measures)

        rich.print("Run complete.")
        return test_suite_run_metadata
