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

# Import the modules
import math
from typing import List, Union, Tuple
from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...Services.WellService import WellData
from ...DataModels.Geosteering.Horizon import TypewellHorizonDepth, Horizon
from matplotlib import pyplot as plt
from ...DataModels.Styles.Colors import RgbType


def main_cross_section(zonevu: Zonevu, well_name: str):
    """
    Retrieve well data from ZoneVu and plot a cross-section
    that includes the first geosteering interpretation
    NOTE: this version plots the horizons from the geosteering interpretation directly
    """
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    print('Well named "%s" was successfully found' % well_name)
    well_svc.load_well(well, {WellData.surveys, WellData.geosteering})  # Load surveys and geosteering into well
    wellbore = well.primary_wellbore  # Get reference to wellbore
    if wellbore is None:
        print('Well has no wellbores, so exiting')
        return
    # Get reference to the deviation surveys on wellbore
    survey = wellbore.actual_survey
    plans = wellbore.plan_surveys
    survey_stations = [s for s in survey.stations if s.tvd is not None and math.isfinite(s.tvd)]
    MDs = [s.md for s in survey.stations]
    TVDs = [s.tvd for s in survey.stations]

    # Find landing point info and plotting window
    landing_index = next((i for i, sta in enumerate(survey.stations) if sta.inclination > 88), 0)
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
        showing_horizons = [h for h in interp.horizons if h.show]   # Find visible horizons
        target_horizon = next((h for h in showing_horizons if h.formation_id == interp.target_formation_id), None)

        # picks = [p for p in interp.picks if p.fault_flag is not True]
        picks = [p for p in interp.picks if math.isfinite(p.tvd)]
        mds = [p.md for p in picks]      # Make list of all geosteering pick MDs
        tvts = {d.key: d.tvt for d in interp.typewell_horizon_depths}  # Make lookup table of tvt values

        # Loop through horizons and geosteering picks and make a list of tvd arrays to plot
        horizon_plots: List[Tuple[Horizon, List[Union[float, None]]]] = []
        for horizon in showing_horizons:
            tvds: List[Union[float, None]] = []
            for pick in picks:
                key = TypewellHorizonDepth.make_key(pick.type_wellbore_id, horizon.id)
                tvd = pick.target_tvd + tvts[key] if key in tvts else None
                tvds.append(tvd)
            if any(tvds):
                horizon_plots.append((horizon, tvds))       # Only save horizon plots that have useful tvds

        # Plot the horizon interfaces
        for horz_plot in horizon_plots:
            horizon, tvds = horz_plot
            is_target = horizon == target_horizon
            horz_color = horizon.line_style.get_color(RgbType.Rgb1)
            line_width, line_style, line_color = (2, '--', 'black') if is_target else (1, '-', horz_color)
            ax.plot(mds, tvds, color=line_color, linewidth=line_width, zorder=1, linestyle=line_style)

        # Do color fill between horizon interfaces
        for hp1, hp2 in zip(horizon_plots, horizon_plots[1:]):
            h1, tvds1 = hp1
            h2, tvds2 = hp2
            fill_color = h1.fill_style.get_color(RgbType.Rgb1)
            opacity = h1.fill_style.opacity / 100
            ax.fill_between(mds, tvds1, tvds2, interpolate=False, alpha=opacity, color=fill_color)

        # Choose sensible plot limits for tvd
        min_tvd = min([tvd for tvd in horizon_plots[0][1] if tvd is not None])    # Find min tvd of all plots
        max_tvd = max([tvd for tvd in horizon_plots[-1][1] if tvd is not None])  # Find max tvd of all plots
        dtvd = max_tvd - min_tvd
        plot_start_tvd = min_tvd - dtvd / 10
        plot_end_tvd = max_tvd + dtvd / 10
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





