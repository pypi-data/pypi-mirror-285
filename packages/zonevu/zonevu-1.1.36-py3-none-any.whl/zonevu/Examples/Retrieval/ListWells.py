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


def main(zonevu: Zonevu, exact_match: bool = True, name: Optional[str] = None) -> List[WellEntry]:
    print('List all wells in ZoneVu account')
    well_svc = zonevu.well_service
    well_entries = well_svc.find_by_name(name, exact_match)
    print('Number of wells retrieved = %s' % len(well_entries))
    for index, well_entry in enumerate(well_entries):
        print('%s, ' % well_entry.full_name, end="")
        if index % 5 == 0:
            print()

    divisions = [w.division.name for w in well_entries]
    unique_divisions = set(divisions)
    print()
    print()
    print('Wells exist in the following divisions:')
    for d in unique_divisions:
        print('   %s' % d)

    return well_entries

