import requests
import json
import urllib.parse

from .document import Document


class CouchDBException(Exception):
    response: requests.Response


class CouchDB:
    def __init__(self,
                 username: str,
                 password: str,
                 db: str,
                 host: str = 'localhost',
                 port: int = 5984,
                 scheme: str = 'http',
                 base_path: str = ''):
        self.base_url = f'{scheme}://{username}:{password}@{host}:{port}/{base_path}'
        self.db_name = db

    def req(self,
            endpoint: str,
            method: str = 'GET',
            data: dict = None,
            query_params: dict = None) -> dict | list:
        if query_params is not None:
            params = '?' + urllib.parse.urlencode(query_params)
        else:
            params = ''
        response = requests.request(
            method,
            self.base_url + self.db_name + '/' + endpoint + params,
            json=data if data is not None else {})

        if not response.ok:
            ex = CouchDBException(response.content)
            ex.response = response
            raise ex

        return json.loads(response.text)

    def get_all_documents(self, skip: int = None, limit: int = None) -> list[Document]:
        params = {
            'include_docs': True
        }
        if skip is not None:
            params['skip'] = skip
        if limit is not None:
            params['limit'] = limit

        result = []
        for doc in self.req('_all_docs', 'GET', query_params=params)['rows']:
            if not doc['id'].startswith('_design'):  # ignore design documents
                result.append(Document(self, doc['doc']))
        return result


    def get_document(self, document_id: str) -> Document | None:
        try:
            return Document(self, self.req(document_id, 'GET'))
        except CouchDBException as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e

    def find_documents(
        self,
        selector: dict,
        fields: dict = None,
        sort: list = None,
        limit: int = None,
        skip: int = None
    ) -> list[Document]:
        data = {
            'selector': selector
        }
        if sort is not None:
            data['sort'] = sort
        if fields is not None:
            data['fields'] = fields
        if limit is not None:
            data['limit'] = limit
        if skip is not None:
            data['skip'] = skip

        result = []
        for doc in self.req('_find', 'POST', data)['docs']:
            result.append(Document(self, doc))
        return result

    def find_one_document(self, selector: dict, fields: dict = None, sort: list = None, skip: int = None) -> Document | None:
        result = self.find_documents(selector, fields, sort, 1, skip)
        if not result:
            return None
        return result[0]

    def document(self, data: dict = None) -> Document:
        return Document(self, data)
