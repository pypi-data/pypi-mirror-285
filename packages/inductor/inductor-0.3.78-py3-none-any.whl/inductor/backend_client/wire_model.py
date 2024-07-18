# Copyright 2023 Inductor, Inc.
"""Types used by backend API that powers Inductor's client (CLI and library)."""

import datetime
from typing import Any, Dict, List, Literal, Optional, TypeVar, Union

import pydantic
# Note: we import Annotated from typing_extensions, rather than from typing,
# to enable compatibility with Python 3.8.
from typing_extensions import Annotated


# Field definitons
_RESTRICTED_NAME_FIELD = pydantic.Field(
    max_length=1000, pattern=r"^[a-zA-Z0-9_-]+$")
_SUBRESOURCE_NAME_FIELD = pydantic.Field(max_length=500)


class _WireModel(pydantic.BaseModel):
    """Base class for wire models to inherit from.

    This class configures the following setting(s):
    - extra: "ignore" (i.e., ignore extra fields passed to the model)
        In the case where the backend's (latest) wire model includes new
        fields that are not present in a given client's (out-of-date) wire
        model, this setting allows the client to still communicate with the
        backend without error. A notable side effect of this setting is that
        conversion from the client's data model to the client's wire model is
        simpler. This is the default value for this setting, but it is
        explicitly set here for clarity.
    - populate_by_name: True (i.e., fields can be populated by the name
        as given by the model attribute or the alias)
    
    To ensure backwards compatibility between the backend and clients, any
    fields added to existing wire models should have default values.
    """
    model_config = pydantic.ConfigDict(extra="ignore", populate_by_name=True)


class CreateApiKeyRequest(_WireModel):
    """Request body type for create API key endpoint.

    Attributes:
        auth0_id: Auth0 ID of the API key.
    """
    auth0_id: str


class TestCase(_WireModel):
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


class TestCaseWithMetadata(TestCase):
    """A test case with metadata.
    
    Attributes:
        id: ID of the test case.
    """
    id: int


