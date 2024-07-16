import uuid
import typing

if typing.TYPE_CHECKING:
    from .couchdb import CouchDB


class Document:
    data = {}

    def __init__(self, db: 'CouchDB', data: dict = None):
        if data is not None:
            self.data = data

        if '_id' not in data:
            self.data['_id'] = str(uuid.uuid4())

        self.id = self.data['_id']

        self.db = db

    def update(self) -> list | dict:
        if '_rev' not in self.data:
            document = self.db.get_document(self.id)
            self.data['_rev'] = document['_rev']
        result = self.db.req(self.id, 'PUT', self.data)
        self.data['_rev'] = result['rev']
        return result

    def create(self) -> list | dict:
        result = self.db.req(self.id, 'PUT', self.data)
        self.data['_rev'] = result['rev']
        return result

    def delete(self) -> list | dict:
        return self.db.req(self.id, 'DELETE', query_params={
            'rev': self.data['_rev']
        })

    def __contains__(self, item: str) -> bool:
        return item in self.data

    def __getitem__(self, key: str) -> any:
        return self.data[key]

    def __setitem__(self, key: str, value: any):
        self.data[key] = value

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.data}>'
