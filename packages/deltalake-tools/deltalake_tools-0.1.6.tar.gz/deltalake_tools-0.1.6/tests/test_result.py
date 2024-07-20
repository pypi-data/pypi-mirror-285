import logging
from deltalake_tools.result import Result, Ok, Err


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Err("Division by zero")
    else:
        return Ok(a / b)

def evaluate_result(result: Result) -> None:
    if result.is_ok():
        logger.info(f"Result: {result.unwrap()}")
    else:
        logging.info(f"Error: {result.unwrap_err()}")

def test_result() -> None:
    result = divide(10, 2)
    assert result.is_ok()
    evaluate_result(result)

    error_result = divide(10, 0)
    assert error_result.is_err()
    evaluate_result(error_result)
