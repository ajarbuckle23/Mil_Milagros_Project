



# THE PURPOSE OF THIS SCRIPT IS:
# 1) DATA CLEANING; READING IN ALL OF MIL MILAGROS'S SPREADSHEETS AND CONSOLIDATING THEM INTO ONE TABLE IN A USABLE FORMAT, THEN EXPORTING IT AS AN EXCEL FILE 
# 2) TO CALCULATE A HEIGHT-FOR-AGE Z-SCORE FOR EVERY CHECK-UP USING THE CHILD'S SEX, AGE AT THE CHECK-UP, AND HEIGHT AT CHECK-UP




# PART 1: DATA CLEANING

# IMPORTING PACKAGES 

import pandas as pd
from datetime import datetime
import re
import numpy as np
import os

# CREATING USEFUL ARRAYS 

# COLUMN NAMES; COLUMNS WITH THE SAME INFOMRATION OFTEN HAVE DIFFERENT NAMES BETWEEN MIL MILAGROS'S SPREADSHEETS
# THESE ARRAYS I'M CREATING ARE THE VARIOUS SETS OF COLUMN NAMES THAT APPEAR IN DIFFERENT SPREADSHEETS; I HAVE MARKED ELSEWHERE WHICH SPREADSHEETS HAVE WHICH SET
# OF COLUMN NAMES BY GIVING THEM A COLOR DESIGNATION; FOR EXAMPLE, "BLUE" SPREADSHEETS HAVE THE COLUMN NAMES IN THE ARRAY cols_blue 
# THESE ARRAYS ARE PASSED AS AN ARGUMENT TO THE FUNCTION cleaner1, A DATA CLEANING FUNCTION IN WHICH I RENAME THE COLUMNS SO THEY'RE ALL THE SAME

cols_red = np.array(["Nombre de la Madre", "Nombre de Niño/a", "Fecha de Nacimiento", "Fecha de monitoreo", "Peso", "Talla"])
cols_blu = np.array(["NOBRE DE LA MADRE", "NOMBRE DEL NIÑO/NIÑA", "FECHA DE NACIMIENTO", "FECHA DE MONITOREO", "PESO", "TALLA"])
cols_orn = np.array(["Nombre de la madre", "Nombre del niño", "Fecha de nacimiento", "Peso", "Talla", "Fecha de peso y talla"])
cols_prp = np.array(["NOBRE DE LA MADRE", "NOMBRE DEL NIÑO/NIÑA", "FECHA DE NACIMIENTO", "SEXO", "FECHA DE MONITOREO", "PESO", "TALLA"])
cols_grn = np.array(["NOMBRE DE LA MADRE", "NOMBRE DEL NIÑO/NIÑA", "FECHA DE NACIMIENTO", "SEXO", "FECHA DE MONITOREO", "PESO", "TALLA"])

# COMMUNITY NAMES; THE SAME COMMUNITY NAME WILL BE REFERRED TO DIFFERENTLY IN DIFFERENT SPREADSHEETS
# I HAVE GATHERED ALL THE WAYS OF WRITING EACH COMMUNITY NAME AND PUT THEM IN AN ARRAY; FOR EXAPMLE, THE COMMUNITY "NUEVO PROGRESO" IS WRITTEN 8 DIFFERENT WAYS, EACH OF WHICH IS ACCOUNTED FOR
# IN THE comm_np ARRAY
# THE community_renamer FUNCTION MAKES USE OF THESE ARRAYS TO MAKE SURE THAT ALL COMMUNITIES ARE REFERRED TO THE SAME WAY 

comm_np = np.array(["NP2016", "NP 2018", "NP2018", "NP2013", "NP", "NP2014", "NP2017", "NP2015"])
comm_ct = np.array(["Chutinamit 2016", "Chuti 2017"])
comm_ph = np.array(["PHV PM", "PH2014", "PHJ VIE AM 2018", "PHMAM", "PHM AM", "PHV AM", "PH2016", "PHJ MIE 2018", "PHJ VIE 2018",
"PH2017", "PHM", "PHVPM", "PHJ VIE PM 2018", "PHM PM", "PH2015", "PHVAM", "PHMPM", "PH2013"])
comm_lp = np.array(["LP 2018", "LP 2017", "LP"])
comm_nk = np.array(["NK"])
comm_xs = np.array(["XES 2018", "XS", "XS 2017"])
comm_lm = np.array(["LM", "LM 2018"])
comm_ch = np.array(["CH", "CHUIJOMIL"])
comm_cb = np.array(["CB"])
comm_cv = np.array(["CV", "CAMPO VERDE"])
comm_cg = np.array(["CG"])
comm_pz = np.array(["PZ", "PAM 2018"])
comm_unknown = np.array(["PRR 2018"])

#  ID COLUMNS; COLUMNS THAT STAY THE SAME FOR EACH CHILD IN THE SAME SPREADSHEET (SINCE dict_origen SPECIFIES WHICH SPREADSHEET THE DATA CAME FROM); 
#  THIS IS FOR THE PURPOSE OF A RATHER MESSY SOLUTION (THE w_to_l FUNCTION) TO CONVERTING THE DATA FROM WIDE FORMAT (WHERE SPREADSHEETS HAD RECURRING 
#  fecha_de_monitoreo, peso, AND talla COLUMNS) TO A LONG FORMAT (WHERE THERE IS ONLY ONE INSTANCE OF EACH OF THE fecha_de_monitoreo, peso, AND talla COLUMNS)  

id_cols = ["nombre_de_la_madre", "nombre_del_niño/niña", "fecha_de_nacimiento", "sexo", "communidad", "dict_origin"]

# DEFINING FUNCTIONS 

# init_reader: CUTS OUT JUNK ROWS IN THE EXCEL FILES BEFORE THE ACTUAL DATA BEGINS 

def init_reader(df):

    # FIND THE KEYWORD ROW; CASE-INSENSITIVE AND WHITESPACE-INSENSITIVE
    start_row = df[df.astype(str).apply(lambda x: x.str.contains("\s*peso\s*", na=False, flags=re.IGNORECASE).any(), axis=1)].index[0]

    # SLICE THE DATAFRAME TO INCLUDE ONLY THE ROWS STARTING FROM THE KEYWORD
    df = df.iloc[start_row:,:]

    # SET THE FIRST ROW AS THE HEADER
    # Set the first row as the header
    df = df.rename(columns = df.iloc[0])

    # DROP THE FIRST ROW
    df = df.drop(df.index[0])

    return df

# community_renamer: RENAMES COMMUNITIES FROM SHEET NAME ABREVIATIONS TO FULL NAMES

