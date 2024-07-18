# Copyright 2023 Inductor, Inc.
"""Entrypoint for the Inductor CLI."""

import asyncio
import functools
import textwrap
from typing import Any, Callable, Dict, List, Optional
import pathlib
import re

import inquirer
import rich
from rich import console, syntax
import typer
# Note: we import Annotated from typing_extensions, rather than from typing,
# to enable compatibility with Python 3.8.
from typing_extensions import Annotated
import websockets
import yaml

from inductor import auth_session, config
from inductor.backend_client import backend_client, wire_model
from inductor.cli import questions
from inductor.data_model import data_model
from inductor.execution import playground_execution


app = typer.Typer()


def _create_test_suite_file(
    auth_access_token: str,
    default_vars: Optional[Dict[str, Any]] = None,):
    """Prompt user for test suite info to create a test suite file.

    1. Prompt user to create a new test suite or use an existing one.
    2. If creating a new test suite, prompt user for test suite info.
    3. If using an existing test suite, prompt user to select one.
    4. Create a test suite file with the provided info.
    
    Args:
        auth_access_token: Auth0 access token.
        default_vars: Optional dictionary containing default values for
            populating the test suite file.
    """
    if default_vars is None:
        default_vars = {}
    test_suite_args = default_vars

    create_new_test_suite: bool = questions.choose_new_test_suite()
    if create_new_test_suite:
        rich.print("Creating a new test suite file ...")
        has_llm_program_fqn = test_suite_args.get(
            "llm_program_fully_qualified_name") is not None
        question_total = 3 if has_llm_program_fqn else 4
        test_suite_file_path = questions.get_new_file_path(
            "test_suite.yaml",
            [".yml", ".yaml"],
            "test suite",
            prefix=f"1/{question_total}")
        test_suite_args["name"] = questions.get_test_suite_name(
            prefix=f"2/{question_total}")
        test_suite_args["description"] = questions.get_test_suite_description(
            prefix=f"3/{question_total}")

        if not has_llm_program_fqn:
            test_suite_args["llm_program_fully_qualified_name"] = (
                questions.get_llm_program_fully_qualified_name(
                    prefix=f"4/{question_total}"))

        test_suite_args["id"] = None

    else:
        # TODO: This `else` block is a placeholder until the backend is
        # implemented.
        # existing_test_suites = backend_client.get_existing_test_suites()
        # inquirer.list_input(
        #     "Select test suite to use", choices=existing_test_suites)
        # existing_test_suite_args = {}
        # test_suite_args["llm_program_fully_qualified_name"] = "module:object"
        # test_suite_args["id"] = "123"
        # test_suite_args = data_model.merge_test_suite_args(
        #     priority_1_dict=test_suite_args,
        #     priority_2_dict=existing_test_suite_args)
        # raise NotImplementedError("Use existing test suite not implemented.")
        rich.print("To use an existing test suite, run `inductor test "
                   "\[TEST_SUITE_FILE_PATH]`.")  # pylint: disable=anomalous-backslash-in-string
        raise typer.Exit()

    # Get parameter keys from LLM program to populate
    # the test suite file's test case section.
    llm_program = data_model.LazyCallable(
        test_suite_args["llm_program_fully_qualified_name"])
    llm_program_param_keys = llm_program.inputs_signature.keys()
    inputs = {}
    for key in llm_program_param_keys:
        inputs[key] = "<REPLACE WITH VALUE>"

    # Create test suite file contents.
    newline = "\n"
    yaml_string = textwrap.dedent(f"""
    # Test suite file

    # Test suite configuration
    - config:
        id: <WILL BE POPULATED AUTOMATICALLY>
        name: {test_suite_args["name"]}
        # description: {
            test_suite_args["description"]
            if test_suite_args["description"] is not None
            else ""}
        llm_program_fully_qualified_name: {
            test_suite_args["llm_program_fully_qualified_name"]}
        replicas: {
            test_suite_args.get("replicas", 1)
            if test_suite_args.get("replicas", 1) is not None
            else 1}
        
    # A test case (add more `- test:` blocks to add more test cases)
    - test:
        inputs:
          {yaml.dump(inputs, sort_keys=False).strip().replace(
            newline, newline + "          ")}
    
    # Sample quality measure (add more `- quality:` blocks to add more
    # quality measures)
    # - quality:
    #     name: <REPLACE WITH HUMAN-READABLE NAME FOR QUALITY MEASURE>
    #     evaluator: <REPLACE WITH "FUNCTION", "HUMAN", OR "LLM">
    #     evaluation_type: <REPLACE WITH "BINARY" OR "RATING_INT">
    #     # If evaluator is "FUNCTION", spec should be the fully qualified
    #     # name of your quality measure function (e.g., "my.module:my_function").
    #     # If evaluator is "HUMAN", spec should be the instruction or question
    #     # to be posed to a human evaluator. If evaluator is "LLM", spec should
    #     # be in the form of model and prompt (e.g. model: "gpt-3.5-turbo" and
    #     # prompt: "...") or the fully qualified name of an LLM program to be
    #     # used as the evaluator (e.g., "my.module:my_function").  Please see
    #     # the Inductor docs for more details.
    #     spec: <REPLACE WITH VALUE>

    # Sample hyperparameter specification (add more `- hparam:` blocks to add more
    # hyperparameters)
    # - hparam:
    #     name: <REPLACE WITH STRING-VALUED NAME FOR HYPERPARAMETER>
    #     type: <REPLACE WITH "SHORT_STRING", "TEXT", OR "NUMBER">
    #     values: <REPLACE WITH LIST OF VALUES FOR HYPERPARAMETER>
    """).lstrip()

    rich.print("\nTest suite file path:")
    rich.print(test_suite_file_path)
    rich.print("\nTest suite file contents:")
    yaml_string_with_syntax = syntax.Syntax(
        yaml_string, "yaml", theme="ansi_dark", line_numbers=True)
    rich_console = console.Console()
    rich_console.print(yaml_string_with_syntax)

    # Write the test suite file.
    confirm = inquirer.confirm(
        "Create test suite and write contents?",
        default=True)
    if confirm:
        # Create test suite on server if it does not already exist.
        if test_suite_args.get("id") is None:
            response = backend_client.create_test_suite(
                wire_model.CreateTestSuiteRequest(
                    name=test_suite_args["name"],
                    description=test_suite_args.get("description")),
                auth_access_token
            )
            test_suite_args["id"] = response.id
        rich.print("Test suite created.")
        # Replace the `id` field in the test suite file with the ID of the
        # test suite created on the server.
        yaml_string = yaml_string.replace(
            "<WILL BE POPULATED AUTOMATICALLY>", str(test_suite_args["id"]))

        # Write the test suite file.
        with open(test_suite_file_path, "w") as file:
            file.write(yaml_string)
        rich.print("Next, add test cases and quality measures to the file, "
                   "and run your test suite via `inductor test "
                   f"{test_suite_file_path}`")


