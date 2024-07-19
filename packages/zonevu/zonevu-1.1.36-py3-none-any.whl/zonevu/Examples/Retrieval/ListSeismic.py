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


def main_list_seismicsurveys(zonevu: Zonevu):
    seismic_svc = zonevu.seismic_service

    print('Seismic Surveys:')
    seismic_entries = seismic_svc.get_surveys()
    for entry in seismic_entries:
        print('%s (%s) (%s)' % (entry.name, entry.id, entry.division.name))
        if entry.num_datasets == 0:
            print('  - Seismic Survey has %s datasets' % entry.num_datasets)
        else:
            try:
                survey = seismic_svc.find_survey(entry.id)
                for volume in survey.seismic_volumes:
                    print('   %s - %s (%s) - %s mbytes' % (volume.vintage, volume.name, volume.domain, volume.size))
            except ZonevuError as seismic_err:
                print('  * ERROR - Could not get details on seismic survey "%s"' % entry.name)

    print("Execution was successful")

