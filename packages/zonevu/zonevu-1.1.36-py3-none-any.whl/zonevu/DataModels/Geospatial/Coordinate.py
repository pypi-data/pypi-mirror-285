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

from dataclasses import dataclass
from dataclasses_json import LetterCase, config, DataClassJsonMixin
import math
from vectormath import Vector3


@dataclass
class Coordinate(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    x: float = 0
    y: float = 0
    z: float = 0

    @property
    def vector(self) -> Vector3:
        return Vector3(self.x, self.y, self.z)

    def rotate(self, angle: float) -> 'Coordinate':
        """
        Rotates this point around the origin by an angle on the 2-dimensional plane
        @param angle: angle from x-axis in radians
        @return: the rotated point
        """
        x = self.x * math.cos(angle) - self.y * math.sin(angle)
        y = self.x * math.sin(angle) + self.y * math.cos(angle)
        return Coordinate(x, y)

    def __add__(self, other: 'Coordinate') -> 'Coordinate':
        return Coordinate(self.x + other.x, self.y + other.y, self.z + other.z)



