# Copyright 2023 Inductor, Inc.
"""Data abstractions and utilities for the Inductor client."""

import asyncio
import copy
import importlib
import inspect
import itertools
import json
import os
import pathlib
import re
import sys
import types
from typing import Any, Callable, Dict, List, Literal, Optional, Type, TypeVar, Union

import pydantic
import rich
import watchfiles
import yaml

from inductor import auth_session, config as inductor_config
from inductor.backend_client import backend_client, wire_model


class TestSuiteValueError(ValueError):
    """Error raised when a test suite is invalid.

    Attributes:
        message: Error message.
        path: Optional path to the test suite file that caused the error.
    """
    def __init__(self, message: str, path: Optional[str] = None):
        """Error raised when a test suite is invalid.

        Args:
            message: Error message.
            path: Optional path to the test suite file that caused the error.
        """
        self.message = message
        self.path = path
        # TODO: Add the line and line number from the test suite file that
        # caused the error, if applicable.
        super().__init__(self.message)


def _extract_fully_qualified_name(value: Any) -> Any:
    """Return the fully qualified name from a Callable, if applicable.
    
    Args:
        value: Object from which to extract the fully qualified name.
    
    Returns:
        The fully qualified name of the given object, if it is a Callable.
        Otherwise, the given object.
    """
    if callable(value):
        return f"{get_module_qualname(value)}:{value.__qualname__}"
    return value


class DataModel(pydantic.BaseModel):
    """Base class for data models to inherit from.

    This class configures the following settings:
    - strict: True (i.e., do not coerce values to the correct type)
        Ensures user understanding of expected data types and prevents
        unexpected behavior as a result of type coercion.
    - extra: "forbid" (i.e., do not allow extra fields to be passed
        to the model)
        Ensures user understanding of the expected fields and prevents
        field typos when the data model is constructed from YAML.
    - populate_by_name: True (i.e., fields can be populated by the name
        as given by the model attribute or the alias)

    This class overrides the default constructor to raise a
    `TestSuiteValueError` if a `pydantic.ValidationError` is raised when
    constructing the data model. This is done for consistency with other
    user-facing errors in the Inductor client and to provide additional
    context about the error.
    """
    model_config = pydantic.ConfigDict(
        strict=True, extra="forbid", populate_by_name=True)

    def __init__(self, **data: Any):
        try:
            super().__init__(**data)
        except pydantic.ValidationError as error:
            raise TestSuiteValueError(  # pylint: disable=raise-missing-from
                f"Please ensure that the data model is defined with the "
                f"correct types and syntax.\nError: {error}.")


# Type variable for the TestCase class.
_T_TestCase = TypeVar("_T_TestCase", bound="TestCase")  # pylint: disable=invalid-name


class TestCase(DataModel):
    """A test case.

    Attributes:
        inputs: Mapping from input parameter name to input value.
        output: Optionally, an example of a desired high-quality output, or
            the output that is to be considered correct, for this test case.
        description: Optionally, a description of this test case.
    """
    inputs: Dict[str, Any]
    output: Optional[Any] = None
    description: Optional[str] = None

    # Define a custom constructor to enable taking `inputs` as a positional,
    # rather than keyword-only, argument.
    def __init__(
        self,
        inputs: Dict[str, Any],
        *,
        output: Optional[Any] = None,
        description: Optional[str] = None,
        **kwargs: Any):
        """Constructs a new test case.

        Args:
            inputs: Mapping from input parameter name to input value.
            output: Optionally, an example of a desired high-quality output, or
                the output that is to be considered correct, for this test case.
            description: Optionally, a description of this test case.
            **kwargs: Additional keyword arguments to be passed to superclass
                constructor.
        """
        super().__init__(
            inputs=inputs, output=output, description=description, **kwargs)

    @classmethod
    def _from_test_suite_file_syntax(
        cls: _T_TestCase,
        params: Dict[str, Union[str, Dict[str, str]]]) -> _T_TestCase:
        """Constructs a new test case using the test suite file syntax.

        Test cases defined in a test suite file can either use the `inputs`
        keyword to specify the inputs, or all the keyword arguments will be
        treated as inputs.

        Args:
            cls: Test case class.
            params: Parameters to construct the test case.

        Returns:
            A new test case.
        
        Raises:
            TestSuiteValueError: If the test case cannot be constructed from
                the given keyword arguments.
        """
        try:
            if "inputs" not in params:
                return cls(inputs=params)
            return cls(**params)
        except TypeError as error:
            raise TestSuiteValueError(
                f"Incorrect syntax for test case: {error}."
                f"\n[yellow]Test case parameters defined in test suite file:"
                f"[/yellow] {params}") from error

    def _validate_inputs_with_signature(
        self, inputs_signature: inspect.Signature):
        """Validate that the inputs are compatible with the given signature.

        Args:
            inputs_signature: Inputs signature to validate against.

        Raises:
            TestSuiteValueError: If the inputs are not compatible with the
                signature.
        """
        try:
            inputs_signature.bind(**self.inputs)
        except TypeError as error:
            raise TestSuiteValueError(
                f"Test case inputs cannot be bound to the LLM program "
                f"signature: {error}."
                f"\n[yellow]Test case inputs:[/yellow] "
                f"{self.inputs}"
                f"\n[yellow]LLM program signature:[/yellow] "
                f"{inputs_signature}") from error


class TestCaseWithMetadata(TestCase):
    """A test case with metadata.
    
    Attributes:
        id: ID of this test case.
    """
    id: int


# Type variable for the QualityMeasure class.
_T_QualityMeasure = TypeVar("_T_QualityMeasure", bound="QualityMeasure")  # pylint: disable=invalid-name


