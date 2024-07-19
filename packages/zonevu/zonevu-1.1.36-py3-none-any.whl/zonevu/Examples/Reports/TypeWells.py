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

from ...Zonevu import Zonevu
from typing import List, Dict
from ...DataModels.Wells.Well import WellEntry
from typing import Optional
from ...Services.WellService import WellData
from ...Services.Client import ZonevuError
from ...DataModels.Geosteering.Calcs import make_evenly_spaced_picks
from ...DataModels.Geosteering.Interpretation import Interpretation
from ...DataModels.Geosteering.CurveDef import CurveDef, CurveDefWellboreRoleEnum
from dataclasses import dataclass
import csv


@dataclass
class TypeWellEntry:
    division_id: int
    division_name: str
    well_id: int
    well_name: str
    target_well_id: int
    target_well_name: str
    interpretation_id: int
    interpretation_name: str


def main(zonevu: Zonevu, output_path: str, exact_match: bool = True, name: Optional[str] = None, max_count: Optional[int] = None):
    print('Generate a CSV file list of type wells, as used by geosteering interpretations in this zonevu account.')
    well_svc = zonevu.well_service
    well_entries = well_svc.find_by_name(name, exact_match)
    num_entries = len(well_entries)
    print('Processing %s wells' % num_entries)

    invalid_interps_count = 0
    type_well_dict: Dict[int, List[TypeWellEntry]] = {}
    well_count = 0

    def process_well_entry(my_well_entry: WellEntry):
        print('Processing well #%s of %s (%s)' % (well_count, num_entries, my_well_entry.full_name))
        well = well_svc.find_by_id(my_well_entry.id)
        well_svc.load_well(well, {WellData.geosteering})

        interps = well.primary_wellbore.interpretations
        for interp in interps:
            if not interp.valid:
                print('   - Warning: Interpretation %s has messed up picks!' % interp.name)
                continue

            try:
                for d in interp.curve_defs:
                    if d.wellbore_role == CurveDefWellboreRoleEnum.TypeWellbore:
                        type_well_entry = TypeWellEntry(my_well_entry.division.id, my_well_entry.division.name,
                                                        d.well_id, d.well_name, well.id, well.full_name,
                                                        interp.id,interp.name)

                        if d.well_id not in type_well_dict:
                            type_well_dict[d.well_id] = []
                        type_well_dict[d.well_id].append(type_well_entry)
            except ZonevuError as err:
                print('   * Processing interp %s failed because %s' % (interp.name, err.message))

    for well_entry in well_entries:
        try:
            well_count += 1
            if well_count >= max_count:
                break
            process_well_entry(well_entry)
        except ZonevuError as well_load_err:
            print('Could not process well "%s" because %s' % well_load_err.message)
        except BaseException as base_err:
            print('Could not process well "%s" because %s' % base_err)

    print('Outputting CSV file as "%s"' % output_path)

    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['DivisionId', 'DivisionName', 'TypeWellId', 'TypeWellName', 'TargetWellId', 'TargetWellName',
                         'InterpretationId', 'InterpretationName'])
        all_entries = [e for entries in type_well_dict.values() for e in entries]
        all_entries.sort(key=lambda e: e.well_name)
        for e in all_entries:
            writer.writerow([e.division_id, e.division_name, e.well_id, e.well_name, e.target_well_id,
                             e.target_well_name, e.interpretation_id, e.interpretation_name])

