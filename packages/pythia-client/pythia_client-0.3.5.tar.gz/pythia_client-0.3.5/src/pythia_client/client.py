"""A client for interacting with the API.

This module provides a client class for interacting with the API, including
indexing documents, listing them, deleting them, get S3 URL to a document,
querying them and extracting structured json data from text.

Classes:
    APIClient: Client for interacting with the API.
"""

import io
import json
import os
from typing import List, Optional, Literal, Tuple, Union, Dict, Any
from urllib.parse import urljoin

import requests

from .schema import (
    IndexingResponse,
    GetFileS3Reponse,
    SearchParams,
    LightSearchParams,
    FilterRequest,
    FilterDocStoreResponse,
    DeleteDocResponse,
    QueryRequest,
    QueryResponse,
    LightQueryResponse,
    DataExtractRequest,
    DataExtractResponse,
    ChatMessage,
    AddIntentResponse,
    PredictIntentResponse,
    DeleteIntentResponse,
    IndexingTask,
    DocInfos,
    KeywordsAvailable,
    DocsAvailable,
    PermissionsEnum,
    ApiKeys,
    ApiKeysRevoked,
)


class APIClient:
    """Client for interacting with the API.

    This class provides methods for interacting with the API, including
    indexing documents, listing them, deleting them, get S3 URL to a document,
    querying them and extracting structured json data from text.

    Attributes:
        url: The base URL for the API.
        api-key: The api key for the API.
        files_endpoint: The endpoint for files operation (upload, get).
        indexing_tasks_endpoint: The endpoint for indexing tasks.
        documents_by_filter_endpoint: The endpoint for documents operation by filters.
        documents_by_s3_key_endpoint: The endpoint for documents operation by S3 key.
        search_endpoint: The endpoint for querying.
        data_extraction_endpoint: The endpoint for extracting JSON data from text.
    """

    def __init__(self, url: str, api_key: str):
        """Initializes the API client with the given URL and the API key.

        Args:
            url: The base URL for the API.
            api_key: The api key for the API.

        Usage:
        ```python
        from pythia_client.client import APIClient
        client = APIClient("http://localhost:8000", "api-key")
        ```
        """
        self.url = url
        self.api_key = api_key
        self.files_endpoint = urljoin(str(self.url), "files")
        self.files_metadata_endpoint = urljoin(str(self.url), "files_metadata")
        self.indexing_tasks_endpoint = urljoin(str(self.url), "files/indexing-tasks")
        self.file_infos_endpoint = urljoin(str(self.url), "files/infos")
        self.documents_by_filter_endpoint = urljoin(str(self.url), "documents/filters")
        self.documents_by_s3_key_endpoint = urljoin(str(self.url), "documents/s3-key")
        self.search_endpoint = urljoin(str(self.url), "search/query")
        self.light_search_endpoint = urljoin(str(self.url), "search/light_query")
        self.data_extraction_endpoint = urljoin(
            str(self.url), "/data_extraction/extract-structured-data"
        )
        self.add_intent_endpoint = urljoin(str(self.url), "alie/intent")
        self.predict_intent_endpoint = urljoin(str(self.url), "alie/intent/predict")
        self.delete_intent_endpoint = urljoin(str(self.url), "alie/intent")
        self.api_keys_endpoint = urljoin(str(self.url), "/api_keys")

    def query(
        self,
        query: str,
        chat_history: Optional[List[ChatMessage]] = None,
            filters: Optional[Dict[str, Any]] = None,
            top_k=30,
        group_id: str = None,
        custom_system_prompt: str = None,
            threshold: float = 0.1,
            return_embedding: bool = False,
    ) -> QueryResponse:
        """Query the API with a user question to get a LLM-generated answer based
            on context from the document store.

            Args:
                query: The user question to be answered.
                chat_history: The chat history to provide context to the model. Should be a list of ChatMessage objects.
                filters: Qdrant native filter dict (https://qdrant.tech/documentation/concepts/filtering/) OR Haystack 2.0 filter dict (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering#filters).
                group_id: The name of the group_id the client making the request, for logging. Defaults to "api".
                custom_system_prompt: A custom system prompt to use for the LLM.
                threshold: The threshold to use for the LLM.
                return_embedding: If True, the response will include the embeddings of the documents that were used to generate the answer.

            Returns:
                The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

            Usage:
            ```python
            # Haystack Filter Style
            filters = {
                "operator": "AND",
                "conditions": [
                    {
                        "field": "meta.source",
                        "operator": "==",
                        "value": "Salesforce"
                    }
                ]
            }
            # Qdrant Filter Style
            filters =  {
                "must":[
                    {
                        "key":"meta.source",
                        "match":{
                            "value": "Salesforce"
                        }
                    }
                ]
            }
            query_response = client.query("Hey how are you", filters=filters)
            query_response.model_dump()
            ```
            Can also be used with chat history:
            ```python
            chat_history = [
                {
                    "content": "Hello Chatbot. My name is Corentin !",
                    "role": "user",
                    "name": None,
                    "meta": {},
                }
            ]
            response = client.query(
                query="Given our previous exchange of messages, what is my name ?",
                chat_history=chat_history,
            )
        ```
        """
        params = SearchParams(
            top_k=top_k,
            group_id=group_id,
            filters=filters,
            system_prompt=custom_system_prompt,
            return_embedding=return_embedding,
            threshold=threshold,
        ).model_dump()
        request = QueryRequest(
            query=query,
            chat_history=chat_history,
            params=params,
        )
        with requests.Session() as session:
            payload = json.loads(request.model_dump_json())
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }
            with session.post(
                self.search_endpoint, headers=headers, json=payload
            ) as response:
                if response.status_code == 200:
                    api_response = QueryResponse(**response.json())
                else:
                    api_response = None
        return api_response

    def light_query(
            self,
            query: str,
            filters: Optional[Dict[str, Any]] = None,
            top_k=30,
            group_id: str = None,
            threshold: float = 0.1,
            return_embedding: bool = True,
    ) -> LightQueryResponse:
        """Query the API with a user question to get a top-K similar document from hybrid search in the document store.
        No LLM-generated answer will be generated here and no complex post-processing for better results (no reranking, context extending).

            Args:
                query: The user request used to find similar documents by hybrid search.
                filters: Qdrant native filter dict (https://qdrant.tech/documentation/concepts/filtering/) OR Haystack 2.0 filter dict (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering#filters).
                top_k: The number of top similar documents to return.
                group_id: The name of the group_id the client making the request, for logging. Defaults to "api".
                threshold: The threshold to use for the LLM.
                return_embedding: If True, the response will include the embeddings of the documents that were used to generate the answer.

            Returns:
                The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

            Usage:
            ```python
            # Haystack Filter Style
            filters = {
                "operator": "AND",
                "conditions": [
                    {
                        "field": "meta.source",
                        "operator": "==",
                        "value": "Salesforce"
                    }
                ]
            }
            # Qdrant Filter Style
            filters =  {
                "must":[
                    {
                        "key":"meta.source",
                        "match":{
                            "value": "Salesforce"
                        }
                    }
                ]
            }
            light_query_response = client.light_query("OXO Update", filters=filters)
            light_query_response.model_dump()
            ```
        """
        params = LightSearchParams(
            top_k=top_k,
            group_id=group_id,
            filters=filters,
            return_embedding=return_embedding,
            threshold=threshold,
        ).model_dump()
        request = QueryRequest(
            query=query,
            params=params,
        )
        with requests.Session() as session:
            payload = json.loads(request.model_dump_json())
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }
            with session.post(
                    self.light_search_endpoint, headers=headers, json=payload
            ) as response:
                if response.status_code == 200:
                    api_response = LightQueryResponse(**response.json())
                else:
                    api_response = None
        return api_response

    def upload_files(
        self,
        files: List[Union[str, Tuple[str, io.IOBase]]],
        meta: Optional[List[dict]] = None,
            indexing_mode: Literal["unstructured", "tika"] = "unstructured",
        priority_queue: bool = False,
    ) -> IndexingResponse:
        """Index one or multiples files (documents) to the document store through the Haystack-API upload-file endpoint.
        It is recommended to add the following minimum metadata fields:
            - pythia_document_category (string, category name tag)
            - document_date (datetime)
            - language (string)
            - keywords (list)
            Example of value for meta field for the indexing of two files:
            ```json
            {
              "meta": [
                {
                    "pythia_document_category":"TDL Document",
                    "document_date":"2024-01-19 14:56",
                    "keywords":["ALE 400", "ALE 500"],
                    "language":"English",
                },
                {
                    "pythia_document_category":"Marketing Document
                    "document_date":"2024-01-19 14:58",
                    "keywords":["OXE 8", "OXE 9"],
                    "language":"Français",
                }
              ]
            }
            ```
        Args:
            files: The paths to the files OR tuples of filename and file object to index.
            meta: The list of metadata for the files.
            indexing_mode: The indexing mode between Unstructured and Apache Tika.

        Returns:
            The response from the API. Returns None if the status code is not 202.

        Usage:
        ```python
        index_response = client.upload_files(["path/to/file.pdf"], meta=[{"source": "Salesforce"}])
        {"message": "Files Submitted. Indexing task created."}
        index_response = client.upload_files([("file.pdf", file)], meta=[{"source": "Salesforce"}])
        {"message": "Files Submitted. Indexing task created."}
        ```
        """
        prepared_files = []
        for file in files:
            if isinstance(file, str):
                file_name = os.path.basename(file)
                with open(file, "rb") as f:
                    file_content = f.read()
            elif (
                isinstance(file, tuple)
                and len(file) == 2
                and isinstance(file[1], io.IOBase)
            ):
                file_name, file_object = file
                file_content = file_object.read()
            else:
                raise ValueError(
                    "Each file must be a file path or a tuple of (filename, fileIObyte)"
                )

            prepared_files.append(("files", (file_name, file_content)))

        with requests.Session() as session:
            payload = {"meta": json.dumps(meta), "priority_queue": priority_queue, "indexing_mode": indexing_mode}
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.post(
                self.files_endpoint,
                files=prepared_files,
                data=payload,
                headers=headers,
            ) as response:
                if response.status_code == 202:
                    api_response = response.json()
                else:
                    api_response = None
        return api_response

    def get_indexing_tasks_by_group_id(
        self, group_id: str, top: int = 20
    ) -> List[IndexingTask]:
        """Get the indexing tasks from the API.

        Args:
            group_id: The name of the group_id the client making the request, for logging. If none, the default group_id is "api" (set by the API itself).
            top: The number of top most recent indexing tasks to return.

        Returns:
            The response from the API. Returns None if the status code is not 200.

        Usage:
        ```python
        indexing_tasks = client.get_indexing_tasks(group_id="api", top=20)
        indexing_tasks.model_dump()
        ```
        """
        with requests.Session() as session:
            params = {"top": top}
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                self.indexing_tasks_endpoint + "/" + group_id,
                params=params,
                headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = [IndexingTask(**resp) for resp in response.json()]
                else:
                    api_response = None
        return api_response

    def get_indexing_task_by_s3_key(self, group_id: str, s3_key: str) -> IndexingTask:
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                self.indexing_tasks_endpoint + "/" + group_id + "/" + s3_key,
                headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = IndexingTask(**response.json())
                else:
                    api_response = None
        return api_response

    def get_file_infos_by_group_id(
        self, group_id: str, limit: int = 20
    ) -> List[DocInfos]:
        """Get all the file infos from the API for a specific group_id (owner).

        Args:
            group_id: The name of the group_id the client making the request (who indexed the file).
            limit: The number of top most recent indexed documents to return.

        Returns:
            The response from the API. Returns None if the status code is not 200.

        Usage:
        ```python
        document_list = client.get_file_infos_by_group_id(group_id="api", limit=20)
        for doc in document_list:
            doc.model_dump()
        ```
        """
        with requests.Session() as session:
            params = {"limit": limit}
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                self.file_infos_endpoint + "/" + group_id,
                params=params,
                headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = [DocInfos(**resp) for resp in response.json()]
                else:
                    api_response = None
        return api_response

    def get_file_infos_by_s3_key(self, group_id: str, s3_key: str) -> DocInfos:
        """Get the file infos from the API for a single file and a specific owner.

        Args:
            group_id: The name of the group_id the client making the request (who indexed the file).
            s3_key: The S3 Key of the file.

        Returns:
            The response from the API. Returns None if the status code is not 200.

        Usage:
        ```python
        document = client.get_file_infos_by_s3_key(group_id="api", s3_key="abc_sample.pdf")
        document.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                self.file_infos_endpoint + "/" + group_id + "/" + s3_key,
                headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = DocInfos(**response.json())
                else:
                    api_response = None
        return api_response

    def get_file_url(self, s3_key: str, page: Optional[int] = 1) -> GetFileS3Reponse:
        """Get a presigned URL to a file located on S3.

        Args:
            s3_key: The filename of the file to get.
            page: The page to directly point the URL.

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        get_doc_response = client.get_file_url("s3fd_sample.pdf", page=2)
        s3_url = get_doc_response.url
        ```
        """
        with requests.Session() as session:
            params = {"page": page}
            url = self.files_endpoint + "/" + s3_key
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                url,
                params=params,
                headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = GetFileS3Reponse(**response.json())
                else:
                    api_response = None
        return api_response

    def get_docs_by_filters(
        self,
            filters: Dict[str, Any] = None,
        return_content: bool = False,
    ) -> List[FilterDocStoreResponse]:
        """List all documents in the document store that match the filter provided.

        Args:
            filters: Qdrant native filter dict (https://qdrant.tech/documentation/concepts/filtering/) OR Haystack 2.0 filter dict (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering#filters).
            return_content: If True, the content of the documents will be returned.

        Returns:
            The response from the API. Returns None if the status code is not 200.

        Usage:
        ```python
        # Haystack Filter Style
        filters = {
            "operator": "AND",
            "conditions": [
                {
                    "field": "meta.source",
                    "operator": "==",
                    "value": "Salesforce"
                }
            ]
        }
        # Qdrant Filter Style
        filters =  {
            "must":[
                {
                    "key":"meta.source",
                    "match":{
                        "value": "Salesforce"
                    }
                }
            ]
        }
        list_response = client.get_docs_by_filters(filters=filters)
        list_response.model_dump()
        ```
        """
        request = FilterRequest(filters=filters)
        with requests.Session() as session:
            payload = json.loads(request.model_dump_json())
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }
            if return_content:
                endpoint = f"{self.documents_by_filter_endpoint}?return_content=true"
            else:
                endpoint = self.documents_by_filter_endpoint

            with session.post(endpoint, headers=headers, json=payload) as response:
                if response.status_code == 200:
                    responses = response.json()
                    api_response = [
                        FilterDocStoreResponse(**resp) for resp in responses
                    ]
                else:
                    api_response = None
        return api_response

    def delete_docs_by_filters(
        self,
            filters: Dict[str, Any] = None,
    ) -> DeleteDocResponse:
        """Remove documents from the API document store.

        Args:
            filters: Qdrant native filter dict (https://qdrant.tech/documentation/concepts/filtering/) OR Haystack 2.0 filter dict (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering#filters).

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.
        Usage:
        ```python
        # Haystack Filter Style
        filters = {
            "operator": "AND",
            "conditions": [
                {
                    "field": "meta.source",
                    "operator": "==",
                    "value": "Salesforce"
                }
            ]
        }
        # Qdrant Filter Style
        filters =  {
            "must":[
                {
                    "key":"meta.source",
                    "match":{
                        "value": "Salesforce"
                    }
                }
            ]
        }
        remove_response = client.delete_docs_by_filters(filters=filters)
        remove_response.model_dump()
        ```
        """
        request = FilterRequest(filters=filters)
        with requests.Session() as session:
            payload = json.loads(request.model_dump_json())
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }
            with session.delete(
                self.documents_by_filter_endpoint, headers=headers, json=payload
            ) as response:
                if response.status_code == 200:
                    api_response = DeleteDocResponse(**response.json())
                else:
                    api_response = None
        return api_response

    def get_docs_by_s3_key(self, s3_key: str) -> List[FilterDocStoreResponse]:
        """Get documents (chunk of files in the Vector DB) from the API document store based on its S3 key.

        Args:
            s3_key: the S3 key of the file

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.
        Usage:
        ```python
        chunks_list = client.get_docs_by_s3_key(s3_key="abc_sample.pdf")
        for chunk in chunks_list:
            chunk.model_dump()
        ```
        """
        with requests.Session() as session:
            url = self.documents_by_s3_key_endpoint + "/" + s3_key
            headers = {"X-API-Key": self.api_key}
            with session.get(url, headers=headers) as response:
                if response.status_code == 200:
                    api_response = [
                        FilterDocStoreResponse(**resp) for resp in response.json()
                    ]
                else:
                    api_response = None
        return api_response

    def delete_docs_by_s3_key(self, s3_key: str) -> DeleteDocResponse:
        """Delete documents (chunk of files in the Vector DB) from the API document store based on its S3 key.

        Args:
            s3_key: the S3 key of the file

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.
        Usage:
        ```python
        delete_response = client.delete_docs_by_s3_key(s3_key="abc_sample.pdf")
        delete_response.model_dump()
        ```
        """
        with requests.Session() as session:
            url = self.documents_by_s3_key_endpoint + "/" + s3_key
            headers = {"X-API-Key": self.api_key}
            with session.delete(url, headers=headers) as response:
                if response.status_code == 200:
                    api_response = DeleteDocResponse(**response.json())
                else:
                    api_response = None
        return api_response

    def extract_structured_data(
        self,
        text_content: str,
    ) -> DataExtractResponse:
        """Query the API to extract structured JSON from unstructured text.

        Args:
            text_content: The text to process.

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        extract_response = client.extract_structured_data("Hello I want to modify the delivery date of order FR73681920")
        extract_response.model_dump()
        ```
        """
        request = DataExtractRequest(
            email_content=text_content,
        )
        with requests.Session() as session:
            payload = json.loads(request.model_dump_json())
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }
            with session.post(
                self.data_extraction_endpoint, headers=headers, json=payload
            ) as response:
                if response.status_code == 200:
                    response = DataExtractResponse(**response.json())
                else:
                    response = None
        return response

    def add_intent(
        self,
        intent_data: Dict[str, List[str]],
    ) -> AddIntentResponse:
        """Add intent data to the intent prediction engine.

        Args:
            intent_data: Dict containing intent data.

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        intent_data = {"greet": ["Hey", "Hello", "Bonjour"], "help": ["I need help", "Show help"]}
        add_intent_response = client.add_intent(intent_data)
        add_intent_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.post(
                self.add_intent_endpoint, headers=headers, data=json.dumps(intent_data)
            ) as response:
                if response.status_code == 200:
                    response = AddIntentResponse(**response.json())
                else:
                    response = None
        return response

    def predict_intent(
        self,
        user_msg: str,
    ) -> PredictIntentResponse:
        """Query the API to predict the intent of a user message.

        Args:
            user_msg: The content of the user message.

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        intent = client.predict_intent("Hello I want to modify the delivery date of order FR73681920")
        intent.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                self.predict_intent_endpoint,
                headers=headers,
                params={"user_message": user_msg},
            ) as response:
                if response.status_code == 200:
                    response = PredictIntentResponse(**response.json())
                else:
                    response = None
        return response

    def delete_intent(
        self,
        intent_name: str,
    ) -> DeleteIntentResponse:
        """Delete the specified intent from the database. Use "*" to delete all intents from the databse (clear the DB).

        Args:
            intent_name: The name of the intent to delete. Use "*" to delete all intents from the databse (clear the DB).

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        delete_intent_response = client.delete_intent("greet")
        delete_intent_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.delete(
                self.delete_intent_endpoint,
                headers=headers,
                params={"intent_name": intent_name},
            ) as response:
                if response.status_code == 200:
                    response = DeleteIntentResponse(**response.json())
                else:
                    response = None
        return response

    def get_keywords_by_group_id(
        self,
        group_id: str,
    ) -> KeywordsAvailable:
        """Get available keywords for a specific group id.

        Args:
            group_id: The group_id that own the documents

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        keyword_response = client.get_keywords_by_group_id("e567-768bey-810c")
        keyword_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                self.files_metadata_endpoint + f"/keywords/by_group_id/{group_id}",
                headers=headers,
            ) as response:
                if response.status_code == 200:
                    response = response.json()
                else:
                    response = None
        return response

    def get_keywords_by_pythia_doc_category(
        self,
        pythia_doc_category: str,
    ) -> KeywordsAvailable:
        """Get available keywords for a specific pythia document category.

        Args:
            pythia_doc_category: The pythia_doc_category that was provided during document indexation.

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        keyword_response = client.get_keywords_by_pythia_doc_category("TDL Document")
        keyword_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                self.files_metadata_endpoint
                + f"/keywords/by_pythia_doc_category/{pythia_doc_category}",
                headers=headers,
            ) as response:
                if response.status_code == 200:
                    response = response.json()
                else:
                    response = None
        return response

    def get_docs_by_group_id(
        self,
        group_id: str,
    ) -> List[DocsAvailable]:
        """Get available documents for a specific group id.

        Args:
            group_id: The group_id that own the documents

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        docs_response = client.get_docs_by_group_id("e567-768bey-810c")
        docs_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                self.files_metadata_endpoint + f"/documents/by_group_id/{group_id}",
                headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = [DocsAvailable(**resp) for resp in response.json()]
                else:
                    api_response = None
        return api_response

    def get_docs_by_pythia_doc_category(
        self,
        pythia_doc_category: str,
    ) -> List[DocsAvailable]:
        """Get available documents for a specific pythia document category.

        Args:
            pythia_doc_category: The pythia_doc_category that was provided during document indexation.

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        docs_response = client.get_docs_by_pythia_doc_category("TDL Document")
        docs_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                self.files_metadata_endpoint
                + f"/documents/by_pythia_doc_category/{pythia_doc_category}",
                headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = [DocsAvailable(**resp) for resp in response.json()]
                else:
                    api_response = None
        return api_response

    def create_api_key(
            self,
            name: str,
            creator_id: str,
            group_id: str,
            permission: PermissionsEnum,
    ) -> ApiKeys:
        """Create an API key for a group_id.

        Args:
            name: The name of the API key.
            creator_id: The creator_id of the API key (streamlit user often).
            group_id: The group_id of the API key (cognito group name).
            permission: The permission of the API key  (full or read).

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        api_response = client.create_api_key("my key", "e9824-d710c-f9018-82jh", "btq-group", "full")
        api_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            data = {
                "name": name,
                "creator_id": creator_id,
                "group_id": group_id,
                "permission": permission,
            }
            with session.post(
                    self.api_keys_endpoint + "/create", headers=headers, json=data
            ) as response:
                if response.status_code == 200:
                    api_response = ApiKeys(**response.json())
                else:
                    api_response = None
        return api_response

    def revoke_api_key(
            self,
            api_key_to_revoke: str,
            creator_id: str,
    ) -> ApiKeys:
        """Revoke and API key.

        Args:
            api_key_to_revoke: The API key to revoke
            creator_id: The creator_id of the API key (streamlit user often).

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        api_response = client.revoke_api_key(api_key_to_revoke="abe4arg84are9g4bear65gb16DS61", creator_id="e9824-d710c-f9018-82jh")
        api_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            data = {"creator_id": creator_id}
            with session.delete(
                    self.api_keys_endpoint + f"/revoke/{api_key_to_revoke}",
                    params=data,
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = ApiKeysRevoked(**response.json())
                else:
                    api_response = None
        return api_response

    def list_api_keys_by_group_id(
            self,
            group_id: str,
    ) -> List[ApiKeys]:
        """List API Keys for a specific group_id.

        Args:
            group_id: Group ID to list the API keys from

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        api_response = client.list_api_keys_by_group_id(group_id="btq-group")
        api_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.api_keys_endpoint + f"/list/group_id/{group_id}",
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = [ApiKeys(**resp) for resp in response.json()]
                else:
                    api_response = None
        return api_response

    def list_api_keys_by_creator_id(
            self,
            creator_id: str,
    ) -> List[ApiKeys]:
        """List API Keys for a specific group_id.

        Args:
            creator_id: Group ID to list the API keys from

        Returns:
            The response from the API as a Pydantic model. You can use reponse.model_dump() to get a Dict. Returns None if the status code is not 200.

        Usage:
        ```python
        api_response = client.list_api_keys_by_creator_id(creator_id="e9824-d710c-f9018-82jh")
        api_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.api_keys_endpoint + f"/list/creator_id/{creator_id}",
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = [ApiKeys(**resp) for resp in response.json()]
                else:
                    api_response = None
        return api_response
