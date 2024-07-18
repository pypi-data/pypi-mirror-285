"""This module provides pre-built quality measures (QMs)."""

from typing import Any, Union

from inductor.data_model import data_model


def llm_qm_valid_output_binary(output: Any) -> bool:
    """Checks if an LLM QM's output is valid for BINARY evaluation_type.

    Args:
        output: The output of the execution of an LLM-powered quality measure.

    Returns:
        True if output is in {"Y", "N", "YES", "NO", True, False}, and False
        otherwise.
    """
    return output in {"Y", "N", "YES", "NO", True, False}


def llm_qm_valid_output_rating_int(output: Any) -> bool:
    """Checks if an LLM QM's output is valid for RATING_INT evaluation_type.

    Args:
        output: The output of the execution of an LLM-powered quality measure.

    Returns:
        True if output is in {"1", "2", "3", "4", "5", 1, 2, 3, 4, 5}, and False
        otherwise.
    """
    return output in {"1", "2", "3", "4", "5", 1, 2, 3, 4, 5}


def llm_qm_exact_agreement(
    output: Union[str, int, bool],
    _,
    test_case: data_model.TestCase
) -> bool:
    """Checks if an LLM quality measure's output is equal to its target value.

    This quality measure is intended for use in "meta" evaluation of an
    LLM quality measure.

    Args:
        output: The output of the execution of an LLM-powered quality measure.
        test_case: The "meta" test case on which the LLM-powered quality
            measure was executed.
    
    Returns:
        True if the output matches the target value given by the test_case,
        False otherwise.
    """
    def _normalize_output(
        output: Union[str, int, bool]
    ) -> Union[str, int, bool]:
        if isinstance(output, str):
            output_normalized = output.strip().upper()
            if output_normalized in ("YES", "Y"):
                return True
            elif output_normalized in ("NO", "N"):
                return False
            elif output_normalized.isdigit():
                return int(output_normalized)
        return output
    return _normalize_output(output) == _normalize_output(test_case.output)


def llm_qm_plus_minus_one_agreement(
    output: Union[str, int, bool],
    _,
    test_case: data_model.TestCase
) -> bool:
    """Checks if an LLM quality measure's output is within +/- 1 of target.

    This quality measure is intended for use in "meta" evaluation of an
    LLM quality measure whose evaluation type is RATING_INT.

    Args:
        output: The output of the execution of an LLM-powered quality measure.
        test_case: The "meta" test case on which the LLM-powered quality
            measure was executed.
    
    Returns:
        True if the output is within +/- 1 of the target value given by
        the test_case, False otherwise.
    """
    output = int(output)
    test_case_output = int(test_case.output)
    return test_case_output - 1 <= output <= test_case_output + 1
