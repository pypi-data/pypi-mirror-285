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
from ...Services.Error import ZonevuError


def main_project_copy(zonevu: Zonevu, project_name: str, delete_code: str):
    """
    Makes a copy of a project
    :param zonevu:
    :param project_name:
    :param delete_code:
    :return:
    NOTE: making a copy of a project is an easy procedure in ZoneVu because all entities (such as wells)
    are stored centrally in ZoneVu, and projects merely refer to them.
    """
    print('Making a copy of project "%s"' % project_name)
    project_service = zonevu.project_service

    project = project_service.get_first_named(project_name)
    if project is None:
        raise ZonevuError.local('No project named "%s" could be found')

    project_copy = copy.deepcopy(project)
    project_copy.name = '%s_Copy' % project.name
    print('Name of copy will be "%s"' % project_copy.name)

    # See if a project with that name exists already. If so, delete it so we avoid making copies
    existing_copy = project_service.get_first_named(project_copy.name)
    if existing_copy is not None:
        project_service.delete_project(existing_copy.id, delete_code)
        print('Deleted existing copy of project')

    project_service.create_project(project_copy)

    print("Execution was successful")

