import pandas as pd
import numpy as np


def sort_by_magnitude(listed_dfstars, df):      # sorts every star in a system by magnitude to decide which is the primary
    stars_by_magnitude, system_dfs_list = [], []
    for i in range(len(listed_dfstars)):
        filtered_df = pd.DataFrame()
        magnitudes = []
        for j in range(len(listed_dfstars[i])):
            if df[(df['SOURCE_ID'].astype(str) == str(listed_dfstars[i][j]))].empty:
                dummy_mag = dummy_star(listed_dfstars[i][j], df.columns)
                magnitudes.append(dummy_mag)
                df = pd.concat([df, dummy_mag])
                df.reset_index(inplace=True, drop=True)
            else:
                magnitudes.append(df[(df['SOURCE_ID'].astype(str) == listed_dfstars[i][j])])

        G, stars_shortname = [], []
        for i in range(len(magnitudes)):
            G.append(magnitudes[i].iloc[0]['GAIAG'].astype(float))
            G_SOURCE_ID = str(magnitudes[i].iloc[0]['SOURCE_ID'])
            if df[(df['SOURCE_ID'].astype(str) == G_SOURCE_ID)].empty == False:
                stars_shortname.append(df[(df['SOURCE_ID'].astype(str) == G_SOURCE_ID)].iloc[0]['SHORTNAME'])
                filtered_df = pd.concat([filtered_df, df[(df['SOURCE_ID'].astype(str) == G_SOURCE_ID)]])    #ignore_index=True, sort=False)
            else:
                stars_shortname.append(G_SOURCE_ID)
                tempdf = pd.DataFrame({'SOURCE_ID':[G_SOURCE_ID]})
                filtered_df = pd.concat([filtered_df, tempdf])
                print("Controlla che abbia aggiunto row = NaN:", stars_shortname)

        filtered_df = filtered_df.sort_values('GAIAG')
        system_dfs_list.append(filtered_df)

        G = [1000 if np.isnan(x) else x for x in G]
        stars_dict = dict(zip(stars_shortname, G))
        sortdict = dict(sorted(stars_dict.items(), key=lambda x: x[1]))

        stars_by_magnitude.append(list(sortdict.keys()))
    return stars_by_magnitude, df, system_dfs_list


def dummy_star(star, colonne):      # creates a fake entry in the dataframe if a star exists as companion but not by herself, thus lacking data
    fakelist = []
    for i in range(len(colonne)):
        fakelist.append([float("NaN")])
    d = dict(zip(colonne, fakelist))
    fakemag = pd.DataFrame(data=d)
    fakemag['SOURCE_ID'] = star
    fakemag['SHORTNAME'] = star
    fakemag['SOURCE_ID_COMP1'] = 0
    fakemag['SOURCE_ID_COMP2'] = 0
    fakemag['GAIATOG'] = 0

    return fakemag


def divide_systems_by_RA(divisions, stars_by_magnitude, df):    #divide systems by RA, based on RA of the primary
    divided_systems_list = []
    for i in range(divisions):
        divided_systems_list.append([])
    for system in stars_by_magnitude: #102:105 da problemi
        RA = df[df['SHORTNAME'].astype(str) == system[0]]['RA2000'].values[0]
        for i in range(divisions):
            if (RA >= i * 360 / divisions) and (RA < (i + 1) * 360 / divisions):
                divided_systems_list[i].append(system)

    return divided_systems_list