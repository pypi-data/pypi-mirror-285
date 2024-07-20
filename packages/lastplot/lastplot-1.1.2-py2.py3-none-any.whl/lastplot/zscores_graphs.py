import os

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import starbars
from scipy import stats

from lastplot.computing_statistics import get_test, get_pvalue
from lastplot.graph_constructor import mpl_calc_series, mpl_debug_series
from lastplot.saving import save_sheet

__all__: [
    "zscore_graph_lipid_class",
    "zscore_graph_lipid",
    "zscore_graph_class_average",
]


# Graphs by Z scores
def zscore_graph_lipid(
        df_final,
        control_name,
        experimental_name,
        output_path,
        palette,
        xlabel=None,
        ylabel=None,
        title=None,
        show=True,
        debug=False,
):
    """
    The `zscore_graph_lipid` function generates boxplots and statistical annotations for visualizing Z scores of lipids
    across regions. It performs the following tasks:

    - Plots boxplots to visualize the distribution of Z scores, distinguishing between control and experimental groups.
    - Perform appropriate statistical tests based on the number of genotype groups and annotate the graph with p-values.
        - If there are two genotypes:
            - Performs normality test (Shapiro-Wilk test) and homogeneity of variances test (Levene's test).
            - Based on the results, choose the appropriate test (e.g., t-test, Welch t-test, or Mann-Whitney U test).
        - If there are more than two genotypes:
            - Perform ANOVA to determine if there are any statistically significant differences between the means of the groups.
            - If ANOVA is significant, perform post-hoc Tukey HSD test to find which specific groups differ.
    - Annotates the plot with statistical significance indicators using `starbars.draw_annotation`.
    - Customizable plots with appropriate labels and title for better visualization.
    - Saves each plot as a PNG file in the specified `output_path`.
    - Optionally displays the plot (`show=True`) and closes it after display.

    The function also saves comments regarding the statistical tests performed for each lipid and region in an Excel
    sheet named "Comments" within the `output_path`.

    :param df_final: DataFrame containing Z scores and statistical test results.
    :param control_name: Name of the control group.
    :param experimental_name:Name of the experimental group.
    :param output_path: Path of the output folder.
    :param palette: Color palette for plotting.
    :param xlabel: Label for the x-axis. If None, defaults to "Genotype".
    :param ylabel: Label for the y-axis. If None, defaults to "Z Scores".
    :param title: Title for the plot. If None, defaults to "Z Scores for {lipid} in {region}".
    :param show: Whether to display plots interactively (default True).
    """

    group_width = 0.4
    bar_width = 0.04
    bar_gap = 0.02
    palette = sns.color_palette(palette)

    if not os.path.exists(output_path + "/output/zscore_graphs/lipid"):
        os.makedirs(output_path + "/output/zscore_graphs/lipid")

    for (region, lipid), data in df_final.groupby(["Regions", "Lipids"]):
        print(f"Creating graph for {lipid} in {region}")

        fig, ax = plt.subplots()
        genotype_labels = list(data["Genotype"].unique())
        genotype_labels.remove(control_name)
        genotype_labels.insert(0, control_name)

        if debug:
            # Draw extra information to visualize the bar width calculations.
            mpl_debug_series(
                len(genotype_labels),
                1,
                group_width=group_width,
                bar_width=bar_width,
                bar_gap=bar_gap,
                ax=ax,
            )

        width, positions = mpl_calc_series(
            len(genotype_labels),
            1,
            group_width=group_width,
            bar_width=bar_width,
            bar_gap=bar_gap,
        )

        boxplot = []

        for g, genotype in enumerate(genotype_labels):
            values = data[data["Genotype"] == genotype]["Z Scores"]

            bp = ax.boxplot(
                values,
                positions=[g],
                widths=width,
                patch_artist=True,
                boxprops=dict(facecolor=palette[g], color="k", alpha=0.8),
                medianprops=dict(color="k"),
            )

            boxplot.append(bp["boxes"][0])

            ax.scatter(
                np.ones(len(values)) * g,
                values,
                color="k",
                s=6,
                zorder=3,
            )

        ax.set_xticks([*range(len(genotype_labels))])
        ax.set_xticklabels(genotype_labels, rotation=90)

        # Add statistical annotation
        pairs = []
        if len(genotype_labels) <= 2:
            for element in genotype_labels:
                shapiro = data.iloc[0]["Shapiro Normality"]
                levene = data.iloc[0]["Levene Equality"]
                test = get_test(shapiro, levene)

                test_comment = [f"{test} will be performed for all of the lipids"]
                save_sheet(test_comment, "Comments", output_path)

                if element != control_name:
                    stat, pvalue = get_pvalue(
                        test,
                        data[data["Genotype"] == control_name]["Z Scores"],
                        data[data["Genotype"] == element]["Z Scores"],
                    )
                    pairs.append((control_name, element, pvalue))

        else:
            test_comment = ["Anova will be performed for all of the lipids"]
            save_sheet(test_comment, "Comments", output_path)
            stat, pvalue = stats.f_oneway(
                *[
                    data[data["Genotype"] == label]["Z Scores"]
                    for label in genotype_labels
                ]
            )
            if pvalue < 0.05:
                res = stats.tukey_hsd(
                    *[
                        data[data["Genotype"] == label]["Z Scores"]
                        for label in genotype_labels
                    ]
                )
                for (i, j), pair_value in np.ndenumerate(res.pvalue):
                    if i != j and i < j:
                        pairs.append(
                            (genotype_labels[i], genotype_labels[j], pair_value)
                        )

        starbars.draw_annotation(pairs, ns_show=False)
        comment = [f"For z scores of {lipid} in {region}, P-value is {pvalue}."]
        save_sheet(comment, "Comments", output_path)

        ax.legend(
            boxplot,
            [control_name, *experimental_name],
            loc="center left",
            bbox_to_anchor=(1, 0.5),
        )

        if xlabel:
            plt.xlabel(xlabel)
        else:
            plt.xlabel("Genotype")
        if ylabel:
            plt.ylabel(ylabel)
        else:
            plt.ylabel("Z Scores")

        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Z Scores for {lipid} in {region}")

        plt.tight_layout()
        plt.savefig(
            output_path
            + f"/output/zscore_graphs/lipid/Z Scores for {lipid} in {region}.png",
            dpi=1200,
        )
        if show:
            plt.show()
        plt.close()


