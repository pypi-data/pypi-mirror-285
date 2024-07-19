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
from ...Services.Storage import Storage
from ...Services.ProjectService import ProjectData


def main(zonevu: Zonevu, storage: Storage, project_name: str) -> None:
    """
    Write or update a named project from a ZoneVu account to user storage.
    :param zonevu: Zonevu client instance
    :param storage: User storage to save projects to
    :param project_name: Name of project to retrieve and save
    """
    print('Save a project to storage')
    # Find project with that name
    project_svc = zonevu.project_service
    project = project_svc.get_first_named(project_name)
    if project is None:
        raise ZonevuError.local('Could not find the project "%s"' % project_name)

    project_svc.load_project(project, {ProjectData.all})

    up_to_date = project.current(storage)  # Find out if project is in user storage & if it is current
    if up_to_date:
        print('That project is already saved in user storage and is up to date')
    if not up_to_date:
        project.save(storage)                          # Save project to storage outside ZoneVu
        project.save_documents(zonevu.document_service, storage)







