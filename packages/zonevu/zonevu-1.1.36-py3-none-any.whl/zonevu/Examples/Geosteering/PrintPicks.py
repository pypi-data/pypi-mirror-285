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

from ...DataModels.Geosteering.Pick import Pick
from ...DataModels.Geospatial.GeoLocation import GeoLocation
from ...DataModels.Geospatial.Coordinate import Coordinate
from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...Services.WellService import WellData
from ...DataModels.Geosteering.Calcs import create_extended_picks
from tabulate import tabulate


def main_geosteering_picks(zonevu: Zonevu, well_name: str):
    """
    Retrieve well data from ZoneVu
    For all the geosteering interpretations, create flattened geosteering picks.
    """
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    well_name = well.full_name
    print('Well named "%s" was successfully found' % well_name)
    well_svc.load_well(well, {WellData.geosteering})  # Load surveys and geosteering into well
    wellbore = well.primary_wellbore  # Get reference to wellbore
    if wellbore is None:
        print('Well has no wellbores, so exiting')
        return

    strat_cols = well_svc.get_stratcolumns(well)
    for interp in wellbore.interpretations:
        # If available, create a flattened out data structure of the geosteering interpretation
        # Output a table of the retrieved geosteering picks
        table = []
        n = 0
        for p in interp.picks:
            n += 1
            pick_kind = 'Block' if p.block_flag else 'Fault' if p.fault_flag else 'Other'
            table.append([n, pick_kind, round(p.md), round(p.target_tvd), round(p.target_elevation)])
        headers = ['N', 'Type', 'MD', "TVD", "Elev"]
        print()
        print('Geosteering picks for interpretation "%s"' % interp.name)
        print(tabulate(table, headers=headers, tablefmt='plain'))

        # Output a table of geosteering picks for each horizon in the interpretation
        print()
        print('Geosteering picks and horizon elevations for interpretation "%s"' % interp.name)
        extended_picks = create_extended_picks(interp, strat_cols)
        table = []
        n = 0
        for p in extended_picks:
            n += 1
            table.append([n, p.md, p.latitude, p.longitude, '', '', ''])
            for h in p.horizon_depths:
                # NOTE: the tvt is h.tvt
                target_symbol = '*' if h.target else ''
                table.append([n, '', '', '', h.formation.symbol, target_symbol, round(h.elevation, 1)])

        headers = ['N', 'MD', "Latitude", "Longitude", "Formation", "Target", "Elevation"]
        print(tabulate(table, headers=headers, tablefmt='plain'))





