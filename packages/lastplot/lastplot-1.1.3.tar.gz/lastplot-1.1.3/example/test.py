import lastplot

df = lastplot.data_workflow(
    file_path="Dementia project.xlsx",
    data_sheet="Quantification",
    mice_sheet="Sheet1",
    output_path=".",
    control_name="WT",
    experimental_name=["FTLD"],
)

lastplot.zscore_graph_class_average(
    df,
    control_name="WT",
    experimental_name=["FTLD"],
    output_path=".",
    palette="tab20b_r",
    show=True,
)
