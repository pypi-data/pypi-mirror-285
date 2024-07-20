# Copyright 2023 Inductor, Inc.
"""Collection of Questions / User Prompts for the Inductor CLI.

This module is intended to include questions that require non-trivial
validation or other complex logic. It does not need to include simple
questions.
"""

import pathlib
import re
from typing import Any, Dict, List, Optional
import inquirer
import rich

from inductor.data_model import data_model


def get_new_file_path(
    default_path: str,
    accepted_extensions: List[str],
    param_name: str,
    prefix: Optional[str] = None
) -> pathlib.Path:
    """Prompt user for a path to a new file.

    Prompt the user to enter a path for a new file. Validate the path. If the
    path is valid, return it. If the path is invalid, continue prompting the
    user until a valid path is entered.

    Args:
        default_path: Default path to display to the user.
        accepted_extensions: List of accepted extensions for the path. The
            extensions should include the leading period (e.g. ".py").
        param_name: Name of the param to display to the user.
        prefix: Prefix to display to the user before the prompt. Displayed
            inside brackets.

    Returns:
        Path to the new file.
    """
    default_path: pathlib.Path = pathlib.Path(default_path)
    path = pathlib.Path(default_path)
    i = 1
    while path.exists():
        path = pathlib.Path(f"{default_path.stem}_{i}{default_path.suffix}")
        i += 1
        if i > 100:
            # If we've tried 100 times, something is wrong.
            # Use the initial default path.
            path = default_path
            break

    # TODO (https://github.com/inductor-hq/saas/issues/18): Add autocomplete
    # for paths.
    def validate_path(_: Dict[str, Any], current: str) -> bool:
        """Validate a given path.

        A path is valid if it:
        1. Has an accepted extension.
        2. Does not already exist.
        3. Can be touched.

        Given a path to a file, validate it. If the path is valid and gets
        created, delete it.

        Args:
            _: Dictionary containing the answers from previous questions
                (not including the current question). This will be an empty
                dictionary because the `file_path` question is not part of a
                collection of questions.
            current: The current answer, which is a path to validate.

        Raises:
            inquirer.errors.ValidationError: If the path is invalid.
        
        Returns:
            True if the path is valid, False otherwise.
        """
        try:
            path = pathlib.Path(current).resolve()
            if path.suffix not in accepted_extensions:
                # NOTE: This will also catch empty paths.
                raise inquirer.errors.ValidationError(
                    "",
                    reason=("File requires an extension in "
                            f"{accepted_extensions}."))

            # Permissions: rw-rw-rw- (0o666)
            path.touch(mode=0o666, exist_ok=False)
            if path.exists():
                path.unlink()
        except FileExistsError:
            raise inquirer.errors.ValidationError(  # pylint: disable=raise-missing-from
                "", reason="File already exists.")
        except PermissionError:
            raise inquirer.errors.ValidationError(  # pylint: disable=raise-missing-from
                "", reason="Missing permissions to create this file.")
        except FileNotFoundError:
            # The path specified by current does not exist.
            raise inquirer.errors.ValidationError(  # pylint: disable=raise-missing-from
                "", reason="Invalid path.")
        return True

    info = (f"Enter the file path for the new {param_name}, ensuring it has an "
            f"extension in {accepted_extensions} and does not already "
            "exist.")
    if prefix is not None:
        info = f"[[yellow]{prefix}[/yellow]] {info}"
    rich.print(f"\n{info}")
    new_file_path = inquirer.text(
        message=f"{param_name.capitalize()} file path",
        default=path,
        validate=validate_path)
    return pathlib.Path(new_file_path).resolve()


def get_test_suite_name(
    default_name: Optional[str] = None,
    param_name: Optional[str] = "test suite",
    prefix: Optional[str] = None
) -> str:
    """Prompt user for a test suite name.

    Prompt the user to enter a test suite name. Validate the name (see
    `validate_test_suite_name` function below). If the name is valid,
    return it. If the name is invalid, continue prompting the user until a
    valid name is entered.

    Args:
        default_name: Default test suite name to display to the user.
        param_name: Name of the test suite to display to the user.
        prefix: Prefix to display to the user before the prompt.  Displayed
            inside brackets.

    Returns:
        Test suite name.
    """
    def validate_test_suite_name(_: Dict[str, Any], current: str) -> bool:
        """Validate test suite name.

        A test suite name is valid if it:
        1. Is non-empty.
        2. Includes only alphanumeric characters, underscores, or dashes.

        Args:
            _: Dictionary containing the answers from previous questions
                (not including the current question). This will be an empty
                dictionary because the `test_suite_name` question is not
                part of a collection of questions.
            current: The current answer, which is a test suite name to
                validate.

        Returns:
            True if the test suite name is valid, False otherwise.
        
        Raises:
            inquirer.errors.ValidationError: If the test suite name is
                invalid.
        """
        name = current

        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise inquirer.errors.ValidationError(
                "", reason="Invalid test suite name.")
        return True

    info = (f"Enter a name for the new {param_name}, ensuring that it "
            "is non-empty and includes only alphanumeric characters, "
            "underscores, or dashes. Your test suites must have unique names.")
    if prefix is not None:
        info = f"[[yellow]{prefix}[/yellow]] {info}"
    rich.print(f"\n{info}")

    return inquirer.text(
        message=f"{param_name.capitalize()} name",
        default=default_name,
        validate=validate_test_suite_name)


