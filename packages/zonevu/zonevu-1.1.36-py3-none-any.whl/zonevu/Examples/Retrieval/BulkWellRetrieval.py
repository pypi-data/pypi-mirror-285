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
from typing import List
from ...DataModels.Wells.Well import WellEntry
from typing import Optional
from ...Services.WellService import WellData
from ...Services.Client import ZonevuError
from ...DataModels.Geosteering.Calcs import make_evenly_spaced_picks
from ...DataModels.Geosteering.Interpretation import Interpretation
import time


def main(zonevu: Zonevu, exact_match: bool = True, name: Optional[str] = None, max_count: Optional[int] = None):
    print('List wells in ZoneVu account with geosteering interpretations')
    well_svc = zonevu.well_service
    geosteer_svc = zonevu.geosteering_service
    entries = well_svc.find_by_name(name, exact_match)

    num_interps_processed = 0
    max_interps_to_process = max_count if max_count is not None else 100
    num_successes = 0
    num_failures = 0
    valid_interps: List[Interpretation] = []
    invalid_interps: List[(WellEntry, Interpretation)] = []
    for entry in entries:
        well = well_svc.find_by_id(entry.id)
        well_svc.load_well(well, {WellData.geosteering, WellData.logs})

        # Hard-wired test.  Delete.
        # wellbore = well.primary_wellbore
        # logs = wellbore.welllogs
        # log = logs[1]
        # curve_groups = log.curve_groups
        # curve_group = curve_groups[0]
        # # Get curve group samples
        # well_log_svc = zonevu.welllog_service
        # well_log_svc.load_splice_curve_samples(curve_group)

        interps = well.primary_wellbore.interpretations
        for interp in interps:
            num_interps_processed += 1
            bad_picks = [p for p in interp.picks if not p.valid]
            print('Well "%s": Processing geosteering interp "%s"' % (well.full_name, interp.name))
            print('   - Num picks = %s' % len(interp.picks))

            if not interp.valid:
                invalid_interps.append((entry, interp))
                print('   - Warning: Interpretation %s has messed up picks!' % interp.name)
                continue

            try:
                valid_interps.append(interp)
                interval = 1
                evenly_spaced_picks = make_evenly_spaced_picks(interp=interp, interval=interval)
                num_successes += 1

                print('   - Made %s evenly spaced picks MD %s - %s.' %
                      (len(evenly_spaced_picks), round(evenly_spaced_picks[0].md), round(evenly_spaced_picks[-1].md)))
            except ZonevuError as err:
                print('   * Processing picks failed because %s' % err.message)
                num_failures += 1

        if num_interps_processed >= max_interps_to_process:
            break

    print('Completed geosteering interpretation processing.')
    print('   %s successfully processed.' % num_interps_processed)
    print('   %s failed to process.' % num_failures)
    print('   %s in total processed' % num_interps_processed)

    print('Interpretations with invalid picks = %s:' % len(invalid_interps))
    for item in invalid_interps:
        well_entry, interp = item
        bad_picks = [p for p in interp.picks if not p.valid]
        print('  Well "%s" - interp "%s"' % (well_entry.full_name, interp.name))