def community_renamer(sheet_name):
    if sheet_name in comm_np:
        return "Nuevo Progreso"
    elif sheet_name in comm_ct:
        return "Chutinamit"
    elif sheet_name in comm_ph:
        return "Pahaj"
    elif sheet_name in comm_lp:
        return "Los Planes"
    elif sheet_name in comm_nk:
        return "Nikajkim"
    elif sheet_name in comm_xs:
        return "Xesampual"
    elif sheet_name in comm_lm:
        return "Los Manantiales"
    elif sheet_name in comm_ch:
        return "Chuijomil"
    elif sheet_name in comm_cb:
        return "Cruz B"
    elif sheet_name in comm_cv:
        return "Campo Verde"
    elif sheet_name in comm_cg:
        return "Ciénaga Grande"
    elif sheet_name in comm_pz:
        return "Pamezabal"
    elif sheet_name in comm_unknown:
        return "Desconocido"
    else:
        return "Desconocido"
    
# cleaner1: init_reader + GETTING RID OF UNWANTED COLUMNS, ADDING IN SOME NEW COLUMNS + community_renamer

def cleaner1(df, col_arr):

    df = init_reader(df)

    # CONVERTING COLUMN NAMES TO STRINGS AND GETTING RID OF WHITESPACES
    df.columns = df.columns.astype(str).str.strip()

    # FILTERING TO GET ONLY THE COLUMNS IN THE ARRAY PASSED IN (TO DISREGARD IRRELEVANT DATA)
    df = df[col_arr]

    # ADDING IN THE COMMUNITY AND DICTIONARY ORIGIN COLUMNS
    df = df.assign(communidad = pd.Series([""] * len(df)))
    df = df.assign(dict_origin = pd.Series([""] * len(df)))


    # RENAMING COLUMNS
    if np.array_equal(col_arr, cols_red):
        df.rename(columns={"Nombre de la Madre":"nombre_de_la_madre",
                            "Nombre de Niño/a":"nombre_del_niño/niña",
                            "Fecha de Nacimiento":"fecha_de_nacimiento",
                            "Fecha de monitoreo":"fecha_de_monitoreo",
                            "Peso":"peso",
                            "Talla":"talla"}, inplace=True)
        df = df.assign(sexo = pd.Series([float('nan')] * len(df)))
    elif np.array_equal(col_arr, cols_blu):
        df.rename(columns={"NOBRE DE LA MADRE":"nombre_de_la_madre",
                            "NOMBRE DEL NIÑO/NIÑA":"nombre_del_niño/niña",
                            "FECHA DE NACIMIENTO":"fecha_de_nacimiento",
                            "FECHA DE MONITOREO":"fecha_de_monitoreo",
                            "PESO":"peso",
                            "TALLA":"talla"}, inplace=True)
        df = df.assign(sexo = pd.Series([float('nan')] * len(df)))
    elif np.array_equal(col_arr, cols_orn):
        df.rename(columns={"Nombre de la madre":"nombre_de_la_madre",
                            "Nombre del niño":"nombre_del_niño/niña",
                            "Fecha de nacimiento":"fecha_de_nacimiento",
                            "Fecha de peso y talla":"fecha_de_monitoreo",
                            "Peso":"peso",
                            "Talla":"talla"}, inplace=True)
        df = df.assign(sexo = pd.Series([float('nan')] * len(df)))
    elif np.array_equal(col_arr, cols_prp):
        df.rename(columns={"NOBRE DE LA MADRE":"nombre_de_la_madre",
                            "NOMBRE DEL NIÑO/NIÑA":"nombre_del_niño/niña",
                            "FECHA DE NACIMIENTO":"fecha_de_nacimiento",
                            "SEXO":"sexo",
                            "FECHA DE MONITOREO":"fecha_de_monitoreo",
                            "PESO":"peso",
                            "TALLA":"talla"}, inplace=True)
    elif np.array_equal(col_arr, cols_grn):
        df.rename(columns={"NOMBRE DE LA MADRE":"nombre_de_la_madre",
                            "NOMBRE DEL NIÑO/NIÑA":"nombre_del_niño/niña",
                            "FECHA DE NACIMIENTO":"fecha_de_nacimiento",
                            "SEXO":"sexo",
                            "FECHA DE MONITOREO":"fecha_de_monitoreo",
                            "PESO":"peso",
                            "TALLA":"talla"}, inplace=True)

    return df

# w_to_l: CONVERTING DATAFRAMES FROM WIDE TO LONG FORMAT THROUGH A VERY MESSY PROCESS OF CREATING TEMPORARY DATAFRAMES; FIRST TEMPORARY DATAFRAME IS id_cols PLUS 
# THE fecha_de_monitoreo COLUMN; SECOND IS id_cols AND THE peso COLUMN; THIRD IS id_cols AND THE talla COLUMN; THEN I PUT ALL THE DATAFRAMES BACK TOGETHER AGAIN BY TAKING THE FIRST
# TEMPORARY DATAFRAME AND ADDING JUST THE peso COLUMN FROM THE SECOND AND JUST THE talla COLUMN FROM THE THIRD

def w_to_l(df, id_cols):

    # CREATING TEMPORARY DATAFRAME 1, WITH ID COLUMNS AND fecha_de_monitoreo
    intermed1 = df[id_cols + ["fecha_de_monitoreo"]]
    # CONVERT DATAFRAME TO LONG FORMAT, WITH ONLY ONE fecha_de_monitoreo COLUMN
    intermed1 = intermed1.melt(id_vars = id_cols,
                   value_name = "fecha_de_monitoreo")
    # DROPPING THE AUTOMATICALLY GENERATED variable COLUMN, SINCE IT IS just fecha_de_monitoreo FOR THEM ALL 
    intermed1 = intermed1.drop(columns = "variable")

     # CREATING TEMPORARY DATAFRAME 2, WITH ID COLUMNS AND peso 
    intermed2 = df[id_cols + ["peso"]]
     # CONVERT DATAFRAME TO LONG FORMAT, WITH ONLY ONE peso COLUMN
    intermed2 = intermed2.melt(id_vars = id_cols,
                   value_name = "peso")
    # DROPPING THE AUTOMATICALLY GENERATED variable COLUMN, SINCE IT IS just peso FOR THEM ALL 
    intermed2 = intermed2.drop(columns = "variable")

     # CREATING TEMPORARY DATAFRAME 3, WITH ID COLUMNS AND talla
    intermed3 = df[id_cols + ["talla"]]
     # CONVERT DATAFRAME TO LONG FORMAT, WITH ONLY ONE talla COLUMN
    intermed3 = intermed3.melt(id_vars = id_cols,
                   value_name = "talla")
    # DROPPING THE AUTOMATICALLY GENERATED variable COLUMN, SINCE IT IS just talla FOR THEM ALL 
    intermed3 = intermed3.drop(columns = "variable")

    # ADD THE peso FROM intermed2 TO intermed1 AND RENAME THE NEW COLUMN peso
    intermed1 = intermed1.assign(new_column=intermed2['peso'])
    intermed1.rename(columns={'new_column': 'peso'}, inplace=True)

    # ADD THE peso FROM intermed3 TO intermed1 AND RENAME THE NEW COLUMN talla
    intermed1 = intermed1.assign(new_column=intermed3['talla'])
    intermed1.rename(columns={'new_column': 'talla'}, inplace=True)

    return intermed1