class QualityMeasure(_WireModel):
    """A quality measure.
    
    Attributes:
        name: Human-readable name of this quality measure.
        evaluator: Evaluator for this quality measure.  Determines whether
            this quality measure will be evaluated by running a function,
            or via human inspection.
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
    name: str = _SUBRESOURCE_NAME_FIELD
    evaluator: Literal["FUNCTION", "HUMAN", "LLM"]
    evaluation_type: Literal["BINARY", "RATING_INT"]
    spec: Union[str, Dict[str, str]]


class QualityMeasureWithMetadata(QualityMeasure):
    """A quality measure with metadata.

    Attributes:
        id: ID of quality measure.
    """
    id: int


def check_hparam_values_type(data: Any) -> Any:
    """Ensure that given hparam values are aligned with given the hparam type.

    This function is designed to be called in a "before" model validator
    for both the data_model.HparamSpec and wire_model.HparamSpec classes.

    For example:
    ```
    @pydantic.model_validator(mode="before")
    @classmethod
    def _check_values_type(cls: _T_HparamSpec, data: Any) -> Any:
        \"\"\"Ensure that the given values and type are aligned.\"\"\"
        check_hparam_values_type(data)
    ```

    This function is for a "before" validator instead of a "after" validator
    to provide an informative error message in the case where `values`
    is not any of the possible types (and therefore fails to pass pydantic's
    type validation). A consequence of this choice is that this function
    also needs to do some additional pre-validation to ensure that the data is
    in the expected format before performing the type validation.

    Args:
        data: The data to validate.

    Returns:
        The validated data. If the data is valid and there is a key
        "hparam_type", the key is replaced with "type".
    
    Raises:
        ValueError: If the data is not in the expected format or if the values
            are not aligned with the given hparam type.
    """
    if isinstance(data, dict):
        type_validations = {
            "SHORT_STRING":
                (str, "Hparam values of type SHORT_STRING must be strings."),
            "TEXT":
                (str, "Hparam values of type TEXT must be strings."),
            "NUMBER":
                ((int, float),
                    "Hparam values of type NUMBER must be ints or floats.")
        }

        # This function is used by both data_model.HparamSpec and
        # wire_model.HparamSpec. In both cases, the keys "type" and
        # "hparam_type" are interchangeable. Thus, unifying the keys
        # before validation is safe to do here and simplifies the
        # validation logic.
        if "type" in data and "hparam_type" in data:
            raise ValueError(
                "Only one of 'type' and 'hparam_type' should be specified "
                "as they refer to the same field.")
        if "hparam_type" in data:
            data["type"] = data.pop("hparam_type")

        if "type" not in data:
            raise ValueError("Hparam type must be specified.")
        if data["type"] not in type_validations:
            raise ValueError(
                f"Invalid hparam type: {data['type']}. Must be one of "
                f"{list(type_validations.keys())}.")
        if "values" not in data:
            raise ValueError("Hparam values must be specified.")

        expected_type, error_message = type_validations.get(
            data["type"], (None, None))
        if expected_type is not None:
            if not all(
                isinstance(value, expected_type)
                for value in data["values"]):
                raise ValueError(error_message)

    return data


# Type variable for the HparamSpec class.
_T_HparamSpec = TypeVar("_T_HparamSpec", bound="HparamSpec")  # pylint: disable=invalid-name


class HparamSpec(_WireModel):
    """Specification of set of hyperparameter values to use for test suite run.

    Attributes:
        hparam_name: Name of hyperparameter.
        hparam_type: Type of hyperparameter.
        values: List of hyperparameter values.
    """
    # Aliases are used to convert from the HparamSpec data model.
    hparam_name: str = pydantic.Field(max_length=500, alias="name")
    hparam_type: Literal["SHORT_STRING", "TEXT", "NUMBER"] = pydantic.Field(
        alias="type")
    values: Union[List[str], List[int], List[float]]

    @pydantic.model_validator(mode="before")
    @classmethod
    def _check_values_type(cls: _T_HparamSpec, data: Any) -> Any:
        """Ensure that the given values and type are aligned."""
        return check_hparam_values_type(data)


class ProgramDetails(_WireModel):
    """Details of an LLM program.

    Attributes:
        fully_qualified_name: Fully qualified name of the LLM program.
        inputs_signature:  Map between input parameter names to strings
            indicating the corresponding parameter types (or to null for
            input parameters that do not have type annotations).
        program_type: Type of LLM program.
    """
    fully_qualified_name: str
    inputs_signature: Dict[str, Optional[str]]
    program_type: Literal["FUNCTION", "LANGCHAIN"]


class LoggedValue(_WireModel):
    """A logged value associated with an LLM program execution.

    Attributes:
        value: The logged value.
        description: Description of the logged value (if any).
        after_complete: Whether the logged value was logged after the LLM
            program completed (as opposed to during its execution).
    """
    value: Any
    description: Optional[str] = None
    after_complete: bool


class DirectEvaluation(_WireModel):
    """A direct evaluation of a quality measure.
    
    Attributes:
        quality_measure_id: ID of the quality measure that was evaluated.
        value_bool: The output of the quality measure, if boolean.
        value_int: The output of the quality measure, if an integer.
    """
    quality_measure_id: int
    value_bool: Optional[bool] = None
    value_int: Optional[int] = None


# Type variable for the TestSuiteImportSpec class.
_T_TestSuiteImportSpec = TypeVar(  # pylint: disable=invalid-name
    "_T_TestSuiteImportSpec", bound="TestSuiteImportSpec")


class TestSuiteImportSpec(_WireModel):
    """Specification for importing test suite components.
    
    Exactly one of test_suite_id or meta_test_suite should be non-None.
    
    Attributes:
        test_suite_id: ID of a test suite from which to import components.
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


