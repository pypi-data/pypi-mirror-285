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
from ...Services.WellData import WellData
from ...Services.Storage import Storage, FileStorage


def main(zonevu: Zonevu, storage: Storage, well_name: str) -> None:
    """
    Write or update a named well from a ZoneVu account to user storage.
    :param zonevu: Zonevu client instance
    :param storage: User storage to save wells to
    :param well_name: Name of well to retrieve and save
    """
    print('Save a well to storage')
    # Find well with that name
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local(f'Could not find the well "{well_name}"')

    up_to_date = well.current(storage)  # Find out if well is in user storage & if it is current
    if up_to_date:
        print(f'Well "{well_name}" is already saved in storage "{storage.get_name()}" and is up to date')
    if not up_to_date:
        well_svc.load_well(well, {WellData.all})    # Load data into well from ZoneVu
        well.save(storage)                          # Save well to storage outside ZoneVu
        well.save_documents(zonevu.document_service, storage)  # Save well documents to storage outside ZoneVu
        print(f'Well "{well_name}" saved to storage "{storage.get_name()}"')
