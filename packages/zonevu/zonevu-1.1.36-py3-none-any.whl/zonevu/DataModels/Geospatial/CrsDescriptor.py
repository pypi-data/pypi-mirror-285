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

from strenum import StrEnum
from typing import Optional, Union
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, config, DataClassJsonMixin
from .Enums import DistanceUnitsEnum
from abc import ABC, abstractmethod


class StateCode(StrEnum):
    AL = 'Alabama'
    AK = 'Alaska'
    AZ = 'Arizona'
    AR = 'Arkansas'
    CA = 'California'
    CO = 'Colorado'
    CT = 'Connecticut'
    DE = 'Delaware'
    FL = 'Florida'
    GA = 'Georgia'
    HI = 'Hawaii'
    ID = 'Idaho'
    IL = 'Illinois'
    IN = 'Indiana'
    IA = 'Iowa'
    KS = 'Kansas'
    KY = 'Kentucky'
    LA = 'Louisiana'
    ME = 'Maine'
    MD = 'Maryland'
    MA = 'Massachusetts'
    MI = 'Michigan'
    MN = 'Minnesota'
    MS = 'Mississippi'
    MO = 'Missouri'
    MT = 'Montana'
    NE = 'Nebraska'
    NV = 'Nevada'
    NH = 'New Hampshire'
    NJ = 'New Jersey'
    NM = 'New Mexico'
    NY = 'New York'
    NC = 'North Carolina'
    ND = 'North Dakota'
    OH = 'Ohio'
    OK = 'Oklahoma'
    OR = 'Oregon'
    PA = 'Pennsylvania'
    RI = 'Rhode Island'
    SC = 'South Carolina'
    SD = 'South Dakota'
    TN = 'Tennessee'
    TX = 'Texas'
    UT = 'Utah'
    VT = 'Vermont'
    VA = 'Virginia'
    WA = 'Washington'
    WV = 'West Virginia'
    WI = 'Wisconsin'
    WY = 'Wyoming'


class Datum(StrEnum):
    NAD27 = 'Nad1927'
    NAD83 = 'Nad1983'
    WGS1984 = 'Wgs1984'


class StateZone(StrEnum):
    North = 'North'
    South = 'South'
    East = 'East'
    West = 'West'
    Central = 'Central'
    SouthCentral = 'SouthCentral'
    EastCentral = 'EastCentral'
    WestCentral = 'WestCentral'
    I = 'I'
    II = 'II'
    III = 'III'
    IV = 'IV'
    V = 'V'
    VI = 'VI'
    VII = 'VII'


class UtmHemisphere(StrEnum):
    N = 'N'
    S = 'S'


@dataclass
class CrsDescriptor(DataClassJsonMixin, ABC):
    units: DistanceUnitsEnum
    datum: Datum


@dataclass
class UtmDescriptor(CrsDescriptor):
    zone: int
    hemisphere: UtmHemisphere

    def get_projection_str(self) -> str:
         return str('Utm%s' % self.datum)
    
    def get_zone_str(self) -> str:
        zone_base = '%s%s' % (self.zone, self.hemisphere)
        return str('%sUtmZone%s' % (self.datum, zone_base)).lower()


@dataclass
class StatePlaneDescriptor(CrsDescriptor):
    zone: Union[StateZone, int]
    code: StateCode

