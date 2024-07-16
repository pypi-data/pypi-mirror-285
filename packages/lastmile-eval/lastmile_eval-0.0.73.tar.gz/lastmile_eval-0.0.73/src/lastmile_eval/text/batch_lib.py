# imports
import concurrent.futures
import random
import time
from typing import Any, Callable, ParamSpec, Type, TypeVar

import openai

T_ParamSpec = ParamSpec("T_ParamSpec")
U = TypeVar("U")


# define a retry decorator
def retry_with_exponential_backoff(
    func: Callable[T_ParamSpec, U],
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple[Type[BaseException]] = (openai.RateLimitError,),
) -> Callable[T_ParamSpec, U]:
    """Retry a function with exponential backoff."""

    def wrapper(*args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs) -> U:
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)

            # Retry on specific errors
            except errors:
                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper


# TODO: replace Any
def ppe_map(f: Callable[T_ParamSpec, U], lst: list[Any]) -> list[U]:
    with concurrent.futures.ProcessPoolExecutor() as executor:
        responses = executor.map(f, lst)

    return list(responses)
