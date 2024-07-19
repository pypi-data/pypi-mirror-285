
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


def main_list_geosteering(zonevu: Zonevu, well_name: str):
    """
    This script will find the named well, and list the geosteering interpretations on its primary wellbore
    :param zonevu: Zonevu instance
    :param well_name: Name of well to work with
    :return:
    """
    # Get needed Web API services
    print('Listing of geosteering interpretations for primary wellbore of well "%s"' % well_name)
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name, True)
    if well is None:
        print('Could not find the well named"%s"' % well_name)
        return
    if well.primary_wellbore is None:
        print('Could not find primary wellbore on well')
        return

    geosteer_svc = zonevu.geosteering_service
    interp_entries = geosteer_svc.get_interpretations(well.primary_wellbore.id)
    if len(interp_entries) == 0:
        print('There are no geosteering interpretations on that well')
    else:
        print('Geosteering Interpretations:')
        for interp in interp_entries:
            starred = '*' if interp.starred else ' '
            print('   Interpretation %s - %s (%s)' % (interp.name, starred, interp.id))
        # Re-retrieve first entry as a test. Can use this to check on status of an interpretation.
        first_entry = interp_entries[0]
        first_entry_changed = geosteer_svc.interpretation_changed(first_entry)
        print('Change flag for interpretation "%s" = %s' % (first_entry.name, first_entry_changed))

    print('Execution complete')