class QualityMeasure(DataModel):
    """A quality measure.
    
    Attributes:
        name: Human-readable name of this quality measure.
        evaluator: Evaluator for this quality measure.  Determines whether
            this quality measure will be evaluated by running a function,
            via human inspection, or via an LLM.
        evaluation_type: The type of value produced by evaluation of this
            quality measure.
        spec: Specification of the details of how to execute this quality
            measure.
            - If evaluator is "FUNCTION", then spec should give the fully
            qualified name of the function (in the format
            "my.module:my_function").
            - If evaluator is "HUMAN", then spec should give the instructions
            or question that should be displayed to human evaluators.
            - If evaluator is "LLM", then spec should either give a dictionary
            with "model" and "prompt" fields, or the fully qualified name of an
            LLM program that implements the quality measure (in the format
            "my.module:my_function").
    """
    name: str
    evaluator: Literal["FUNCTION", "HUMAN", "LLM"]
    evaluation_type: Literal["BINARY", "RATING_INT"]
    spec: Union[str, Dict[str, str]]

    @pydantic.field_validator("spec", mode="before")
    @classmethod
    def _extract_fully_qualified_spec_name(
        cls: _T_QualityMeasure, v: Any) -> Any:
        """Return the fully qualified name from the spec, if applicable."""
        return _extract_fully_qualified_name(v)


class QualityMeasureWithMetadata(QualityMeasure):
    """A quality measure with metadata.

    Attributes:
        id: ID of this quality measure.
    """
    id: int


# Type variable for the HparamSpec class.
_T_HparamSpec = TypeVar("_T_HparamSpec", bound="HparamSpec")  # pylint: disable=invalid-name


class HparamSpec(DataModel):
    """Specification of a set of hyperparameter values.

    Attributes:
        name: Name of hyperparameter.
        type: Type of hyperparameter.
        values: List of hyperparameter values.
    """
    name: str = pydantic.Field(alias="hparam_name")
    type: Literal["SHORT_STRING", "TEXT", "NUMBER"] = pydantic.Field(
        alias="hparam_type")
    values: Union[List[str], List[int], List[float]]

    @pydantic.model_validator(mode="before")
    @classmethod
    def _check_values_type(cls: _T_HparamSpec, data: Any) -> Any:
        """Ensure that the given values and type are aligned."""
        return wire_model.check_hparam_values_type(data)


# Type variable for the TestSuiteImportSpec class.
_T_TestSuiteImportSpec = TypeVar(  # pylint: disable=invalid-name
    "_T_TestSuiteImportSpec", bound="TestSuiteImportSpec")


class TestSuiteImportSpec(DataModel):
    """Specification for importing test suite components.
    
    Exactly one of test_suite_id or meta_test_suite should be non-None.
    
    Attributes:
        test_suite_id: ID of a test suite from which to import test cases.
        meta_test_suite: Meta test suite specification in the format
            "<test_suite_run_id>:<quality_measure_id>".
    """
    test_suite_id: Optional[int] = None
    meta_test_suite: Optional[str] = None

    @pydantic.model_validator(mode="after")
    def check_test_suite_id_xor_meta_test_suite(self) -> "TestSuiteImportSpec":
        """Ensure that either test_suite_id or meta_test_suite is specified.
        
        Returns:
            self
        """
        if (self.test_suite_id is None) == (self.meta_test_suite is None):
            raise ValueError(
                "Exactly one of test_suite_id or meta_test_suite must be "
                "specified.")
        return self

    @pydantic.field_validator("meta_test_suite", mode="after")
    @classmethod
    def _validate_meta_test_suite(
        cls: _T_TestSuiteImportSpec, v: Optional[str]) -> Optional[str]:
        """Validate the meta_test_suite field.
        
        Args:
            cls: The TestSuiteImportSpec class.
            v: The meta_test_suite value to be validated.
            
        Raises:
            ValueError if v does not adhere to the required format (per
            attribute description in class docstring above).
            
        Returns:
            v
        """
        if v is not None:
            try:
                if len(list(map(int, v.split(":")))) != 2:
                    raise ValueError
            except (TypeError, ValueError) as error:
                raise ValueError(
                    "meta_test_suite must be in the format "
                    "<test_suite_run_id>:<quality_measure_id>.") from error
        return v


# Type variable for the Config class.
_T_Config = TypeVar("_T_Config", bound="Config")  # pylint: disable=invalid-name


