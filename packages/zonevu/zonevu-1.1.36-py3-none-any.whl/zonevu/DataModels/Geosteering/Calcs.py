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

from dataclasses import dataclass, field
from ...DataModels.Geosteering.Horizon import TypewellHorizonDepth, Horizon
from ...DataModels.Geosteering.Pick import Pick
from ...DataModels.Geosteering.Interpretation import Interpretation
from ...DataModels.Geosteering.CurveDef import CurveDef
from ...DataModels.Wells.Station import Station
from ...DataModels.Strat.StratColumn import StratColumn, Formation
from ...DataModels.Wells.Welllog import Welllog
from ...DataModels.Wells.Curve import Curve
from shapely.geometry import LineString
from typing import List, Optional, Dict, Union, Tuple
import numpy as np
from ...DataModels.DataModel import WellElevationUnitsEnum
from ...Services.Client import UnitsSystemEnum
from ...Zonevu import Zonevu
from itertools import groupby
import math
from ...DataModels.Geosteering.Blocks import Block, Layer, Fault, Throw
import warnings

"""
Utilities to convert geosteering interpretation into blocks, and to compute percent in zone
"""


@dataclass
class ZoneCalc:
    horizon: Horizon
    length: float = 0
    layers: List[Layer] = field(default_factory=list[Layer])
    percent: float = 0


@dataclass
class HorizonDepth:
    """
    A TypewellHorizonDepth with additional flattened information.
    """
    formation: Optional[Formation] = None  # Formation of this horizon depth from strat column
    horizon: Optional[Horizon] = None  # Interpretation horizon of this horizon depth
    elevation: float = 0  # Elevation of the geosteering pick
    tvd: float = 0
    tvt: float = 0
    target: bool = False  # Whether this horizon is the target formation of the geosteering interpretation


@dataclass
class PickEx(Pick):
    """
    A geosteering pick with flattened information about the horizons, formations, etc., for this pick
    """
    horizon_depths: list[HorizonDepth] = field(default_factory=list[HorizonDepth])


def calc_percent_in_zone(interp: Interpretation, stations: List[Station]) -> List[ZoneCalc]:
    """
    Computes the percent in zone for a wellbore (that is, a deviation survey) for a geosteering interpretation
    :param interp:
    :param stations: a list of survey stations that defines the wellbore that was geosteered
    :return:
    """
    blocks, faults = make_blocks_and_faults(interp)  # Get a list of blocks for this geosteering interpretation
    zone_calcs = {h.id: ZoneCalc(h) for h in interp.horizons}  # Dictionary to accumulate zone lengths

    for block in blocks:
        for layer in block.layers:
            for s1, s2 in zip(stations, stations[1:]):
                line = LineString(((s1.md, s1.tvd), (s2.md, s2.tvd)))  # Make a line from survey station pair
                intersection = line.intersection(layer.polygon)  # Get intersection of line with layer polygon
                zone_calcs[layer.horz.id].length += intersection.length  # Accumulate intersection length
                if intersection.length > 0:
                    zone_calcs[layer.horz.id].layers.append(layer)

    zone_calc_list = list(zone_calcs.values())
    zones_length = sum(calc.length for calc in zone_calc_list)  # Sum of all horizon/formation traversals
    if zones_length != 0:
        for calc in zone_calc_list:
            calc.percent = 100 * calc.length / zones_length  # Compute percent in zone for this horizon
    return zone_calc_list


def make_evenly_spaced_picks(interp: Interpretation, interval: float, first_md: Optional[float] = None,
                             last_md: Optional[float] = None) -> List[Pick]:
    """
    Converts the actual picks in a geosteering interpretation into evenly spaced picks, with no faults.
    :param interp: A geosteering interpretation
    :param interval: The sample interval in MD for output picks
    :param first_md: Beginning MD for output picks
    :param last_md: Ending MD for output picks
    :return:
    Note: faults are discarded.
    """
    blocks = make_contiguous_blocks(interp)
    first_block = blocks[0]
    last_block = blocks[-1]
    first_md = first_block.md_start if first_md is None else first_md
    last_md = last_block.md_end if last_md is None else last_md
    md = first_md
    current_block = first_block
    evenly_spaced_picks: List[Pick] = []
    with warnings.catch_warnings():
        warnings.filterwarnings('error')
        while md < last_md:
            while not current_block.contains_md(md):
                current_block = current_block.find_next_block()
                if current_block is None:
                    break
            try:
                pick = current_block.make_pick(md)
            except RuntimeWarning as e:
                print('*** Runtime Error at md = %s: %s' % (md, e))
                pick = current_block.make_pick(md)   # Redo calc to cause error
            evenly_spaced_picks.append(pick)
            md += interval

    return evenly_spaced_picks


