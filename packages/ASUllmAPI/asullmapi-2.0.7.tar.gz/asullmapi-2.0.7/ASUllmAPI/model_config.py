from typing import List, Union, Dict, Iterable
import collections.abc

__author__ = ['swliu', 'vshourie']


class ModelConfig:

    def __init__(self, access_token: str = None, action: str = None, api_url: str = "",
                 enhance_prompt_timezone: str = None, enhance_prompt_time: bool = None,
                 enhance_prompt_date: bool = None, enhance_prompt_verbosity: str = None,
                 enable_history: bool = False, enable_search: bool = True,  history: List[Dict[str, str]] = None,
                 model_max_tokens: int = None, model_temperature: float = None, model_top_k: int = None,
                 model_top_p: int = None, name: str = "", project_id: str = None, provider: str = "",
                 response_format_type: str = "", search_collection: str = "asu", search_db_type: str = "opensearch",
                 search_expr: str = None, search_output_fields: List[str] = None, search_reranker: bool = False,
                 search_retrieval_type: str = "chunk", search_source_name: List[str] = None, search_tags: list = None,
                 search_top_k: int = 3, search_prompt_mode: str = "unrestricted", search_prompt: str = None,
                 semantic_caching: bool = False, session_id: str = None, system_prompt: str = None):
        self.access_token = access_token
        self.action = action
        self.api_url = api_url
        self.enable_history = enable_history
        self.enable_search = enable_search
        self.enhance_prompt_timezone = enhance_prompt_timezone
        self.enhance_prompt_time = enhance_prompt_time
        self.enhance_prompt_date = enhance_prompt_date
        self.enhance_prompt_verbosity = enhance_prompt_verbosity
        self.history = history
        self.model_max_tokens = model_max_tokens
        self.model_temperature = model_temperature
        self.model_top_k = model_top_k
        self.model_top_p = model_top_p
        self.name = name
        self.project_id = project_id
        self.provider = provider
        self.response_format_type = response_format_type
        self.search_collection = search_collection
        self.search_db_type = search_db_type
        self.search_expr = search_expr
        self.search_output_fields = search_output_fields
        self.search_prompt = search_prompt
        self.search_prompt_mode = search_prompt_mode
        self.search_reranker = search_reranker
        self.search_retrieval_type = search_retrieval_type
        self.search_source_name = search_source_name
        self.search_tags = search_tags
        self.search_top_k = search_top_k
        self.semantic_caching = semantic_caching
        self.session_id = session_id
        self.system_prompt = system_prompt

        self.__validate_access()

    def add_history(self, history: Union[dict, Iterable[Dict[str, str]]]):
        if self.history is None:
            self.history = []
        if isinstance(history, dict):
            self.history.append(history)
        elif isinstance(history, collections.abc.Iterable):
            self.history.extend(history)
        else:
            raise ValueError("Iterable not supplied to `add_history()`.")

    def compute_headers(self):
        headers = {
            "Accept": "application/json",
            "Authorization": f'Bearer {self.access_token}'
        }
        return headers

    def compute_payload(self, query: str):
        payload = {"query": query}
        if self.action:
            payload["action"] = self.action
        if self.enable_history is not None:
            payload["enable_history"] = self.enable_history
        if self.enable_search is not None:
            payload["enable_search"] = self.enable_search
        if self.history:
            payload["history"] = self.history
        if self.name:
            payload["model_name"] = self.name
        if self.model_params:
            payload["model_params"] = self.model_params
        if self.provider:
            payload["model_provider"] = self.provider
        if self.project_id:
            payload["project_id"] = self.project_id
        if self.prompt_enhancers:
            payload["enhance_prompt"] = self.prompt_enhancers
        if self.response_format:
            payload["response_format"] = self.response_format
        if self.search_params:
            payload["search_params"] = self.search_params
        if self.semantic_caching:
            payload["semantic_caching"] = self.semantic_caching

        return payload

    @property
    def model_params(self):
        self.__validate_access()

        model_params = {}
        if self.model_temperature is not None:
            model_params["temperature"] = self.model_temperature
        if self.model_max_tokens is not None:
            model_params["max_tokens"] = self.model_max_tokens
        if self.model_top_p is not None:
            model_params["top_p"] = self.model_top_p
        if self.model_top_k is not None:
            model_params["top_k"] = self.model_top_k
        if self.system_prompt is not None:
            model_params["system_prompt"] = self.system_prompt
        return model_params

    @property
    def prompt_enhancers(self):
        self.__validate_access()

        prompt_enhancer_params = {}
        if self.enhance_prompt_date is not None:
            prompt_enhancer_params["date"] = self.enhance_prompt_date
        if self.enhance_prompt_time is not None:
            prompt_enhancer_params["time"] = self.enhance_prompt_time
        if self.enhance_prompt_timezone is not None:
            prompt_enhancer_params["timezone"] = self.enhance_prompt_timezone
        if self.enhance_prompt_verbosity is not None:
            prompt_enhancer_params["verbosity"] = self.enhance_prompt_verbosity

        return prompt_enhancer_params

    @property
    def search_params(self):
        self.__validate_access()

        search_params = {}
        if self.enable_search is True:
            search_params["db_type"] = self.search_db_type
            search_params["collection"] = self.search_collection
            search_params["top_k"] = self.search_top_k
            search_params["retrieval_type"] = self.search_retrieval_type

            if self.search_prompt_mode is not None:
                search_params["prompt_mode"] = self.search_prompt_mode
            if self.search_expr is not None:
                search_params["expr"] = self.search_expr
            if self.search_prompt is not None:
                search_params["search_prompt"] = self.search_prompt
            if self.search_source_name is not None:
                search_params["source_name"] = self.search_source_name
            if self.search_reranker is not None:
                search_params["reranker"] = self.search_reranker
            if self.search_tags is not None:
                search_params["tags"] = self.search_tags
            if self.search_output_fields is not None:
                search_params["output_fields"] = self.search_output_fields
        return search_params

    @property
    def response_format(self):
        self.__validate_access()

        response_format = {}
        if self.response_format_type:
            response_format['type'] = self.response_format_type
        return response_format

    def __validate_access(self):
        if not self.access_token:
            raise AccessTokenMissing
        if not self.api_url:
            raise APIUrlMissing

    def __str__(self):
        if self.enable_search:
            return f"{self.name}_search_enabled"
        else:
            return self.name

    def __repr__(self):
        return f"Model: {self.name}\tSearch Enabled: {str(self.enable_search)}"


class AccessTokenMissing(Exception):
    def __init__(self):
        self.message = "API access token is missing."


class APIUrlMissing(Exception):
    def __init__(self):
        self.message = "API url token is missing."