@app.command("test")
def test(
    test_suite_file_paths: Annotated[
        Optional[List[pathlib.Path]],
        typer.Argument(help=(
            "One or more paths to test suites to run, separated by spaces.")
        )] = None,
    llm_program: Annotated[Optional[str], typer.Option(  # pylint: disable=unused-argument
        "-l",
        "--llm_program",
        help=(
            "Fully qualified name of the Python function representing "
            "this LLM program, in the format:"
            "`<fully qualified module name>:<fully qualified function name>` "
            "(e.g., `my.module:my_function`). <fully qualified module name> "
            "can be in the format: `path.to.module` or `path/to/module.py`."
    ))] = None,
    replicas: Annotated[Optional[int], typer.Option(  # pylint: disable=unused-argument
        "-r",
        "--replicas",
        help="Number of runs to execute for each test case in test suite(s)."
    )] = None,
    parallelize: Annotated[Optional[int], typer.Option(  # pylint: disable=unused-argument
        "-p",
        "--parallelize",
        help="Maximum number of test cases to run simultaneously in parallel."
    )] = None,
    # TODO: Add support for imports.
    # imports: Annotated[Optional[List[Path]], typer.Option(  # pylint: disable=unused-argument
    #     "-i",
    #     "--imports",
    #     help=("One or more paths to files containing additional test cases "
    #           "or quality measures to include in the test suite(s).")
    # )] = None,
    verbose: Annotated[Optional[bool], typer.Option(
        "-v",
        "--verbose",
        help="Print verbose output.",
    )] = False,
):
    """Run one or more Inductor test suites."""
    local_vars = locals()

    config.verbose = verbose

    # Every time the access token is requested from the session, it is
    # refreshed if it is expired.
    auth_access_token = auth_session.get_auth_session().access_token

    if not test_suite_file_paths:
        _create_test_suite_file(auth_access_token, local_vars)
        raise typer.Exit()

    try:
        test_suites = data_model.get_test_suites_via_cli_args(local_vars)
    except data_model.TestSuiteValueError as error:
        if error.path is not None:
            rich.print(
                f"[bold][red][ERROR][/bold] Error processing test suite file, "
                f"[/red][cyan italic]{error.path}[/cyan italic][red].[/red]"
                f"\n{error.message}"
            )
        else:
            rich.print(
                f"[bold][red][ERROR][/bold] Error processing test suite.[/red]"
                f"\n{error.message}"
            )
        raise typer.Exit()

    multiple_runs = len(test_suites) > 1

    for i, test_suite in enumerate(test_suites):

        if multiple_runs:
            rich.print(rich.rule.Rule(
                f"Test Suite {i+1} of {len(test_suite_file_paths)}",
                style="bold #ffffff"))

        test_suite._run(auth_access_token, prompt_open_results=True)  # pylint: disable=protected-access