def create_extended_picks(interp: Interpretation, strat_cols: list[StratColumn],
                          picks: Optional[List[Pick]] = None) -> List[PickEx]:
    """
    Flattens the data in a geosteering interpretation into a list of extended geosteering picks
    :param interp: A geosteering interpretation
    :param strat_cols: The stratigraphic columns of the well that was geosteered
    :param picks: Picks to extend. If None, will extend the picks on the interpretation
    :return:

    Note: Each pick will have a list of horizon depths for all horizons in the interpretation.
    """
    interp.typewell_horizon_depths.sort(key=lambda d: d.type_wellbore_id)  # Make sure horz depths in type well order
    type_well_groups = groupby(interp.typewell_horizon_depths, key=lambda d: d.type_wellbore_id)  # Group by type well
    type_well_depth_dict = {key: list(group) for key, group in type_well_groups}  # Make depth list LUT by type well id
    for wellbore_id, type_h_depths in type_well_depth_dict.items():
        type_h_depths.sort(key=lambda h_depth: h_depth.tvt)  # Make sure lists are in TVT order

    horizons_dict = {h.id: h for h in interp.horizons}  # Make a horizon lookup dictionary
    formations_dict = {f.id: f for sc in strat_cols for f in sc.formations}

    picks = interp.picks if picks is None else picks
    extended_picks: List[PickEx] = []
    for p in picks:
        pick_ex = PickEx(**p.__dict__)
        extended_picks.append(pick_ex)
        type_h_depths = type_well_depth_dict.get(p.type_wellbore_id)  # Get type well horizon depths for this pick
        for type_hd in type_h_depths or []:
            horizon = horizons_dict[type_hd.horizon_id]
            formation = formations_dict[horizon.formation_id]
            target_hd = HorizonDepth(formation=formation, horizon=horizon)
            target_hd.elevation = p.target_elevation - type_hd.tvt
            target_hd.tvd = p.target_tvd + type_hd.tvt
            target_hd.tvt = p.target_tvt - type_hd.tvt
            target_hd.target = interp.target_formation_id == formation.id
            pick_ex.horizon_depths.append(target_hd)

    return extended_picks


