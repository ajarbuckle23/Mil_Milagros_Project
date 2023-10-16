# Mil Milagros Project — Data Cleaning, Visualization, and Analysis

## About Mil Milagros 
Mil Milagros is a non-profit in Guatemala that equips mothers and teachers with skills and resources to improve the lives of children and families. In their Early Childhood Development (ECD) program, Community Coordinators teach other mothers and grandmothers how to prevent malnutrition and give their children a healthy foundation. This includes workshops on proper nutrition and hygiene for pregnant women and babies, monthly height and weight clinics, and home visits to support new mothers and their children. 

Learn more at their website: https://www.milmilagros.org/

## About the project
My role with Mil Milagros was to explore the impact that their initiatives had made in their partner communities. The organization had gathered a decade's worth of data from their height and weight clinics, but it was scattered across nearly 30 different spreadsheet in different formats that made it impossible to analyze. My first task was to clean and integrate this data into one table in a format that streamlined analysis. Next, I created visualizations and dashboards in Tableau (https://public.tableau.com/app/profile/aj.arbuckle) to communicate summary statistics to the program directors. Then, I derived several tables that showed summary statistics of progress for various segments of the population (community, age-sex group, and cohort by starting year). The metric used to assess progress was the rate of change in height-for-age z-score per year, which is one of the main indicators of malnutrition. For brevity I will continue to refer to it as 'change rate of HFA z-score.' Finally, I ran statistical tests to assess whether the change rate of HFA z-score differed between these segments in order to provide insight into potential ways to improve the program. 

## About the scripts
* mm_data_cleaning.py: Script used to clean and integrate data from various Excel files; calculate W.H.O-referenced HFA z-scores for each clinic visit; and remove potentially misleading outliers
  
* mm_individual.ipynb: Script used to 1) create a table with one row for each child who attended at least two height and weight clinics, meant to showcase changes in individual childen's HFA z-score during their time with Mil Milagros; 2) create visualizations for the distribution of change rate of HFA z-score; 3) compute summary statistics for the distribution of change rate of HFA z-score and the rate of stunting at first and last check-up

* mm_community.ipynb: Script used to 1) create a table with one row for each community, meant to showcase information such as years in partnership with Mil Milagros, total number of check-ups and kids, average change rate of HFA z-score, etc; 2) run a statistical test (Tukey's HSD) that investigates whether any of the communities differ from each other in their average change rate of HFA z-score

* mm_age_sex.ipynb: Script used to 1) create a table with one row for each age-sex group (where each child is classified based on their age-sex group at first check-up) to show average change rate of HFA z-score for each group 2) run a statistical test (Tukey's HSD) that investigates whether any of the age-sex groups differ from each other in their average change rate of HFA z-score

* mm_cohort.ipynb: Script used to 1) create a table with one row for each cohort by starting year (where each child is classified based on the year of their first check-up ) to show average change rate of HFA z-score for each cohort 2) run a statistical test (Tukey's HSD) that investigates whether any of the cohorts differ from each other in their average change rate of HFA z-score

## Results and Recommendations 
Assessing the efficacy of the program is not straightforward, as there is little height-for-age data for Guatemalan children available for comparison. At first glance, it might seem discouraging that under half (44.8%) of the children saw an improvement in HFA z-score during their time with the program. However, if it were expected that under a quarter of the children would see improvement in HFA z-score, this statistic would imply a great success. Thus, with no basis for comparison, this statistic does not lead to any firm conclusions about program efficacy. 

Data quality was an issue throughout the dataset. Missing information, such as birthday and name, led to some unfortunate loss of data points. Additionally, there were many unrealistic values for change in HFA z-score and rate of change in HFA z-score, which were likely caused by inaccurate measurements and/or erroneous data entry. To ensure accurate record-keeping, the program should be aware of these issues and try to prevent them. 

The Tukey's HSD tests for community and cohort both showed that there were no statistically significant differences in average change rate of HFA z-score between groups. This likely means that the program is equally successful in every community and for every cohort. However, the Tukey's HSD test for age-sex groups revealed that there was a statistically significant difference in average change rate of HFA z-score between two groups: 0-1 year old females and 1-2 year old males. The 1-2 year old males showed much better progress (average change rate of HFA z-score = 0.14 SD's) than the 0-1 year old females (average change rate of HFA z-score = -0.36 SD's). In fact, on average, the 1-2 year old males' condition was improving substantially while the 0-1 year old females' condition was deteriorating at an even faster rate. This could mean two potential implications: 1) the program's approach to treating the 1-2 year old males is different from their approach for 0-1 year old females, and the program should be adjusted to replicate the success of the 1-2 year old male group in the 0-1 year old female group; 2) 0-1 year old females are particulary at risk for malnutrition, and additional attention and resources should be allocated to them to prevent the deterioration of their conditions.


  


