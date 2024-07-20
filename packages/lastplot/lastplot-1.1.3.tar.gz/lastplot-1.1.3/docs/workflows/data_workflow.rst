Data Workflow
=============

.. autofunction:: lastplot.data_workflow

Description of data_workflow
============================

The `data_workflow` function is designed to streamline the process of cleaning, analyzing, and normalizing lipid data.
This workflow includes several key steps: data cleanup, statistical testing, and Z score computation.
Below is a detailed explanation of each step and the overall workflow:

Detailed Descriptions of Each Step
----------------------------------

Data Cleanup:
~~~~~~~~~~~~~

- The function starts by removing samples labeled as 'Internal Standard' from the dataset.
- Lipids with 3 or more missing values in any region are filtered out.
- Remaining zero values are replaced with 80% of the minimum non-zero value within the corresponding group to handle missing or invalid data.
- The cleaned data and eliminated lipids are saved into different sheets of an output Excel file for further analysis.

Statistical Tests:
~~~~~~~~~~~~~~~~~~

- The function tests the normality of the residuals using the Shapiro-Wilk test.
- It also tests the equality of variances between the control group and experimental groups using Levene's test.
- The results of these tests (p-values) are compiled into a DataFrame, indicating the statistical properties of the data.

Z Score Computation:
~~~~~~~~~~~~~~~~~~~~

- The function computes the mean and standard deviation of normalized values for each lipid for each region.
- Z scores are then calculated for each data point.
- It also computes the average Z scores per lipid class for each region.
- The Z scores and average Z scores are merged into the final DataFrame.

By following these steps, the `data_workflow` function provides a comprehensive and systematic approach to cleaning, analyzing, and normalizing lipid data, ensuring that the dataset is ready for subsequent statistical analysis and interpretation.

It returns an Excel file for easy visualization of the data, and a final Dataframe for further data manipulation.