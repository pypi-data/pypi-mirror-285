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


def main(zonevu: Zonevu, storage: Storage, stratcolumn_name: str) -> None:
    """
    Write or update a named well from a ZoneVu account to user storage.
    :param zonevu: Zonevu client instance
    :param storage: User storage to save strat column to
    :param stratcolumn_name: Name of well to retrieve and save
    """
    print('Save a stratcolumn to storage')
    # Find stratcolumn with that name
    strat_svc = zonevu.strat_service
    stratcolumn = strat_svc.find_stratcolumn(6)
    if stratcolumn is None:
        raise ZonevuError.local('Could not find the stratcolumn "%s"' % stratcolumn_name)

    stratcolumn.save(storage)                          # Save stratcolumn to storage outside ZoneVu

