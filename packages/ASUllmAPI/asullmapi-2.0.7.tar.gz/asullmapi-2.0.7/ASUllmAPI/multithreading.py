from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Union

from tqdm.auto import tqdm

from .api import query_llm
from .model_config import ModelConfig
from .utils import time_api


@time_api
def batch_query_llm(model: ModelConfig, 
                    queries: Dict[Union[str, int], str], 
                    max_threads: int,
                    num_retry: int = 3, 
                    auto_increase_retry: bool = False,
                    success_sleep: float = 0.0, 
                    fail_sleep: float = 1.0) -> Dict[Union[str, int], dict]:
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Submit tasks to the executor - order of return will be asynchronous.
        # If `auto_increase_retry` enabled, then scaling API backoff is implemented.
        if auto_increase_retry:
            future_to_query = {executor.submit(query_llm, model, question,
                                               qid, success_sleep, fail_sleep): qid
                               for qid, question in queries.items()}
        else:
            future_to_query = {executor.submit(query_llm, model, question,
                                               num_retry, success_sleep, fail_sleep): qid
                               for qid, question in queries.items()}

        # Collect and return results as they complete while maintaining order.
        results = {}
        for future in tqdm(as_completed(future_to_query)):
            qid = future_to_query[future]
            try:
                result = future.result()
                results[qid] = result
                print(f"......Received response for question {qid}...")
            except Exception as exc:
                print(f"{qid} generated an exception: {exc}")
                results[qid] = None

        return results
