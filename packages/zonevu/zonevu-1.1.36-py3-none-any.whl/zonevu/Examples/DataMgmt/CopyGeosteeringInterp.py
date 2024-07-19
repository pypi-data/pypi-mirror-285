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


# Phase I - Get an interpretation to copy
def main_copy_geosteer(zonevu: Zonevu, well_name: str, delete_code: str):
    """
    This script will locate a well in ZoneVu, and make a copy of the first geosteering interpretation named 'Main'.
    """
    well_svc = zonevu.well_service
    interp_svc = zonevu.geosteering_service

    well = well_svc.get_first_named(well_name)
    if well is None:
        print("Exiting since no well named '%s' found." % well_name)
        exit(1)

    well_svc.load_well(well, {WellData.geosteering})  # Load geosteering interpretations into well
    wellbore = well.primary_wellbore                # Get reference to wellbore
    if wellbore is None:
        print('Well has no wellbores, so exiting')
        return
    # Get reference to first geosteering interpretation on wellbore that doesn't end with 'copy'
    interp = next((item for item in wellbore.interpretations if not item.name.endswith('copy')), None)
    interp_svc.load_interpretation(interp)              # Load up the geosteering interpretation with all its data

    print("Geosteering interpretation = %s:" % interp.name)
    print("   Num picks = %d:" % len(interp.picks))
    print("   Num horizons = %d:" % len(interp.horizons))
    print("   Num curve defs = %d:" % len(interp.curve_defs))
    print()
    print("Successful execution")

    do_copy = True

    if do_copy:
        # Phase II - Delete Copy if it exists
        service = zonevu.geosteering_service
        interp_copy_name = "%s-copy" % interp.name
        try:
            existing_copy = next((item for item in wellbore.interpretations if item.name == interp_copy_name), None)
            if existing_copy is not None:
                service.delete_interpretation(existing_copy, delete_code)
                print("Delete_interpretation process was successful")
        except ZonevuError as error:
            print("Could not delete interpretation '%s' because %s" % (interp_copy_name, error.message))
            raise error

        # Phase III - Make a copy of the interpretation on the wellbore
        try:
            interp_copy = copy.deepcopy(interp)
            interp_copy.name = interp_copy_name
            service.add_interpretation(wellbore.id, interp_copy)
            print("Copy process was successful")
        except ZonevuError as error:
            print("Could not copy interpretation because %s" % error.message)



