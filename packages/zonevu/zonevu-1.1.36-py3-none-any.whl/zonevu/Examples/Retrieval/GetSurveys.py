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
from ...DataModels.Wells.Survey import DeviationSurveyUsageEnum


def main(zonevu: Zonevu, well_name: str):
    print('Retrieve a named well and get its deviation surveys')

    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    # Retrieve surveys
    survey_svc = zonevu.survey_service
    partially_loaded_surveys = survey_svc.get_surveys(well.primary_wellbore.id)
    print('Deviation Survey List:')
    for index, survey in enumerate(partially_loaded_surveys):
        print('   #%s: Survey "%s", Usage %s' % (index, survey.name, survey.usage))

    # Find the actual survey (as opposed to plan surveys).  Retrieve stations
    actual_survey = next((survey for survey in partially_loaded_surveys if survey.usage == DeviationSurveyUsageEnum.Actual), None)
    if actual_survey is None:
        print('Could not find actual survey')
        return

    # Load the survey stations into the existing instance of 'actual_survey'
    actual_survey_existing_instance = survey_svc.load_survey(actual_survey)

    # Retrieve a new fully loaded instance of actual survey
    actual_survey_new_instance = survey_svc.find_survey(actual_survey.id)
    print('Actual Survey retrieved. Num stations = %s' % len(actual_survey_new_instance.stations))
    for index, station in enumerate(actual_survey_new_instance.stations):
        print('   #%s:  MD %s, INCL %s, AZ %s' % (index, station.md, station.inclination, station.azimuth))
    print('Successfully got surveys')
    print()
