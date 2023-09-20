# Mil Milagros Project — Data Cleaning, Visualization, and Analysis

## About Mil Milagros 
Mil Milagros is a non-profit in Guatemala that equips mothers and teachers with skills and resources to improve the lives of children and families. In their Early Childhood Development (ECD) program, Community Coordinators teach other mothers and grandmothers how to prevent malnutrition and give their children a healthy foundation. This includes workshops on proper nutrition and hygiene for pregnant women and babies, monthly height and weight clinics, and home visits to support new mothers and their children. 

## About the project
My role with Mil Milagros was to explore the impact that their initiatives had had in their partner communities. The organization had gathered 10 years of data from their height and weight clinics, but it was scattered across nearly 30 different spreadsheet in different formats that made it difficult to analyze. My first task was to consolidate this data into one spreadsheet in one format that streamlined analysis. Next, I created visualizations and dashboards in Tableau (https://public.tableau.com/app/profile/aj.arbuckle) to communicate summary statistics to the program directors. Finally, I derived several tables showing aggegated statistics, which helped evaluat the success of the program and identify areas for improvement. 

## About the scripts
* mm_data_cleaning.py: Script used to pull all the spreadsheets together and reformat them, as well as reference W.H.O. data to calculate height-for-age z-scores (the main indicator of malnutrition) for each height and weight clinic visit.
* mm_individual_table.py: Script used to create a table for each child who attended at least two height and weight clinics, meant to showcase individual changes in height-for-age z-score during their time with Mil Milagros
* mm_community_table: Script used to create a table displaying aggregated statistics for each of Mil Milagros's partner communities, meant to highlight the relative success of the program across the different communities
* mm_age_sex_table: Script used to create a table displaying aggregated statistics for different sex-age groups, meant to highlight the relative success of the program across the different sex-age groups
  


