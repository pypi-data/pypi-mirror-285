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


def main_list_stratcolumns(zonevu: Zonevu):
    strat_svc = zonevu.strat_service

    print('Strat Columns:')
    stratcolumn_entries = strat_svc.get_stratcolumns()
    for entry in stratcolumn_entries:
        print('%s (%s) (%s)' % (entry.name, entry.id, entry.division.name))

    if len(stratcolumn_entries) > 0:
        entry = stratcolumn_entries[0]
        stratcolumn = strat_svc.find_stratcolumn(entry.id)

    # Find a named strat column
    permian_strat_col = strat_svc.get_first_named("Permian")
    found_permian = permian_strat_col is not None

    print("Execution was successful")
