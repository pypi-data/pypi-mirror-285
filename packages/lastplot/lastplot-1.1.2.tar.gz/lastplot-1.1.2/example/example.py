import lastplot

df = lastplot.data_workflow(
    file_path="My project.xlsx",
    data_sheet="data",
    mice_sheet="mice id",
    output_path=".",
    control_name="WT",
    experimental_name=["FTD", "BPD", "HFD"]
)

lastplot.zscore_graph_lipid(
    df,
    control_name="WT",
    experimental_name=["FTD", "BPD", "HFD"],
    output_path=".",
    palette="Set1",
)
