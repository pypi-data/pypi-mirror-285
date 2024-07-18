import json
import logging
import os
import time

import requests
from src.pythia_client.client import APIClient


class ValueStorage:
    s3_keys = None
    s3_keys_nbd = None
    api_key = None
    api_key_revoked = None


logging.basicConfig(
    filename="test.log",
    filemode="w",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s: %(message)s",
)

URL = os.getenv("HAYSTACK_API_URL", "http://localhost:8000/")
SECRET_MASTER_API_KEY = os.getenv("SECRET_MASTER_API_KEY", "corentin")

timestamp = time.strftime("%Y%m%d-%H%M%S")

client = APIClient(url=URL, api_key=SECRET_MASTER_API_KEY)


def test_create_api_key():
    response = client.create_api_key(
        name="test_nbd_key",
        creator_id="streamlit_userid",
        group_id="nbd",
        permission="read_only",
    )
    assert response is not None
    response_dict = response.model_dump()
    assert response_dict["name"] == "test_nbd_key"
    assert response_dict["creator_id"] == "streamlit_userid"
    assert response_dict["group_id"] == "nbd"
    assert response_dict["permission"] == "read_only"
    ValueStorage.api_key = response_dict

    response = client.create_api_key(
        name="test_nbd_key",
        creator_id="streamlit_userid",
        group_id="nbd",
        permission="read_only",
    )
    ValueStorage.api_key_revoked = response.model_dump()


def test_revoke_api_key():
    response = client.revoke_api_key(
        api_key_to_revoke=ValueStorage.api_key_revoked["api_key"],
        creator_id="streamlit_userid",
    )
    assert response is not None
    response_dict = response.model_dump()
    assert response_dict["name"] == "test_nbd_key"
    assert response_dict["creator_id"] == "streamlit_userid"
    assert response_dict["group_id"] == "nbd"
    assert response_dict["permission"] == "read_only"
    assert response_dict["revoked"] == True


def test_list_api_keys_by_group_id():
    response = client.list_api_keys_by_group_id(group_id="nbd")
    assert response is not None
    assert len(response) == 1
    assert response[0].model_dump()["group_id"] == ValueStorage.api_key["group_id"]


def test_list_api_keys_by_creator_id():
    response = client.list_api_keys_by_creator_id(creator_id="streamlit_userid")
    assert response is not None
    assert len(response) == 1
    assert response[0].model_dump()["creator_id"] == ValueStorage.api_key["creator_id"]


def test_key_working():
    client_nbd = APIClient(url=URL, api_key=ValueStorage.api_key["api_key"])
    response = client_nbd.query(
        query="How to give port 8 a power of 1337 milliwatts ?", top_k=2
    )
    assert len(response.AnswerBuilder.answers[0].data) > 10


def test_api_key_filters_qdrant():
    filters = {
        "must": [
            {
                "key": "meta.group_id",
                "match": {
                    "value": timestamp
                }
            }
        ]
    }
    client_nbd = APIClient(url=URL, api_key=ValueStorage.api_key["api_key"])
    response = client_nbd.get_docs_by_filters(filters=filters, return_content=True)

    assert response is not None
    assert response == []  # Nothing uploaded yet

def test_key_limited():
    client_nbd = APIClient(url=URL, api_key=ValueStorage.api_key["api_key"])
    file_paths = [
        "test/samples/sample3.pdf",
    ]
    file_names = ["sample3.pdf"]
    tuple_files = [
        (file_name, open(file_path, "rb"))
        for file_name, file_path in zip(file_names, file_paths)
    ]
    meta = [
        {
            "meta3": "value3",
            "source_test": "pytest_client_api",
            "group_id": timestamp,
            "portfolio": ["value1", "value2"],
        },
    ]
    response = client_nbd.upload_files(
        files=tuple_files, meta=meta, priority_queue=False
    )
    assert response is None  # Error Forbidden !


