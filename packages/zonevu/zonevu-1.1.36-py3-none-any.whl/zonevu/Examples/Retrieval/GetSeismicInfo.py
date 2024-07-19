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
import json


def main_get_seismicsurvey_info(zonevu: Zonevu, seismic_survey_name: str):
    seismic_svc = zonevu.seismic_service

    print('Getting Seismic Info for seismic survey named "%s"' % seismic_survey_name)
    survey = seismic_svc.get_first_named(seismic_survey_name)
    if survey is None:
        raise ZonevuError.local('Could not locate the seismic survey named %s' % seismic_survey_name)

    # Get info on first volume
    if len(survey.seismic_volumes) == 0:
        print('That seismic survey has no volumes')
        return

    volume = survey.seismic_volumes[0]
    print('Getting seismic info for seismic volume named %s' % volume.name)
    info = seismic_svc.volume_info(volume.id)
    info_dict = info.to_dict()
    print(json.dumps(info_dict, indent=3))

    print("Execution was successful")
