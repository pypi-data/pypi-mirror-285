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
from ...Services.Client import ZonevuError
from ...Services.WellService import WellData
from ...DataModels.Geosteering.Calcs import create_extended_picks
from tabulate import tabulate
from typing import Union, List
from ...DataModels.Geosteering.Blocks import Block, Fault
from ...DataModels.Geosteering.Calcs import make_blocks_and_faults, get_block_type_curve_info, GeosteerIter


def print_blocks_table(zonevu: Zonevu, well_name: str):
    """
    Retrieve well data from ZoneVu
    For the first geosteering interpretation, output a table of geosteering blocks and faults
    """
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    well_name = well.full_name
    print(f'Well named "{well_name}" was successfully found with id={well.id}')
    well_svc.load_well(well, {WellData.geosteering})  # Load geosteering into well
    wellbore = well.primary_wellbore  # Get reference to wellbore
    if wellbore is None:
        print('Well has no wellbores, so exiting')
        return
    print(f'Primary wellbore id={wellbore.id}')

    # If available, create a flattened out data structure of the geosteering interpretation
    interps = wellbore.interpretations
    for interp in interps:
        print(f'Interpretation: {interp.name}, starred={interp.starred}, owner={interp.owner_name}, company={interp.owner_company_name}, vis={interp.visibility}, edit={interp.editability}')
        print(f'Geosteering blocks and faults for interpretation "{interp.name}"')
        table = []
        n = 0
        headers = ['N', 'Type', 'MD Start', 'MD End', 'MDLength', 'TVD Start', 'TVD End', 'Throw',
                   'Inclination', 'Type Curve']
        for item in GeosteerIter(interp):
            if isinstance(item, Block):
                n += 1
                layer = item.target_layer
                inclination = item.inclination
                type_curve = get_block_type_curve_info(interp, item)
                info = type_curve.name if type_curve is not None else 'Unknown'
                table.append([n, item.kind, round(item.md_start, 1), round(item.md_end, 1), round(item.md_length, 1),
                              round(layer.tvd_start, 1), round(layer.tvd_end, 1), '',
                              round(inclination, 3), info])
            elif isinstance(item, Fault):
                throw = item.target_throw
                table.append([n, item.kind, round(item.md), '', '', round(throw.tvd_start),
                              round(throw.tvd_end), round(throw.throw_amt, 1), ''])
        print(tabulate(table, headers=headers, tablefmt='plain'))


