


# THE PURPOSE OF THIS SCRIPT IS TO TAKE IN THE CLEANED MIL MILAGROS DATASET AND DERIVE A NEW TABLE FROM IT
# WHEREAS THE CLEANED DATASET HAS A ROW FOR EVERY CHECK-UP, THIS NEW TABLE WILL HAVE A ROW FOR EACH CHILD WHO HAD AT LEAST 2 CHECK-UPS
# THE MAIN POINT IS TO SHOWCASE THE CHANGE IN HEIGHT-FOR-AGE Z-SCORE BETWEEN THEIR FIRST AND LAST CHECK-UPS, WHICH HAS OBVIOUS
# IMPORTANCE FOR EVALUATING THE IMPACT OF MIL MILAGROS'S PROGRAM


# IMPORTING PACKAGES
import pandas as pd

# READING IN DATA FROM CLEANED DATASET
mm_data = pd.read_excel("/Users/ajarbuckle/Desktop/MM_PROJECT/mm_data_redo/mm_data_clean.xlsx")

# FILTERING DOWN TO ONLY CHILDREN WHO APPEAR MORE THAN ONCE IN THE DATAFRAME; THIS IS BECAUSE I NEED AT LEAST 2 OBSERVATIONS TO CALCULATE 
# A CHANGE IN HEIGHT-FOR-AGE Z-SCORE
mm_data = mm_data.groupby('ID').filter(lambda x: len(x) > 1)

# GROUP THE DATAFRAME BY CHILD (USING UNIQUE IDENTIFIER ID) AND FIND THE EARLIEST AND LATEST CHECK-UP DATES, ALONG WITH THEIR ASSOCIATED HEIGHTS AND HEIGHT-FOR-AGE Z-SCORES
mm_data_grouped = mm_data.groupby('ID').agg(
    ID=('ID', 'first'),
    nombre_del_niño=('nombre_del_niño/niña', 'first'),
    fecha_de_nacimiento=('fecha_de_nacimiento', 'first'),
    comunidad=('comunidad', 'first'),
    sexo=('sexo', 'first'),
    monitoreo_prim = ('fecha_de_monitoreo', 'min'),
    monitoreo_ult = ('fecha_de_monitoreo', 'max'),
    talla_prim = ('talla', lambda x: x[mm_data.loc[x.index, 'fecha_de_monitoreo'].idxmin()]),
    talla_ult = ('talla', lambda x: x[mm_data.loc[x.index, 'fecha_de_monitoreo'].idxmax()]),
    z_prim = ('puntaje_z', lambda x: x[mm_data.loc[x.index, 'fecha_de_monitoreo'].idxmin()]),
    z_ult = ('puntaje_z', lambda x: x[mm_data.loc[x.index, 'fecha_de_monitoreo'].idxmax()]),
    observaciones=('fecha_de_monitoreo', 'count')
    )

# CREATING COLUMNS FOR THE DIFFERENCES BETWEEN HEIGHT AND HEIGHT-FOR-AGE Z-SCORE BETWEEN FIRST AND LAST CHECK-UPS
mm_data_grouped['talla_dif'] = mm_data_grouped['talla_ult'] - mm_data_grouped['talla_prim']
mm_data_grouped['z_dif'] = mm_data_grouped['z_ult'] - mm_data_grouped['z_prim']

# CREATING A COLUMN FOR HOW OLD THE CHILD WAS AT THEIR FIRST CHECK-UP (IN YEARS)
mm_data_grouped['monitoreo_prim_edad'] = (mm_data_grouped['monitoreo_prim'] - mm_data_grouped['fecha_de_nacimiento']).astype('timedelta64[D]') / 365.25

# CREATING A COLUMN FOR HOW MANY YEARS BETWEEN FIRST AND LAST CHECK-UP  
mm_data_grouped['duración'] = (mm_data_grouped['monitoreo_ult'] - mm_data_grouped['monitoreo_prim']).astype('timedelta64[D]') / 365.25

# CREATING A COLUMN FOR THE RATE OF HEIGHT-FOR-AGE Z-SCORE CHANGE OVER TIME
mm_data_grouped['z_dif_rate'] = (mm_data_grouped['z_dif'] / mm_data_grouped['duración'])

# CREATING A COLUMN FOR HOW FREQUENTLY THE CHILD HAD CHECK-UPS (NUMBER OF CHECK-UPS PER YEAR)
mm_data_grouped['frecuencia'] = mm_data_grouped['observaciones'] / mm_data_grouped['duración']

# CREATING COLUMNS FOR WHETHER THE CHILD WAS EXPERIENCING STUNTING AT FIRST AND LAST CHECK-UP
mm_data_grouped['stunted_at_first'] = mm_data_grouped['z_prim'] < -2
mm_data_grouped['stunted_at_end'] = mm_data_grouped['z_ult'] < -2

# EXPORTING
mm_data_grouped.to_excel('mm_data_individual_table.xlsx', index=False)