# TODO: https://github.com/inductor-hq/saas/issues/404 - This class is
# currently not used to transmit data to the backend, but instead is a
# placeholder until the backend supports recording quality measure
# execution details (i.e. errors, stdout, and stderr).
class QualityMeasureExecutionDetails(_WireModel):
    """Details of a quality measure execution.

    Attributes:
        input: The input to the quality measure.
        output: The output of the quality measure, if available.  Should be
            None if the execution terminated with an error.
        error: If an error occurred during quality measure execution, this
            field should contain a specification of the error.
        stdout: The content printed to stdout during the quality measure's
            execution.
        stderr: The content printed to stderr during the quality measure's
            execution.
    """
    input: Any
    output: Optional[Any] = None
    error: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class ExecutionDetails(_WireModel):
    """An LLM program execution.

    Attributes:
        mode: Mode in which this execution was performed (e.g., via CLI, or as
            part of a deployment), if known.
        inputs: JSON-serializable mapping from input argument name to input
            value.
        hparams: JSON-serializable mapping from hyperparameter name to
            hyperparameter value.
        output: The output of the LLM program, if available.  Should be None
            if the execution terminated with an error, without producing an
            output.
        error: If an error occurred during LLM program execution, this column
            should contain a specification of the error.
        stdout: The content printed to stdout during the LLM program's
            execution.
        stderr: The content printed to stderr during the LLM program's
            execution.
        execution_time_secs: The total wall clock time elapsed during this
            execution.
        started_at: The timestamp at which the execution started.
        ended_at: The timestamp at which the execution ended (whether
            successfully or due to an error).
        logged_values: The values logged during the LLM program's execution.
        direct_evaluations: The direct evaluations performed during the LLM
            program's execution.
        live_deployment_config_id: The ID of the live deployment config
            associated with this execution, if any.
    """
    mode: Literal["CLI", "DEPLOYED", "PLAYGROUND"]
    inputs: Dict[str, Any]
    hparams: Optional[Dict[str, Union[str, int, float]]] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_time_secs: float
    started_at: datetime.datetime
    ended_at: datetime.datetime
    logged_values: Optional[List[LoggedValue]] = None
    direct_evaluations: Optional[List[DirectEvaluation]] = None
    live_deployment_config_id: Optional[int] = None


class CreateTestSuiteRequest(_WireModel):
    """Request body for create test suite endpoint.

    Attributes:
        name: Name of test suite. Test suite names must be unique per user.
        description: Description of test suite.
    """
    name: str = _RESTRICTED_NAME_FIELD
    description: Optional[str] = None


class CreateTestSuiteResponse(_WireModel):
    """Response for create test suite endpoint upon successful creation.
    
    Attributes:
        id: ID of the created test suite.
    """
    id: int


# Type variable for the CreateTestSuiteRunRequest class.
_T_CreateTestSuiteRunRequest = TypeVar(  # pylint: disable=invalid-name
    "_T_CreateTestSuiteRunRequest", bound="CreateTestSuiteRunRequest")


class CreateTestSuiteRunRequest(_WireModel):
    """Request body for create test suite run endpoint.

    Attributes:
        test_suite_id: ID of test suite to run.
        test_suite_name: Name of test suite to run.
        test_cases: List of test cases.
        quality_measures: List of quality measures (if any).
        hparam_specs: List of hyperparameter specifications (if any).
        llm_program_details: Details of LLM program to run.
        replicas: Number of times that LLM program will be run on each pair of
            (test case, set of hyperparameters).
        parallelize: Degree of parallelism used for this run.
        started_at: The timestamp at which the test suite run started.
        test_suite_id_or_name: ID or name of test suite to run. This field is
            used for backwards compatibility with previous versions of the
            Inductor client. Use `test_suite_id` and `test_suite_name` instead.
        test_suite_import_specs: List of test suite import specifications.
        num_executions: The total number of executions that will be executed
            via running this test suite.
    """
    test_suite_id: Optional[int] = None
    test_suite_name: Optional[str] = None
    test_cases: List[TestCase]
    quality_measures: Optional[List[QualityMeasure]] = None
    hparam_specs: Optional[List[HparamSpec]] = None
    llm_program_details: ProgramDetails
    replicas: int = 1
    parallelize: int = 1
    started_at: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    test_suite_id_or_name: Optional[Union[int, str]] = None
    test_suite_import_specs: Optional[List[TestSuiteImportSpec]] = None
    num_executions: int = 0

    @pydantic.model_validator(mode="before")
    @classmethod
    def unpack_test_suite_id_or_name(
        cls: _T_CreateTestSuiteRunRequest, data: Any) -> Any:
        """Unpack test_suite_id_or_name into id or name fields."""
        if isinstance(data, dict):
            test_suite_id_or_name = data.get("test_suite_id_or_name")
            if test_suite_id_or_name is not None:
                if (isinstance(test_suite_id_or_name, int) and
                    "test_suite_id" not in data):
                    data["test_suite_id"] = test_suite_id_or_name
                elif (isinstance(test_suite_id_or_name, str) and
                      "test_suite_name" not in data):
                    data["test_suite_name"] = test_suite_id_or_name
        return data

    @pydantic.model_validator(mode="after")
    def check_test_suite_id_or_name(self):
        """Ensure that id or name is specified."""
        if self.test_suite_id is None and self.test_suite_name is None:
            raise ValueError(
                "Either test_suite_id or test_suite_name must be specified.")
        return self