def get_test_suite_description(prefix: Optional[str] = None) -> Optional[str]:
    """Prompt user for a test suite description.

    Args:
        prefix: Prefix to display to the user before the prompt. Displayed
            inside brackets.
    
    Returns:
        Test suite description, or None if the user skipped this question.
    """
    info = ("Optionally enter a description for the new test suite. Press "
            "enter to skip.")
    if prefix is not None:
        info = f"[[yellow]{prefix}[/yellow]] {info}"
    rich.print(f"\n{info}")

    description = inquirer.text(message="Test suite description")
    if not description:
        return None
    return description


def get_llm_program_fully_qualified_name(
    prefix: Optional[str] = None
) -> str:
    """Prompt user for a LLM program fully qualified name.

    Prompt the user to enter a LLM program fully qualified name. Validate the
    name (see `validate_llm_program` function below). If the name is valid,
    return it. If the name is invalid, continue prompting the user until a
    valid name is entered.

    Args:
        prefix: Prefix to display to the user before the prompt. Displayed
            inside brackets.

    Returns:
        LLM program fully qualified name.
    """
    def validate_llm_program(_: Dict[str, Any], current: str) -> bool:
        """Validate LLM program fully qualified name.

        A LLM program fully qualified name is valid if it:
        1. Is in the format <fully qualified module name>:<fully qualified
            object name>.
        2. Can instantiate a `data_model.LazyCallable` object.
        3. The instantiated object can import the underlying LLM program
            and get its parameter keys with `get_parameter_keys`.

        Args:
            _: Dictionary containing the answers from previous questions
                (not including the current question). This will be an empty
                dictionary because the `llm_program_fully_qualified_name`
                question is not part of a collection of questions.
            current: The current answer, which is a LLM program fully
                qualified name to validate.

        Returns:
            True if the LLM program fully qualified name is valid, False
            otherwise.

        Raises:
            inquirer.errors.ValidationError: If the LLM program fully
                qualified name is invalid.
        """
        try:
            if not re.match(r".+:.+", current):
                raise inquirer.errors.ValidationError(
                    "",
                    reason="Invalid format.")

            # A valid LLM program fully qualified name should be able to
            # instantiate a `data_model.LazyCallable` object, which will
            # attempt to access the underlying callable object of the LLM
            # program. If it is unable to do so, it will raise an exception.
            data_model.LazyCallable(current)
        except inquirer.errors.ValidationError as error:
            raise error
        except Exception as error:
            # It is not trival identify the relevant Exception subtypes that
            # should be considered actual validation errors, so we catch all
            # exceptions and raise a generic validation error with the
            # exception message appended. The issue with this method is that
            # the validation error message is limited to a single line. If
            # the exception message is too long, it will be truncated. In
            # testing, exception messages seem to be able to fit on a single
            # line, but this should be revisited if we are encountering
            # exceptions with long messages.
            raise inquirer.errors.ValidationError(  # pylint: disable=raise-missing-from
                "", reason=f"Invalid object: {str(error)}")
        return True

    info = ("Enter the fully qualified name (FQN) of the LLM program to test. "
            "The LLM program should be a Python function with a "
            "FQN in the format `path.to.python.module:function_name`. ")
    if prefix is not None:
        info = f"[[yellow]{prefix}[/yellow]] {info}"
    rich.print(f"\n{info}")

    return inquirer.text(
        message=("LLM program FQN"),
        validate=validate_llm_program)


def get_new_fully_qualified_name() -> str:
    """Prompt user to enter a new fully qualified name for an LLM program.

    Prompt the user to enter a fully qualified name. Validate the name (see
    `validate_fully_qualified_name` function below). If the name is valid,
    return it. If the name is invalid, continue prompting the user until a
    valid name is entered.

    Returns:
        Fully qualified name for a new LLM program.
    """
    def validate_fully_qualified_name(_: Dict[str, Any], current: str) -> bool:
        """Validate a fully qualified name.

        A fully qualified name is valid if it:
        1. Is in the format <fully qualified module name>:<fully qualified
            object name>.
        2. The file path for the specified module does not already exist.

        Args:
            _: Dictionary containing the answers from previous questions
                (not including the current question). This will be an empty
                dictionary because this question is not part of a collection
                of questions.
            current: The current answer, which is a fully qualified name to
                validate.
        
        Raises:
            inquirer.errors.ValidationError: If the fully qualified name is
                invalid.

        Returns:
            True if the fully qualified name is valid, False otherwise.
        """
        if not re.match(r"\A[^:]+:[^:]+\Z", current):
            raise inquirer.errors.ValidationError(
                "",
                reason="Invalid format.")
        module, _ = current.split(":")
        path_segments = module.split(".")
        path_segments[-1] = path_segments[-1] + ".py"
        path = pathlib.Path(*path_segments)
        if pathlib.Path(path).exists():
            raise inquirer.errors.ValidationError(
                "",
                reason="File already exists.")
        return True

    rich.print("\nEnter the fully qualified name (FQN) for the LLM program "
               "to be created. The FQN should be in the format "
               "\"path.to.python.module:function_name\".")
    return inquirer.text(
        message="LLM program FQN",
        validate=validate_fully_qualified_name)


def choose_new_test_suite() -> bool:
    """Prompt user to create a new test suite or use an existing one.

    Returns:
        True if the user wants to create a new test suite, False if the user
        wants to use an existing test suite.
    """
    create_new, use_existing = ("Create new", "Use existing")
    answer = inquirer.list_input(
        "Create new or use existing test suite?",
        choices=[create_new, use_existing])
    if answer == create_new:
        return True
    return False
