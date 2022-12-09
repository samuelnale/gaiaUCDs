import pandas as pd
from astropy.table import Table


def initialize_dataframe(data_columns, data_files):
    df, file_names = create_df(data_files)
    columns_by_file = get_columns_and_type(data_columns, file_names)
    merged_cols = columns_by_file[0][0]
    for i in range(1, len(columns_by_file)):
        merged_cols = merged_cols + columns_by_file[i][0]
    df = df[merged_cols]

    df = prepare_columns(df)
    df = approx_columns(df, columns_by_file)

    dfstars = create_dfstars(df)
    return df, dfstars, columns_by_file


def create_df(data_files):  # creates a single DataFrame from all the listed files
    with open(data_files, 'r') as data_file:
        lines = data_file.read().splitlines()
    files = []
    for line in lines:
        if len(line) > 1 and line[0] != "#":
            files.append("Data/" + line)
    print("Data files to be imported:")
    for i in files:
        print("FILE:", i)
    print()

    if files[0].split(".")[-1] == "fits":
        df = Table.read(files[0], format="fits").to_pandas()
        print(files[0], "imported as FITS")
    elif files[0].split(".")[-1] == "csv":
        df = Table.read(files[0], format="csv").to_pandas()
        print(files[0],"imported as CSV")
    else:
        print("IMPOSSIBLE TO IMPORT THE MAIN FILE")

    df.columns = df.columns.str.upper()
    print("Importing data files...")
    if len(files) > 1:
        for i in range(1, len(files)):
            if files[i].split(".")[-1] == "fits":
                tbl = Table.read(files[i], format="fits")
                print(files[i] + " imported as FITS")
            elif files[i].split(".")[-1] == "csv":
                tbl = Table.read(files[i], format="csv")
                print(files[i] + " imported as CSV")
            names = [name for name in tbl.colnames if len(tbl[name].shape) <= 1]
            secondary_df = tbl[names].to_pandas()
            secondary_df.columns = secondary_df.columns.str.upper()

            df = pd.merge(df, secondary_df, how='left', on="SOURCE_ID", suffixes=('', '_drop'))
            df.drop([col for col in df.columns if 'drop' in col], axis=1, inplace=True)
    print("\nDATAFRAMES MERGED SUCCESSFULLY")

    return df, files


def get_columns_and_type(data_columns, file_names):
    columns_by_file = []
    for file in file_names:
        file = file.lstrip("Data/").replace(".fits", ".txt").replace(".csv", ".txt")
        with open("Data/" + file, 'r') as text_file:
            lines = text_file.read().splitlines()
        colonne, approx, column_type, error_col = [], [], [], []

        for line in lines:
            if len(line) > 0:
                if line[0] != "#":  # removes comment lines (indicated by #)
                    line = line.replace(" ", "")
                    line = line.replace("\t", "")
                    line = line.split(",")

                    if len(line) > 1:
                        colonne.append(line[0].upper())
                        approx.append(int(line[1]))
                        column_type.append(line[2].upper())
                        if len(line) > 3:
                            error_col.append(line[3].upper())
                        else:
                            error_col.append("")
                    else:
                        colonne.append(line[0].upper())
                        approx.append(0)
                        column_type.append("S")

                        error_col.append("")                # here?
        columns_by_file.append([colonne, approx, column_type, error_col])

    for i in range(len(columns_by_file)):
        file_names[i] = file_names[i].lstrip("Data/").replace(".fits", ".txt").replace(".csv", ".txt")
        columns_by_file[i].append(file_names[i])

    return columns_by_file


def prepare_columns(df):        #prepares the data to handle LaTeX characters
    for colonna in df.columns:
        if df[colonna].dtype == object:
            df[colonna] = df[colonna].str.decode("utf-8")
            df[colonna] = df[colonna].str.strip()
    df = df.replace('&', r'\&', regex=True)
    df = df.replace('_', r'\_', regex=True)
    df = df.replace(-99999, float('NaN'))

    return df


def approx_columns(df, columns_by_file):    # approximate dataset values as set in the Master.txt files
    for i in range(len(columns_by_file)):
        for j in range(len(columns_by_file[i][0])):
            try:
                if (columns_by_file[i][2][j] != "S") and (columns_by_file[i][2][j] != "s"):
                    if (columns_by_file[i][2][j] == "F") or (columns_by_file[i][2][j] == "f"):
                        df[columns_by_file[i][0][j]] = df[columns_by_file[i][0][j]].astype(float).round(columns_by_file[i][1][j])
            except:
                print("Problem with .txt data file: check if data type is correct")
    return df


def create_dfstars(df):     # creates a dataframe which will be used to merge linked stars in individual systems
    dfstars = df[df['SOURCE_ID'] != 0]
    dfstars = df[(df['SOURCE_ID_COMP1'] != 0) | (df['SOURCE_ID_COMP2'] != 0)]
    dfstars = dfstars[['SOURCE_ID', 'SOURCE_ID_COMP1', 'SOURCE_ID_COMP2']]
    dfstars = dfstars.applymap(lambda x: str(x))
    dfstars.reset_index(inplace=True, drop=True)

    return dfstars