def zscore_graph_lipid_class(
        df_final,
        control_name,
        experimental_name,
        output_path,
        palette,
        xlabel=None,
        ylabel=None,
        title=None,
        show=True,
        debug=False,
):
    """
    The `zscore_graph_lipid_class` function generates boxplots to visualize the distribution of Z scores across different lipid classes within each region. It performs the following tasks:

    - Iterates through each region in the DataFrame (`df_final`).
    - Plots boxplots to show the distribution of Z scores for each lipid class, distinguishing between control and experimental groups (`control_name` and `experimental_name`).
    - Customizable plots with appropriate labels and title for better visualization.
    - Saves each plot as a PNG file in the specified `output_path`.
    - Optionally displays the plot (`show=True`).

    :param df_final: Final DataFrame containing Z scores and statistical test results.
    :param control_name: Name of the control group genotype.
    :param experimental_name: Name of the experimental group genotype.
    :param output_path: Path to save output graphs.
    :param palette: Color palette for plotting.
    :param xlabel: Label for the x-axis. If None, defaults to "Lipid Class".
    :param ylabel: Label for the y-axis. If None, defaults to "Z Scores".
    :param title: Title for the plot. If None, defaults to "Z Scores in {region}".
    :param show: Whether to display plots interactively (default True).

    """

    group_width = 0.4
    bar_width = 0.04
    bar_gap = 0.02
    palette = sns.color_palette(palette)

    if not os.path.exists(output_path + "/output/zscore_graphs/lipid_class"):
        os.makedirs(output_path + "/output/zscore_graphs/lipid_class")

    for region, region_data in df_final.groupby("Regions"):
        print(f"Creating graphs for {region}")

        lipid_classes = region_data["Lipid Class"].unique()

        for i, lipid_class in enumerate(lipid_classes):
            fig, ax = plt.subplots()
            data = region_data[region_data["Lipid Class"] == lipid_class]
            lipids = data["Lipids"].unique()
            genotype_data = list(data["Genotype"].unique())
            genotype_data.remove(control_name)
            genotype_data.insert(0, control_name)

            if debug:
                # Draw extra information to visualize the bar width calculations.
                mpl_debug_series(
                    len(lipids),
                    len(genotype_data),
                    group_width=group_width,
                    bar_width=bar_width,
                    bar_gap=bar_gap,
                    ax=ax,
                )

            width, positions = mpl_calc_series(
                len(lipids),
                len(genotype_data),
                group_width=group_width,
                bar_width=bar_width,
                bar_gap=bar_gap,
            )

            boxplot = []

            for j, lipid in enumerate(lipids):
                for g, genotype in enumerate(genotype_data):
                    experimental_values = data[
                        (data["Lipids"] == lipid) & (data["Genotype"] == genotype)
                        ]["Z Scores"]

                    bp = ax.boxplot(
                        experimental_values,
                        positions=[positions[j][g]],
                        widths=width,
                        patch_artist=True,
                        boxprops=dict(facecolor=palette[g], color="k", alpha=0.8),
                        medianprops=dict(color="k"),
                    )

                    boxplot.append(bp["boxes"][0])

                    ax.scatter(
                        np.ones(len(experimental_values)) * positions[j][g],
                        experimental_values,
                        color="k",
                        s=6,
                        zorder=3,
                    )

            ax.set_xticks([*range(len(lipids))])
            ax.set_xticklabels(lipids, rotation=90)
            ax.legend(
                boxplot,
                [control_name, *experimental_name],
                loc="center left",
                bbox_to_anchor=(1, 0.5),
            )

            if xlabel:
                ax.set_xlabel(xlabel)
            else:
                ax.set_xlabel(lipid_class)
            if ylabel:
                ax.set_ylabel(ylabel)
            else:
                ax.set_ylabel("Z Scores")
            if title:
                ax.set_title(title)
            else:
                ax.set_title(f"Z Scores in {region}")

            plt.tight_layout()
            plt.savefig(
                f"{output_path}/output/zscore_graphs/lipid_class/ZScores {region} {lipid_class}.png",
                dpi=1200,
            )
            if show:
                plt.show()

            plt.close()


