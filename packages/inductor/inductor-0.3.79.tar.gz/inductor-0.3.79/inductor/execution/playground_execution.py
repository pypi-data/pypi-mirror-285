# Copyright 2023 Inductor, Inc.
"""Functionality for playground execution tasks."""

import collections
from typing import Dict, List, Set, Union

import pydantic
import rich

from inductor import config
from inductor.backend_client import wire_model
from inductor.data_model import data_model
from inductor.execution import execution, test_suite_execution


def execute_llm_program(
    execution_request: wire_model.PlaygroundExecuteLlmProgramRequest,
    llm_program_id: str,
    llm_program_snapshot_id: str,
    llm_program_fqn: str,
) -> wire_model.PlaygroundExecuteLlmProgramResponse:
    """Execute a LLM program within a playground.
    
    Args:
        execution_request: PlaygroundExecuteLlmProgramRequest object.
        llm_program_id: LLM program ID.
        llm_program_snapshot_id: LLM program snapshot ID.
        llm_program_fqn: Fully qualified name of the LLM program.
    
    Returns:
        PlaygroundExecuteLlmProgramResponse object.
    """
    execution_results = []
    for execution_spec in execution_request.specs:
        test_case_inputs = execution_spec.inputs.copy()
        hparams = execution_spec.hparams

        # Create any inductor.ChatSession objects in the inputs.
        inputs_signature = data_model.LazyCallable(
            llm_program_fqn).inputs_signature
        for input_name, input_type in inputs_signature.items():
            if input_type == (
                "<class 'inductor.data_model.data_model.ChatSession'>"):
                if input_name in test_case_inputs:
                    test_case_inputs[input_name] = data_model.ChatSession(
                        **test_case_inputs[input_name])

        hparam_sets: Dict[str, Set[Union[str, int, float]]
            ] = collections.defaultdict(set)
        if hparams is not None:
            for hparam_name, hparam_value in hparams.items():
                hparam_sets[hparam_name].add(hparam_value)

        if config.verbose:
            rich.print(
                f"Executing LLM program: "
                f"{{'inputs': {test_case_inputs}, 'hparams': {hparams}}}")

        # Execute the LLM program with the given spec.
        test_case = data_model.TestCase(test_case_inputs)
        with execution.capture_default_hparams() as default_hparams:
            # Note: we use execute_test_case here as a convenience,
            # given that it provides the functionality that we require
            # for executing an LLM program (and despite the fact
            # that we are not in fact executing a test case here).
            execution_details, _, _ = (
                test_suite_execution.execute_test_case(
                    llm_program_fully_qualified_name=llm_program_fqn,
                    test_case=test_case,
                    hparams=hparams,
                    mode="PLAYGROUND",
                    suppress_stdout_stderr=False))
            # Add default_hparams to the hparam_sets.
            for hparam_name, hparam_values in default_hparams.items():
                hparam_sets[hparam_name].update(hparam_values)

        # Convert hparam_sets to hparam_specs.
        hparam_specs: List[wire_model.HparamSpec] = []
        for hparam_name, hparam_values in hparam_sets.items():
            # Only a single value for a given hparam needs to be
            # checked to determine the type, since if other values are
            # of a different type, a ValidationError will be raised.
            if isinstance(next(iter(hparam_values)), str):
                hparam_type = "TEXT"
            else:
                hparam_type = "NUMBER"

            try:
                hparam_specs.append(
                    wire_model.HparamSpec(
                        name=hparam_name,
                        type=hparam_type,
                        values=list(hparam_values)))
            except pydantic.ValidationError as error:
                rich.print(
                    f"[yellow bold][WARNING][/yellow bold] Hparam spec, "
                    f"[cyan italic]{hparam_name}[/cyan italic], "
                    f"has invalid values and its spec will not be "
                    f"updated in the playground UI. {error}")

        execution_results.append(
            wire_model.ExecutionDetailsWithPlaygroundMetadata(
                **execution_details.model_dump(),
                fingerprint=execution_spec.fingerprint,
                hparam_specs=hparam_specs,
                chat_metadata=execution_spec.chat_metadata))

    return wire_model.PlaygroundExecuteLlmProgramResponse(
        llm_program_id=llm_program_id,
        llm_program_snapshot_id=llm_program_snapshot_id,
        execution_details=execution_results)


def execute_test_suite(
    execution_request: wire_model.PlaygroundExecuteTestSuiteRequest,
    llm_program_fqn: str,
    auth_access_token: str,
) -> wire_model.PlaygroundExecuteTestSuiteResponse:
    """Execute a test suite, as triggered via a playground.
    
    Args:
        execution_request: PlaygroundExecuteTestSuiteRequest object.
        llm_program_fqn: Fully qualified name of the LLM program.
        auth_access_token: Auth0 access token.
    
    Returns:
        PlaygroundExecuteTestSuiteResponse object.
    """
    test_suite_id = execution_request.test_suite_id

    test_suite = data_model.TestSuite(
        id_or_name=test_suite_id,
        llm_program=llm_program_fqn)
    test_suite.import_test_cases(test_suite_id=test_suite_id)

    test_suite_run_metadata = test_suite._run(auth_access_token)  # pylint: disable=protected-access

    return wire_model.PlaygroundExecuteTestSuiteResponse(
        test_suite_run_id=test_suite_run_metadata.test_suite_run_id,
        fingerprint=execution_request.fingerprint)
