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

from typing import Optional, ClassVar, List
from dataclasses import dataclass, field
from dataclasses_json import config
from .DataModel import DataModel, ChangeAgentEnum
from .PrimaryDataObject import PrimaryDataObject, DataObjectTypeEnum
from .Map.UserLayer import UserLayer
from .Document import Document
from ..Services.Storage import Storage
from strenum import PascalCaseStrEnum
from enum import auto
from datetime import datetime
from pathlib import Path
from .Helpers import MakeIsodateOptionalField
from ..DataModels.Company import Division
from ..DataModels.Wells.Well import WellEntry
from ..DataModels.Geospatial.Crs import CrsSpec
from ..DataModels.Seismic.SeismicSurvey import SeismicSurveyEntry
from ..DataModels.Geomodels.Geomodel import GeomodelEntry
from ..DataModels.Strat.StratColumn import StratColumnEntry
from .Geospatial.Crs import DistanceUnitsEnum


class ProjectTypeEnum(PascalCaseStrEnum):
    Unspecified = auto()
    Prospect = auto()
    AreaOfInterest = auto()
    Development = auto()
    Operations = auto()
    Job = auto()
    Subscription = auto()
    DealRoom = auto()
    DataRoom = auto()
    SeismicSurvey = auto()
    Well = auto()
    Pad = auto()


@dataclass
class Project(PrimaryDataObject):
    """
    ZoneVu project
    """
    #: Corporate division
    division: Optional[Division] = None
    #: Mandatory CRS
    coordinate_system: Optional[CrsSpec] = None
    number: Optional[str] = None
    description: Optional[str] = None
    project_type: ProjectTypeEnum = ProjectTypeEnum.Unspecified
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    creator: Optional[str] = None
    change_agent: ChangeAgentEnum = ChangeAgentEnum.Unknown
    creation_date: Optional[datetime] = MakeIsodateOptionalField()
    last_modified_date: Optional[datetime] = MakeIsodateOptionalField()
    property_number: Optional[str] = None
    afe_number: Optional[str] = None
    basin: Optional[str] = None
    play: Optional[str] = None
    zone: Optional[str] = None
    producing_field: Optional[str] = field(default=None, metadata=config(field_name="Field"))
    country: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    is_active: bool = False
    is_complete: bool = False
    is_confidential: bool = False
    start_date: Optional[datetime] = MakeIsodateOptionalField()
    completion_date: Optional[datetime] = MakeIsodateOptionalField()
    confidential_release_date: Optional[datetime] = MakeIsodateOptionalField()
    wells: List[WellEntry] = field(default_factory=list[WellEntry])
    layers: List[UserLayer] = field(default_factory=list[UserLayer])
    documents: List[Document] = field(default_factory=list[Document])
    seismic_surveys: List[SeismicSurveyEntry] = field(default_factory=list[SeismicSurveyEntry])
    strat_column: Optional[StratColumnEntry] = None
    geomodel: Optional[GeomodelEntry] = None

    archive_dir_name: ClassVar[str] = 'projects'
    archive_json_filename: ClassVar[str] = 'project.json'

    @property
    def full_name(self) -> str:
        return self.name

    @property
    def data_object_type(self) -> DataObjectTypeEnum:
        return DataObjectTypeEnum.Project

    @property
    def archive_local_dir_path(self) -> Path:
        return Path(self.archive_dir_name) / self.safe_name

    @property
    def archive_local_file_path(self) -> Path:
        return self.archive_local_dir_path / self.archive_json_filename

    def save(self, storage: Storage) -> None:
        super().save(storage)

        # Give change for specialized items to be written.
        for layer in self.layers:
            layer.save(self.archive_local_dir_path, storage)

    @classmethod
    def retrieve(cls, dir_path: Path, storage: Storage) -> 'Project':
        project_json_path = dir_path / cls.archive_json_filename
        json_obj = PrimaryDataObject.retrieve_json(project_json_path, storage)
        project = cls.from_dict(json_obj)

        # Give change for specialized items to be read.
        for layer in project.layers:
            layer.retrieve(dir_path, storage)

        return project


@dataclass
class ProjectEntry(DataModel):
    # Represents a ZoneVu Project catalog entry Object (lightweight)
    #: Corporate division
    division: Optional[Division] = None
    number: Optional[str] = None
    description: Optional[str] = None
    row_version: Optional[str] = None

    @property
    def project(self) -> Project:
        return Project(id=self.id, name=self.name, row_version=self.row_version, description=self.description,
                       division=self.division, number=self.number)
