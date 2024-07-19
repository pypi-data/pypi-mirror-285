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
from ...Services.Storage import Storage


def main(zonevu: Zonevu, well_name: str, storage: Storage) -> None:
    """
    Find a named well in ZoneVu and in user storage, and compare them
    :param zonevu: Zonevu client instance
    :param well_name: Name of well to retrieve and save
    :param storage: User storage to save wells to
    """
    print('Retrieve the same well from ZoneVu and from Storage and compare')

    # Find well with that name in Zonevu
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    # Load data into well from Zonevu
    well_svc.load_well(well, {WellData.all})

    # Get stored well
    stored_well = well.retrieve(well.archive_local_dir_path, storage)
    if stored_well is None:
        print('There was no stored version of that well')
        return

    # Compare
    if stored_well is not None:
        same_version = well.row_version == stored_well.row_version
        assert same_version, 'Stored version of that well has a different version number that zonevu version'

        same = well == stored_well
        assert same, 'The data in the stored version should match the zonevu version but does not'




