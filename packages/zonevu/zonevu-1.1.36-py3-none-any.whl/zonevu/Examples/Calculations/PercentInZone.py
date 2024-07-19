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

# Import the modules
import math
from ...Services.Client import ZonevuError
from ...Zonevu import Zonevu
from ...Services.WellService import WellData
from tabulate import tabulate
from ...DataModels.Geosteering.Calcs import calc_percent_in_zone


def main_zone_calcs(zonevu: Zonevu, well_name: str):
    """
    Retrieve well data from ZoneVu and do some zone calculations
    """
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    print('Well named "%s" was successfully found' % well_name)
    well_svc.load_well(well, {WellData.surveys, WellData.geosteering})  # Load surveys and geosteering into well
    wellbore = well.primary_wellbore  # Get reference to wellbore
    if wellbore is None:
        print('Well has no wellbores, so exiting')
        return

    # Get reference to the deviation surveys on wellbore
    survey = wellbore.actual_survey
    if survey is None:
        print('Wellbore has no actual survey, so exiting')
        return

    # If available, plot the starred or first geosteering interpretation
    interps = wellbore.interpretations
    if len(interps) == 0:
        print('No geosteering interpretations available for that well')
        return

    for interp in interps:
        print(f'Interpretation: {interp.name}, starred={interp.starred}, owner={interp.owner_name}, company={interp.owner_company_name}, vis={interp.visibility}, edit={interp.editability}')
        zonevu.geosteering_service.load_interpretation(interp)      # Load picks into interpretation

        # Output a table of the geosteering picks
        # picks = interp.picks
        picks = [p for p in interp.picks if p.tvd is not None and math.isfinite(p.tvd)]
        # pick_type = 'Block' if p.block_flag else 'Fault' if p.fault_flag else 'Other'
        headers = ["n", "MD",  "TVD", "Type", "TypeWellId"]
        alignment = ["left", "left", "left", "left"]
        table = [
            [index,
            round(p.md, 1),
            round(p.tvd or 0, 1),
            'Block' if p.block_flag else 'Fault' if p.fault_flag else 'Other',
            p.type_wellbore_id] for index, p in enumerate(picks)
        ]

        print()
        print('Geosteering picks')
        print(tabulate(table, headers, tablefmt="plain", colalign=alignment))
        print()

        # Compute and output a table of the percent in zone for each horizon in the interpretation
        valid_stations = survey.valid_stations
        landing_index = next((i for i, sta in enumerate(valid_stations) if sta.inclination is not None and sta.inclination > 88), 0)  # Start of lateral
        lateral_stations = valid_stations[landing_index:]
        # stations = [s for s in raw_lateral_stations if s.tvd is not None]  # Cleaned up list of lateral stations
        zone_calcs = calc_percent_in_zone(interp, lateral_stations)
        lateral_length = sum(
            s2.md - s1.md for s1, s2 in zip(lateral_stations, lateral_stations[1:]))  # Sum of all horizon/formation traversals
        if lateral_length != 0:
            for calc in zone_calcs:
                calc.percent = 100 * calc.length / lateral_length
        zones_length = sum(calc.length for calc in zone_calcs)  # Sum of all horizon/formation traversals
        headers = ["Horizon",  "Length", "%", "Color"]
        alignment = ["left", "left", "Left", "Left"]
        table = [
            [calc.horizon.name, round(calc.length, 1), '%s%%' % round(calc.percent, 1), calc.horizon.get_line_color()] for calc in zone_calcs
        ]
        table.append(['Total', round(zones_length), '100%', '(All Zones Length)'])
        table.append(['Total', round(lateral_length), '100%', '(Lateral Length)'])
        print('Zone Calculations')
        print(tabulate(table, headers, tablefmt="plain", colalign=alignment))

    print('end')