def test_key_revoked():
    client_nbd = APIClient(url=URL, api_key=ValueStorage.api_key_revoked["api_key"])
    response = client_nbd.query(
        query="How to give port 8 a power of 1337 milliwatts ?", top_k=2
    )
    assert response is None  # Error Forbidden !


def test_upload_files():
    file_paths = [
        "test/samples/sample1.pdf",
        "test/samples/sample2.pdf",
    ]
    meta = [
        {
            "meta1": "value1",
            "source_test": "pytest_client_api",
            "group_id": timestamp,
            "keywords": ["keyword1", "keyword2"],
            "portfolio": ["value1", "value2"],
            "pythia_document_category": "category1",
        },
        {
            "meta2": "value2",
            "source_test": "pytest_client_api",
            "group_id": timestamp,
            "portfolio": ["value1", "value2"],
            "keywords": ["keyword3"],
            "pythia_document_category": "category2",
        },
    ]
    response = client.upload_files(files=file_paths, meta=meta, priority_queue=True, indexing_mode="unstructured")
    ValueStorage.s3_keys = response["s3_keys"]
    assert response["message"] == "Files Submitted. Indexing tasks created."
    assert len(response["s3_keys"]) == 2
    assert response["group_id"] == timestamp


def test_client_upload_files_from_bytes():
    file_paths = [
        "test/samples/sample3.pdf",
    ]
    file_names = ["sample3.pdf"]
    tuple_files = [
        (file_name, open(file_path, "rb"))
        for file_name, file_path in zip(file_names, file_paths)
    ]
    meta = [
        {
            "meta3": "value3",
            "source_test": "pytest_client_api",
            "group_id": timestamp,
            "portfolio": ["value1", "value2"],
        },
    ]
    response = client.upload_files(files=tuple_files, meta=meta, priority_queue=False, indexing_mode="tika")
    assert response["message"] == "Files Submitted. Indexing tasks created."
    assert len(response["s3_keys"]) == 1
    assert response["group_id"] == timestamp


def test_client_get_indexing_task_by_s3_key():
    response = client.get_indexing_task_by_s3_key(
        group_id=timestamp, s3_key=ValueStorage.s3_keys[0]
    )
    response_dict = response.model_dump()
    assert response is not None
    assert isinstance(response.model_dump(), dict)
    assert response_dict["status"] in ["initialized", "processing", "completed"]
    assert response_dict["group_id"] == timestamp
    assert response_dict["s3_key"] == ValueStorage.s3_keys[0]


def test_client_get_indexing_tasks():
    time.sleep(60)
    response = client.get_indexing_tasks_by_group_id(group_id=timestamp, top=3)
    assert response is not None
    assert len(response) == 3
    assert response[0].status == "completed"


def test_client_get_file_info_by_s3_key():
    time.sleep(60)
    response = client.get_file_infos_by_s3_key(
        group_id=timestamp, s3_key=ValueStorage.s3_keys[0]
    )
    assert response is not None
    response_dict = response.model_dump()
    assert response_dict["s3_key"] == ValueStorage.s3_keys[0]
    assert response_dict["group_id"] == timestamp
    assert isinstance(response_dict["file_meta"], dict)


def test_client_get_file_info_by_group_id():
    time.sleep(60)
    response = client.get_file_infos_by_group_id(group_id=timestamp, limit=2)
    assert response is not None
    assert len(response) == 2
    response_dict = response[0].model_dump()
    assert response_dict["group_id"] == timestamp


def test_client_get_file_url():
    s3_key = ValueStorage.s3_keys[0]
    page = 1
    response = client.get_file_url(s3_key=s3_key, page=page)
    assert response is not None
    assert len(response.url) >= 100
    aws_s3_response = requests.get(response.url, verify=False)
    assert aws_s3_response.status_code == 200


def test_client_get_keywords_available_for_group_id():
    response_get_keywords = client.get_keywords_by_group_id(group_id=timestamp)
    assert response_get_keywords is not None
    assert "value1" in response_get_keywords["keywords"]
    assert "keyword1" in response_get_keywords["keywords"]
    assert len(response_get_keywords["keywords"]) == 5