def make_blocks_and_faults(interp: Interpretation, interval: Optional[float] = None) -> Tuple[List[Block], List[Fault]]:
    """
    Computes the blocks and faults for a geosteering interpretation
    :param interp: A geosteering interpretation
    :param interval: If provided, blocks will be of width 'interval' and no faults will be generated.
    :return: a list of geosteering blocks and faults
    """
    # Make a list of layer thicknesses for each employed typewell
    interp.typewell_horizon_depths.sort(key=lambda d: d.type_wellbore_id)  # Make sure horz depths in type well order
    target_formation = interp.target_formation_id
    type_well_groups = groupby(interp.typewell_horizon_depths, key=lambda d: d.type_wellbore_id)  # Group by type well
    type_well_depth_dict = {key: list(group) for key, group in type_well_groups}  # Make depth list LUT by type well id
    for wellbore_id, h_depths in type_well_depth_dict.items():
        h_depths.sort(key=lambda h_depth: h_depth.tvt)  # Make sure lists are in TVT order

    # Create a list of geosteering blocks
    horizons_dict = {h.id: h for h in interp.horizons}  # Make a horizon lookup dictionary
    picks = interp.picks if interval is None else make_evenly_spaced_picks(interp, interval)
    blocks: List[Block] = []
    faults: List[Fault] = []

    missing_horizon_id = 0
    if horizons_dict.get(missing_horizon_id) is None:
        hz = Horizon(id=missing_horizon_id, name=f"<Missing Target Formation Id {target_formation}>", formation_id=target_formation)
        horizons_dict[missing_horizon_id] = hz
        interp.horizons.append(hz)

    p1 = picks[0]
    last_block_or_fault: Union[Block, Fault, None] = None
    for p2 in picks[1:]:
        h_depths = type_well_depth_dict.get(p1.type_wellbore_id)  # Get type well horizon depths for this pick
        if p1.block_flag:   # Create block
            block = Block(next_item=None, start_pick=p1, end_pick=p2)
            blocks.append(block)
            if last_block_or_fault is not None:
                last_block_or_fault.next_item = block
            last_block_or_fault = block
            if h_depths is not None:
                depth_pairs = zip(h_depths, h_depths[1:])
                for d, d2 in depth_pairs:
                    tvd1 = p1.target_tvd + d.tvt  # Compute geometry of the layer for this horizon pair
                    tvd2 = p2.target_tvd + d.tvt
                    thickness = d2.tvt - d.tvt
                    horizon = horizons_dict[d.horizon_id]  # Find horizon for this type well depth
                    layer = Layer(block, horizon, tvd1, tvd2, thickness)
                    block.layers.append(layer)  # Create layer and add to block for this pick
                    if horizon.formation_id == target_formation:
                        block.target_layer = layer
            else:
                tvd1 = p1.target_tvd # Compute geometry of the layer for top only
                tvd2 = p2.target_tvd
                thickness = 0
                horizon = horizons_dict[missing_horizon_id]  # Find horizon for this type well depth
                layer = Layer(block, horizon, tvd1, tvd2, thickness)
                block.layers.append(layer)  # Create layer and add to block for this pick
                #if horizon.formation_id == target_formation:
                block.target_layer = layer
        elif p1.fault_flag:  # Create fault
            fault = Fault(next_item=None, pick=p1)
            faults.append(fault)
            if last_block_or_fault is not None:
                last_block_or_fault.next_item = fault
            last_block_or_fault = fault
            if h_depths is not None:
                for d in h_depths:
                    tvd1 = p1.target_tvd + d.tvt  # Compute geometry of the layer for this horizon pair
                    tvd2 = p2.target_tvd + d.tvt
                    throw_amt = tvd2 - tvd1
                    if math.fabs(throw_amt) > 0:
                        horizon = horizons_dict[d.horizon_id]  # Find horizon for this type well depth
                        throw = Throw(fault, horizon, tvd1, tvd2, throw_amt)
                        fault.throws.append(throw)  # Create fault throw and add to block for this pick
                        if horizon.formation_id == target_formation:
                            fault.target_throw = throw
            else:
                tvd1 = p1.target_tvd  # Compute geometry of the layer for top only
                tvd2 = p2.target_tvd
                throw_amt = tvd2 - tvd1
                if math.fabs(throw_amt) > 0:
                    horizon = horizons_dict[missing_horizon_id]  # Find horizon for this type well depth
                    throw = Throw(fault, horizon, tvd1, tvd2, throw_amt)
                    fault.throws.append(throw)  # Create fault throw and add to block for this pick
                    #if horizon.formation_id == target_formation:
                    fault.target_throw = throw
        p1 = p2

    return blocks, faults


def get_block_type_curve_info(interp: Interpretation, block: Block) -> Optional[CurveDef]:
    """
    Find information about the type curve used on a geosteering block.
    :param interp: The geosteering interpretation that this block is from
    :param block: The block in question
    :return:
    """
    curve_defs = interp.curve_defs  # All the well log curve definitions used in this interpretation
    pick = block.start_pick  # A block is defined by two geosteering picks. The first pick establishes the type curve.
    curve_def_id = pick.type_curve_def_id
    curve_def = next((d for d in curve_defs if d.id == curve_def_id), None)  # Lookup the curve def for this block
    return curve_def


