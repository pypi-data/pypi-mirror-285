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
#
#

from ..DataModels.Project import Project
from ..DataModels.Project import ProjectEntry
from ..DataModels.Wells.Well import Well, WellEntry
from ..DataModels.Wells.Survey import Survey
from ..DataModels.Geomodels.Geomodel import Geomodel, GeomodelEntry
from ..DataModels.Seismic.SeismicSurvey import SeismicSurvey, SeismicSurveyEntry
from ..Services.MapService import MapService
from .Client import Client, ZonevuError
from typing import Tuple, Union, Dict, Optional, Any, List, Set
from strenum import StrEnum


class ProjectData(StrEnum):
    default = 'default'     # Default behavior is to not load anything extra
    layer_data = 'layer_data'
    all = 'all'             # If specified, load all data, as long as 'default' flag not present


class ProjectDataOptions:
    project_data: Set[ProjectData]

    def __init__(self, project_data: Optional[Set[ProjectData]]):
        self.project_data = project_data or set()

    def _calc_option(self, project_data: ProjectData) -> bool:
        return (project_data in self.project_data or self.all) and self.some

    @property
    def all(self):
        return ProjectData.all in self.project_data

    @property
    def some(self) -> bool:
        return ProjectData.default not in self.project_data

    @property
    def layer_data(self) -> bool:
        return self._calc_option(ProjectData.layer_data)


class ProjectService:
    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_projects(self, match_token: Optional[str] = None) -> List[ProjectEntry]:
        url = "projects"
        if match_token is not None:
            url += "/%s" % match_token
        items = self.client.get_list(url)
        entries = [ProjectEntry.from_dict(w) for w in items]
        return entries

    def get_first_named(self, name: str) -> Optional[Project]:
        """
        Get first project with the specified name, populate it, and return it.
        :param name: name of project to get
        :return:
        """
        project_entries = self.get_projects(name)
        if len(project_entries) == 0:
            return None
        projectEntry = project_entries[0]
        project = self.find_project(projectEntry.id)
        return project

    def project_exists(self, name: str) -> Tuple[bool, int]:
        projects = self.get_projects(name)
        exists = len(projects) > 0
        project_id = projects[0].id if exists else -1
        return exists, project_id

    def find_project(self, project_id: int) -> Project:
        url = "project/%s" % project_id
        item = self.client.get(url)
        project = Project.from_dict(item)
        return project

    def load_project(self, project: Project, project_data: Optional[Set[ProjectData]]) -> None:
        options = ProjectDataOptions(project_data)
        loaded_project = self.find_project(project.id)
        project.merge_from(loaded_project)

        if options.layer_data:
            try:
                map_svc = MapService(self.client)
                for layer in project.layers:
                    map_svc.load_user_layer(layer)
            except Exception as err:
                print('Could not load project layers because %s' % err)

    def create_project(self, project: Project) -> None:
        """
        Create a project.
        @param project: project object to be added.
        @return: Throw a ZonevuError if method fails
        """
        url = "project/create"
        item = self.client.post(url, project.to_dict())
        server_project = Survey.from_dict(item)
        project.copy_ids_from(server_project)

    def delete_project(self, project_id: int, delete_code: str) -> None:
        url = "project/delete/%s" % project_id
        url_params: Dict[str, Any] = {"deletecode": delete_code}
        self.client.delete(url, url_params)

    def add_well(self, project: Union[Project, ProjectEntry], well: Union[Well, WellEntry]) -> None:
        """
        Add a well to a project
        @param project:
        @param well:
        @return:
        """
        url = "project/%s/addwell/%s" % (project.id, well.id)
        # params = [project.id, well.id]
        self.client.post(url, {}, False)

    def remove_well(self, project: Union[Project, ProjectEntry], well: Union[Well, WellEntry]) -> None:
        """
        Remove a well from a project
        @param project:
        @param well:
        @return:
        """
        url = "project/%s/removewell/%s" % (project.id, well.id)
        self.client.post(url, {}, False)

    def add_geomodel(self, project: Union[Project, ProjectEntry], geomodel: Union[Geomodel, GeomodelEntry]) -> None:
        """
        Associate a geomodel with a project
        @param project:
        @param geomodel:
        @return:
        """
        url = "project/%s/linkgeomodel/%s" % (project.id, geomodel.id)
        self.client.post(url, {}, False)

    def remove_geomodel(self, project: Union[Project, ProjectEntry], geomodel: Union[Geomodel, GeomodelEntry]) -> None:
        """
        Remove the association of a geomodel with a project
        @param project:
        @param geomodel:
        @return:
        """
        url = "project/%s/unlinkgeomodel/%s" % (project.id, geomodel.id)
        self.client.post(url, {}, False)

    def add_seismicsurvey(self, project: Union[Project, ProjectEntry], survey: Union[SeismicSurvey, SeismicSurveyEntry]) -> None:
        """
        Associate a geomodel with a project
        @param project:
        @param survey:
        @return:
        """
        url = "project/%s/linkseismic/%s" % (project.id, survey.id)
        self.client.post(url, {}, False)

    def remove_seismicsurvey(self, project: Union[Project, ProjectEntry], survey: Union[SeismicSurvey, SeismicSurveyEntry]) -> None:
        """
        Remove the association of a geomodel with a project
        @param project:
        @param survey:
        @return:
        """
        url = "project/%s/unlinkseismic/%s" % (project.id, survey.id)
        self.client.post(url, {}, False)

    # TODO: add method for setting the strat column on the project.
