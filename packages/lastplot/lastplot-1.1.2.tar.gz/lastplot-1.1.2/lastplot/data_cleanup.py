import os

import numpy as np
import pandas as pd


def load_data(datapath, sheet_name, mice_sheet):
    print("Loading data from " + datapath)
    # Getting the values for the lipids
    df = pd.read_excel(datapath, sheet_name=sheet_name, header=2)
    df.dropna(axis=1, how="all", inplace=True)

    # Getting the genotypes and regions of the mice samples
    df_mice = pd.read_excel(datapath, sheet_name=mice_sheet, header=None).T
    return df, df_mice


def data_cleanup(df, df_mice, output_path):
    """
    Cleans and processes lipid data from the provided DataFrame.

    This function performs several steps to clean and process lipid data:
    1. Removes 'Internal Standard' samples.
    2. Transforms and reshapes the data to long format.
    3. Filters out lipids with 3 or more missing values per region.
    4. Replaces zero values with 80% of the minimum value for the corresponding group.
    5. Logs and normalizes the cleaned values.
    6. Saves the cleaned and eliminated lipid data to an Excel file.

    """

    print("Cleaning data")

    # Eliminating the 'Internal Standard' samples
    print("Removing the Internal Standard samples")
    df = df[df["Lipid Class"] != "Internal Standard"]

    index = df.columns.tolist()
    subjects = []
    lipids = []
    values = []
    regions = []
    genotype = []
    lipid_class = []

    for i, lipid in enumerate(df["Short Name"]):
        for j, subject in enumerate(df.columns[4:]):
            if j != 0:
                y = index.index(j)
                subjects.append(subject)
                lipids.append(lipid)
                lipid_class.append(df.iloc[i, 3])
                values.append(df.iloc[i, y])
                regions.append(df_mice.iloc[1, j])
                genotype.append(df_mice.iloc[0, j])
            else:
                pass

    cleaned_values = [float(value) for value in values]
    lipids = [string.replace("/", "-") for string in lipids]

    df_sorted = pd.DataFrame(
        {
            "Mouse ID": subjects,
            "Lipids": lipids,
            "Lipid Class": lipid_class,
            "Regions": regions,
            "Genotype": genotype,
            "Values": cleaned_values,
        }
    )

    print("Filtering the lipids that have 3 or more values missing")

    # Filter out lipids in the region where they have 3 values missing
    def filter_lipids(df):
        lipid_zero_counts = df.groupby("Lipids")["Values"].apply(
            lambda x: (x == 0).sum()
        )
        valid_lipids = lipid_zero_counts[lipid_zero_counts < 3].index
        invalid_lipids = lipid_zero_counts[lipid_zero_counts >= 3].index
        valid_df = df[df["Lipids"].isin(valid_lipids)]
        invalid_df = df[df["Lipids"].isin(invalid_lipids)]
        return valid_df, invalid_df

    df_clean = pd.DataFrame()
    df_eliminated = pd.DataFrame()
    for name, group in df_sorted.groupby("Regions"):
        valid_df, invalid_df = filter_lipids(group)
        df_clean = pd.concat([df_clean, valid_df])
        df_eliminated = pd.concat([df_eliminated, invalid_df])

    print(
        "Replacing the zero values with 80% of the minimum value for the corresponding group"
    )

    # Replace zero values with 80% of the minimum value for the corresponding group
    def replace_zero_values(row, data):
        if row["Values"] == 0:
            group_df = data[
                (data["Lipids"] == row["Lipids"])
                & (data["Regions"] == row["Regions"])
                & (data["Genotype"] == row["Genotype"])
                & (data["Values"] != 0)
                ]
            if not group_df.empty:
                min_value = group_df["Values"].min()
                if min_value != 0:
                    new_value = 0.8 * min_value
                    return new_value
        return row["Values"]

    df_clean["Values"] = df_clean.apply(
        lambda row: replace_zero_values(row, df_clean), axis=1
    )
    df_clean["Log10 Values"] = np.log10(df_clean["Values"])

    if not os.path.exists(output_path + "/output"):
        os.makedirs(output_path + "/output")

    # Save the eliminated lipids and the normalized data with the Z Scores
    try:
        with pd.ExcelWriter(output_path + "/output/Output file.xlsx") as writer:
            df_eliminated.to_excel(writer, sheet_name="Removed lipids")
            print("Saving data to new Excel file")
    except PermissionError:
        print("Close the Excel file and try again.")

    return df_clean, invalid_df
