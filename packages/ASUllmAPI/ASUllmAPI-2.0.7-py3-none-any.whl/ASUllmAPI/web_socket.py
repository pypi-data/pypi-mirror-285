import asyncio
import json
import logging
import traceback
from typing import Dict, Any, Union
import ssl
import time

import websockets
import certifi

from .model_config import ModelConfig
from .utils import load_json_buffer, begin_task_execution

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
END_OF_STREAM = '<EOS>'
DEFAULT_RESPONSE = {"response": "", "success": 0}
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


class ResponseDataError(Exception):
    def __init__(self, message="An error message has been sent by the endpoint."):
        super().__init__(message)
        self.message = message


async def interact_with_websocket(uri: str, queue: asyncio.Queue,
                                  response_payloads: Dict[Union[str, int], Dict[str, Any]],
                                  ws_timeout_min: int = 8,
                                  error_threshold: int = 100,
                                  reconnect_timeout_secs: int = 2):
    """
    :param uri: WebSocket URI
    :param queue: An instantiated asyncio Queue with your dataset fully inserted.
    :param response_payloads: A dictionary with base responses set up for processing.
    :param ws_timeout_min: The number of minutes before a connection to the WebSocket is terminated on the async task.
    :param error_threshold: The number of errors permissible for a query in the WebSocket before the program
    moves to the next question.
    :param reconnect_timeout_secs: The number of seconds before another connection is instantiated.
    :return: the `response_payloads` object initially passed into the function
    """
    error_ct = 0
    ws_timeout = ws_timeout_min * 60
    qid = None
    tmp_input_payload = None

    # START - WEBSOCKET LOOP
    while not (queue.empty() and error_ct == 0):
        connection_start_time = time.time()
        try:
            async with websockets.connect(uri, ssl=SSL_CONTEXT) as ws:
                # START - QUERY QUEUE LOOP
                while not (queue.empty() and error_ct == 0):
                    if error_ct == 0:
                        qid, tmp_input_payload = await queue.get()

                    # To prevent unnecessary timeouts DURING a query, we can
                    # cautiously opt out of the connection at a user specified threshold.
                    query_time = time.time()
                    connection_time = query_time - connection_start_time
                    if connection_time >= ws_timeout:
                        raise asyncio.TimeoutError()

                    if tmp_input_payload["query"] != "":
                        await ws.send(json.dumps(tmp_input_payload))
                        # START - QUERY CHUNK LOOP
                        while True:
                            # First chunk will typically take 29 seconds of time for every model
                            # Remaining chunks can take up to 9 minutes to be received.
                            # First chunk will take more time with GeminiPro - long time to load in comparison
                            # to other models
                            response = await asyncio.wait_for(ws.recv(), ws_timeout)

                            parsed_response = load_json_buffer(response)
                            if isinstance(parsed_response, dict):
                                if 'response' in parsed_response.keys():
                                    cleaned = parsed_response["response"].replace(END_OF_STREAM, "")
                                    response_payloads[qid]["response"] += cleaned
                                    if 'metadata' in parsed_response.keys() \
                                            or END_OF_STREAM in parsed_response['response']:
                                        response_payloads[qid]["metadata"] = parsed_response["metadata"]
                                        response_payloads[qid]["success"] = 1
                                        error_ct = 0
                                        break
                                else:
                                    # Connection ID expires - first chunk took more than 29 seconds.
                                    response_payloads[qid].update(parsed_response)
                                    raise ResponseDataError()
                            else:
                                response_payloads[qid]["response"] += response.replace(END_OF_STREAM, "")
                                if END_OF_STREAM in response:
                                    response_payloads[qid]["success"] = 1
                                    error_ct = 0
                                    break
                        # END - QUERY CHUNK LOOP
                        if error_ct == 0:
                            logging.info(f"Query ID {qid} completed... Message: {response_payloads[qid]['response']}")
                    queue.task_done()
                # END - QUERY QUEUE LOOP
        except (asyncio.TimeoutError, websockets.ConnectionClosed, Exception) as exc:
            if isinstance(exc, asyncio.TimeoutError):
                logging.error(f"Error {error_ct} on Question ID {qid} stream timeout: resetting connection...")
            elif isinstance(exc, ResponseDataError):
                logging.error(f"Error {error_ct} on Question ID {qid}: invalid response from endpoint.\n"
                              f"{response_payloads[qid]}")
            elif isinstance(exc, websockets.ConnectionClosed):
                logging.error(f"Error {error_ct} on Question ID {qid}: WebSocket connection closed on "
                              f"query ID {qid}. Reopening...")
            elif isinstance(exc, websockets.exceptions.InvalidStatusCode):
                logging.error(f"Error {error_ct} on Question ID {qid}: Server rejected the connection. "
                              f"Check URI again.")
            else:
                logging.error(f"Error {error_ct} on Question ID {qid}: {traceback.format_exc()}")

            try:
                # If the query is already complete, we don't want to increment the error count
                if response_payloads[qid]["success"] == 0:
                    error_ct += 1
                    # Reset buffer stream so that you don't get messed by pre-existing data.
                    response_payloads[qid]["response"] = ""
                else:
                    logging.info(f"Query ID {qid} completed...")
                    queue.task_done()
            except KeyError:
                logging.error(f"Question ID {qid} does not exist in the queue. Exiting...")
                return
            finally:
                # prevent any further retries if at error limit.
                if error_ct == error_threshold:
                    error_ct = 0
                time.sleep(reconnect_timeout_secs)
    # END - WEBSOCKET LOOP
    logging.info("WebSocket connection closed. Queue appears to be empty...")


@begin_task_execution
async def batch_query_llm_socket(model: ModelConfig, queries: Dict[Union[str, int], str],
                                 max_concurrent_tasks: int = 3,
                                 ws_timeout_min: int = 8,
                                 error_threshold: int = 100,
                                 reconnect_timeout_secs: int = 2) -> Dict[Union[str, int], Dict[str, Any]]:
    payloads = {}
    for qid, message in queries.items():
        payloads[qid] = model.compute_payload(message)

    response_payloads = {qid: DEFAULT_RESPONSE.copy() for qid in queries}

    if len(response_payloads) > 0:
        queue = asyncio.Queue()
        for qid, payload in payloads.items():
            await queue.put((qid, payload))
        tasks = [interact_with_websocket(model.api_url, queue, response_payloads,
                                         ws_timeout_min, error_threshold, reconnect_timeout_secs)
                 for _ in range(max_concurrent_tasks)]
        await asyncio.gather(*tasks)

    return response_payloads


@begin_task_execution
async def query_llm_socket(model: ModelConfig, query: str,
                           ws_timeout_min: int = 8,
                           error_threshold: int = 100,
                           reconnect_timeout_secs: int = 2) -> Dict[str, Any]:
    response_payloads = {0: DEFAULT_RESPONSE.copy()}
    tmp_payload = model.compute_payload(query=query)
    if query != "":
        queue = asyncio.Queue()
        await queue.put((0, tmp_payload))

        await interact_with_websocket(model.api_url, queue, response_payloads, ws_timeout_min,
                                      error_threshold, reconnect_timeout_secs)
    return response_payloads[0]