def _create_meta_test_suite(
    test_suite_run_id: int,
    quality_measure: wire_model.QualityMeasureWithMetadata,
    llm_quality_measure: Optional[wire_model.QualityMeasure],
    meta_test_suite_name: str,
    meta_test_suite_file_path: pathlib.Path,
    llm_program_fqn: str,
    auth_access_token: str):
    """Create a new meta test suite, and its YAML file.

    Args:
        test_suite_run_id: ID of test suite run based upon which to create a new
            "meta" test suite for meta-evaluation of an LLM-powered quality
            measure.
        quality_measure: The quality measure whose values will serve as target
            values in the meta test suite's test cases.
        llm_quality_measure: The LLM-powered quality measure to be
            meta-evaluated.
        meta_test_suite_name: The name of the new meta test suite.
        meta_test_suite_file_path: The path to the new meta test suite file.
        llm_program_fqn: The fully qualified name of the LLM program
            representing the LLM-powered quality measure to be
            meta-evaluated by the new meta test suite.
        auth_access_token: Auth0 access token.
    """
    # Create test suite on server.
    response = backend_client.create_test_suite(
        wire_model.CreateTestSuiteRequest(name=meta_test_suite_name),
        auth_access_token)

    yaml_string = textwrap.dedent(f"""
    # Test suite file

    # Test suite configuration
    - config:
        id: {response.id}
        name: {meta_test_suite_name}
        llm_program_fully_qualified_name: {llm_program_fqn}
        # Dynamically import new "meta" test cases generated from the following test
        # suite run and quality measure. The new test cases' inputs are based on the
        # given quality measure's inputs (for the given test suite run), and the new
        # test cases' target values are based on the given quality measure's result
        # values (for the given test suite run).
        import:
            - meta_test_suite: "{test_suite_run_id}:{quality_measure.id}"
    """).lstrip()

    if llm_quality_measure is not None:
        yaml_string += "\n"
        yaml_string += textwrap.dedent(f"""
            # Quality measure evaluating if the output of the LLM program (representing
            # the LLM-powered quality measure, {llm_quality_measure.name}) is valid
            # for {llm_quality_measure.evaluation_type} evaluation.
            - quality:
                name: Valid output
                evaluator: FUNCTION
                evaluation_type: BINARY
                spec: inductor.quality:llm_qm_valid_output_{llm_quality_measure.evaluation_type.lower()}
        """).lstrip()

        yaml_string += "\n"
        yaml_string += textwrap.dedent(f"""
            # Quality measure evaluating if the output of the LLM program (representing
            # the LLM-powered quality measure, {llm_quality_measure.name}) is equal to
            # the result of the specified (human-powered) quality measure,
            # {quality_measure.name}, in the test suite run having ID {test_suite_run_id}.
            - quality:
                name: Exact agreement with {quality_measure.name}
                evaluator: FUNCTION
                evaluation_type: BINARY
                spec: inductor.quality:llm_qm_exact_agreement
        """).lstrip()

        if quality_measure.evaluation_type == "RATING_INT":
            yaml_string += "\n"
            yaml_string += textwrap.dedent(f"""
            # Quality measure evaluating if the output of the LLM program
            # (representing the LLM-powered quality measure,
            # {llm_quality_measure.name}) is within +/- 1 rating point of the
            # result value of the specified (human-powered) quality measure,
            # {quality_measure.name}, in the test suite run having ID {test_suite_run_id}.
            - quality:
                name: Plus-or-minus-one agreement with {quality_measure.name}
                evaluator: FUNCTION
                evaluation_type: BINARY
                spec: inductor.quality:llm_qm_plus_minus_one_agreement
            """).lstrip()

    # If ancestor directories do not exist, create them.
    meta_test_suite_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the test suite file.
    with open(meta_test_suite_file_path, "w") as file:
        file.write(yaml_string)


