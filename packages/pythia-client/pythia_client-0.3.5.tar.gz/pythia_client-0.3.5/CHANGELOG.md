#### v0.3.5
- Add Tika indexation mode. Compatible `haystack-api` v1.8.0

#### v0.3.4
- Add native qdrant filters compatibility. Compatible `haystack-api` v1.7.0

#### v0.3.3
- Small rework of the handling of parameters + new paremeters about threshold and returning embedding for light_query.
  Compatible `haystack-api` v1.6.0

#### v0.3.1
- New light_query function to do fast hybrid retrieval without LLM generated answer. Compatible `haystack-api` v1.5.0

#### v0.3.0
- New API key management functions (add, list, revoke). Compatible `haystack-api` v1.4.0

#### v0.2.4
- New optional priority_queue boolean for indexing job function. Compatible `haystack-api` v1.3.0

#### v0.2.3
- New function to get available documents for a specific group_id or pythia_document_category. Compatible with `haystack-api` v1.2.0
 
#### v0.2.2
- New function to get available keywords for a specific group_id or pythia_document_category. Compatible with `haystack-api` v1.1.0

#### v0.2.1
- Remove print debug. Compatible with `haystack-api` v1.0.0

#### v0.2.0
- Rewrote for future compatibility with the Pythia using PostGre. New endpoints (get files infos). Compatible with `haystack-api` v1.0.0

#### v0.1.10
- Remove req for Python 3.11 (>3.8 now). Compatible with `haystack-api` v0.2.4

#### v0.1.9
- Top K params for query function. Compatible with `haystack-api` v0.2.4

#### v0.1.8
- Custom system prompt params for query endpoint. Compatible with `haystack-api` v0.2.3

#### v0.1.7
- MetaJSON schema fix for Mistral models. Compatible with `haystack-api` v0.2.2

#### v0.1.6
- New intent functions: add_intent, predict_intent, delete_intent. Compatible with `haystack-api` v0.2.1

#### v0.1.4
- Minor ESR Ticket schema fix

#### v0.1.3
- Minor modification of Schema for structured data extraction.  Compatible with `haystack-api` v0.2.0

#### v0.1.0
- Major refactor of endpoints and function name to follow `haystack-api` refactoring

#### v0.0.11
- Renaming `owner` to `owner`.  Compatible with `haystack-api` v0.0.5

#### v0.0.10
- Fix Schema to make score optional (Qdrant compatibility).  Compatible with `haystack-api` v0.0.5

#### v0.0.9
- `upload_files` now return a simple json indicating that the background indexing task have been acception. New `get_indexing_tasks` function take an `owner` value as parameters and return the top 20 most recent indexing task and their results or status. New optional `owner` parameter for the query endpoint to indicate which user sent the message in the DB table log. Compatible with `haystack-api` v0.0.5

#### v0.0.8
- NEW: New optional parameter `chat_history` in the `.query()` method. It allows to add previous exchange with the LLM to the new query. Chat History must follow the ChatMessages format (dict containing: content, role, name, meta), see https://docs.haystack.deepset.ai/v2.0/docs/data-classes#chatmessage
- Compatible with `haystack-api` v0.0.4

#### v0.0.7
- New response Schema for the Haystack-API after version bump and removal of LiteLLM.

#### v0.0.6
- Added the new parameter `return_content` to the `get_docs_by_filters` method. The method `get_docs_by_filters` now by default doesn't return document content (to save on bandwidth). Set `return_content` to `True` to return the content of the documents.  

#### v0.0.5
- Initial Release. Compatible with `haystack-api` v0.0.1