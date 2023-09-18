


# THE PURPOSE OF THIS SCRIPT IS TO TAKE IN THE CLEANED MIL MILAGROS DATASET AND DERIVE A NEW TABLE FROM IT
# WHEREAS THE CLEANED DATASET HAS A ROW FOR EVERY CHECK-UP, THIS NEW TABLE WILL HAVE A ROW FOR EACH COMBINATION OF AGE (ROUNDED, AND IN YEARS) AND SEX
# THE UTILITY OF THIS NEW TABLE IS THAT IT ALLOWS US TO IDENTIFY PARTICULARLY VULNERABLE SEX-AGE GROUPS, INFORMING RECOMMENDATIONS TO IMPROVE MIL MILAGROS'S WORK



# IMPORTING PACKAGES
import pandas as pd
import numpy as np

# READING IN MIL MILAGROS'S FULL DATASET, WITH EVERY ROW CORRESPONDING TO CHECK-UP
mm_data = pd.read_excel("/Users/ajarbuckle/Desktop/MM_PROJECT/mm_data_redo/mm_data_clean.xlsx") 

# DEFINING CONDITIONS AND VALUES FOR THE CREATION OF AN AGE GROUP COLUMN
values = ['0-1', '1-2', '2-3', '3-4', '4-5']
conditions = [
    (mm_data['edad_a'] < 1),
    (mm_data['edad_a'] >= 1) & (mm_data['edad_a'] < 2),
    (mm_data['edad_a'] >= 2) & (mm_data['edad_a'] < 3),
    (mm_data['edad_a'] >= 3) & (mm_data['edad_a'] < 4),
    (mm_data['edad_a'] >= 4) & (mm_data['edad_a'] < 5)
]


# CREATING THE AGE GROUP COLUMN WITH THE DEFINED CONDITIONS AND VALUES 
mm_data['age_group'] = np.select(conditions, values, default = "5+")

# CREATING A NEW COLUMN FOR SEX-AGE GROUPS, WHICH IS JUST CONCATENATING THE ALREADY PRESENT SEX AND AGE COLUMNS
mm_data['sexo_age_group'] = mm_data['sexo'] + ' ' + mm_data['age_group'] + ' Years'

# CREATING THE NEW TABLE WITH INFORMATION ON EVERY SEX-AGE GROUP
age_sex_table = mm_data.groupby('sexo_age_group').agg(
    grupo = ('sexo_age_group', 'first'),
    chequeos_total = ('ID', 'count'),
    niños_total = ('ID', lambda x: x.nunique()),
    avg_z = ('puntaje_z', 'mean')
    )

# ADDING IN A FREQUENCY COLUMN (TOTAL CHECK-UPS / TOTAL CHILDREN)
age_sex_table['frecuencia'] = age_sex_table['chequeos_total'] / age_sex_table['niños_total']

# EXPORTING TABLE AS AN EXCEL FILE 
age_sex_table.to_excel('mm_data_age_sex_table.xlsx', index=False)
