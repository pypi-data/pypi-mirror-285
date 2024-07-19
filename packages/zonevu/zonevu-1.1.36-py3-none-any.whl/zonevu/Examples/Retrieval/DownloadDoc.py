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

from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from azure.storage.blob import BlobServiceClient
from pathlib import Path


def main(zonevu: Zonevu, well_name: str) -> None:
    print('Retrieve a well and one of its documents')
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    if len(well.documents) > 0:
        doc = well.documents[0]
        doc_service = zonevu.document_service
        cred = doc_service.get_doc_download_credential(doc)
        blob_svc = BlobServiceClient(account_url=cred.url, credential=cred.token)
        client = blob_svc.get_blob_client(container=cred.container, blob=cred.path)
        blob_exists = client.exists()

        if blob_exists:
            cloud_path = Path(cred.path)
            path = Path('c:/delme') / (cloud_path.stem + '2' + cloud_path.suffix)
            with open(file=path, mode="wb") as local_file:
                download_stream = client.download_blob()
                local_file.write(download_stream.readall())

    print('Completed')




