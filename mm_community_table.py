


# THE PURPOSE OF THIS SCRIPT IS TO TAKE IN MIL MILAGROS'S FULL DATASET (CONTAINING INFORMATION ON EVERY CHECK-UP) AND A SECOND DATASET DERIVED FROM THE 
# FIRST THAT HAS ONE ROW FOR EVERY CHILD (WHO HAD AT LEAST TWO CHECKUPS), AND DERIVE ANOTHER TABLE THAT DISPLAYS COMMUNITY-WIDE INFORMATION,
# SUCH AS YEARS AFFILIATED WITH MIL MILAGROS, TOTAL NUMBER OF KIDS AND CHECK-UPS, AVERAGE CHANGE IN HEIGHT-FOR-AGE Z-SCORE AMONG ITS KIDS, ETC.


# IMPORTANT PACKAGES
import pandas as pd

# READING IN DATASET WITH ONE ROW FOR EVERY CHECK-UP
mm_data = pd.read_excel("/Users/ajarbuckle/Desktop/MM_PROJECT/mm_data_redo/mm_data_clean.xlsx") 

# CREATING A TEMPORARY TABLE THAT HAS COMMUNITY-WIDE INFORMATION ON INFORMATION NOT RELATED TO INDIVIDUAL CHILDREN
temp1 = mm_data.groupby('comunidad').agg(
    comunidad = ('comunidad', 'first'),
    año_primero = ('fecha_de_monitoreo', lambda x: x.min().year),
    año_último = ('fecha_de_monitoreo', lambda x: x.max().year),
    chequeos_total = ('ID', 'count'), 
    niños_total = ('ID', lambda x: x.nunique())
    )

# READING IN DATASET WITH ONE ROW FOR EVERY CHILD
mm_data = pd.read_excel("/Users/ajarbuckle/Desktop/MM_PROJECT/mm_data_redo/mm_data_individual_table.xlsx") 

# CREATING A TEMPORARY TABLE THAT HAS COMMUNITY-WIDE INFORMATION ON INFORMATION RELATED TO INDIVIDUAL CHILDREN
temp2 = mm_data.groupby('comunidad').agg(
    comunidad = ('comunidad', 'first'),
    avg_num_check = ('observaciones', 'mean'),
    avg_duration = ('duración', 'mean'),
    avg_freq = ('frecuencia', 'mean'),
    avg_start_age = ('monitoreo_prim_edad', 'mean'),
    avg_start_z = ('z_prim', 'mean'),
    avg_end_z = ('z_ult', 'mean')
    )

# CREATING A NEW COLUMN IN TEMP2 FOR AVERAGE CHANGE IN HEIGHT-FOR-AGE Z-SCORE PER CHILD
temp2['avg_change_z'] = temp2['avg_end_z'] - temp2['avg_start_z']

# CREATING A COLUMN FOR THE RATE OF HEIGHT-FOR-AGE Z-SCORE CHANGE OVER TIME
temp2['avg_z_dif_rate'] = (temp2['avg_change_z'] / temp2['avg_duration'])

# PUTTING THE TWO TEMPORARY TABLES TOGETHER TO ARRIVE AT THE FINAL DATAFRAME
# IT WAS NECESSARY TO FIRST RESET THE INDICES OF THE TEMPORARY TABLES SO THE MERGE FUNCTION WOULD WORK
temp1 = temp1.reset_index(drop=True)
temp2 = temp2.reset_index(drop=True)
final_table = pd.merge(temp1, temp2, left_on='comunidad', right_on='comunidad', how = 'outer')

# EXPORTING NEW DATAFRAME AS EXCEL FILE 
final_table.to_excel('mm_data_community_table.xlsx', index=False)