def test_client_get_keywords_available_for_pythia_doc_category():
    response_get_keywords = client.get_keywords_by_pythia_doc_category(
        pythia_doc_category="category2"
    )
    assert response_get_keywords is not None
    assert "keyword3" in response_get_keywords["keywords"]
    assert len(response_get_keywords["keywords"]) == 3


def test_client_get_docs_by_group_id():
    response_get_docs = client.get_docs_by_group_id(group_id=timestamp)
    assert response_get_docs is not None
    assert "s3_keys" in response_get_docs[0].model_dump()
    assert response_get_docs[0].meta_subfolder == timestamp
    assert isinstance(response_get_docs, list)
    assert len(response_get_docs) == 3


def test_client_get_docs_by_pythia_doc_category():
    response_get_docs = client.get_docs_by_pythia_doc_category(
        pythia_doc_category="category2"
    )
    assert response_get_docs is not None
    assert "s3_keys" in response_get_docs[0].model_dump()
    assert isinstance(response_get_docs, list)
    assert len(response_get_docs) == 1


def test_client_query():
    response = client.query(
        query="How to give port 8 a power of 1337 milliwatts ?", top_k=2
    )
    assert response is not None
    assert len(response.AnswerBuilder.answers[0].data) > 20
    assert len(response.AnswerBuilder.answers[0].documents) == 2


def test_client_light_query():
    response = client.light_query(
        query="How to give port 8 a power of 1337 milliwatts ?", top_k=2
    )
    assert response is not None
    assert response.AnswerBuilder.answers[0].data == ""
    assert len(response.AnswerBuilder.answers[0].documents) == 2
    assert len(response.AnswerBuilder.answers[0].documents[0].embedding) >= 100


def test_client_query_with_custom_prompt():
    system_prompt = (
        """Start all your answers with the word "Banana", this is really important."""
    )
    response = client.query(
        query="Hey how are you ?", custom_system_prompt=system_prompt
    )
    assert response is not None
    generated_content = response.AnswerBuilder.answers[0].data
    assert "Banana" in generated_content
    assert len(generated_content) > 20


def test_client_query_with_history():
    chat_history = [
        {
            "content": "Hello Chatbot. My name is Corentin !",
            "role": "user",
            "name": None,
            "meta": {},
        },
        {
            "content": "Hello, nice to meet you. How can I help you today",
            "role": "assistant",
            "name": None,
            "meta": {},
        },
    ]
    response = client.query(
        query="Given our previous exchange of messages, what is my name ?",
        chat_history=chat_history,
    )
    assert response is not None
    assert "corentin" in response.AnswerBuilder.answers[0].data.lower()


def test_client_query_with_history_and_group_id():
    chat_history = [
        {
            "content": "Hello Chatbot. My name is Corentin !",
            "role": "user",
            "name": None,
            "meta": {},
        },
        {
            "content": "Hello, nice to meet you. How can I help you today",
            "role": "assistant",
            "name": None,
            "meta": {},
        },
    ]
    response = client.query(
        query="Given our previous exchange of messages, what is my name ?",
        chat_history=chat_history,
        group_id="corentin",
    )
    assert response is not None
    assert "corentin" in response.AnswerBuilder.answers[0].data.lower()


def test_client_get_docs_by_s3_key():
    s3_key = ValueStorage.s3_keys[0]
    response = client.get_docs_by_s3_key(s3_key)
    response_dict = response[0].model_dump()
    assert response is not None
    assert len(response) >= 2
    assert isinstance(response_dict["meta"], dict)


def test_client_get_docs_by_filters():
    filters = {
        "operator": "AND",
        "conditions": [
            {
                "field": "meta.group_id",
                "operator": "==",
                "value": timestamp,
            }
        ],
    }
    response = client.get_docs_by_filters(filters=filters, return_content=True)

    assert response is not None
    assert len(response) >= 5
    assert len(response) < 20
    assert len(response[0].content) > 20
    assert response[0].meta["source_test"] == "pytest_client_api"
    assert response[0].meta["filename"] in response[0].meta["s3_key"]


