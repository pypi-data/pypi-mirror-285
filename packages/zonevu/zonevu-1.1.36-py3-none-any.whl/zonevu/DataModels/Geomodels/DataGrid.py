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

from typing import Optional
from enum import StrEnum
from dataclasses import dataclass
from pathlib import Path
from ...Services.Utils import Naming
from .GriddedData import GriddedData


class GridUsageEnum(StrEnum):
    Undefined = 'Undefined'
    Structural = 'Structural'
    Isopach = 'Isopach'
    Attribute = 'Attribute'


@dataclass
class DataGrid(GriddedData):
    usage: Optional[GridUsageEnum] = GridUsageEnum.Undefined

    def get_v_file_path(self, geomodel_folder: Path) -> Path:
        safe_name = Naming.make_safe_name_default(self.name, 'datagrid', self.id)
        file_path = geomodel_folder / 'datagrids' / ('%s-%s.npy' % (safe_name, self.id))
        return file_path