# cleaner2: w_to_l FUNCTION + DROPPING ROWS WHERE THERE IS NO SPECIFIED MEASUREMENT DATE OR NAME, AND RECASTING VARIABLES AS APPROPRITE DATA TYPES

def cleaner2(df, id_cols):

    # CONVERTING DATAFRAME FROM WIDE TO LONG FORMAT
    df = w_to_l(df, id_cols)

    # GETTING RID OF ROWS WHERE THERE IS NO MEASUREMENT DATE OR NAME
    df = df.dropna(subset=['fecha_de_monitoreo'])
    df = df.dropna(subset=['nombre_del_niño/niña'])

    # GETTING RID OF LETTERS AND WHITESPACES IN peso AND talla COLUMNS, THEN CONVERTING THEM TO NUMERIC TYPE
    df['peso'] = pd.to_numeric(df['peso'].astype(str).str.replace(r'[^0-9\.]', ''), errors='coerce')
    df['talla'] = pd.to_numeric(df['talla'].astype(str).str.replace(r'[^0-9\.]', ''), errors='coerce')

    # GETTING RID OF NA'S IN talla COLUMN AFTER GETTING RID OF LETTERS, SINCE THERE WERE SOME VALUES WITH ONLY LETTERS 
    # THAT ENDED UP NOT BEING DROPPED BY THE FIRST LINE OF CODE TO DROP NA'S
    df = df.dropna(subset=['talla'])

    # RECASTING sexo, comunidad, AND dict_origin COLUMNS AS CATEGORICAL VARIABLES 
    df['sexo'] = df['sexo'].astype('category')
    df['communidad'] = df['communidad'].astype('category')
    df['dict_origin'] = df['dict_origin'].astype('category')

    return df

# datetime_converter: CONVERTS THE fecha_de_monitoreo AND fecha_de_nacimiento COLUMNS INTO DATETIME VARIABLES; SINCE DIFFERENT EXCEL FILES USE 
# DIFFERENT DATETIME FORMATS, THE FORMAT TO CONVERT THE fecha_de_monitoreo AND fecha_de_nacimiento COLUMNS TO VARIES WITH THE "specification" ARGUMENT

def datetime_converter(df, specification):

    if specification == "month_first":
        df['fecha_de_monitoreo'] = pd.to_datetime(df['fecha_de_monitoreo'], format = None, errors = "coerce")
        df['fecha_de_nacimiento'] = pd.to_datetime(df['fecha_de_nacimiento'], format = None, errors = "coerce")
    elif specification == "day_first":
        df['fecha_de_monitoreo'] = pd.to_datetime(df['fecha_de_monitoreo'], dayfirst = True, format = None, errors = "coerce")
        df['fecha_de_nacimiento'] = pd.to_datetime(df['fecha_de_nacimiento'], dayfirst = True, format = None, errors = "coerce")

    return df




# READING IN EACH EXCEL FILE AND EACH RELEVANT SHEET IN IT ONE BY ONE 
# EACH SHEET BECOMES ITS OWN TABLE, WHICH IS STORED IN A DICTIONARY; AFTER I STANDARDIZE THE FORMAT OF EACH SHEET (AS A DATAFRAME)
# I PUT ALL THE DICTIONARIES TOGETHER TO FORM ONE FINAL DATAFRAME WITH ALL THE DATA, WHICH I THEN EXPORT AS AN EXCEL FILE 

# READING EACH EXCEL FILE INTO A DICTIONARY, WITH EACH RELEVANT SHEET AS A SEPARATE DATAFRAME IN THE DICTIONARY; 
# ITERATION BEGINGS OVER EACH DATAFRAME IN THE DICTIONARY, WITH THE FOLLOWING PROCESS APPLIED TO EACH DATAFRAME
# 1) cleaner1 FUNCTION IS APPLIED
# 2) THE SHEET IS GIVEN A NEW COLUMN (dict_origin) WHICH TELLS US WHICH EXCEL FILE THAT IT CAME FROM 
# 3) THE SHEET IS GIVEN ANOTHER NEW COLUMN (communidad); ITS VALUE COMES FROM THE RESULT OF THE community_renamer FUNCTION, WHICH CONVERTS THE 
# SHEET NAME TO THE ACTUAL NAME OF THE COMMUNITY
# 4) cleaner2 FUNCTION IS APPLIED
# 5) datetime_converter FUNCTION IS APPLIED 


#### DI 2013-2018 FOLDER ####

# PAHAJ

dict_DI_PH = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/DI/2013-2018/Prevenir_Pahaj.xlsx',
    sheet_name = ["PH2013","PH2014","PH2015","PH2016","PH2017"], header = None)

for sheet_name, df in dict_DI_PH.items():
    dict_DI_PH[sheet_name] = cleaner1(df, col_arr = cols_red)
    dict_DI_PH[sheet_name]["dict_origin"] = "dict_DI_PH"
    dict_DI_PH[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_DI_PH[sheet_name] = cleaner2(dict_DI_PH[sheet_name], id_cols)
    dict_DI_PH[sheet_name] = datetime_converter(dict_DI_PH[sheet_name], "month_first")

# XESAMPUAL AND LOS PLANES

dict_DI_XSLP = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/DI/2013-2018/Prevenir_Xesampual_y_Los_Planes.xlsx',
    sheet_name = ["LP 2017","XS 2017"], header = None)

for sheet_name, df in dict_DI_XSLP.items():
    dict_DI_XSLP[sheet_name] = cleaner1(df, col_arr = cols_blu)
    dict_DI_XSLP[sheet_name]["dict_origin"] = "dict_DI_XSLP"
    dict_DI_XSLP[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_DI_XSLP[sheet_name] = cleaner2(dict_DI_XSLP[sheet_name], id_cols)
    dict_DI_XSLP[sheet_name] = datetime_converter(dict_DI_XSLP[sheet_name], "month_first")

# NUEVO PROGRESO

dict_DI_NP = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/DI/2013-2018/Prevenir_Nuevo_Progreso.xlsx',
    sheet_name = ["NP2013","NP2014","NP2015","NP2016","NP2017","NP2018"], header = None)

