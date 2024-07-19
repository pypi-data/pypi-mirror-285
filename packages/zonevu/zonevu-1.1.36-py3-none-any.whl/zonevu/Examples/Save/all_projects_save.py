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
from ...Services.WellData import WellData
from ...Services.Storage import Storage
import time


def main_save_projects(zonevu: Zonevu, storage: Storage):
    """
    Write or update all projects from a ZoneVu account to user storage.
    :param zonevu: Zonevu client instance
    :param storage: User storage to save projects to
    """
    print('Write all projects in ZoneVu account to disk - Running...')
    projects_svc = zonevu.project_service          # Reference to Zonevu project service

    # List projects in account.  Write them out to storage.
    project_entries = projects_svc.get_projects()     # Get a list of all projects in zonevu account
    print('Number of projects retrieved = %s' % len(project_entries))
    num_updated = 0
    for index, project_entry in enumerate(project_entries):
        print('%s, ' % project_entry.name, end="")
        if index % 8 == 0:
            print()

        project = project_entry.project
        up_to_date = project.current(storage)  # See if there is a copy of project in storage & if it is current
        if up_to_date:
            continue        # If the row version of the stored version of the project the same, no need to save it.

        try:
            # projects_svc.load_well(project, {WellData.all})    # Load project with all well data
            project.save(storage)                # Save project to storage. Overwrite the project if it  already exists
            project.save_documents(zonevu.document_service, storage)   # Save well documents to storage
            num_updated += 1
            time.sleep(.1)       # Give Zonevu a 1-second break.
        except ZonevuError as err:
            print('Could not update project "%s" because %s' % (project.full_name, err.message))

    print()
    print('%s projects were written or updated' % num_updated)
    print('Write all projects in ZoneVu account to disk - Done.')