def test_client_get_docs_by_qdrant_filters():
    filters = {
        "must": [
            {
                "key": "meta.group_id",
                "match": {
                    "value": timestamp
                }
            }
        ]
    }

    response = client.get_docs_by_filters(filters=filters, return_content=True)

    assert response is not None
    assert len(response) >= 5
    assert len(response) < 20
    assert len(response[0].content) > 20
    assert response[0].meta["source_test"] == "pytest_client_api"
    assert response[0].meta["filename"] in response[0].meta["s3_key"]

def test_client_delete_docs_by_s3_key():
    response = client.delete_docs_by_s3_key(s3_key=ValueStorage.s3_keys[0])
    assert response is not None
    assert response.n_deleted_documents >= 1
    assert response.n_deleted_s3 == 1
    assert len(response.deleted_s3_keys) == 1


def test_client_delete_docs_by_filters():
    filters = {
        "operator": "AND",
        "conditions": [
            {
                "field": "meta.group_id",
                "operator": "==",
                "value": timestamp,
            }
        ],
    }
    response = client.delete_docs_by_filters(filters=filters)

    assert response is not None
    assert response.n_deleted_documents >= 3
    assert response.n_deleted_s3 == 2
    assert len(response.deleted_s3_keys) == 2


def test_client_extract_structured_data():
    email = """Bonjour, Je vous écris car j'ai un problème avec la commande FR082475927. Deux DECT Intercorm ont un défaut et ne s'allument pas, pouvez-vous m'aider ? Bonne journée, Cordialement,Entreprise MEDICOMPANY SAS"""

    response = client.extract_structured_data(text_content=email)

    assert len(response.schema_validator.validated) == 1

    formatted_json = json.loads(response.schema_validator.validated[0].content)

    assert response is not None
    assert len(formatted_json["company_or_client_name"]) > 5
    assert formatted_json["ticket_category"] == "AVR or DOA or HWS"
    assert len(formatted_json["ticket_category"]) > 5
    assert formatted_json["command_number"][0:2] == "FR"


def test_client_add_intent():
    data = {
        "pycharm_update": ["help to update pycharm", "latest pycharm update is bugged"],
        "elden_ring": ["elden ring boss", "tree of life from elden ring"],
        "team_fortress": [
            "team fortress best class",
            "unlock all achievement team fortress",
        ],
    }
    response = client.add_intent(intent_data=data)
    response_dict = response.model_dump()
    assert response is not None
    assert response_dict["Writter"]["documents_written"] == 6


def test_client_predict_intent():
    response = client.predict_intent(
        user_msg="How to go to the tree of life in elden ring"
    )
    response_dict = response.model_dump()
    assert response is not None
    assert response_dict["intent"] == "elden_ring"


def test_client_delete_intent():
    response = client.delete_intent(intent_name="elden_ring")
    response_dict = response.model_dump()
    assert response is not None
    assert response_dict["deleted_intent"] == "elden_ring"
    assert response_dict["n_deleted_intent_data"] == 2

    response = client.delete_intent(intent_name="pycharm_update")
    response_dict = response.model_dump()
    assert response is not None
    assert response_dict["deleted_intent"] == "pycharm_update"
    assert response_dict["n_deleted_intent_data"] == 2

    response = client.delete_intent(intent_name="team_fortress")
    response_dict = response.model_dump()
    assert response is not None
    assert response_dict["deleted_intent"] == "team_fortress"
    assert response_dict["n_deleted_intent_data"] == 2


def test_clean_up_after_test():
    response = client.revoke_api_key(
        api_key_to_revoke=ValueStorage.api_key["api_key"], creator_id="streamlit_userid"
    )
    filters = {
        "operator": "AND",
        "conditions": [
            {
                "field": "meta.pythia_document_category",
                "operator": "==",
                "value": "category2",
            }
        ],
    }
    response_doc_delete = client.delete_docs_by_filters(filters=filters)
    assert response is not None
    assert response_doc_delete is not None
