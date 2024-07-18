import pandas as pd
import scipy.stats as stats


def get_pvalue(test, control_values, experimental_values):
    if any(value == "Mann Whitney" for value in test):
        stat = "Mann Whitney"
        statistics, pvalue = stats.mannwhitneyu(control_values, experimental_values)
    elif any(value == "Welch T-Test" for value in test):
        stat = "Welch T-Test"
        statistics, pvalue = stats.ttest_ind(
            control_values, experimental_values, equal_var=False
        )
    else:
        stat = "T-Test"
        statistics, pvalue = stats.ttest_ind(control_values, experimental_values)

    return stat, pvalue


def get_test(shapiro, levene):
    test = []
    if shapiro < 0.05 and levene < 0.05:
        test.append("T-Test")
    elif shapiro < 0.05 and levene > 0.05:
        test.append("Welch T-Test")
    else:
        test.append("Mann Whitney")

    return test


def statistics_tests(df_clean, control_name, experimental_name):
    """
    Performs statistical tests on cleaned lipid data to check for normality and equality of variances.

    This function performs the Shapiro-Wilk test for normality of residuals and Levene's test for equality
    of variances between control and experimental groups for each combination of region and lipid.
    """

    regions = []
    lipids = []
    shapiro_normality = []
    levene_equality = []

    print(
        "Checking for the normality of the residuals and the equality of the variances"
    )

    # Test for the normality of the residuals and for the equality of variances
    for (region, lipid), data in df_clean.groupby(["Regions", "Lipids"]):
        control_group = data[data["Genotype"] == control_name]
        genotype_data = df_clean.groupby(["Genotype"])["Log10 Values"].apply(list)
        values = data["Log10 Values"]
        shapiro_test = stats.shapiro(values)
        control_data = control_group["Log10 Values"]
        for genotype in experimental_name:
            if genotype != control_name:
                levene = stats.levene(control_data, genotype_data[genotype])
        shapiro_normality.append(shapiro_test.pvalue)
        levene_equality.append(levene.pvalue)
        regions.append(region)
        lipids.append(lipid)

    # Creating a new dataframe with the normality and equality information
    statistics = pd.DataFrame(
        {
            "Regions": regions,
            "Lipids": lipids,
            "Shapiro Normality": shapiro_normality,
            "Levene Equality": levene_equality,
        }
    )

    return statistics


def z_scores(df_clean, statistics):
    """
    Performs statistical tests to check for normality of residuals and equality of variances.

    This function:
    1. Tests the normality of the residuals using the Shapiro-Wilk test.
    2. Tests the equality of variances using Levene's test.
    3. Compiles the results of these tests for each region and lipid.
    """

    print("Computing the Z scores and the average Z scores per lipid class")

    # Z Scores and average Z Scores per lipid class
    grouped = (
        df_clean.groupby(["Regions", "Lipids"])["Log10 Values"]
        .agg(["mean", "std"])
        .reset_index()
    )
    grouped.rename(columns={"mean": "Mean", "std": "STD"}, inplace=True)
    df_final = pd.merge(df_clean, grouped, on=["Regions", "Lipids"], how="left")
    df_final["Z Scores"] = (
                                   df_final["Log10 Values"] - df_final["Mean"]
                           ) / df_final["STD"]

    average_z_scores = (
        df_final.groupby(["Regions", "Lipid Class", "Mouse ID"])["Z Scores"]
        .mean()
        .reset_index(name="Average Z Scores")
    )
    df_final = pd.merge(
        df_final, average_z_scores, on=["Lipid Class", "Regions", "Mouse ID"]
    )
    df_final = pd.merge(df_final, statistics, on=["Regions", "Lipids"], how="left")

    return df_final


def lipid_selection(df_final, invalid_df, control_name, experimental_name):
    unique_lipids = df_final['Lipids'].unique()
    unique_invalid = invalid_df['Lipids'].unique()
    common_values = set(unique_lipids).intersection(set(unique_invalid))

    for lipid in common_values:
        print("lipid", lipid)
        genotype_data = list(df_final["Genotype"].unique())
        genotype_data.remove(control_name)
        genotype_data.insert(0, control_name)
        value = []

        for region, data in df_final.groupby(["Regions"]):
            shapiro = stats.shapiro(data['Average Z Scores'])
            control_group = data[data["Genotype"] == control_name]
            control_data = control_group['Average Z Scores']
            for genotype in genotype_data:
                if genotype != control_name:
                    levene = stats.levene(control_data, genotype_data[genotype])
            test = get_test(shapiro, levene)

            for element in genotype_data:
                if element != control_name:
                    stat, pvalue = get_pvalue(
                        test,
                        data[data["Genotype"] == control_name]["Average Z Scores"],
                        data[data["Genotype"] == element]["Average Z Scores"],
                    )
                    value.append(pvalue)

    filtered = df_final[~df_final['Lipids'].isin(unique_invalid)]
    print(filtered.head())

    #
    # if any(value) < 0.05:
    #     pass
    # else:
    #     df_final = df_final[df_final["Lipids"] != lipid]

    return df_final
