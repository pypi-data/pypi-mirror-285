import lastplot

df = lastplot.data_workflow(
    file_path="Dementia project.xlsx",
    data_sheet="Quantification",
    mice_sheet="Sheet1",
    output_path="./example",
    control_name="WT",
    experimental_name=["FTLD"],
)

lastplot.log_values_graph_lipid_class(
    df,
    control_name="WT",
    experimental_name=["FTLD"],
    output_path="./example",
    palette="Set3",
    show=False,
)