class Config(DataModel):
    """Config for a test suite.

    Attributes:
        id: ID of test suite.
        name: Name of test suite.
        llm_program: Fully qualified name of LLM program.
        replicas: Number of times that LLM program will be run on each pair of
            (test case, set of hyperparameters).
        parallelize: Degree of parallelism used when running the LLM program.
        autolog: Whether to automatically log select function calls that occur
            during the execution of the LLM program.
        imports: Specifications of test suites to import into the test suite
            containing this Config.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    llm_program: str = pydantic.Field(alias="llm_program_fully_qualified_name")
    replicas: int = 1
    parallelize: int = 1
    autolog: bool = True
    imports: Optional[List[TestSuiteImportSpec]] = pydantic.Field(
        default=None,
        alias="import")

    @pydantic.model_validator(mode="after")
    def _check_id_and_name(self):
        """Ensure that either id or name is specified.
        
        Raises:
            TestSuiteValueError: If neither id nor name is specified.
        """
        if self.id is None and self.name is None:
            raise TestSuiteValueError("Either id or name must be specified.")
        return self

    @pydantic.field_validator("llm_program", mode="before")
    @classmethod
    def _extract_fully_qualified_llm_program_name(
        cls: _T_Config, v: Any) -> Any:
        """Return the fully qualified name for the program, if applicable."""
        return _extract_fully_qualified_name(v)


# A YAML file path is either a string or a path-like object.
YAMLFilePath = Union[str, os.PathLike]


def _get_components_from_file(
    path: YAMLFilePath
) -> Dict[
    str,
    Union[List[TestCase], List[QualityMeasure], List[HparamSpec], Config]]:
    """Return a dictionary of test suite components from a YAML file.
    
    Args:
        path: Path to the YAML file.
    
    Returns:
        Dictionary of test suite components, with keys:
        - test_cases: List of test cases.
        - quality_measures: List of quality measures.
        - hparam_specs: List of hyperparameter specifications.
        - config: Test suite config.
    """
    with open(path, "r", encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)

    is_list_of_dicts = (
        isinstance(yaml_content, list) and
        all(isinstance(entry, dict) for entry in yaml_content))
    if not is_list_of_dicts:
        raise TestSuiteValueError(
            "Test suite file must contain a list/sequence of "
            "dictionaries/maps.")

    test_cases = []
    quality_measures = []
    hparam_specs = []
    config = None

    for entry in yaml_content:
        for key, value in entry.items():
            if key in ["test", "test case", "test_case"]:
                test_cases.append(
                    TestCase._from_test_suite_file_syntax(value))  # pylint: disable=protected-access
            elif key in [
                "quality",
                "quality measure",
                "quality_measure",
                "measure"]:
                quality_measures.append(QualityMeasure(**value))
            elif key in ["hparam", "hparam spec", "hparam_spec"]:
                hparam_specs.append(HparamSpec(**value))
            elif key in ["config", "configuration"]:
                if config is not None:
                    raise TestSuiteValueError(
                        "Test suite file must contain at most one config "
                        "block.")
                config = Config(**value)
            else:
                raise TestSuiteValueError(
                    f"Invalid entry in test suite file: {key}",
                    path)

    return {
        "test_cases": test_cases,
        "quality_measures": quality_measures,
        "hparam_specs": hparam_specs,
        "config": config,
    }


# Test suite components are classes that can be added to a test suite
# (e.g., test cases, quality measures, and hyperparameter specifications)
# or files that contain test suite components (e.g., paths to YAML files).
_TestSuiteComponent = Union[
    Config, TestCase, QualityMeasure, HparamSpec, YAMLFilePath]


def get_test_suite_components(
    *args: Union[_TestSuiteComponent, List[_TestSuiteComponent]]
) -> Dict[
    str,
    Union[List[TestCase], List[QualityMeasure], List[HparamSpec], Config]]:
    """Return a dictionary of test suite components.

    Args:
        *args: One or more test cases, quality measures, hyperparameter
            specifications, paths to YAML files containing test suite
            components, or lists thereof. A config object can also be passed
            in the same way as the other components, but if more than one
            config object is found, a TestSuiteValueError is raised.

    Returns:
        Dictionary of test suite components, with keys:
        - test_cases: List of test cases.
        - quality_measures: List of quality measures.
        - hparam_specs: List of hyperparameter specifications.
        - config: Test suite config.
    
    Raises:
        TypeError: If an invalid type is passed.
        TestSuiteValueError: If more than one config block is found.
    """
    test_cases = []
    quality_measures = []
    hparam_specs = []
    config = None

    def add(arg: Union[_TestSuiteComponent, List[_TestSuiteComponent]]):
        nonlocal config
        if isinstance(arg, list):
            for item in arg:
                add(item)
        elif isinstance(arg, TestCase):
            test_cases.append(arg)
        elif isinstance(arg, QualityMeasure):
            quality_measures.append(arg)
        elif isinstance(arg, HparamSpec):
            hparam_specs.append(arg)
        elif isinstance(arg, Config):
            if config is not None:
                raise TestSuiteValueError(
                    "Test suite must contain at most one config block.")
            config = arg
        elif isinstance(arg, (str, os.PathLike)):
            add(list(_get_components_from_file(arg).values()))
        else:
            raise TypeError(
                "Invalid type. Expected TestCase, QualityMeasure, "
                f"HparamSpec, Config, or path to yaml file, but got "
                f"{type(arg)}.")

    for arg in args:
        add(arg)

    return {
        "test_cases": test_cases,
        "quality_measures": quality_measures,
        "hparam_specs": hparam_specs,
        "config": config,
    }


def _get_hparams_combinations(
    hparam_specs: Optional[List[HparamSpec]] = None
) -> List[Dict[str, Union[str, int, float]]]:
    """Get all combinations of hyperparameters.

    Given a list of hyperparameters and their possible values, return a list
    of dictionaries, where each dictionary represents a unique combination
    of hyperparameters.

    For example, if the given hyperparameters are:
    [
        data_model.HparamSpec(
            hparam_name="a",
            values=[1, 2],
        ),
        data_model.HparamSpec(
            hparam_name="b",
            values=[3, 4],
        ),
    ]
    then the returned list will be:
    [
        {"a": 1, "b": 3},
        {"a": 1, "b": 4},
        {"a": 2, "b": 3},
        {"a": 2, "b": 4},
    ]

    Args:
        hparam_specs: List of hyperparameters specs, where all
            hyperparameter specs have distinct names.

    Returns:
        A list of dictionaries, where each dictionary represents a unique
            combination of hyperparameters.

    Raises:
        ValueError: If hyperparameter names are not distinct.
    """
    if hparam_specs is None:
        return [{}]

    # Convert list of HparamSpec to dictionary
    hparams_dict = {
        hparam.name: hparam.values for hparam in hparam_specs}

    # Ensure that all hyperparameter names in hparam_specs are distinct.
    if len(hparams_dict) != len(hparam_specs):
        raise ValueError(
            "Hyperparameter names in hparam_specs must be distinct.")

    keys = list(hparams_dict.keys())
    value_lists = [hparams_dict[key] for key in keys]

    # Generate combinations.
    value_combinations = list(itertools.product(*value_lists))

    # Convert to dictionaries.
    hparam_combinations = []
    for value_combination in value_combinations:
        hparam_combinations.append(dict(zip(keys, value_combination)))

    return hparam_combinations


class QualityMeasureResultSummary(DataModel):
    """Summary of results for a quality measure within a test suite run.
    
    Attributes:
        num_evals: Number of evaluations of this quality measure within the
            test suite run.
        average_value: The average value of the quality measure within the
            the test suite run (for BINARY quality measures, True is mapped to
            1 and False is mapped to 0 in order to compute average values),
            if the run's results include any evaluations of the quality measure.
            Should be None if the run's results do not include any evaluations
            of the quality measure.
    """
    num_evals: int
    average_value: Optional[float] = None


class TestSuiteRunResults:
    """Results of a test suite run."""

    def __init__(self, test_suite_run_id: int, auth_access_token: str):
        """Constructs a new TestSuiteRunResults instance.

        Retrieves results for test suite run having given test_suite_run_id,
        and populates this instance.

        Args:
            test_suite_run_id: ID of test suite run for which to retrieve
                results.
            auth_access_token: Auth0 access token (used to retrieve results
                from server).
        """
        self._test_suite_run_id = test_suite_run_id
        self._retrieve_results(auth_access_token)

    def _retrieve_results(self, auth_access_token: str):
        """Retrieves results for test suite run and populates instance fields.

        Specifically, retrieves results for run having test suite run ID given
        by self._test_suite_run_id.
        
        Args:
            auth_access_token: Auth0 access token (used to retrieve results
                from server).
        """
        response = backend_client.get_test_suite_run_results(
            self._test_suite_run_id, auth_access_token)
        self._quality_measures = [
            QualityMeasureWithMetadata(
                id=quality_measure.id,
                name=quality_measure.name,
                evaluator=quality_measure.evaluator,
                evaluation_type=quality_measure.evaluation_type,
                spec=quality_measure.spec)
            for quality_measure in response.quality_measures
        ]
        self._quality_measure_result_summaries = {
            qm_id: QualityMeasureResultSummary(
                num_evals=summary.num_evals,
                average_value=summary.average_value)
            for qm_id, summary
            in response.quality_measure_result_summaries.items()
        }

    @property
    def test_suite_run_id(self) -> int:
        """ID of test suite run."""
        return self._test_suite_run_id

    @property
    def quality_measures(self) -> List[QualityMeasureWithMetadata]:
        """List of quality measures included in the test suite run."""
        return self._quality_measures

    @property
    def quality_measure_result_summaries(self) -> Dict[
        int, QualityMeasureResultSummary]:
        """Mapping from quality measure ID to result summary for that measure.
        
        Each result summary includes an average_value field giving the average
        value of the quality measure within the test suite run (for BINARY
        quality measures, True is mapped to 1 and False is mapped to 0 in order
        to compute average values), or None if the run's results do not (yet)
        include any evaluations of the quality measure.
        """
        return self._quality_measure_result_summaries


class TestSuite:
    """Test suite.
    
    A collection of test cases, quality measures, and hyperparameter
    specifications that can be run together.
    
    Attributes:
        config: Config for this test suite.
        test_cases: List of test cases to run.
        quality_measures: List of quality measures to compute.
        hparam_specs: List of hyperparameter specifications.
    """
    def __init__(
        self,
        id_or_name: Union[int, str],
        llm_program: Union[Callable, str]):
        """Create a test suite.
        
        Args:
            id_or_name: ID or name of the test suite.
            llm_program: LLM program to test. Either a Python function
                or a string containing the fully qualified name of the Python
                function. If a string is passed, it must be in the
                format:
                `<fully qualified module name>:<fully qualified function name>`
                (e.g., `my.module:my_function`). `<fully qualified module name>`
                can be in the format: `path.to.module` or `path/to/module.py`.
        """
        id, name = None, None  # pylint: disable=redefined-builtin
        if isinstance(id_or_name, int):
            id = id_or_name
        elif isinstance(id_or_name, str):
            name = id_or_name
            if not re.match(r"\A[a-zA-Z0-9_-]+\Z", name):
                raise ValueError(
                    "Test suite names must contain only alphanumeric "
                    "characters, dashes, or underscores "
                    f"(you attempted to create a test suite named \"{name}\").")
        else:
            raise TypeError(
                "Invalid type for id_or_name. Expected int or str, "
                f"but got {type(id_or_name)}.")

        self.config = Config(
            id=id,
            name=name,
            llm_program=llm_program)
        self.test_cases: List[TestCase] = []
        self.quality_measures: List[QualityMeasure] = []
        self.hparam_specs: List[HparamSpec] = []
        self.hparam_combinations: List[Dict[str, Union[str, int, float]]] = [{}]

        self._auth_session = auth_session.get_auth_session()

    def add(
        self,
        *args: Union[_TestSuiteComponent, List[_TestSuiteComponent]]):
        """Add test cases, quality measures, or hyperparameter specifications.

        Args:
            *args: One or more test cases, quality measures, hyperparameter
                specifications, or path to a YAML file containing test suite
                components to add to the test suite. If a list is passed,
                each item in the list is added to the test suite. Any Config
                objects passed are ignored.
        
        Raises:
            TypeError: If an invalid type is passed.
        """
        components = get_test_suite_components(*args)
        self.test_cases.extend(components["test_cases"])
        self.quality_measures.extend(components["quality_measures"])
        self.hparam_specs.extend(components["hparam_specs"])
        if components["hparam_specs"]:
            self.hparam_combinations = _get_hparams_combinations(
                self.hparam_specs)


    def import_test_cases(
        self,
        test_suite_id: Optional[int] = None,
        *,
        meta_test_suite: Optional[str] = None
    ):
        """Import test cases from another test suite.

        Stores the details of the import in this test suite's config. Only when
        this test suite is run will the test cases from the specified test suite
        be retrieved and included in the test suite run.
        
        Exactly one of test_suite_id or meta_test_suite must be non-None.
        
        Args:
            test_suite_id: ID of a test suite from which to import test cases.
            meta_test_suite: Meta test suite specification in the format
                "<test_suite_run_id>:<quality_measure_id>".
        """
        new_import_spec = TestSuiteImportSpec(
            test_suite_id=test_suite_id,
            meta_test_suite=meta_test_suite)

        if self.config.imports is None:
            self.config.imports = [new_import_spec]
        else:
            self.config.imports.append(new_import_spec)

    def _validate(self):
        """Validate the test suite.
        
        Perform the following checks to ensure that the test suite is valid:
        - LLM program is callable.
        - Test cases inputs can be bound to the LLM program signature.

        Raises:
            TestSuiteValueError: If the test suite is invalid.
        """
        # Check that the LLM program is callable.
        llm_program = self.config.llm_program
        try:
            llm_program_callable = LazyCallable(
                llm_program).get_callable()
        except Exception as error:
            # It is not trival identify the relevant Exception subtypes that
            # should be considered actual validation errors, so we catch all
            # exceptions and raise a generic validation error with the
            # exception message appended.
            raise TestSuiteValueError(
                f"LLM program {llm_program} is not callable. "
                f"{error}") from error

        # Check that the test cases inputs can be bound to the LLM program
        # signature.
        # TODO(#323): Include validation for LangChain objects.
        if inspect.isfunction(llm_program_callable):
            llm_program_signature = inspect.signature(llm_program_callable)
            for test_case in self.test_cases:
                test_case._validate_inputs_with_signature(llm_program_signature)  # pylint: disable=protected-access

        # TODO: https://github.com/inductor-hq/saas/issues/324 - Remove any
        # duplicate test suite components.

    def run(
        self,
        *,
        replicas: Optional[int] = None,
        parallelize: Optional[int] = None,
        return_results: bool = False) -> Optional[TestSuiteRunResults]:
        """Run the test suite.

        Args:
            replicas: Number of replicated executions to perform for each
                (test case, unique set of hyperparameter values) pair. Defaults
                to 1.
            parallelize: Number of LLM program executions to run in parallel.
                Defaults to 1.
            return_results: If True, then this function will return the results
                of this test suite run as of completion of the run's execution.
        
        Returns:
            None if the return_results argument is False (default), or the
            results of this test suite run (as of completion of the run's
            execution) if return_results is True.
        """
        auth_access_token = self._auth_session.access_token

        if replicas is None and parallelize is None:
            response = self._run(auth_access_token)
        else:
            # Test suites are run using the settings in their own config. In
            # order to functionally modify the config for only this run, we
            # create a shallow copy of the test suite and its config.
            test_suite_to_run = copy.copy(self)
            test_suite_to_run.config = copy.copy(self.config)
            if replicas is not None:
                test_suite_to_run.config.replicas = replicas
            if parallelize is not None:
                test_suite_to_run.config.parallelize = parallelize

            response = test_suite_to_run._run(auth_access_token)  # pylint: disable=protected-access

        if return_results:
            return TestSuiteRunResults(
                response.test_suite_run_id, self._auth_session.access_token)
        return None

    def _run(
        self,
        auth_access_token: str,
        *,
        prompt_open_results: bool = False
    ) -> wire_model.CreateTestSuiteRunResponse:
        """Run the test suite using its current config.
        
        Args:
            auth_access_token: Access token for authentication.
            prompt_open_results: Whether to prompt the user to open the
                results in the browser.
        
        Returns:
            CreateTestSuiteRunResponse object, containing test suite run
            metadata.
        """
        self._validate()
        # Import here to avoid circular imports.
        from inductor.execution.test_suite_execution import execute_test_suite  # pylint: disable=import-outside-toplevel
        return execute_test_suite(
            test_suite=self,
            auth_access_token=auth_access_token,
            prompt_open_results=prompt_open_results)

    def _get_run_request(self) -> wire_model.CreateTestSuiteRunRequest:
        """Return a CreateTestSuiteRunRequest for this test suite.
        
        Returns:
            A CreateTestSuiteRunRequest for this test suite.
        """
        return wire_model.CreateTestSuiteRunRequest(
            test_suite_id_or_name=(
                self.config.id or self.config.name),
            test_cases=[
                test_case.model_dump()
                for test_case in self.test_cases],
            quality_measures=[
                quality_measure.model_dump()
                for quality_measure in self.quality_measures],
            hparam_specs=[
                hparam_spec.model_dump()
                for hparam_spec in self.hparam_specs],
            llm_program_details=LazyCallable(
                self.config.llm_program).get_program_details(),
            replicas=self.config.replicas,
            parallelize=self.config.parallelize,
            test_suite_import_specs=[
                import_spec.model_dump()
                for import_spec in self.config.imports or []] or None,
            num_executions=(len(self.hparam_combinations) *
                            len(self.test_cases) *
                            self.config.replicas)
        )


def get_test_suites_via_cli_args(cli_args: Dict[str, Any]) -> List[TestSuite]:
    """Return a list of test suites.

    Parse the relevant arguments from the given command line arguments.
    Use a combination of the command line arguments and the test suite file
    contents (where the test suite file is specified by the required
    `test_suite_file_paths` command line argument) to construct the test
    suites. The config for each test suite is constructed based on the
    following hierarchy of configuration sources:
    1. Command line arguments.
    2. Test suite file arguments.
    3. Default arguments.
    In the case of a conflict, the lower-numbered item in the list takes
    precedence.
    
    Args:
        cli_args: Dictionary of command line arguments. Note that not all the
            command line arguments are used in this function.

    Returns:
        A list of `TestSuite` objects.

    Raises:
        TestSuiteValueError: If any test suite is invalid.
    """
    test_suite_file_paths = cli_args.get("test_suite_file_paths")
    if test_suite_file_paths is None:
        raise ValueError("`test_suite_file_paths` must be defined.")

    test_suites = []
    for test_suite_file_path in test_suite_file_paths:
        try:
            # Get the test suite components from the test suite file.
            test_suite_components = _get_components_from_file(
                test_suite_file_path)
            test_suite_config: Optional[Config] = test_suite_components[
                "config"]
            if test_suite_config is None:
                raise TestSuiteValueError(
                    "Test suite file must contain a config.")

            # Update the test suite config with the command line arguments.
            for key, value in cli_args.items():
                if key in Config.model_fields and value is not None:
                    setattr(test_suite_config, key, value)

            # Create the test suite.
            test_suite = TestSuite(
                id_or_name=test_suite_config.id or test_suite_config.name,
                llm_program=test_suite_config.llm_program)
            test_suite.config = test_suite_config
            test_suite.add(list(test_suite_components.values()))
            test_suites.append(test_suite)

        except TestSuiteValueError as error:
            # Add details about the source of the error.
            error.path = test_suite_file_path
            raise error

    return test_suites


def components_with_ids(
    components: List[Union[TestCase, QualityMeasure]],
    ids: List[int],
    component_with_id_type: Union[
        Type[TestCaseWithMetadata], Type[QualityMeasureWithMetadata]]
) -> List[Union[TestCaseWithMetadata, QualityMeasureWithMetadata]]:
    """Returns components with their IDs.

    Args:
        components: List of components.
        ids: List of IDs in the same order as the components. (i.e.,
            `ids[i]` is the ID of `components[i]`.) The length of `ids` must
            match the length of `components`.
        component_with_id_type: Class that extends the component type with
            an `id` attribute.

    Returns:
        List of components with their IDs.
    
    Raises:
        ValueError: If the number of components does not match the number of
            IDs.
    """
    if len(components) != len(ids):
        raise ValueError(
            "Number of components does not match number of IDs.")
    return [
        component_with_id_type(
            id=component_id,
            **component.model_dump())
        for component_id, component in zip(ids, components)
    ]


def in_google_colab() -> bool:
    """Return True if currently running in Google Colab, and False otherwise."""
    try:
        import google.colab  # pylint: disable=import-outside-toplevel,unused-import
        return True
    except ImportError:
        return False


def get_module_qualname(f: Callable) -> str:
    """Return the fully qualified name of the module in which f is defined.

    Args:
        f: A function, class, or method.

    Returns:
        The fully qualified name of the module in which f is defined. If f is
        defined in the __main__ module, then the name of the file containing f
        (without its ".py" extension) is returned as the fully qualified module
        name. If f is defined in a Google Colab notebook, then "google_colab" is
        returned as the fully qualified module name.

    Raises:
        RuntimeError if f is defined in the __main__ module, the current
        environment is not Google Colab, and the name of the file
        containing f does not end with ".py".
    """
    qualname = f.__module__
    if qualname == "__main__":
        # Special case for Google Colab.
        if in_google_colab():
            return "google_colab"

        qualname, ext = os.path.splitext(
            os.path.basename(f.__globals__["__file__"]))
        if ext != ".py":
            raise RuntimeError(
                f"f ({f.__qualname__}) is defined in the __main__ module but "
                f"is contained in a file ({f.__globals__['__file__']}) that "
                "does not have extension '.py'.")
    return qualname


def deepcopy_or_str(value: Any) -> Any:
    """Return a deep copy of the given value or a string representation of it.

    If the value is not deep copyable or not JSON serializable, it will be
    converted to a string. Otherwise, a deep copy of the value will be returned.

    Args:
        value: Value to deep copy or convert to a string.
    
    Returns:
        Deep copy of the given value, if applicable, otherwise the given value
        converted to a string.
    """
    try:
        json.dumps(value)
        value = copy.deepcopy(value)
    except (TypeError, OverflowError, RecursionError, AttributeError):
        value = str(value)
    return value


class LazyCallable:
    """Container for a function or LangChain object that is lazily imported.
    
    Represents a function or LangChain object that is provided by the user as
    part of a test suite. Objects of this class are callable, and calling them
    will import the required module if necessary to call the object.

    Attributes:
        fully_qualified_name (str): Fully qualified name of the callable
            object, in the format "<fully qualified module name>:<fully
            qualified object name>". (e.g. "my.module:my_function")
        path_to_module_dir (str): Path to the directory that contains the
            module that contains the callable object.
        input_signature (Dict[str, Optional[str]]): Inputs signature of the
            callable object. Inputs signature is a map between input parameter
            names to strings indicating the corresponding parameter types (or to
            None for input parameters that do not have type annotations).
    """
    def __init__(
        self,
        callable_or_fully_qualified_name: Union[Callable, str],
        path_to_module_dir: str = os.getcwd()):
        """Initialize a LazyCallable object.

        Args:
            callable_or_fully_qualified_name: Callable object or fully
                qualified name of the callable object, in the format
                "<fully qualified module name>:<fully qualified object name>".
                (e.g. "my.module:my_function")
            path_to_module_dir: Path to the directory that contains the module
                that contains the callable object. If not provided, the
                current working directory is used. This argument is ignored if
                `callable_or_fully_qualified_name` is a callable object.
        """
        if isinstance(callable_or_fully_qualified_name, Callable):
            callable_object = callable_or_fully_qualified_name
            module_qualname = get_module_qualname(callable_object)
            object_qualname = callable_object.__qualname__

            self.fully_qualified_name = f"{module_qualname}:{object_qualname}"
            self.path_to_module_dir = os.path.dirname(
                inspect.getfile(callable_object))
        elif isinstance(callable_or_fully_qualified_name, str):
            self.fully_qualified_name = callable_or_fully_qualified_name
            self.path_to_module_dir = path_to_module_dir

            callable_object = self.get_callable()
        else:
            raise ValueError(
                "callable_or_fully_qualified_name must be a callable or a "
                "string.")

        self._program_type = self._get_program_type(callable_object)
        self.inputs_signature = self._get_inputs_signature(callable_object)

    def get_program_details(self) -> wire_model.ProgramDetails:
        """Return a `wire_model.ProgramDetails` object.
        
        Returns:
            `wire_model.ProgramDetails` object.
        """
        return wire_model.ProgramDetails(
            fully_qualified_name=self.fully_qualified_name,
            program_type=self._program_type,
            inputs_signature=self.inputs_signature)

    def _import_module(
        self,
        module_qualname: str,
        reload: bool,
    ) -> types.ModuleType:
        """Import the module given by module_qualname.

        Args:
            module_qualname: Fully qualified name of the module to import.
            reload: Whether to reload the callable's module after importing
                it. This only has an effect if the module has been imported
                previously.

        Returns:
            The imported module.
        """
        orig_sys_path = sys.path.copy()
        sys.path.insert(0, self.path_to_module_dir)
        module = importlib.import_module(module_qualname)
        if reload:
            importlib.reload(module)
        sys.path = orig_sys_path
        return module

    def get_callable(self, reload: bool = False) -> Callable:
        """Import the callable object and return it.

        Args:
            reload: Whether to reload the module after importing it. This only
                has an effect if the module has been imported previously.
        
        Returns:
            Callable object.
        """
        module_qualname, object_qualname = (
            self.fully_qualified_name.split(":"))
        module_qualname = module_qualname.replace(
            "/", ".")
        # Note: we do not use removesuffix() here in order to enable
        # compatibility with Python 3.8.
        if module_qualname.endswith(".py"):
            module_qualname = module_qualname[:-len(".py")]

        module_is_main = (module_qualname == "google_colab") or (
            # To prevent re-importing the __main__ module under the name
            # given by its filename (in order to prevent inadvertently
            # re-executing the __main__ module's contents).
            "__main__" in sys.modules and
            hasattr(sys.modules["__main__"], "__file__") and
            module_qualname == os.path.splitext(
                os.path.basename(sys.modules["__main__"].__file__))[0])  # pylint: disable=no-member
        if module_is_main:
            module_qualname = "__main__"

        module = self._import_module(module_qualname, reload)
        callable_object = module
        for name in object_qualname.split("."):
            callable_object = getattr(callable_object, name)
        return callable_object

    def __call__(self, *args, **kwargs) -> Any:
        """Call the callable object.
        
        Args:
            *args: Positional arguments to pass to the callable object.
            **kwargs: Keyword arguments to pass to the callable object.
        
        Returns:
            The return value of the callable object.
        """
        orig_sys_path = sys.path.copy()
        try:
            sys.path.insert(0, self.path_to_module_dir)

            callable_object = self.get_callable()
            if self._program_type == "LANGCHAIN":
                return callable_object.run(*args, **kwargs)
            else:
                if asyncio.iscoroutinefunction(callable_object):
                    return asyncio.run(callable_object(*args, **kwargs))
                return callable_object(*args, **kwargs)
        finally:
            sys.path = orig_sys_path

    def _get_program_type(
        self,
        callable_object: Optional[Callable] = None
    ) -> Literal["FUNCTION", "LANGCHAIN"]:
        """Return the program type of the callable object.
        
        Args:
            callable_object: Callable object. If not provided, the callable
                object will be retrieved by calling self.get_callable().

        Returns:
            Program type of the callable object, which can be either "FUNCTION"
            or "LANGCHAIN".
        
        Raises:
            ValueError: If the object is not a function or LangChain object.
        """
        if callable_object is None:
            callable_object = self.get_callable()
        if callable_object.__class__.__name__ == "LLMChain":
            return "LANGCHAIN"
        elif inspect.isfunction(callable_object):
            return "FUNCTION"
        raise ValueError(
            f"Object {self.fully_qualified_name} is not a function or "
            "LangChain object.")

    def _get_inputs_signature(
        self,
        callable_object: Optional[Callable] = None
    ) -> Dict[str, Optional[str]]:
        """Return the inputs signature of the callable object.
        
        Inputs signature is a map between input parameter names to
        strings indicating the corresponding parameter types (or to None for
        input parameters that do not have type annotations).

        Args:
            callable_object: Callable object. If not provided, the callable
                object will be imported.
        
        Returns:
            Inputs signature of the callable object.
        """
        if callable_object is None:
            callable_object = self.get_callable()
        if self._program_type == "LANGCHAIN":
            return {key: None for key in callable_object.input_keys}
        else:
            signature = inspect.signature(callable_object)
            return {
                name: (
                    str(param.annotation)
                    if param.annotation != inspect._empty  # pylint: disable=protected-access
                    else None)
                for name, param in signature.parameters.items()
            }

    def reload(self):
        """Reload the callable object.
        
        Reloads the module containing the callable object and updates the
        program type and inputs signature.
        """
        callable_object = self.get_callable(reload=True)
        self._program_type = self._get_program_type(callable_object)
        self.inputs_signature = self._get_inputs_signature(callable_object)


class LiveExecution:
    """Object linking to an LLM program post execution after it has returned."""

    def __init__(
        self,
        llm_program_execution_auth_session: Optional[auth_session.AuthSession]
    ):
        """Initialize a LlmProgramExecution object.

        Args:
            llm_program_execution_auth_session: AuthSession object representing
                the session for this LLM program execution.
        """
        # Initialize identifier for the LLM program execution as None.
        # This will be set later asynchronously by `_set_id`.
        self._execution_id = None
        # Create list of LoggedValue objects. Used to store logged values
        # before an execution_id is set.
        self._logged_values = []

        self._auth_session = llm_program_execution_auth_session

    def _set_id(self, execution_id: int):
        """Sets the LLM program execution id field and flushes logged values.

        Args:
            execution_id: ID of the LLM program execution.
        """
        self._execution_id = execution_id
        # Flush any values logged before the id was set
        if self._logged_values:
            self._send_log_request(self._logged_values)
            self._logged_values = []

    def _send_log_request(
        self,
        logged_values_list: List[wire_model.LoggedValue]
    ):
        """Sends the log information to the client API.

        Log information is only sent if self._auth_session is not None.
        This function should only be called if self._execution_id is not None.

        Args:
            logged_values_list: List of LoggedValue objects.
        """
        if self._auth_session is not None:
            request = wire_model.LogValuesForExecutionRequest(
                execution_id=self._execution_id,
                logged_values=logged_values_list
            )
            auth_access_token = self._auth_session.access_token
            backend_client.log_values_for_execution(request, auth_access_token)

    def log(self, value: Any, *, name: Optional[str] = None):
        """Log a value and associate it with the LLM program execution.

        Args:
            value: The value to be logged.
            name: An optional human-readable name for the logged value.
        """
        logged_value = wire_model.LoggedValue(
            value=deepcopy_or_str(value),
            description=name,
            after_complete=True)
        if self._execution_id is not None:
            self._send_log_request([logged_value])
        else:
            self._logged_values.append(logged_value)


class ChatMessage(DataModel):
    """A chat message.

    Attributes:
        role: Role of the entity that issued this message.
            - "program" indicates that the message was issued by the LLM
                program.
            - "user" indicates that the message was issued by the user of the
                LLM program.
        content: Content of the message.
    """
    role: Literal["program", "user"]
    content: str


class ChatSession(DataModel):
    """Information about a chat session.

    Attributes:
        messages: Chat messages in the order in which they were issued.
    """
    messages: List[ChatMessage]

    def openai_messages(self) -> List[Dict]:
        """Returns messages in format accepted by the OpenAI API.

        Specifically, this method updates each message's `role` field to conform
        to the role values accepted by the OpenAI API.  See the
        [OpenAI docs](https://platform.openai.com/docs/api-reference/chat/create)
        for more information about the OpenAI API's message format.
        """  # pylint: disable=line-too-long
        new_messages = []
        for message in self.messages:
            new_message = message.model_dump(mode="json")
            if new_message["role"] == "program":
                new_message["role"] = "assistant"
            new_messages.append(new_message)
        return new_messages

    # Ignore the types of public methods to robustify to transformations
    # apparently performed by cython compilation.
    model_config = pydantic.ConfigDict(ignored_types=(type(openai_messages),))


async def reload_llm_program_on_changes(
    llm_program_fqn: str,
    playground_details: Dict[str, str]):
    """Reloads the LLM program's module when changes are detected in it.

    Asynchronously and indefinitely watches the LLM program's module for
    changes. When changes are detected, the LLM program is reloaded and,
    if the signature has changed, the provided playground details are updated
    with the response from a new `backend_client.get_playground` request.
    Terminates only upon receiving a KeyboardInterrupt exception.

    Args:
        llm_program_fqn: Fully qualified name of the LLM program.
        playground_details: Dictionary containing a response from a
            `backend_client.get_playground` request to the backend.
            This dictionary is updated with the response from a new
            `backend_client.get_playground` request when the LLM
            program's signature changes.
    """
    llm_program = LazyCallable(llm_program_fqn)
    module = inspect.getmodule(llm_program.get_callable())
    module_path = pathlib.Path(module.__file__).resolve()

    async for _ in watchfiles.awatch(module_path):
        if inductor_config.verbose:
            rich.print("Changes detected in LLM program file. Reloading...")

        previous_signature = copy.deepcopy(llm_program.inputs_signature)
        try:
            llm_program.reload()
        except KeyboardInterrupt as error:
            raise error
        except Exception as error:  # pylint: disable=broad-except
            if inductor_config.verbose:
                rich.print(
                    f"Unable to successfully reload {module_path}.\n"
                    f"Awaiting next change to file.\nError: {error}")
            continue

        if previous_signature != llm_program.inputs_signature:
            if inductor_config.verbose:
                rich.print("LLM program signature has changed. "
                           "Updating playground...")
            response = backend_client.get_playground(
                wire_model.GetPlaygroundRequest(
                    llm_program_details=
                        LazyCallable(llm_program_fqn).get_program_details()),
                auth_session.get_auth_session().access_token)
            # Dictionary update() is an atomic operation, so there is no need
            # to use a lock when accessing playground_details.
            playground_details.update(response.model_dump())
            if inductor_config.verbose:
                rich.print(f"Playground details updated: {playground_details}")

        if inductor_config.verbose:
            rich.print(f"Reloaded {module_path}.")
