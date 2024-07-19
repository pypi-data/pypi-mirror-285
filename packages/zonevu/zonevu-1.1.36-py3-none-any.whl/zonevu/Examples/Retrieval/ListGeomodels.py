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


def main_list_geomodels(zonevu: Zonevu, name: str):
    geomodel_svc = zonevu.geomodel_service

    print('Geomodels:')
    geomodels = geomodel_svc.get_geomodels(name)
    for entry in geomodels:
        print('%s (%s) (%s - %s)' % (entry.name, entry.id, entry.division.name, entry.division.id))
        if entry.name != 'Elk Hills':
            continue
        try:
            geomodel = geomodel_svc.find_geomodel(entry.id)
            print('   Geomodel %s has %s datagrids and %s structures' %
                  (geomodel.name, len(geomodel.data_grids), len(geomodel.structures)))
            print('   Strat column = %s (%s)' % (geomodel.strat_column.name, geomodel.strat_column.id))

        except ZonevuError as err:
            print('Geomodel "%s" had an issue: %s' % (entry.name, err.message))

    print("Execution was successful")

