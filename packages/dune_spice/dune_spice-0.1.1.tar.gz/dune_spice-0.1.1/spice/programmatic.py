"""Functions for managing queries programmatically. Most users do not need this."""
from __future__ import annotations

from typing import Any, Literal, Mapping, Sequence, TypedDict, cast
from typing_extensions import NotRequired

from . import _urls
from ._types import Query


class QueryMetadata(TypedDict):
    query_id: int
    name: str
    description: str
    tags: Sequence[str]
    version: int
    parameters: Mapping[str, Any]
    query_sql: str
    params: Mapping[str, ParameterSpec]
    is_private: bool
    archived: bool


class ParameterSpec(TypedDict):
    name: str
    type: Literal['text', 'number', 'datetime', 'enum']
    value: Any
    enum_options: NotRequired[Sequence[Any]]


def create_query(
    sql: str,
    *,
    name: str | None = None,
    description: str | None = None,
    parameters: Mapping[str, ParameterSpec] | None = None,
    private: bool = True,
    api_key: str | None = None,
) -> int:
    """create new query

    # Parameters
    - sql: sql content of query
    - name: name of query
    - description: description of query
    - parameters: parameters of query
    - private: whether query is private
    - api_key: Dune api key
    """
    import requests

    # process inputs
    headers = _urls.get_headers(api_key=api_key)
    url = _urls.url_templates['query_create']
    data = {
        'name': name,
        'description': description,
        'parameters': parameters,
        'query_sql': sql,
        'is_private': private,
    }
    data = {k: v for k, v in data.items() if v is not None}

    # perform request
    response = requests.post(url, headers=headers)

    # process result
    result = response.json()
    if 'query_id' in result:
        query_id: int = result['query_id']
        return query_id
    else:
        raise Exception(result['error'])


def read_query(query: Query, api_key: str | None = None) -> QueryMetadata:
    """read query content and metadata

    # Parameters
    - query: query id or query url
    - api_key: Dune api key
    """
    import requests

    # process inputs
    headers = _urls.get_headers(api_key=api_key)
    query_id = _urls.get_query_id(query)
    url = _urls.url_templates['query'].format(query_id=query_id)

    # perform request
    response = requests.get(url, headers=headers)

    # process result
    result = response.json()
    if 'query_id' in result:
        return cast(QueryMetadata, result)
    else:
        raise Exception(result['error'])


def update_query(
    query: Query,
    *,
    sql: str | None = None,
    name: str | None = None,
    description: str | None = None,
    tags: Sequence[str] | None = None,
    parameters: Mapping[str, ParameterSpec] | None = None,
    private: bool | None = None,
    archive: bool | None = None,
    api_key: str | None = None,
) -> int:
    """update query

    # Parameters
    - query: query id or query url
    - sql: sql content of query
    - name: name of query
    - description: description of query
    - tags: list of tags for query
    - parameters: parameters of query
    - private: whether query is private
    - archive: whether to archive or unarchive query
    - api_key: Dune api key
    """
    import json
    import requests

    # process inputs
    headers = _urls.get_headers(api_key=api_key)
    query_id = _urls.get_query_id(query)
    url = _urls.url_templates['query'].format(query_id=query_id)
    data = {
        'name': name,
        'description': description,
        'tags': tags,
        'parameters': parameters,
        'query_sql': sql,
        'is_private': private,
        'is_archived': archive,
    }
    data = {k: v for k, v in data.items() if v is not None}

    # perform request
    response = requests.patch(url, headers=headers, data=json.dumps(data))

    # process result
    result = response.json()
    if 'query_id' in result:
        query_id = result['query_id']
        return query_id
    else:
        raise Exception(result['error'])


def delete_query(query: Query, api_key: str | None = None) -> int:
    """delete query (archive the query)

    # Parameters
    - query: query id or query url
    - api_key: Dune api key
    """
    return update_query(query=query, api_key=api_key, archive=True)
