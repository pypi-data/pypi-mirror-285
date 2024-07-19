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
from tests.test_globals import get_test_zonevu


def main_list_projects(zonevu: Zonevu):
    project_svc = zonevu.project_service

    print('Projects:')
    project_entries = project_svc.get_projects()
    project_entries.sort(key=lambda x: x.name)

    for entry in project_entries:
        print('%s (%s) (%s)' % (entry.name, entry.id, entry.division.name))
        project = project_svc.find_project(entry.id)
        if project.strat_column is not None:
            print('   Strat column = %s' % project.strat_column.name)
        print('   Num wells = %s' % len(project.wells))
        if len(project.seismic_surveys) > 0:
            print('   Seismic 3D survey = %s' % project.seismic_surveys[0].name)
        if project.geomodel is not None:
            print('   Geomodel = %s' % project.geomodel.name)
        if len(project.layers) > 0:
            print('   Num map layers = %s' % len(project.layers))

    print("Execution was successful")

