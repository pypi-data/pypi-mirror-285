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

import math
from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...Services.WellService import WellData
from matplotlib import pyplot as plt
from shapely.ops import unary_union
from shapely.geometry import Polygon
from ...DataModels.Styles.Colors import RgbType
from ...DataModels.Geosteering.Blocks import Block, Fault
from ...DataModels.Geosteering.Calcs import make_blocks_and_faults


def main_cross_section(zonevu: Zonevu, well_name: str):
    """
    Retrieve well data from ZoneVu and plot a cross-section
    that includes the first geosteering interpretation
    NOTE: this version converts the interpretation picks into blocks, and plots those.
    """
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    well_name = well.full_name
    print('Well named "%s" was successfully found' % well_name)
    well_svc.load_well(well, {WellData.surveys, WellData.geosteering})  # Load surveys and geosteering into well
    wellbore = well.primary_wellbore  # Get reference to wellbore
    if wellbore is None:
        print('Well has no wellbores, so exiting')
        return
    # Get reference to the deviation surveys on wellbore
    survey = wellbore.actual_survey
    plans = wellbore.plan_surveys
    valid_stations = survey.valid_stations
    MDs = [s.md for s in valid_stations]
    TVDs = [s.tvd for s in valid_stations]

    # Find landing point info and plotting window
    landing_index = next((i for i, sta in enumerate(valid_stations) if sta.inclination > 88), 0)
    landing_tvd = TVDs[landing_index]
    plot_start_tvd = landing_tvd - 300    # MAKE 300
    plot_end_tvd = landing_tvd + 300    # MAKE 300
    plot_start_index = next((i for i, val in enumerate(TVDs) if val > plot_start_tvd), 0)
    plot_start_md = MDs[plot_start_index] - 100
    plot_end_md = max(MDs)

    # Plot a cross-section of TVD versus MD
    f = plt.figure(figsize=(9, 6))
    ax = f.add_subplot(111)
    plot_name = 'Well "%s"' % well.full_name

    # Maybe plot the wellbore plan
    if plans:
        plan = plans[0]     # Plot 1st plan
        plt.plot([s.md for s in plan.stations], [s.tvd for s in plan.stations], color='blue', label='Plan', zorder=2)

    # Plot actual wellbore and survey stations
    ax.plot(MDs, TVDs, color='black', label='Actual', zorder=3)
    ax.scatter(MDs, TVDs, color='black', zorder=3)

    # If available, plot the starred or first geosteering interpretation
    interp = wellbore.get_starred_interp()
    plot_geosteering = interp is not None
    if plot_geosteering:
        zonevu.geosteering_service.load_interpretation(interp)      # Load picks into interpretation
        if interp.valid:
            showing_horizons = [h for h in interp.horizons if h.show]   # Find visible horizons
            target_horizon = next((h for h in showing_horizons if h.formation_id == interp.target_formation_id), None)

            interval = None
            # interval = 50
            blocks, faults = make_blocks_and_faults(interp, interval)

            plot_end_md = max(plot_end_md, *[p.md for p in interp.picks])
            plot_min_tvd = 100000000
            plot_max_tvd = -10000000

            # Plot blocks and faults
            for block in blocks:
                for layer in block.layers:
                    (p_minx, p_miny, p_maxx, p_maxy) = layer.polygon.bounds
                    plot_min_tvd = min(plot_min_tvd, p_miny)
                    plot_max_tvd = max(plot_max_tvd, p_maxy)
                    x, y = layer.polygon.exterior.xy
                    horz = layer.horz
                    is_target = horz == target_horizon
                    horz_color = horz.line_style.get_color(RgbType.Rgb1)
                    fill_color = horz.fill_style.get_color(RgbType.Rgb1)
                    opacity = horz.fill_style.opacity / 100
                    line_width, line_style, line_color = (2, '--', 'black') if is_target else (1, '-', horz_color)
                    ax.fill(x, y, alpha=opacity, color=fill_color)
                    if is_target:
                        ax.plot(x, y, color=line_color, linewidth=1, zorder=1, linestyle=line_style)

            for fault in faults:
                # Plot overall fault trace
                trace = fault.trace
                ax.plot(trace.xy[0], trace.xy[1], color='gray', linewidth=1, zorder=2, alpha=1)
                # Plot fault throws on individual horizons
                for throw in fault.throws:
                    x = throw.line.xy[0]
                    y = throw.line.xy[1]
                    ax.plot(x, y, color='black', linewidth=2, zorder=2, alpha=1)

            # Choose sensible plot limits for tvd
            dtvd = plot_max_tvd - plot_min_tvd
            plot_start_tvd = plot_min_tvd - dtvd / 10
            plot_end_tvd = plot_max_tvd + dtvd / 10
            plot_name += ' with Geosteering Interpretation "%s" for Target Formation "%s"' % (interp.name, target_horizon.name)

    # Finish plot
    plt.ylim(plot_start_tvd, plot_end_tvd)
    plt.xlim(plot_start_md, plot_end_md)
    plt.xlabel("MD")
    plt.ylabel("TVD")
    plt.legend()
    plt.title(plot_name)
    # plt.savefig('samplewellplot.pdf');
    plt.gca().invert_yaxis()
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()
    print('end')





