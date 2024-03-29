import logging
import os
from typing import Optional

import attr
from google.cloud import firestore as firestore
from google.cloud.firestore_v1 import DocumentSnapshot


@attr.s(auto_attribs=True)
class IFirestoreDb:
    _client: firestore.Client
    _logger = logging.getLogger(__name__)

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

    def add_document_to_collection(
            self,
            collection_id: str,
            document_dict: dict,
            document_id: Optional[str] = None
    ):
        self._logger.debug(f'Adding {document_dict} to collection {collection_id}')
        self._client.collection(collection_id).add(
            document_data=document_dict,
            document_id=document_id
        )
        self._logger.debug('Document added')

    def read_document_data(
            self,
            collection_id: str,
            document_id: str,
            document_fields: Optional[str] = None
    ) -> DocumentSnapshot:
        collection = self._client.collection(collection_id)
        document = collection.document(document_id)
        document_data = document.get(document_fields)
        return document_data

    def read_all_data_from_collection(
            self,
            collection_id: str,
    ) -> dict:
        collection = self._client.collection(collection_id)
        documents = collection.stream()

        documents_dict = {document.id: document.to_dict() for document in documents}
        return documents_dict if len(documents_dict) > 0 else {'empty': None}