class CreateTestSuiteRunResponse(_WireModel):
    """Response for create test suite run endpoint upon successful creation.
    
    Attributes:
        test_suite_run_id: ID of the created test suite run.
        test_case_ids: IDs of the created test cases. The order of test case
            IDs is guaranteed to be the same as the order of test cases in the
            request. If test cases were imported from other test suites, this
            field will be extended with the IDs of the imported test cases in
            the same order as the `imported_test_cases` field below.
        quality_measure_ids: IDs of the quality measures included in the
            request. The order of quality measure IDs is guaranteed to be
            the same as the order of quality measures in the request.
        hparam_spec_ids: IDs of the hyperparameter specifications included in
            the request. The order of hyperparameter specification IDs is
            guaranteed to be the same as the order of hyperparameter
            specifications in the request.
        url: URL at which the created test suite run can be accessed.
        imported_test_cases: List of test cases imported based on test suite
            import specifications specified in the request.
    """
    test_suite_run_id: int
    test_case_ids: List[int]
    quality_measure_ids: List[int]
    hparam_spec_ids: List[int]
    url: str
    imported_test_cases: Optional[List[TestCase]] = None


class LogTestCaseExecutionRequest(_WireModel):
    """Request body for log test case execution endpoint.

    Attributes:
        test_suite_run_id: ID of test suite run as part of which this
            execution occurred (if any).
        test_case_id: ID of test case on which this execution occurred.
        test_case_replica_index: Index of execution replica on test case given
            by test_case_id. Replica indices should start at zero.
        execution_details: Details of the test case execution.
    """
    test_suite_run_id: int
    test_case_id: int
    test_case_replica_index: int
    execution_details: ExecutionDetails


class CompleteTestSuiteRunRequest(_WireModel):
    """Request body for complete test suite run endpoint.

    Contains all remaining fields required by TestSuiteRun backend data model
    that have not already been logged.

    Attributes:
        test_suite_run_id: ID of the test suite run to complete.
        ended_at: The timestamp at which the test suite run ended.
    """
    test_suite_run_id: int
    ended_at: datetime.datetime


class QualityMeasureResultSummary(_WireModel):
    """Summary of results for a quality measure within a test suite run.
    
    Attributes:
        num_evals: Number of evaluations of this quality measure within the
            test suite run.
        average_value: The average value of the quality measure within the
            test suite run (for BINARY quality measures, True is mapped to
            1 and False is mapped to 0 in order to compute average values),
            if the run's results include any evaluations of the quality measure.
            Should be None if the run's results do not include any evaluations
            of the quality measure.
    """
    num_evals: int
    average_value: Optional[float] = None


class GetTestSuiteRunResultsResponse(_WireModel):
    """Response for the get test suite run results endpoint.

    Attributes:
        test_suite_run_id: ID of the test suite run.
        quality_measures: The quality measures included in the test suite run.
        quality_measure_result_summaries: Mapping from quality measure ID to
            result summary for that quality measure.
    """
    test_suite_run_id: int
    quality_measures: List[QualityMeasureWithMetadata]
    quality_measure_result_summaries: Dict[int, QualityMeasureResultSummary]


