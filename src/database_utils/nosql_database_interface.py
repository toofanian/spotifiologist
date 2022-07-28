import os
from abc import ABC, abstractmethod
from typing import Optional

import attr
from google.cloud import firestore as firestore


@attr.s(auto_attribs=True)
class INoSqlDatabase(ABC):

    @abstractmethod
    def add_document(
            self,
            collection_id: str,
            document_dict: dict,
            document_id: Optional[str] = None
    ):
        ...

    @abstractmethod
    def read_data(
            self,
            collection_id: str
    ):
        ...


@attr.s(auto_attribs=True)
class IMongoDb(INoSqlDatabase):

    def add_document(
            self,
            collection_id: str,
            document_dict: dict,
            document_id: Optional[str] = None
    ):
        ...

    def read_data(self, collection_id: str):
        pass


@attr.s(auto_attribs=True)
class IFirebaseDb(INoSqlDatabase):
    client: firestore.Client

    @classmethod
    def from_credentials(
            cls,
            credentials: Optional[any] = None
    ):
        client = firestore.Client(
            credentials=credentials
        )
        return cls(
            client=client
        )

    @classmethod
    def with_env_variable(
            cls,
            env_var_path: str
    ):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env_var_path
        client = firestore.Client()
        return cls(
            client=client
        )

    def add_document(
            self,
            collection_id: str,
            document_dict: dict,
            document_id: Optional[str] = None
    ):
        self.client.collection(collection_id).add(
            document_data=document_dict,
            document_id=None
        )

    def read_data(
            self,
            collection_id: str,
    ):
        collection = self.client.collection(collection_id)
        documents = collection.stream()

        documents_dict = {document.id: document.to_dict() for document in documents}
        return documents_dict
