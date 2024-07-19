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
from ...DataModels.Project import ProjectEntry
from ...Services.ProjectService import ProjectData
from ...Services.Storage import Storage


def main(zonevu: Zonevu, project_name: str, storage: Storage) -> None:
    """
    Find a named project in ZoneVu and in user storage, and compare them
    :param zonevu: Zonevu client instance
    :param project_name: Name of project to retrieve and save
    :param storage: User storage to save projects to
    """
    print('Retrieve the same well from ZoneVu and from Storage and compare')

    # Find well with that name in Zonevu
    project_svc = zonevu.project_service
    project = project_svc.get_first_named(project_name)
    if project is None:
        raise ZonevuError.local('Could not find the project "%s"' % project_name)

    # Load data into well from Zonevu
    project_svc.load_project(project, {ProjectData.all})

    # Get stored well
    stored_project = project.retrieve(project.archive_local_dir_path, storage)
    if stored_project is None:
        print('There was no stored version of that project')
        return

    # Compare
    same_version = project.row_version == stored_project.row_version
    if not same_version:
        print('Stored version of that project has a different version number that zonevu version')
        return

    same = project == stored_project
    assert same, 'The data in the stored version should match the zonevu version but does not'




