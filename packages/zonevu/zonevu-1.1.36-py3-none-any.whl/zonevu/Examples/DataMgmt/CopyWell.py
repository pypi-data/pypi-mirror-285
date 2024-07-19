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

import copy
from ...Zonevu import Zonevu
from ...Services.WellService import WellData
from ...Services.Error import ZonevuError
from typing import Dict


def main_copy_well(zonevu: Zonevu, well_name: str, delete_code: str):
    """
    Retrieve a well and its surveys and make a copy
    :param zonevu: Zonevu instance
    :param well_name: Name of well to work with
    :param delete_code: delete code to use if an existing copy will be deleted
    :return:
    """
    well_svc = zonevu.well_service
    geosteer_svc = zonevu.geosteering_service

    well = well_svc.get_first_named(well_name, True)
    well_svc.load_well(well, {WellData.all})  # Load well and its surveys
    print('Copying Well %s%s (id=%d, UWI=%s)' % (well.name, well.number, well.id, well.uwi))
    print()

    well_copy_name = '%s_Copy' % well.name
    well_copy_uwi = '%s 3' % well_copy_name
    print('Copy will be named "%s"' % well_copy_name)

    # Delete well with same UWI as copy if any
    try:
        existing_copy = well_svc.find_by_uwi(well_copy_uwi)
        if existing_copy is not None:
            well_svc.delete_well(existing_copy.id, delete_code)
            print("Successfully deleted existing copy of the well named '%s'" % well_copy_name)
    except ZonevuError as error:
        print("Execution failed because %s" % error.message)
        raise error

    well_copy = well_svc.copy_well(well, well_copy_name, well_copy_uwi)

    print('Well copy for %s%s (id=%d, UWI=%s) succeeded' % (well_copy.name, well_copy.number, well_copy.id, well_copy.uwi))
    print()