for sheet_name, df in dict_DI_NP.items():
    dict_DI_NP[sheet_name] = cleaner1(df, col_arr = cols_red)
    dict_DI_NP[sheet_name]["dict_origin"] = "dict_DI_NP"
    dict_DI_NP[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_DI_NP[sheet_name] = cleaner2(dict_DI_NP[sheet_name], id_cols)
    dict_DI_NP[sheet_name] = datetime_converter(dict_DI_NP[sheet_name], "month_first")

# CHUTINAMIT

dict_DI_CT = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/DI/2013-2018/Prevenir_chutinamit_2016.xlsx',
    sheet_name = ["Chutinamit 2016","Chuti 2017"], header = None)

for sheet_name, df in dict_DI_CT.items():
    dict_DI_CT[sheet_name] = cleaner1(df, col_arr = cols_orn)
    dict_DI_CT[sheet_name]["dict_origin"] = "dict_DI_CT"
    dict_DI_CT[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_DI_CT[sheet_name] = cleaner2(dict_DI_CT[sheet_name], id_cols)
    dict_DI_CT[sheet_name] = datetime_converter(dict_DI_CT[sheet_name], "month_first")

#### DI 2019 FOLDER ####

# SPREADSHEET WITHOUT THE (1)

dict_DI2019 = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/DI/2019/Desarrollo_Infantil_DB_2019.xlsx',
    sheet_name = ["CH","CG","CB","LM","LP","NK","NP","PHM AM","PHM PM","PHV AM","PHV PM","PZ","XS","CV"], header = None)