def make_contiguous_blocks(interp: Interpretation) -> List[Block]:
    """
    Computes a "blocks only" set of blocks of the interpretation, where blocks are contiguous in MD (any gaps filled).
    :param interp: a geosteering interpretation
    :return: a list of geosteering blocks that are contiguous with no faults
    """
    blocks, faults = make_blocks_and_faults(interp)
    just_blocks = [b.make_copy() for b in blocks]  # Make a list of copies of blocks
    contiguous_blocks: List[Block] = []

    for bb1, bb2 in zip(just_blocks, just_blocks[1:]):
        b1: Block = bb1
        b2: Block = bb2
        b1.next_item = b2
        contiguous_blocks.append(b1)
        if b1.md_end < b2.md_start:  # Check for gap and make an infill block if needed
            infill_block = Block.make_infill_block(b1, b2)
            b1.next_item = infill_block
            infill_block.next_item = b2
            contiguous_blocks.append(infill_block)

    last_block = just_blocks[-1]
    last_block.next_item = None
    contiguous_blocks.append(last_block)
    return contiguous_blocks


def create_pseudo_welllog(zonevu: Zonevu, interp: Interpretation, strat_cols: list[StratColumn], interval: float,
                          first_md: Optional[float] = None, last_md: Optional[float] = None) -> Welllog:
    """
    Convert the picks and horizons of a geosteering interpretation into a well log data structure.
    :param zonevu: ZoneVu client instance
    :param interp: A geosteering interpretation
    :param strat_col: The strat column referenced by the geosteering interpretation
    :param interval: The sample interval in MD for horizon data points
    :param first_md: Beginning MD for horizon data points
    :param last_md: Ending MD for horizon data points
    :return: A "pseudo" well log and well log curves.

    Note: A well log data structure might be a convenient data structure of a geosteering interpretation for some
       applications.
          Each pseudo curve will be one horizon from the geosteering interpretation with its curve mnemonic
       set to the formation symbol of that horizon.
          The index_curve_id of the well log will be set to the curve index of the target horizon.
    """

    evenly_spaced_picks = make_evenly_spaced_picks(interp=interp, interval=interval, first_md=first_md, last_md=last_md)
    evenly_spaced_picks_ex = create_extended_picks(interp, strat_cols, evenly_spaced_picks)

    N = len(evenly_spaced_picks_ex)
    n = 0
    samples_lut: Dict[str, np.ndarray] = {}
    for p in evenly_spaced_picks_ex:
        for h in p.horizon_depths:
            if h.formation.symbol not in samples_lut:
                samples_lut[h.formation.symbol] = np.empty(N, dtype=float)
            samples = samples_lut[h.formation.symbol]
            samples[n] = h.tvd
        n += 1

    well_depth_units = WellElevationUnitsEnum.Meters if zonevu.units_system == UnitsSystemEnum.Metric else \
        WellElevationUnitsEnum.Feet
    reference_pick = evenly_spaced_picks_ex[0]
    formation_ids = [d.horizon.formation_id for d in reference_pick.horizon_depths if d.horizon is not None]
    target_index = formation_ids.index(interp.target_formation_id)
    log = Welllog(id=0, name=interp.name, description='Pseudo well log created from geosteering interpretation',
                  start_depth=evenly_spaced_picks_ex[0].md, end_depth=evenly_spaced_picks_ex[-1].md,
                  step_length=interval, depth_units=well_depth_units, index_curve_id=target_index)
    for h in reference_pick.horizon_depths:
        samples = samples_lut[h.formation.symbol]
        curve = Curve(id=0, name=h.formation.name, description='A pseudo well log curve of a geosteering horizon',
                      mnemonic=h.formation.symbol, unit=well_depth_units, samples=samples)
        log.curves.append(curve)

    return log


class GeosteerIter:
    """
    Iterator to easily iterate through the block and faults in MD order of a geosteering interpretation.
    """
    def __init__(self, interp: Interpretation):
        blocks, faults = make_blocks_and_faults(interp)
        self._item = blocks[0]

    def __iter__(self):
        return self

    def __next__(self):
        if self._item.next is None:
            raise StopIteration
        else:
            item = self._item
            self._item = self._item.next
            return item