def zscore_graph_class_average(
        df_final,
        control_name,
        experimental_name,
        output_path,
        palette,
        xlabel=None,
        ylabel=None,
        title=None,
        show=True,
        debug=False,
):
    """
    The `zscore_graph_class average` function generates boxplots and statistical annotations for visualizing average Z scores of lipids classes
    across regions. It performs the following tasks:

    - Plots boxplots to visualize the distribution of Z scores, distinguishing between control and experimental groups.
    - Perform appropriate statistical tests based on the number of genotype groups and annotate the graph with p-values.
        - If there are two genotypes:
            - Performs normality test (Shapiro-Wilk test) and homogeneity of variances test (Levene's test).
            - Based on the results, choose the appropriate test (e.g., t-test, Welch t-test, or Mann-Whitney U test).
        - If there are more than two genotypes:
            - Perform ANOVA to determine if there are any statistically significant differences between the means of the groups.
            - If ANOVA is significant, perform post-hoc Tukey HSD test to find which specific groups differ.
    - Annotates the plot with statistical significance indicators using `starbars.draw_annotation`.
    - Customizable plots with appropriate labels and title for better visualization.
    - Saves each plot as a PNG file in the specified `output_path`.
    - Optionally displays the plot (`show=True`) and closes it after display.

    The function also saves comments regarding the statistical tests performed for each lipid and region in an Excel
    sheet named "Comments" within the `output_path`.

    :param df_final: DataFrame containing Z scores and statistical test results.
    :param control_name: Name of the control group.
    :param experimental_name:Name of the experimental group.
    :param output_path: Path of the output folder.
    :param palette: Color palette for plotting.
    :param xlabel: Label for the x-axis. If None, defaults to "Genotype".
    :param ylabel: Label for the y-axis. If None, defaults to "Z Scores".
    :param title: Title for the plot. If None, defaults to "Z Scores for {lipid} in {region}".
    :param show: Whether to display plots interactively (default True).
    """

    group_width = 1
    bar_width = 0.1
    bar_gap = 0.01
    palette = sns.color_palette(palette)

    if not os.path.exists(output_path + "/output/zscore_graphs/class_average"):
        os.makedirs(output_path + "/output/zscore_graphs/class_average")

    for (region, lipid), data in df_final.groupby(["Regions", "Lipid Class"]):
        shapiro = data.iloc[0]["Shapiro Normality"]
        levene = data.iloc[0]["Levene Equality"]
        test = get_test(shapiro, levene)

    test_comment = [f"{test} will be performed for all of the lipids"]
    save_sheet(test_comment, "Comments", output_path)

    for (region, lipid), data in df_final.groupby(["Regions", "Lipid Class"]):
        print(f"Creating graph for {lipid} in {region}")

        fig, ax = plt.subplots()
        genotype_labels = list(data["Genotype"].unique())
        genotype_labels.remove(control_name)
        genotype_labels.insert(0, control_name)

        if debug:
            # Draw extra information to visualize the bar width calculations.
            mpl_debug_series(
                len(genotype_labels),
                1,
                group_width=group_width,
                bar_width=bar_width,
                bar_gap=bar_gap,
                ax=ax,
            )

        width, positions = mpl_calc_series(
            len(genotype_labels),
            1,
            group_width=group_width,
            bar_width=bar_width,
            bar_gap=bar_gap,
        )

        boxplot = []

        for g, genotype in enumerate(genotype_labels):
            values = data[data["Genotype"] == genotype]["Average Z Scores"]

            bp = ax.boxplot(
                values,
                positions=[g],
                widths=width,
                patch_artist=True,
                boxprops=dict(facecolor=palette[g], color="k", alpha=0.8),
                medianprops=dict(color="k"),
            )

            boxplot.append(bp["boxes"][0])

            ax.scatter(
                np.ones(len(values)) * g,
                values,
                color="k",
                s=6,
                zorder=3,
            )

        ax.set_xticks([*range(len(genotype_labels))])
        ax.set_xticklabels(genotype_labels, rotation=90)

        # Add statistical annotation
        pairs = []
        if len(genotype_labels) <= 2:
            for element in genotype_labels:
                test_comment = [f"{test} will be performed for all of the lipids"]
                save_sheet(test_comment, "Comments", output_path)
                if element != control_name:
                    stat, pvalue = get_pvalue(
                        test,
                        data[data["Genotype"] == control_name]["Average Z Scores"],
                        data[data["Genotype"] == element]["Average Z Scores"],
                    )
                    pairs.append((control_name, element, pvalue))

        else:
            test_comment = ["ANOVA test will be performed for all of the lipids"]
            save_sheet(test_comment, "Comments", output_path)
            stat, pvalue = stats.f_oneway(
                *[
                    data[data["Genotype"] == label]["Average Z Scores"]
                    for label in genotype_labels
                ]
            )
            if pvalue < 0.05:
                res = stats.tukey_hsd(
                    *[
                        data[data["Genotype"] == label]["Average Z Scores"]
                        for label in genotype_labels
                    ]
                )
                for (i, j), pair_value in np.ndenumerate(res.pvalue):
                    if i != j and i < j:
                        pairs.append(
                            (genotype_labels[i], genotype_labels[j], pair_value)
                        )

        starbars.draw_annotation(pairs, ns_show=False)
        comment = [f"For average z scores of {lipid} in {region}, P-value is {pvalue}."]
        save_sheet(comment, "Comments", output_path)

        ax.legend(
            boxplot,
            [control_name, *experimental_name],
            loc="upper left",
            bbox_to_anchor=(1, 0.5),
        )

        if xlabel:
            plt.xlabel(xlabel)
        else:
            plt.xlabel("Genotype")
        if ylabel:
            plt.ylabel(ylabel)
        else:
            plt.ylabel("Average Z Scores")

        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Average Z Scores for {lipid} in {region}")

        plt.tight_layout()
        plt.savefig(
            output_path
            + f"/output/zscore_graphs/class_average/Average Z Scores for {lipid} in {region}.png",
            dpi=1200,
        )
        if show:
            plt.show()
        plt.close()