def _create_meta_llm_program_file(
    llm_program_fqn: str,
    llm_quality_measure_spec: Optional[Dict[str, str]] = None
):
    """Create a new LLM program file for testing an LLM quality measure.
    
    Args:
        llm_program_fqn: The fully qualified name of the LLM program to create.
        llm_quality_measure_spec: The spec of the LLM-powered quality measure.
    """
    llm_program_path, llm_program_function_name = llm_program_fqn.split(":")
    llm_program_path = llm_program_path.replace(".", "/")
    llm_program_path = pathlib.Path(f"{llm_program_path}.py")

    import_openai = (
        "import openai\n" if llm_quality_measure_spec is not None else "")

    python_string = f"""
        \"\"\"This file was automatically generated by Inductor. You can modify
        it as needed.\"\"\"

        from typing import Any, Dict

        import inductor
        {import_openai}

        def {llm_program_function_name}(
            llm_program_output: str,
            llm_program_inputs: Dict[str, Any]
        ) -> str:
            \"\"\"Evaluates the quality of an LLM program's output.

            Args:
                llm_program_output: Output of the LLM program.
                llm_program_inputs: Inputs to the LLM program.

            Returns:
                The value produced by this LLM-powered quality measure.
            \"\"\"
    """

    if llm_quality_measure_spec is not None:
        prompt = llm_quality_measure_spec["prompt"]
        prompt_lines = prompt.split("\n")
        prompt_lines = [
            line.replace("\"", "\\\"") for line in prompt_lines]
        prompt = "\n" + "\n".join(
            [f"                \"{line}\"" for line in prompt_lines])
        python_string += f"""
            client = openai.OpenAI()
            prompt = ({prompt})
            model = "{llm_quality_measure_spec["model"]}"

            execution = {{
                "output": llm_program_output,
                "inputs": llm_program_inputs
            }}
            chat_completion = client.chat.completions.create(
                messages=[
                    {{
                        "role": "system",
                        "content": prompt.format_map(execution)
                    }},
                ],
                model=model)
            return chat_completion.choices[0].message.content
        """
    else:
        python_string += (
            "        # Add code here "
            "to implement this LLM-powered quality measure\n")

    python_string = textwrap.dedent(python_string).lstrip()

    # If ancestor directories do not exist, create them.
    llm_program_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the LLM program file.
    with open(llm_program_path, "w") as file:
        file.write(python_string)


