#  Copyright (c) 2024 Ubiterra Corporation. All rights reserved.
#  #
#  This ZoneVu Python SDK software is the property of Ubiterra Corporation.
#  You shall use it only in accordance with the terms of the ZoneVu Service Agreement.
#  #
#  This software is made available on PyPI for download and use. However, it is NOT open source.
#  Unauthorized copying, modification, or distribution of this software is strictly prohibited.
#  #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
#
#
#
#

from .Client import Client
from ..DataModels.Document import Document
from ..Services.Storage import AzureCredential, Storage
from pathlib import Path
from azure.storage.blob import BlobServiceClient
from typing import Optional
from ..Services.Client import ZonevuError


class DocumentService:
    client: Client

    def __init__(self, c: Client):
        self.client = c

    def create_document(self, doc: Document):
        """
        Create document in ZoneVu document index
        :param doc: The document index entry.
        :return:
        """
        if not doc.is_valid():
            raise ZonevuError.local('The document entry for "%s" is not valid' % doc.name)

        url = 'document/add'
        item = self.client.post(url, doc.to_dict(), False)
        server_doc = Document.from_dict(item)
        doc.id = server_doc.id

    def get_doc_download_credential(self, doc: Document) -> AzureCredential:
        url = 'document/download/credential/%s' % doc.id
        item = self.client.get(url)
        cred = AzureCredential.from_dict(item)
        return cred

    def get_doc_upload_credential(self, doc: Document) -> AzureCredential:
        url = 'document/upload/credential/%s' % doc.id
        item = self.client.get(url)
        cred = AzureCredential.from_dict(item)
        return cred

    def save_doc(self, doc: Document, base_path: Path, storage: Storage) -> None:
        """
        Download and save a document to storage
        :param doc:
        :param base_path:
        :param storage:
        :return:
        """
        cred = self.get_doc_download_credential(doc)
        blob_svc = BlobServiceClient(account_url=cred.url, credential=cred.token)
        client = blob_svc.get_blob_client(container=cred.container, blob=cred.path)
        byte_data: bytes = client.download_blob().readall()

        if client.exists():
            local_path = base_path / doc.path
            storage.save(local_path, byte_data)

    def download_doc(self, doc: Document, directory: Path, filename: Optional[str] = None) -> None:
        """
        Download a document to a specified path on disk
        :param doc: the specified document
        :param directory: path for output document.
        :param filename: optional filename for output document file. If not provided, the original file name is used.
        :return:
        """
        cred = self.get_doc_download_credential(doc)
        blob_svc = BlobServiceClient(account_url=cred.url, credential=cred.token)
        client = blob_svc.get_blob_client(container=cred.container, blob=cred.path)

        exists = client.exists()
        if exists:
            try:
                output_path = directory / filename if filename else directory / doc.name
                with open(output_path, 'wb') as output_file:
                    total_bytes = 0
                    for chunk in client.download_blob().chunks():
                        total_bytes += len(chunk)
                        output_file.write(chunk)
                        percent_downloaded = round(100 * total_bytes / (1024 * 1024 * doc.size))
                        print('%s%% downloaded' % percent_downloaded)
            except ZonevuError as err:
                print('Download of the requested document "%s" failed because.' % err.message)
                raise err
        else:
            print('The requested document "%s" does not exist.' % doc.name)

    def upload_doc(self, doc: Document, input_doc_path: Path) -> None:
        cred = self.get_doc_upload_credential(doc)
        blob_svc = BlobServiceClient(account_url=cred.url, credential=cred.token)
        client = blob_svc.get_blob_client(container=cred.container, blob=cred.path)
        try:
            with open(input_doc_path, "rb") as data:
                client.upload_blob(data)
        except ZonevuError as err:
            print('Download of the requested document "%s" failed because.' % err.message)
            raise err