for sheet_name, df in dict_DI2019.items():
    dict_DI2019[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_DI2019[sheet_name]["dict_origin"] = "dict_DI2019"
    dict_DI2019[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_DI2019[sheet_name] = cleaner2(dict_DI2019[sheet_name], id_cols)
    dict_DI2019[sheet_name] = datetime_converter(dict_DI2019[sheet_name], "month_first")


# SPREADSHEET WITH THE (1)

dict_DI2019_1 = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/DI/2019/Desarrollo_Infantil_DB_2019_(1).xlsx',
    sheet_name = ["CH","CG","CB","LM","LP","NK","NP","PHM AM","PHM PM","PHV AM","PHV PM","PZ","XS","CV"], header = None)

for sheet_name, df in dict_DI2019_1.items():
    dict_DI2019_1[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_DI2019_1[sheet_name]["dict_origin"] = "dict_DI2019_1"
    dict_DI2019_1[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_DI2019_1[sheet_name] = cleaner2(dict_DI2019_1[sheet_name], id_cols)
    dict_DI2019_1[sheet_name] = datetime_converter(dict_DI2019_1[sheet_name], "month_first")

#### ME 2018 FOLDER ####

# SPREADSHEET WITHOUT 2018 IN THE NAME

dict_ME2018_1_red = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2018/Desarrollo_Infantil_DB.xlsx',
    sheet_name = ["PHJ MIE 2018", "PHJ VIE 2018", "PHJ VIE AM 2018", "PHJ VIE PM 2018", "XES 2018",
     "NP 2018", "LM 2018"], header = None)

dict_ME2018_1_blu = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2018/Desarrollo_Infantil_DB.xlsx',
    sheet_name = ["LP 2018", "PAM 2018", "CHUIJOMIL", "CAMPO VERDE", "PRR 2018"], header = None)

for sheet_name, df in dict_ME2018_1_red.items():
    dict_ME2018_1_red[sheet_name] = cleaner1(df, col_arr = cols_red)
    dict_ME2018_1_red[sheet_name]["dict_origin"] = "dict_ME2018_1"
    dict_ME2018_1_red[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2018_1_red[sheet_name] = cleaner2(dict_ME2018_1_red[sheet_name], id_cols)
    dict_ME2018_1_red[sheet_name] = datetime_converter(dict_ME2018_1_red[sheet_name], "month_first")

for sheet_name, df in dict_ME2018_1_blu.items():
    dict_ME2018_1_blu[sheet_name] = cleaner1(df, col_arr = cols_blu)
    dict_ME2018_1_blu[sheet_name]["dict_origin"] = "dict_ME2018_1"
    dict_ME2018_1_blu[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2018_1_blu[sheet_name] = cleaner2(dict_ME2018_1_blu[sheet_name], id_cols)
    dict_ME2018_1_blu[sheet_name] = datetime_converter(dict_ME2018_1_blu[sheet_name], "month_first")

# SPREADSHEET WITH 2018 IN THE NAME

dict_ME2018_2_red = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2018/Desarrollo_Infantil_DB.xlsx',
    sheet_name = ["PHJ MIE 2018", "PHJ VIE 2018", "PHJ VIE AM 2018", "PHJ VIE PM 2018", "XES 2018",
     "NP 2018", "LM 2018"], header = None)

dict_ME2018_2_blu = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2018/Desarrollo_Infantil_DB.xlsx',
    sheet_name = ["LP 2018", "PAM 2018", "CHUIJOMIL", "CAMPO VERDE", "PRR 2018"], header = None)

for sheet_name, df in dict_ME2018_2_red.items():
    dict_ME2018_2_red[sheet_name] = cleaner1(df, col_arr = cols_red)
    dict_ME2018_2_red[sheet_name]["dict_origin"] = "dict_ME2018_2"
    dict_ME2018_2_red[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2018_2_red[sheet_name] = cleaner2(dict_ME2018_2_red[sheet_name], id_cols)
    dict_ME2018_2_red[sheet_name] = datetime_converter(dict_ME2018_2_red[sheet_name], "month_first")

for sheet_name, df in dict_ME2018_2_blu.items():
    dict_ME2018_2_blu[sheet_name] = cleaner1(df, col_arr = cols_blu)
    dict_ME2018_2_blu[sheet_name]["dict_origin"] = "dict_ME2018_2"
    dict_ME2018_2_blu[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2018_2_blu[sheet_name] = cleaner2(dict_ME2018_2_blu[sheet_name], id_cols)
    dict_ME2018_2_blu[sheet_name] = datetime_converter(dict_ME2018_2_blu[sheet_name], "month_first")


#### ME 2019 FOLDER ####

# SPREADSHEET 1

dict_ME2019_julio_1 = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/1.Análisis_DI_julio_2019.xlsx',
    sheet_name = ["NK","NP","PHM AM","PHM PM","PHV AM","PHV PM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_julio_1.items():
    dict_ME2019_julio_1[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_julio_1[sheet_name]["dict_origin"] = "dict_ME2019_julio_1"
    dict_ME2019_julio_1[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_julio_1[sheet_name] = cleaner2(dict_ME2019_julio_1[sheet_name], id_cols)
    dict_ME2019_julio_1[sheet_name] = datetime_converter(dict_ME2019_julio_1[sheet_name], "month_first")

# SPREADSHEET 2

dict_ME2019_enero = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/1.Análisis_DIDC_enero_2019_[With Formulas].xlsx',
    sheet_name = ["CV","CH","LM","LP","NP","PHM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_enero.items():
    dict_ME2019_enero[sheet_name] = cleaner1(df, col_arr = cols_blu)
    dict_ME2019_enero[sheet_name]["dict_origin"] = "dict_ME2019_enero"
    dict_ME2019_enero[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_enero[sheet_name] = cleaner2(dict_ME2019_enero[sheet_name], id_cols)
    dict_ME2019_enero[sheet_name] = datetime_converter(dict_ME2019_enero[sheet_name], "month_first")

# SPREADSHEET 3

dict_ME2019_febrero = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/2.Análisis_DIDC_feb_2019.xlsx',
    sheet_name = ["CV","CH","LM","LP","NP","PHM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_febrero.items():
    dict_ME2019_febrero[sheet_name] = cleaner1(df, col_arr = cols_blu)
    dict_ME2019_febrero[sheet_name]["dict_origin"] = "dict_ME2019_febrero"
    dict_ME2019_febrero[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_febrero[sheet_name] = cleaner2(dict_ME2019_febrero[sheet_name], id_cols)
    dict_ME2019_febrero[sheet_name] = datetime_converter(dict_ME2019_febrero[sheet_name], "month_first")

# SPREADSHEET 4

dict_ME2019_marzo = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/3.Análisis_DIDC_marzo_2019.xlsx',
    sheet_name = ["CV","CH","CG","CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_marzo.items():
    dict_ME2019_marzo[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_marzo[sheet_name]["dict_origin"] = "dict_ME2019_marzo"
    dict_ME2019_marzo[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_marzo[sheet_name] = cleaner2(dict_ME2019_marzo[sheet_name], id_cols)
    dict_ME2019_marzo[sheet_name] = datetime_converter(dict_ME2019_marzo[sheet_name], "month_first")

# SPREADSHEET 5

dict_ME2019_abril = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/4.Análisis_DIDC_abril_2019.xlsx',
    sheet_name = ["CV","CH","CG","CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_abril.items():
    dict_ME2019_abril[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_abril[sheet_name]["dict_origin"] = "dict_ME2019_abril"
    dict_ME2019_abril[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_abril[sheet_name] = cleaner2(dict_ME2019_abril[sheet_name], id_cols)
    dict_ME2019_abril[sheet_name] = datetime_converter(dict_ME2019_abril[sheet_name], "month_first")

# SPREADSHEET 6

dict_ME2019_mayo = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/5.Análisis_DI_mayo_2019.xlsx',
    sheet_name = ["CH","CG","CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_mayo.items():
    dict_ME2019_mayo[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_mayo[sheet_name]["dict_origin"] = "dict_ME2019_mayo"
    dict_ME2019_mayo[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_mayo[sheet_name] = cleaner2(dict_ME2019_mayo[sheet_name], id_cols)
    dict_ME2019_mayo[sheet_name] = datetime_converter(dict_ME2019_mayo[sheet_name], "month_first")

# SPREADSHEET 7

dict_ME2019_junio = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/6.Análisis_DI_junio_2019_(1).xlsx',
    sheet_name = ["CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_junio.items():
    dict_ME2019_junio[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_junio[sheet_name]["dict_origin"] = "dict_ME2019_junio"
    dict_ME2019_junio[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_junio[sheet_name] = cleaner2(dict_ME2019_junio[sheet_name], id_cols)
    dict_ME2019_junio[sheet_name] = datetime_converter(dict_ME2019_junio[sheet_name], "month_first")

# SPREADSHEET 8

dict_ME2019_julio_7 = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/7.Análisis_DI_julio_2019_(1).xlsx',
    sheet_name = ["CG","CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_julio_7.items():
    dict_ME2019_julio_7[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_julio_7[sheet_name]["dict_origin"] = "dict_ME2019_julio_7"
    dict_ME2019_julio_7[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_julio_7[sheet_name] = cleaner2(dict_ME2019_julio_7[sheet_name], id_cols)
    dict_ME2019_julio_7[sheet_name] = datetime_converter(dict_ME2019_julio_7[sheet_name], "month_first")

# SPREADSHEET 9

dict_ME2019_agosto = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/8.Análisis_DI_agosto_2019_(1).xlsx',
    sheet_name = ["CH","CG","CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_agosto.items():
    dict_ME2019_agosto[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_agosto[sheet_name]["dict_origin"] = "dict_ME2019_agosto"
    dict_ME2019_agosto[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_agosto[sheet_name] = cleaner2(dict_ME2019_agosto[sheet_name], id_cols)
    dict_ME2019_agosto[sheet_name] = datetime_converter(dict_ME2019_agosto[sheet_name], "month_first")

# SPREADSHEET 10

dict_ME2019_noviembre_8 = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/8.Análisis_DI_Noviembre_2019_(1).xlsx',
    sheet_name = ["CG","CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_noviembre_8.items():
    dict_ME2019_noviembre_8[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_noviembre_8[sheet_name]["dict_origin"] = "dict_ME2019_noviembre_8"
    dict_ME2019_noviembre_8[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_noviembre_8[sheet_name] = cleaner2(dict_ME2019_noviembre_8[sheet_name], id_cols)
    dict_ME2019_noviembre_8[sheet_name] = datetime_converter(dict_ME2019_noviembre_8[sheet_name], "month_first")

# SPREADSHEET 11

dict_ME2019_octubre = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/8.Análisis_DI_Octubre_2019_Copy_(1).xlsx',
    sheet_name = ["CH","CG","CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_octubre.items():
    dict_ME2019_octubre[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_octubre[sheet_name]["dict_origin"] = "dict_ME2019_octubre"
    dict_ME2019_octubre[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_octubre[sheet_name] = cleaner2(dict_ME2019_octubre[sheet_name], id_cols)
    dict_ME2019_octubre[sheet_name] = datetime_converter(dict_ME2019_octubre[sheet_name], "month_first")

# SPREADSHEET 12

dict_ME2019_septiembre = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/8.Análisis_DI_Septiembre_2019_(1).xlsx',
    sheet_name = ["CH","CG","CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_septiembre.items():
    dict_ME2019_septiembre[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_septiembre[sheet_name]["dict_origin"] = "dict_ME2019_septiembre"
    dict_ME2019_septiembre[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_septiembre[sheet_name] = cleaner2(dict_ME2019_septiembre[sheet_name], id_cols)
    dict_ME2019_septiembre[sheet_name] = datetime_converter(dict_ME2019_septiembre[sheet_name], "month_first")


# SPREADSHEET 13

dict_ME2019_noviembre_11 = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/11.Análisis_DI_Noviembre_2019_(1).xlsx',
    sheet_name = ["CH","CG","CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_noviembre_11.items():
    dict_ME2019_noviembre_11[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_noviembre_11[sheet_name]["dict_origin"] = "dict_ME2019_noviembre_11"
    dict_ME2019_noviembre_11[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_noviembre_11[sheet_name] = cleaner2(dict_ME2019_noviembre_11[sheet_name], id_cols)
    dict_ME2019_noviembre_11[sheet_name] = datetime_converter(dict_ME2019_noviembre_11[sheet_name], "month_first")

# SPREADSHEET 14

dict_ME2019_diciembre = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2019/12.Análisis_DI_Diciembre_2019_(1).xlsx',
    sheet_name = ["CH","CG","CB","LM","LP","NK","NP","PHMAM","PHMPM","PHVAM","PHVPM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2019_diciembre.items():
    dict_ME2019_diciembre[sheet_name] = cleaner1(df, col_arr = cols_prp)
    dict_ME2019_diciembre[sheet_name]["dict_origin"] = "dict_ME2019_diciembre"
    dict_ME2019_diciembre[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2019_diciembre[sheet_name] = cleaner2(dict_ME2019_diciembre[sheet_name], id_cols)
    dict_ME2019_diciembre[sheet_name] = datetime_converter(dict_ME2019_diciembre[sheet_name], "month_first")

#### ME 2020 FOLDER ####

dict_ME2020 = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2020/Monitoreo_de_crecimiento.xlsx',
    sheet_name = ["CH","CG","CB","LM","LP","NK","NP","PHM AM","PHM PM","PHV AM","PHV PM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2020.items():
    dict_ME2020[sheet_name] = cleaner1(df, col_arr = cols_grn)
    dict_ME2020[sheet_name]["dict_origin"] = "dict_ME2020"
    dict_ME2020[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2020[sheet_name] = cleaner2(dict_ME2020[sheet_name], id_cols)
    dict_ME2020[sheet_name]["fecha_de_monitoreo"] = dict_ME2020[sheet_name]["fecha_de_monitoreo"]
    dict_ME2020[sheet_name] = datetime_converter(dict_ME2020[sheet_name], "day_first")


#### ME 2021 FOLDER ####

dict_ME2021 = pd.read_excel('/Users/ajarbuckle/Desktop/MM_Project/mm_raw_data/ME/2021/Monitoreo_de_Crecimiento_Peso_Talla_2021.xlsx',
    sheet_name = ["CH","CG","CB","LM","LP","NK","NP","PHM AM","PHM PM","PHV AM","PHV PM","PZ","XS"], header = None)

for sheet_name, df in dict_ME2021.items():
    dict_ME2021[sheet_name] = cleaner1(df, col_arr = cols_grn)
    dict_ME2021[sheet_name]["dict_origin"] = "dict_ME2021"
    dict_ME2021[sheet_name]["communidad"] = community_renamer(sheet_name)
    dict_ME2021[sheet_name] = cleaner2(dict_ME2021[sheet_name], id_cols)
    dict_ME2021[sheet_name] = datetime_converter(dict_ME2021[sheet_name], "day_first")

# PUTTING ALL THE DATAFRAMES FROM EACH DICTIONARY TOGETHER INTO ONE MASTER DATAFRAME

master_df = pd.concat([*dict_DI_CT.values(), *dict_DI_NP.values(), *dict_DI_XSLP.values(),
*dict_DI_PH.values(), *dict_ME2020.values(), *dict_ME2021.values(), *dict_DI2019_1.values(),
*dict_DI2019.values(), *dict_ME2018_2_blu.values(), *dict_ME2018_2_red.values(),
*dict_ME2018_1_blu.values(), *dict_ME2018_1_red.values(), *dict_ME2019_diciembre.values(),
*dict_ME2019_noviembre_11.values(), *dict_ME2019_septiembre.values(), *dict_ME2019_octubre.values(),
*dict_ME2019_noviembre_8.values(), *dict_ME2019_agosto.values(),
*dict_ME2019_julio_7.values(), *dict_ME2019_junio.values(),
*dict_ME2019_mayo.values(), *dict_ME2019_abril.values(), *dict_ME2019_marzo.values(),
*dict_ME2019_febrero.values(), *dict_ME2019_enero.values(), *dict_ME2019_julio_1.values()], ignore_index=True)

# GETTING RID OF WHITESPACE IN ALL STRING COLUMNS

master_df = master_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# GETTING RID OF NUMBERS AND WHITESPACE IN MOTHER'S NAME COLUMN 

master_df['nombre_de_la_madre'] = master_df['nombre_de_la_madre'].apply(lambda x: re.sub(r'\d', '', str(x)) if pd.notnull(x) else x)
master_df['nombre_de_la_madre'] = master_df['nombre_de_la_madre'].str.strip()

# GETTING RID OF NUMBERS AND WHITESPACE IN CHILD'S NAME COLUMN

master_df['nombre_del_niño/niña'] = master_df['nombre_del_niño/niña'].apply(lambda x: re.sub(r'\d', '', str(x)) if pd.notnull(x) else x)
master_df['nombre_del_niño/niña'] = master_df['nombre_del_niño/niña'].str.strip()

# FILLING IN SEX FOR CHILDREN WHO HAD SEX SPECIFIED IN AT LEAST ONE OBSERVATION AND DIDN'T HAVE IT SPECIFIED IN AT LEAST ONE OTHER
# SEX HAS TO BE SPECIFIED IN ORDER FOR A HEIGHT-FOR-AGE Z-SCORE TO BE CALCULATED

# CREATING A BOOLEAN MASK THAT IS TRUE WHEN SEX IS NOT SPECIFIED FOR THE ROW
mask = master_df['sexo'].isna()

# SPLITTING THE MASTER DATAFRAME INTO TWO PARTS, ONE WHERE SEX IS SPECIFIED AND ONE WHERE IT'S NOT
specified = master_df[~mask]
not_specified = master_df[mask]

# ITERATING OVER EACH ROW IN not_specified
for index, row in not_specified.iterrows():
    # GET THE CHILD'S NAME
    nombre_nino = row['nombre_del_niño/niña']
    # SEARCH FOR A ROW IN specified WHERE THE NAME MATCHES nombre_nino
    match = specified.loc[(specified['nombre_del_niño/niña'] == nombre_nino)]
    # IF A MATCH IS FOUND, ASSIGN THE VALUE OF sexo FROM specified TO not_specified
    if not match.empty:
        sexo_value = match['sexo'].iloc[0]
        not_specified.at[index, 'sexo'] = sexo_value
# NOW PUT THE DATAFRAMES BACK TOGETHER 
master_df = pd.concat([not_specified, specified])

# FILLING IN BIRTHDAY INFO FOR CHILDREN WHO HAD IT SPECIFIED IN AT LEAST ONE OBSERVATION AND DIDN'T HAVE IT SPECIFIED IN AT LEAST ONE OTHER
# BIRTHDAY MUST BE SPECIFIED IN ORDER FOR A HEIGHT-FOR-AGE Z-SCORE TO BE CALCULATED

# CREATING A BOOLEAN MASK THAT IS TRUE WHEN BIRTHDAY IS NOT SPECIFIED FOR THE ROW
mask = master_df['fecha_de_nacimiento'].isna()

# SPLITTING THE MASTER DATAFRAME INTO TWO PARTS, ONE WHERE SEX IS SPECIFIED AND ONE WHERE IT'S NOT
specified = master_df[~mask]
not_specified = master_df[mask]

# ITERATING OVER EACH ROW IN not_specified
for index, row in not_specified.iterrows():
    # GET THE CHILD'S NAME
    nombre_nino = row['nombre_del_niño/niña']
    # SEARCH FOR A ROW IN specified WHERE THE NAME MATCHES nombre_nino
    match = specified.loc[(specified['nombre_del_niño/niña'] == nombre_nino)]
    # IF A MATCH IS FOUND, ASSIGN THE VALUE OF fecha_de_nacimiento FROM specified TO not_specified
    if not match.empty:
        birthday_value = match['fecha_de_nacimiento'].iloc[0]
        not_specified.at[index, 'fecha_de_nacimiento'] = birthday_value
# NOW PUT THE DATAFRAMES BACK TOGETHER 
master_df = pd.concat([not_specified, specified])

# DEDUPLICATING WHILE IGNORING DIFFERENCES IN dict_origin COLUMN (SINCE DUPLICATES COULD COME FROM THE DIFFERENT FILES, GIVING THEM DIFFERENT 
# VALUES FOR dict_origin, WHICH WOULD MAKE US MISS THAT WE HAVE DUPLICATES)

master_df = master_df.drop_duplicates(subset=master_df.columns.difference(['dict_origin']))

# GETTING RID OF ROWS WITH NO CHILD'S NAME

master_df = master_df.drop(index=master_df[master_df['nombre_del_niño/niña'].isin(['Embarazada', 'RN', 'R.N.'])].index)

# CREATING 3 AGE COLUMNS; FOR YEARS, MONTHS, AND WEEKS
master_df['edad_a'] = ((master_df['fecha_de_monitoreo'] - master_df['fecha_de_nacimiento']).astype('timedelta64[D]')) / 365.25
master_df['edad_m'] = ((master_df['fecha_de_monitoreo'] - master_df['fecha_de_nacimiento']).astype('timedelta64[M]'))
master_df['edad_s'] = ((master_df['fecha_de_monitoreo'] - master_df['fecha_de_nacimiento']).astype('timedelta64[D]')) // 7

# GETTING RID OF KIDS WHO EVER HAVE A NEGATIVE AGE (IF THIS IS EVER TRUE WE CAN ASSUME THEIR BIRTHDAY IS INACCURATE)

mask = master_df['edad_a'] < 0
name_obj = master_df.loc[mask, 'nombre_del_niño/niña']
mask = master_df['nombre_del_niño/niña'].isin(name_obj)
master_df = master_df[~mask]

# GETTING RID OF KIDS WHO HAVE MULTIPLE BIRTHDAYS

birthday_counts = master_df.groupby('nombre_del_niño/niña')['fecha_de_nacimiento'].nunique()
master_df = master_df[master_df["nombre_del_niño/niña"].isin(birthday_counts[birthday_counts <= 1].index)]

# GETTING RID OF ROWS WHERE BIRTHDAY IS NA

master_df = master_df.dropna(subset = ["fecha_de_nacimiento"])

# MANUALLY CORRECTING AN ERROR

master_df['nombre_del_niño/niña'] = master_df['nombre_del_niño/niña'].replace("`", "Débora Liset Saloj Sazo")

# REMOVING ROWS WHERE SEX IS NOT SPECIFIED SINCE IT'S NECESSARY INFORMATION FOR CALCULATING Z-SCORES

master_df = master_df.dropna(subset = ["sexo"])

# REMOVING ROWS WHERE AGE IN YEARS (edad_a) IS GREATER THAN 5, SINCE I CAN ONLY CALCULATE Z-SCORE FOR CHILDREN UNDER 5

master_df = master_df[master_df['edad_a'] <= 5]

# GIVE EACH CHILD THEIR OWN ID

master_df['ID'] = pd.factorize(master_df['nombre_del_niño/niña'])[0] + 1

# REMOVING THE DICTIONARY ORIGIN COLUMN SINCE IT'S NOW UNNECESSARY (SINCE IT WAS ONLY USED FOR ERROR CHECKING)

master_df.drop(columns=['dict_origin'], inplace=True)




# PART 2: CALCULATING HEIGHT-FOR-AGE Z-SCORES




# DEFINING  FUNCTIONS

# col_selector: TAKES IN A DATAFRAME AND RETURNS A DATAFRAME WITH ONLY COLUMNS THAT ARE OF INTEREST
# IT IS APPLIED TO THE EXCEL FILES CONTAINING W.H.O. DATA SO THAT WE ONLY GET THE COLUMNS NECESSARY TO MAKE OUR HEIGHT-FOR-AGE Z-SCORE CALCULATIONS

def col_selector(df):

    # DEFINE ARRAY OF COLUMN NAMES THAT ARE OF INTEREST
    col_list = ["Week", "Month", "M", "SD"]

    # DEFINE ARRAY THAT IS THE COLUMN NAMES PRESENT IN THE DATAFRAME THAT ARE ALSO IN col_list
    present_cols = [col for col in col_list if col in df.columns]

    # FILTER THE DATAFRAME DOWN TO ONLY THE COLUMNS SPECIFIED IN present_cols
    return df.loc[:, present_cols]

# z_calculator: TAKES IN A DATAFRAME AND RETURNS A DATAFRAME WITH A NEW COLUMN WITH HEIGHT-FOR-AGE Z-SCORE IN IT
# MEANT TO BE APPLIED TO THE TEMPORARY DATAFRAMES THAT ARE CREATED BY SPLITTING THE MASTER DATAFRAME UP BY SEX AND AGE GROUPS
# AFTER THEY ARE SEPARATELY JOINED WITH THE W.H.O. DATAFRAMES CONTAINING THE RELEVANT MEANS AND STANDARD DEVIATIONS WE USE TO MAKE OUR HEIGHT-FOR-AGE Z-SCORE CALCULATIONS

def z_calculator(df):

    # CALCULATE Z-SCORE
    df["puntaje_z"] = (df["talla"] - df["M"]) / df["SD"]

    # DROP THE NOW UNNECESSARY COLUMNS
    df = df.drop('M', axis=1)
    df = df.drop('SD', axis=1)

    # DROP WHICHEVER UNNECESSARY COLUMN OF THESE TWO IS PRESENT
    if 'Week' in df.columns:
        df = df.drop('Week', axis=1)
    if 'Month' in df.columns:
        df = df.drop('Month', axis=1)

    return df

# SPLITTING THE MASTER DATAFRAME UP INTO SEX AND AGE-GROUP PARTS 

# TEMPORARY MALE TABLE 
mm_data_b = master_df[master_df['sexo'] == "M"]

# TEMPORARY FEMALE TABLE
mm_data_g = master_df[master_df['sexo'] == "F"]

# MALES 13 WEEKS AND YOUNGER
mm_data_b13b = mm_data_b[mm_data_b["edad_s"] <= 13]

# MALES BETWEEN 13 WEEKS AND 2 YEARS OLD
mm_data_b2b = mm_data_b[(mm_data_b["edad_a"] <= 2) & (mm_data_b["edad_s"] > 13)]

# MALES OLDER THAN 2 YEARS
mm_data_25b = mm_data_b[mm_data_b["edad_a"] > 2]

# FEMALES 13 WEEKS AND YOUNGER
mm_data_b13g = mm_data_g[mm_data_g["edad_s"] <= 13]

# FEMALES BETWEEN 13 WEEKS AND 2 YEARS OLD 
mm_data_b2g = mm_data_g[(mm_data_g["edad_a"] <= 2) & (mm_data_g["edad_s"] > 13)]

# FEMALES OLDER THAN 2 YEARS 
mm_data_25g = mm_data_g[mm_data_g["edad_a"] > 2]

# SET THE DIRECTORY WHERE THE EXCEL FILES CONTAINING W.H.O. DATA ARE STORED 
directory = "/Users/ajarbuckle/Desktop/MM_PROJECT/who_zscores"

# CREATE AN EMPTY DIRECTORY TO STORE EACH W.H.O. TABLE FROM THE EXCEL FILES
who_data = {}

# LOOP THROUGH EACH FILE IN THE DIRECTORY WITH A ".xlsx" FILE EXTENSION
for filename in os.listdir(directory):
    if filename.endswith(".xlsx"):
        # READ IN THE EXCEL FILE AS A DATAFARME
        df = pd.read_excel(os.path.join(directory, filename))
        # STRIP COLUMN NAMES OF WHITESPACES
        df.columns = df.columns.str.strip()
        # FILTER THE COLUMNS OF THE DATAFARMES
        df = col_selector(df)
        # GET THE NAME OF THE FILE WITHOUT THE EXTENSION
        name = os.path.splitext(filename)[0]
        # ADD THE DATAFRAME TO THE DICTIONARY WITH ITS NAME AS THE KEY
        who_data[name] = df

# JOINING TEMPORARY AGE-SEX GROUP DATAFRAMES (FROM MASTER DATAFRAME) TOGETHER WITH THEIR CORRESPONDING W.H.O. DATAFRAME

# ON WEEK FOR THIS YOUNGEST GROUP (13 WEEKS AND UNDER)
mm_data_b13b = pd.merge(mm_data_b13b, who_data["b13b_zscores"], left_on='edad_s', right_on='Week', how = 'left')
mm_data_b13g = pd.merge(mm_data_b13g, who_data["b13g_zscores"], left_on='edad_s', right_on='Week', how = 'left')

# ON MONTH FOR THIS MIDDLE AGE GROUP (13 WEEKS TO 2 YEARS OLD)
mm_data_b2b = pd.merge(mm_data_b2b, who_data["b2b_zscores"], left_on='edad_m', right_on='Month', how = 'left')
mm_data_b2g = pd.merge(mm_data_b2g, who_data["b2g_zscores"], left_on='edad_m', right_on='Month', how = 'left')

# ON MONTH FOR THIS OLDEST AGE GROUP (2 YEARS TO 5 YEARS OLD)
mm_data_25b = pd.merge(mm_data_25b, who_data["25b_zscores"], left_on='edad_m', right_on='Month', how = 'left')
mm_data_25g = pd.merge(mm_data_25g, who_data["25g_zscores"], left_on='edad_m', right_on='Month', how = 'left')

# CALCULATING Z-SCORES 

mm_data_b13b    = z_calculator(mm_data_b13b)
mm_data_b13g    = z_calculator(mm_data_b13g)
mm_data_b2b     = z_calculator(mm_data_b2b)
mm_data_b2g     = z_calculator(mm_data_b2g)
mm_data_25b     = z_calculator(mm_data_25b)
mm_data_25g     = z_calculator(mm_data_25g)

# PUTTING ALL OF THESE DATAFRAMES (NOW WITH Z-SCORES CALCULATED) BACK TOGETHER 

mm_data_z = pd.concat([mm_data_25b, mm_data_25g, mm_data_b2b, mm_data_b2g, mm_data_b13b, mm_data_b13g])

# REMOVING OUTLIERS BY HAVING ONLY THE Z-SCORES THAT ARE WITHIN 3 STANDARD DEVIATIONS
# OF THE MEAN Z-SCORE; BECAUSE OTHERWISE THERE ARE SOME PRETTY UNBELIEVABLE NUMBERS
mm_data_z = mm_data_z[(mm_data_z['puntaje_z'] < (mm_data_z['puntaje_z'].mean() + 3 * (mm_data_z['puntaje_z'].std()))) & (mm_data_z['puntaje_z'] > (mm_data_z['puntaje_z'].mean() - 3 * (mm_data_z['puntaje_z'].std())))]

# CORRECTING SPELLING OF A COLUMN NAME 

mm_data_z = mm_data_z.rename(columns={'communidad': 'comunidad'})

# REMOVING ANY ROWS THAT HAVE A DUPLICATE COMBINATION OF ID AND DATE OF RECORDING (BECAUSE A CHILD CANNOT BE MEASURED TWICE IN A DAY WITH DIFFERENT MEASUREMENTS), WHICH MEANS WE CAN'T KNOW
# THE CORRECT DATE FOR THE MEASUREMENT, WHICH MESSES UP THE CHILD'S AGE, AND IN TURN THE HEIGHT-FOR-AGE Z-SCORE, SO THE MEASUREMENTS MUST BE REMOVED 
mm_data_z = mm_data_z.drop_duplicates(subset=['ID', 'fecha_de_monitoreo'])

# EXPORTING

mm_data_z.to_excel('mm_data_clean.xlsx', index=False)