@app.command("create-meta-test-suite")
def create_meta_test_suite(
    meta_test_suite_spec: Annotated[str, typer.Argument(
        help="Specification of meta test suite to be used for "
        "evaluating an LLM-powered quality measure, in the "
        "format \"<test suite run ID>:<quality measure ID>\".  "
        "The specified (human-powered) quality measure's "
        "outputs (in the specified test suite run) will be used "
        "as target values within the new meta test suite."
    )],
    llm_quality_measure_id: Annotated[Optional[int], typer.Option(
        "-l",
        "--llm_quality_measure",
        help="ID of an LLM-powered quality measure (in the test suite "
             "run given by `meta_test_suite_spec`), from which a new LLM "
             "program will be created."
    )] = None,
    verbose: Annotated[Optional[bool], typer.Option(
        "-v",
        "--verbose",
        help="Print verbose output.",
    )] = False
):
    """Create a new test suite based on an existing test suite run in order to
    "meta-evaluate" an LLM-powered quality measure and ensure that it aligns
    with an existing human-powered quality measure.  Please see Inductor's docs
    for more information."""
    config.verbose = verbose

    auth_access_token = auth_session.get_auth_session().access_token

    # Validate and parse meta_test_suite_spec argument.
    try:
        if len(list(map(int, meta_test_suite_spec.split(":")))) != 2:
            raise ValueError
    except (TypeError, ValueError) as error:
        rich.print(
            "meta_test_suite_spec argument must be in the format "
            "<test suite run ID>:<quality measure ID>.")
        raise typer.Exit() from error
    test_suite_run_id, quality_measure_id = list(
        map(int, meta_test_suite_spec.split(":")))

    # Get specified quality measures
    quality_measure_ids_to_get = [quality_measure_id]
    if llm_quality_measure_id is not None:
        quality_measure_ids_to_get.append(llm_quality_measure_id)
    test_suite_run_quality_measures_response = (
        backend_client.get_test_suite_run_quality_measures(
            test_suite_run_id,
            wire_model.GetTestSuiteRunQualityMeasuresRequest(
                quality_measure_ids=quality_measure_ids_to_get),
            auth_access_token))
    quality_measure = (
        test_suite_run_quality_measures_response.quality_measures[0])
    llm_quality_measure = (
        test_suite_run_quality_measures_response.quality_measures[1]
        if llm_quality_measure_id is not None
        else None)

    if quality_measure is None:
        rich.print("Quality measure not found.")
        raise typer.Exit()

    # Remove all non-alphanumeric and non-underscore characters, replace
    # spaces with underscores, and convert all characters to lowercase.
    quality_measure_name_underscored = re.sub(
        r"[^a-zA-Z0-9_]", "", quality_measure.name.replace(" ", "_")).lower()

    new_meta_test_suite_name = questions.get_test_suite_name(
        quality_measure_name_underscored + "_meta_test_suite",
        "meta test suite")

    meta_test_suite_file_path = questions.get_new_file_path(
        "meta_test_suite.yaml",
        [".yml", ".yaml"],
        "meta test suite",)

    llm_program_fqn = None
    llm_quality_measure_spec = None

    if llm_quality_measure_id is not None:
        if llm_quality_measure is None:
            rich.print("LLM-powered quality measure not found.")
            raise typer.Exit()

        if llm_quality_measure.evaluator != "LLM":
            rich.print(
                "Quality measure specified by "
                "llm_quality_measure_id is not LLM-powered.")
            raise typer.Exit()

        if isinstance(llm_quality_measure.spec, str):
            llm_program_fqn = llm_quality_measure.spec
        else:
            llm_quality_measure_spec = llm_quality_measure.spec

    if llm_program_fqn is None:
        llm_program_fqn = questions.get_new_fully_qualified_name()

    # Write the test suite file and LLM program file.
    create_meta_llm_program_file = (
        llm_quality_measure is None or
        not isinstance(llm_quality_measure.spec, str))
    info = "\n[[yellow]?[/yellow]] Create meta test suite file"
    if create_meta_llm_program_file:
        info += " and LLM program file,"
    rich.print(info)
    confirm = inquirer.confirm("and write contents?", default=True)
    if confirm:
        if create_meta_llm_program_file:
            _create_meta_llm_program_file(
                llm_program_fqn,
                llm_quality_measure_spec)

        _create_meta_test_suite(
            test_suite_run_id,
            quality_measure,
            llm_quality_measure or wire_model.QualityMeasure(
                name=llm_program_fqn,
                evaluator="LLM",
                evaluation_type=quality_measure.evaluation_type,
                spec=llm_program_fqn),
            new_meta_test_suite_name,
            meta_test_suite_file_path,
            llm_program_fqn,
            auth_access_token)

        meta_test_suite_file_path = meta_test_suite_file_path.resolve()
        if create_meta_llm_program_file:
            rich.print("New LLM program for quality measure meta-evaluation "
                    f"created in [green]{llm_program_fqn}[/green].")
        rich.print("New test suite for quality measure meta-evaluation created "
                   f"in {meta_test_suite_file_path}.")
        rich.print("To run your meta test suite, execute the command `inductor "
                   f"test {meta_test_suite_file_path}`")