class LogLlmProgramExecutionRequest(_WireModel):
    """Request body for log LLM program execution endpoint.

    Attributes:
        program_details: Details of the LLM program.
        execution_details: Details of the LLM program execution.
    """
    program_details: ProgramDetails
    execution_details: ExecutionDetails


class LogLlmProgramExecutionResponse(_WireModel):
    """Response for log LLM program execution upon successful creation.

    Attributes:
        id: ID of the created LLM program execution.
    """
    id: int


class CreateLiveDeploymentRequest(_WireModel):
    """Request body for create live deployment endpoint.

    Attributes:
        program_details: Details of the LLM program to be
            associated with the live deployment.
        quality_measures: List of quality measures (if any).
        hparam_specs: List of hyperparameter specifications (if any).
    """
    program_details: ProgramDetails
    quality_measures: Optional[List[QualityMeasure]] = None
    hparam_specs: Optional[List[HparamSpec]] = None


class CreateLiveDeploymentResponse(_WireModel):
    """Response for create live deployment endpoint.

    Attributes:
        live_deployment_config_id: ID of the created live deployment
            configuration, if any.
        quality_measure_ids: IDs of the quality measures included in the
            request. The order of quality measure IDs is guaranteed to be
            the same as the order of quality measures in the request.
        hparam_spec_ids: IDs of the hyperparameter specifications included in
            the request. The order of hyperparameter specification IDs is
            guaranteed to be the same as the order of hyperparameter
            specifications in the request.
    """
    live_deployment_config_id: Optional[int]
    quality_measure_ids: Optional[List[int]]
    hparam_spec_ids: Optional[List[int]]


class GetTestSuiteRunQualityMeasuresRequest(_WireModel):
    """Request body for get test suite run quality measures endpoint.

    Attributes:
        quality_measure_ids: IDs of quality measures.
    """
    quality_measure_ids: List[int]


class GetTestSuiteRunQualityMeasuresResponse(_WireModel):
    """Response for get test suite run quality measures endpoint.

    Attributes:
        quality_measures: Quality measures (with metadata) corresponding to
            quality_measure_ids specified in request body.
    """
    quality_measures: List[QualityMeasureWithMetadata]


class LogValuesForExecutionRequest(_WireModel):
    """Request body for logging values post execution.
    
    Attributes:
        execution_id: ID mapping to an execution of an LLM program.
        logged_values: List of LoggedValue objects to be logged for
            the execution given by execution_id.
    """
    execution_id: int
    logged_values: List[LoggedValue]


class GetPlaygroundRequest(_WireModel):
    """Request body for get playground endpoint.

    Attributes:
        llm_program_details: Details of the LLM program to
            associate with the playground.
    """
    llm_program_details: ProgramDetails


class GetPlaygroundResponse(_WireModel):
    """Response for get playground endpoint.

    Attributes:
        playground_id: ID of the playground associated with the user ID and
            LLM program given by the request.
        llm_program_id: ID of the LLM program associated with the playground.
        llm_program_snapshot_id: ID of the LLM program snapshot associated
            with the playground.
    """
    playground_id: int
    llm_program_id: int
    llm_program_snapshot_id: int


class PlaygroundChatMetadata(_WireModel):
    """Metadata for a chat session in playground execution.

    Attributes:
        chat_session_input_name: Name of the LLM program input that was
            type-annotated with the inductor.ChatSession type.
        root_execution_id: ID of the first LLM program execution in the chat
            session, unless the current execution is the first in the chat
            session, in which case this field should be None.
        parent_execution_id: ID of the previous LLM program execution in the
            chat session. This field should be None if the current execution is
            the first in the chat session.
    """
    chat_session_input_name: str
    root_execution_id: Optional[int]
    parent_execution_id: Optional[int]


