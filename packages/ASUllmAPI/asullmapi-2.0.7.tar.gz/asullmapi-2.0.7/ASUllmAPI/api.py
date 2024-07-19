import json
import requests
import traceback
from time import sleep

from .model_config import ModelConfig

__author__ = ['swliu', 'vshourie']


def query_llm(model: ModelConfig, query: str, num_retry: int = 3,
              success_sleep: float = 0, fail_sleep: float = 1) -> dict:
    response_dict = {"response": ""}
    for i in range(num_retry):
        try:
            payload = model.compute_payload(query=query)
            headers = model.compute_headers()
            response = requests.post(model.api_url, json=payload, headers=headers)
            response_text = response.json()

            # We parse through relevant keys
            for key in response_text.keys():
                response_dict[key] = response_text[key]

            if success_sleep > 0:
                sleep(success_sleep)

        except Exception as e:
            print(traceback.format_exc())
            if fail_sleep > 0:
                sleep(fail_sleep)
    return response_dict


def query_model_info_api(model: ModelConfig, num_retry: int = 3,
                         success_sleep: float = 1.0, fail_sleep: float = 1.0) -> list:
    """
    :param model: A ModelConfig configured with the model info endpoint URL AND the access key at a minimum.
    :param num_retry: int
    :param success_sleep: seconds to delay execution when API call successful (float)
    :param fail_sleep: seconds to delay execution when API call unsuccessful (float)
    :return: a list of large language models that are hosted by ASU
    """
    for i in range(num_retry):
        try:
            headers = model.compute_headers()
            response = requests.get(url=model.api_url, headers=headers)
            models_dict = json.loads(response.content)
            models = models_dict["models"]
            if success_sleep > 0:
                sleep(success_sleep)
            return models
        except Exception as e:
            print(traceback.format_exc())
            if fail_sleep > 0:
                sleep(fail_sleep)
            continue
    return []


def model_provider_mapper(models: list) -> dict:
    mapper = {
        model["name"]: model["provider"]
        for model in models
    }
    return mapper


def model_list(models: list) -> set:
    models = {model["name"] for model in models}
    return models
