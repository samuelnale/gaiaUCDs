import pandas as pd
#NOTE: the first table has to be modified MANUALLY
#SD[i] is a list with the i stars in the system. You can access of the n-th star single data with SD[n]['COLUMN_NAME'].
#COLUMN_NAME is the exact name of the column given in the Master.txt file.
#the for loop is there to write data from all the i stars in the list


def writelines_targetfiles(columns_by_file, system_df, head_target_text, tail_target_text, texpath, sorted_stars_shortnames, SD, href_lines, separation_AU):
    pd.options.mode.chained_assignment = None  # default='warn'
    head_target_text[2] = r'\section{' + " \& ".join(sorted_stars_shortnames) + r'}' + '\n' +  '\label{sec:' + SD[0]['SHORTNAME'] + r'}'
    # FIRST TABLE CODE
    with open(texpath, 'w', encoding='utf-8') as file:
        file.writelines(head_target_text)
        file.writelines(r"\caption{" + columns_by_file[0][4].replace("_", "\_").rstrip(".txt") + "}\n")
        file.writelines(r"\endfirsthead" + "\n" + r"\endhead" + "\n")
        ############### Row N.1 ###############
        file.writelines(r'\toprule'+'\n')
        file.writelines(r'Shortname & \multicolumn{2}{l}{Discovery name} & $DiscoveryRefName$ & \multicolumn{2}{l}{Source ID} \\' + '\n')
        file.writelines(r'\midrule' + '\n')
        for i in range(len(SD)):
            data_line = SD[i]['SHORTNAME'], ' & \multicolumn{2}{l}{' + str(SD[i]['DISCOVERYNAME']) + '} & ', SD[i]['DISCOVERYREFNAME'], ' &  \multicolumn{2}{l}{' + str(SD[i]['SOURCE_ID']) + '}', r' \\' + '\n'
            file.writelines(data_line)

        ############### Row N.2 ###############
        file.writelines(r'\toprule'+'\n')
        file.writelines(r'$Separation [AU]$ & $RA2000$ & $DEC2000$ & $TMASS_J$ & $SPT_{OPT}$ & $SPT_{NIR}$ \\' + '\n')
        file.writelines(r'\midrule' + '\n')
        for i in range(len(SD)):
            data_line = str(separation_AU[i]), ' & ', SD[i]['RA2000'], ' & ', SD[i]['DEC2000'], ' & ', SD[i]['TMASSJ'], ' $\pm$ ', SD[i]['TMASSJERR'], ' & ', SD[i]['SPTOPTNAME'], ' & ', SD[i]['SPTNIRNAME'], r" \\" + '\n'
            file.writelines(data_line)

        ############### Row N.3 ###############
        file.writelines(r'\toprule' + '\n')
        file.writelines(r'$Parallax$ & $PMRA$ & $PMDEC$ & $SPT_{GEN}$ & \multicolumn{2}{l}{Parallax ref name} \\' + '\n')
        file.writelines(r'\midrule' + '\n')
        for i in range(len(SD)):
            data_line = SD[i]['PARALLAX'], ' $\pm$ ', SD[i]['PARALLAXERR'], ' & ', SD[i]['PMRA'], ' $\pm$ ', SD[i]['PMRAERR'], ' & ', SD[i]['PMDEC'], ' $\pm$ ', SD[i]['PMDECERR'],' & ', SD[i]['VTAN'], ' $\pm$ ', SD[i]['EVTAN'], ' & \multicolumn{2}{l}{', SD[i]['PARALLAXREFNAME'], '}', r' \\' + '\n'
            file.writelines(data_line)

        ############### Row N.4 ###############
        file.writelines(r'\toprule' + '\n')
        file.writelines(r'$Gaia_G$ & $Gaia_{BP}$ & $Gaia_{RP}$ & $J_{GEN}$ & $V_{tan}$ &  \\' + '\n')
        file.writelines(r'\midrule' + '\n')
        for i in range(len(SD)):
            data_line = SD[i]['GAIAG'], ' $\pm$ ', SD[i]['GAIAGERR'],' & ', SD[i]['GAIABP'], ' $\pm$ ', SD[i]['GAIABPERR'],' & ',SD[i]['GAIARP'], ' $\pm$ ', SD[i]['GAIARPERR'], ' & ', SD[i]['JGEN'],' & ',SD[i]['VTAN'], ' $\pm$ ', SD[i]['EVTAN'], r' \\'+ '\n'
            file.writelines(data_line)

        ############################## edits tail of the targetfile #########################################
        backup = tail_target_text[4]
        temp = []
        for i in range(len(href_lines)):
            temp.append(tail_target_text[4].replace("DISCOVERYNAME", href_lines[i].replace("+", "%2B").replace("-", "%2D").replace(" ","+")).replace("STARNAME", href_lines[i]))
        tail_target_text[4] = r"\\".join(temp)
        tail_target_text[6] = r'\includegraphics[width=3.0in]{targetfiles/' + sorted_stars_shortnames[0] + "/" + sorted_stars_shortnames[0] + '.jpg}\n'
        tail_target_text[7] = r'\includegraphics[width=3.5in]{targetfiles/' + sorted_stars_shortnames[0] + "/" + sorted_stars_shortnames[0] + '_2MASS.jpg}\n'
        tail_target_text[12] = r'From comments/' + sorted_stars_shortnames[0].replace("_", "\_") + r'.tex:\\' + '\n'
        tail_target_text[13] = r'\input{comments/' + sorted_stars_shortnames[0] + '.tex}\n'
        file.writelines(tail_target_text)
        tail_target_text[4] = backup

        ############################## writing secondary datafiles ##############################

        for i in range(1, len(columns_by_file)):
            temp_df_columns = columns_by_file[i][0]
            temp_df = system_df[temp_df_columns]
            #print(columns_by_file[i][4])
            #if "Master_X_" not in columns_by_file[i][4]:
            temp_filename = columns_by_file[i][4].replace("Master_X_","").replace("_", "\_")
            #print(temp_filename)
            if not temp_df.isnull().values.all():
                file.writelines(r"\setlength\LTleft{0pt}" + "\n" + r"\setlength\LTright{0pt}" + "\n")
                file.writelines(r"\begin{longtable}{@{\extracolsep{\fill}}llllll}" + "\n")
                file.writelines(r"\caption{" + temp_filename.rstrip(".txt") + "}\n")
                file.writelines(r"\endfirsthead" + "\n" + r"\endhead" + "\n")

                droplist = []
                for t in range(len(temp_df_columns)):
                    if len(columns_by_file[i][3][t]) > 0:
                        temp_df[temp_df_columns[t]] = temp_df[temp_df_columns[t]].astype(str) + " +conj+ " + temp_df[columns_by_file[i][3][t]].astype(str)
                        droplist.append(columns_by_file[i][3][t])
                temp_df = temp_df.drop(columns=droplist)

                x = 6
                temp_df_columns = temp_df.columns.values.tolist()
                templist = lambda temp_df_columns, x: [temp_df_columns[i:i + x] for i in range(0, len(temp_df_columns), x)]
                split_temp_df_cols = templist(temp_df_columns, x)

                for chunk in split_temp_df_cols:
                    header_split = "$ & $".join([x[0:14] for x in chunk]).lower().replace("_", ".")
                    file.writelines(r"\toprule" + "\n $" + header_split + r"$ \\" + "\n" + "\midrule" + "\n")
                    for t in range(len(temp_df)):
                        system_list = temp_df[chunk].iloc[t].astype(str).values.tolist()
                        system_string = " & ".join(system_list).replace("+conj+", r"$\pm$")
                        file.writelines(system_string + r"\\" + "\n")
                file.writelines(r"\end{longtable}" + "\n\n")


    return