class PlaygroundExecuteLlmProgramSpec(_WireModel):
    """Specification for executing an LLM program via a playground.

    Attributes:
        inputs: JSON-serializable mapping from input argument name to input
            value.
        hparams: JSON-serializable mapping from hyperparameter name to
            hyperparameter value.
        fingerprint: Unique identifier for this spec, if any.
        chat_metadata: Metadata for chat messages in the inputs (if any).
    """
    inputs: Dict[str, Any]
    hparams: Optional[Dict[str, Union[str, int, float]]] = None
    fingerprint: Optional[str] = None
    chat_metadata: Optional[PlaygroundChatMetadata] = None


class PlaygroundExecuteLlmProgramRequest(_WireModel):
    """Request body for playground execute LLM program endpoint.

    Attributes:
        message_discriminator: Discriminator for this playground request,
            for use in distinguishing object types after JSON serialization.
        specs: List of LLM program execution specifications.
    """
    message_discriminator: Literal["PlaygroundExecuteLlmProgramRequest"] = (
        "PlaygroundExecuteLlmProgramRequest")
    specs: List[PlaygroundExecuteLlmProgramSpec]


class PlaygroundExecuteTestSuiteRequest(_WireModel):
    """Request body for playground execute test suite endpoint.

    Attributes:
        message_discriminator: Discriminator for this playground request,
            for use in distinguishing object types after JSON serialization.
        test_suite_id: ID of the test suite to execute.
        fingerprint: Unique identifier for this execution, if any.
    """
    message_discriminator: Literal["PlaygroundExecuteTestSuiteRequest"] = (
        "PlaygroundExecuteTestSuiteRequest")
    test_suite_id: int
    fingerprint: Optional[str] = None


# Type adapter to distinguish between playground request types.
PlaygroundRequestAdapter = pydantic.TypeAdapter(Annotated[Union[
    PlaygroundExecuteLlmProgramRequest, PlaygroundExecuteTestSuiteRequest],
    pydantic.Field(discriminator="message_discriminator")])


class ExecutionDetailsWithPlaygroundMetadata(ExecutionDetails):
    """An LLM program execution with playground metadata.

    Attributes:
        fingerprint: Unique identifier for this execution, if any.
        hparam_specs: List of hyperparameter specifications associated with
            this execution. The hparam specs are constructed from hparams in
            the execution spec and any default hparam values that were used in
            the execution.
        chat_metadata: Metadata for chat messages in playground
            execution (if any).
    """
    fingerprint: Optional[str]
    hparam_specs: Optional[List[HparamSpec]] = None
    chat_metadata: Optional[PlaygroundChatMetadata] = None


class PlaygroundExecuteLlmProgramResponse(_WireModel):
    """Response for playground execute LLM program endpoint.

    Attributes:
        message_discriminator: Discriminator for this playground response,
            for use in distinguishing object types after JSON serialization.
        llm_program_id: ID of the LLM program associated with the executions.
        llm_program_snapshot_id: ID of the LLM program snapshot associated
            with the executions.
        execution_details: List of LLM program executions with fingerprint.
            The executions in this list should correspond to the specs in the
            request that triggered this response.
    """
    message_discriminator: Literal["PlaygroundExecuteLlmProgramResponse"] = (
        "PlaygroundExecuteLlmProgramResponse")
    llm_program_id: int
    llm_program_snapshot_id: int
    execution_details: List[ExecutionDetailsWithPlaygroundMetadata]


class PlaygroundExecuteTestSuiteResponse(_WireModel):
    """Response for playground execute test suite endpoint.

    Attributes:
        message_discriminator: Discriminator for this playground response,
            for use in distinguishing object types after JSON serialization.
        test_suite_run_id: ID of the test suite run that was created.
        fingerprint: Unique identifier for this execution, if any.
    """
    message_discriminator: Literal["PlaygroundExecuteTestSuiteResponse"] = (
        "PlaygroundExecuteTestSuiteResponse")
    test_suite_run_id: int
    fingerprint: Optional[str] = None


# Type adapter to distinguish between playground response types.
PlaygroundResponseAdapter = pydantic.TypeAdapter(Annotated[Union[
    PlaygroundExecuteLlmProgramResponse, PlaygroundExecuteTestSuiteResponse],
    pydantic.Field(discriminator="message_discriminator")])
