import numpy as np
from matplotlib.axes import Axes


def mpl_calc_series(
    n_groups, n_bars, group_width, bar_width, bar_gap, min_bar_gap=0.01
):
    # IMPORTANT: This algorithm only produces correct bar widths when the
    # figure's width is determined exclusively by the n_groups given.
    # When you combine the plot with other elements that change the x-axis
    # limits, the bars will be rescaled and have an incorrect width.
    bar_gap *= n_groups
    bar_width *= n_groups
    min_bar_gap = min(bar_gap, min_bar_gap * n_groups)
    min_width = bar_width * n_bars + min_bar_gap * (n_bars - 1)
    if min_width > group_width:
        bar_gap = min_bar_gap
        group_points = mpl_calc_scaled_group_series(n_bars, group_width, bar_gap)
        bar_width = mpl_calc_bar_width(n_bars, group_width, bar_gap)
    else:
        if bar_width * n_bars + bar_gap * (n_bars - 1) > group_width:
            bar_gap = (group_width - n_bars * bar_width) / (n_bars - 1)
        group_points = mpl_calc_clustered_group_series(n_bars, bar_width, bar_gap)
    return bar_width, [i + group_points for i in range(n_groups)]


def mpl_calc_scaled_group_series(n_bars, group_width, bar_gap):
    width = max(1, n_bars - 1)
    half_width = width / 2
    centered = np.arange(n_bars) - half_width
    bar_width = mpl_calc_bar_width(n_bars, group_width, bar_gap)
    return centered / width * (group_width - bar_width)


def mpl_calc_clustered_group_series(n_bars, bar_width, bar_gap):
    hop = bar_width + bar_gap
    return np.array([hop * i - (hop * (n_bars - 1)) / 2 for i in range(n_bars)])


def mpl_calc_bar_width(n_bars, group_width, gap):
    return (group_width - gap * (n_bars - 1)) / n_bars


def mpl_debug_series(
    n_groups, n_bars, group_width, bar_width, bar_gap, ax: Axes, min_bar_gap=0.03
):
    debug = f"Input: w{bar_width:.2f}, g{bar_gap:.2f};"
    bar_gap *= n_groups
    bar_width *= n_groups
    min_bar_gap = min(bar_gap, min_bar_gap)
    full_width = bar_width * n_bars + bar_gap * (n_bars - 1)
    min_width = bar_width * n_bars + min_bar_gap * (n_bars - 1)
    debug += f" Zoomed: w{bar_width:.2f}, g{bar_gap:.2f}, fw{full_width:.2f}, mw{min_width:.2f};"
    if min_width > group_width:
        algorithm = "scaled"
        bar_gap = min_bar_gap
        bar_width = mpl_calc_bar_width(n_bars, group_width, min_bar_gap)
    else:
        if full_width > group_width:
            bar_gap = (group_width - n_bars * bar_width) / (n_bars - 1)
            algorithm = "clustered"
        else:
            algorithm = "gapped"
    debug += f" Calc: w{bar_width:.2f}, g{bar_gap:.2f}, {algorithm};"
    mpl_calc_series(n_groups, n_bars, group_width, bar_width, bar_gap)
    ax.axhline(0, linestyle="--", color="k")
    for x in range(n_groups):
        ax.axvline(x, color="gray", linewidth=0.5)
        ax.axvspan(x - group_width / 2, x + group_width / 2, alpha=0.5, color="red")
    ax.text(0, 0, debug, fontsize=8, transform=ax.transAxes)
