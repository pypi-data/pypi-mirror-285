from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
import time
import json
import asyncio
import sys


def begin_task_execution(async_func):
    """
    See https://stackoverflow.com/a/75341431 for underlying rationale.
    This code should allow any async function to be called synchronously by circumventing
    Jupyter's existing event loop via the creation of a separate thread.
    If an event loop doesn't exist, it reverts back to existing asyncio logic.
    """
    def wrap(*args, **kwargs):
        # It is safer to use a if/else statement than try/except since
        # the underlying code we wrap our function around can also raise RuntimeErrors.
        # When this happens, multiple asyncio.run() executions occur, which is dangerous.
        if is_jupyter():
            with ThreadPoolExecutor(1) as pool:
                result = pool.submit(lambda: asyncio.run(async_func(*args, **kwargs))).result()
        else:
            result = asyncio.run(async_func(*args, **kwargs))
        return result
    return wrap


def is_jupyter():
    try:
        # Check if 'IPython' is in sys.modules
        if 'IPython' in sys.modules:
            from IPython import get_ipython
            # Check if we're in an IPython environment
            if get_ipython() is not None:
                return True
    except ImportError:
        pass
    return False


def load_json_buffer(string):
    try:
        return json.loads(string)
    except json.JSONDecodeError:
        return None


def split_dict_into_chunks(input_dict: Dict, n: int) -> List[Dict]:
    """
    Split a dictionary into `n` chunks.

    Parameters:
    input_dict (dict): The dictionary to split.
    n (int): The number of chunks to split the dictionary into.

    Returns:
    List[Dict]: A list of dictionaries, where each dictionary is a chunk of the input dictionary.
    """
    if n <= 0:
        raise ValueError("Number of chunks must be greater than 0")

    if not input_dict:
        return []

    items = list(input_dict.items())
    chunk_size = len(items) // n
    remainder = len(items) % n

    chunks = []
    start = 0
    for i in range(n):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunk = dict(items[start:end])
        chunks.append(chunk)
        start = end

    return chunks


def time_api(func):
    """
    Decorator to measure the execution time of a function.
    """

    def time_wrapper(*args, **kwargs):
        """
        Passed function reference is utilized to run the function with its
        original arguments while maintaining timing and logging functions.
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} executed in {elapsed_time:.4f} seconds.")
        return result

    # We return the augmented function's reference.
    return time_wrapper
