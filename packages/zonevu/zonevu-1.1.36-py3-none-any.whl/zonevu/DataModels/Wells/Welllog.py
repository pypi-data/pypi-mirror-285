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

from typing import Optional, List
from dataclasses import dataclass, field
from ...DataModels.DataModel import DataModel, WellElevationUnitsEnum
from ...DataModels.Wells.Curve import Curve, AppMnemonicCodeEnum
from ...DataModels.Wells.CurveGroup import CurveGroup
from strenum import StrEnum
from pathlib import Path
from ...Services.Utils import Naming
from ...Services.Storage import Storage


class WellLogTypeEnum(StrEnum):
    Digital = 'Digital'
    Raster = 'Raster'
    Witsml = 'Witsml'
    Frac = 'Frac'


class WellLogIndexTypeEnum(StrEnum):
    Depth = 'Depth'
    Time = 'Time'


@dataclass
class Welllog(DataModel):
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    file_name: Optional[str] = None
    description: Optional[str] = None
    source: Optional[WellLogTypeEnum] = None
    start_depth: Optional[float] = None
    end_depth: Optional[float] = None
    step_length: Optional[float] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    step_time: Optional[float] = None
    depth_units: Optional[WellElevationUnitsEnum] = None
    index_type: Optional[WellLogIndexTypeEnum] = None
    curves: List[Curve] = field(default_factory=list[Curve])
    curve_groups: List[CurveGroup] = field(default_factory=list[CurveGroup])
    index_curve_id: Optional[int] = None
    # las_file: Optional[str] = None  # ASCII text of LAS file

    def copy_ids_from(self, source: DataModel):
        super().copy_ids_from(source)
        if isinstance(source, Welllog):
            DataModel.merge_lists(self.curves, source.curves)

    def find_curve(self, mne: AppMnemonicCodeEnum) -> Optional[Curve]:
        curve = next((c for c in self.curves if c.system_mnemonic == mne), None)
        return curve

    def save(self, dir_path: Path, storage: Storage):
        log_name = self.v_log_name
        for curve in self.curves:
            curve.save(dir_path, log_name, storage)

    def retrieve(self, dir_path: Path, storage: Storage):
        log_name = self.v_log_name
        for curve in self.curves:
            curve.retrieve(dir_path, log_name, storage)

    @property
    def v_log_name(self) -> str:
        base_name = self.name or 'log'
        name = '%s-%s' % (base_name, self.id)
        safe_name = Naming.make_safe_name(name)
        return safe_name