def _async_to_sync_decorator(func: Callable) -> Callable:
    """Decorator to enable calling an async function like a sync function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


@app.command("playground")
@_async_to_sync_decorator
async def playground(
    llm_program_fqn: Annotated[
        str,
        typer.Argument(help=(
            "Fully qualified name of the Python function representing your LLM "
            "program, in the format: "
            "`<fully qualified module name>:<fully qualified object name>` "
            "(e.g., `my.module:object`). <fully qualified module name> can be "
            "in the format: `path.to.module` or `path/to/module.py`."
        ))],
    verbose: Annotated[Optional[bool], typer.Option(
        "-v",
        "--verbose",
        help="Print verbose output.",
    )] = False,
):
    """Auto-generate a custom, shareable playground to interact with your LLM
    program."""
    config.verbose = verbose
    auth_access_token = auth_session.get_auth_session().access_token
    rich.print("Starting playground...")

    # Playground details is a shared dictionary between this function and
    # a `reload_llm_program_on_changes` task (see below), which may
    # update it.
    playground_details = {}

    llm_program = data_model.LazyCallable(llm_program_fqn)
    response = backend_client.get_playground(
        wire_model.GetPlaygroundRequest(
            llm_program_details=llm_program.get_program_details()),
        auth_access_token)
    playground_details.update(response.model_dump())
    playground_id = playground_details["playground_id"]
    llm_program_id = playground_details["llm_program_id"]

    # Reload the LLM program on changes. Any change to the LLM program
    # snapshot will result in the playground_details being updated.
    asyncio.create_task(data_model.reload_llm_program_on_changes(
        llm_program_fqn, playground_details))

    websocket_iterator = backend_client.get_playground_websocket_iterator(
        playground_id)

    rich.print("Playground running!")
    playground_url = (
        f"{config.settings.inductor_api_url}/playground/"
        f"{playground_id}")
    rich.print(
        f"Go to {playground_url} to use your playground - "
        "opening in your browser.")
    typer.launch(playground_url)
    rich.print("You can press Ctrl+c to shut down your playground anytime.")

    async for websocket in websocket_iterator:
        try:
            async for message in websocket:
                processed_message = (
                    wire_model.PlaygroundRequestAdapter.validate_json(message))

                # Access the playground details, since they may have been updated.
                assert playground_id == playground_details["playground_id"]
                assert llm_program_id == playground_details["llm_program_id"]
                llm_program_snapshot_id = playground_details["llm_program_snapshot_id"]

                if isinstance(processed_message,
                    wire_model.PlaygroundExecuteLlmProgramRequest):
                    response = playground_execution.execute_llm_program(
                        execution_request=processed_message,
                        llm_program_id=llm_program_id,
                        llm_program_snapshot_id=llm_program_snapshot_id,
                        llm_program_fqn=llm_program_fqn)
                elif isinstance(processed_message,
                                wire_model.PlaygroundExecuteTestSuiteRequest):
                    response = playground_execution.execute_test_suite(
                        execution_request=processed_message,
                        llm_program_fqn=llm_program_fqn,
                        # Refresh the access token if it has expired, since the
                        # playground could be long-lived.
                        auth_access_token=auth_session.get_auth_session().access_token)
                else:
                    raise ValueError(
                        f"Invalid message type: {type(processed_message)}")

                await websocket.send(response.model_dump_json())
        except websockets.ConnectionClosed:
            continue
