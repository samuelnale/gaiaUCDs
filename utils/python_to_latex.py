import math
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
from utils.primary_star_name import dummy_star
from utils.functions import get_separation_AU, copy_files_and_zip_folder
from utils.latex_table_code import *


def image_to_latex(imgpath, stars_shortnames, df):  #creates HR diagrams and saves them
    fig, ax = plt.subplots(figsize=(9, 11))
    # generates HR diagram dots, filtering useless magnitudes and parallaxes
    HRdf = df[(df['GAIAG'] < 22) & (df['GAIAG'] > 10) & (df['PARALLAX'] > 2.) & (df['GAIATOG'] > 1)]

    HRGaiaG = HRdf['GAIAG'].values.tolist()
    HRGaiaRP = HRdf['GAIARP'].values.tolist()
    HRparallax = HRdf['PARALLAX'].values.tolist()
    HRabs_mag = np.empty(len(HRGaiaG))
    for i in range(len(HRGaiaG)):
        HRabs_mag[i] = HRGaiaG[i] + 5 - 5*math.log10(1000/HRparallax[i])

    x = list(np.array(HRGaiaG) - np.array(HRGaiaRP))
    y = list(HRabs_mag)
    for index, item in enumerate(x):
        if (float(item) < -30) or (float(item) > 30):
            x.pop(index)
            y.pop(index)
    for index2, item2 in enumerate(y):
        if (float(item2) < -30) or (float(item2) > 30):
            x.pop(index2)
            y.pop(index2)

    # generates target stars
    GaiaG, GaiaRP, parallax, absolute_mag, missing_token = [], [], [], [], 0
    xtargets, ytargets = [], []
    for i in range(len(stars_shortnames)):  # takes data only for stars with parallax != NaN and > 0
        stardf = df[df['SHORTNAME'].astype(str) == stars_shortnames[i]][['GAIAG', 'GAIARP', 'PARALLAX']]
        if (stardf.iloc[0]['PARALLAX'] > 0) and (stardf.isnull().values.any() == False):    # chissà se può risultare x vuoto?
            xtargets.append(stardf.iloc[0]['GAIAG'] - stardf.iloc[0]['GAIARP'])
            ytargets.append(stardf.iloc[0]['GAIAG'] + 5 - 5 * math.log10(1000 / stardf.iloc[0]['PARALLAX']))
        elif stardf.iloc[0]['PARALLAX'] <= 0:
            fig.text(0.01, missing_token * 0.015, 'Negative or null parallax ' + stars_shortnames[i],
                     verticalalignment='bottom', horizontalalignment='left',
                     transform=ax.transAxes, fontsize=10, fontfamily="monospace")
            missing_token += 1
        else:
            fig.text(0.01, missing_token * 0.015, 'Missing ' + stars_shortnames[i],
                     verticalalignment='bottom', horizontalalignment='left',
                     transform=ax.transAxes, fontsize=10, fontfamily="monospace")
            missing_token += 1

    ax.scatter(x, y, c="#A9A9A9", s=1.5)
    ax.scatter(xtargets, ytargets, c="r")
    ax.grid(True)
    ax.set_ylim(max(y), min(y))
    ax.set_xlim(-1, 4)
    # for i in range(1, len(xtargets)):
    #     ax.arrow(xtargets[0], ytargets[0], xtargets[i], ytargets[i], width=0.01)
    ax.set_xlabel('G-G$_{RP}$')
    ax.set_ylabel('M$_{G}$')
    ax.set_title(str(len(stars_shortnames)) + " targets on G-G$_{RP}$ CMD diagram")

    plt.savefig(imgpath, bbox_inches='tight', format="jpg")
    plt.close()

    return


def generate_tex_targetfile(system_tex_path, sorted_stars_shortnames, df, columns_by_file, system_df, head_target_text, tail_target_text, comments_path, targetfiles_path):
    # writes the single targetfiles files
    stars_data_dict = {}
    href_lines = []
    RA_DEC = []

    primary_parallax = df[(df['SHORTNAME'].astype(str) == sorted_stars_shortnames[0])].iloc[0]['PARALLAX']
    for i in range(len(sorted_stars_shortnames)):
        check = df[(df['SHORTNAME'].astype(str) == sorted_stars_shortnames[i])]
        if not check.empty:
            stars_data_dict[i] = dict(zip(df.columns, check.astype(str).values.tolist()[0]))  # RIMUOVERE ASTYPE() ?
            if (check[['RA2000', 'DEC2000']].isnull().values.any() == False):
                RA_DEC.append([check.iloc[0]['RA2000'], check.iloc[0]['DEC2000']])
            else:
                RA_DEC.append([float("NaN"), float("NaN")])
            if check['DISCOVERYNAME'].notnull().values.any():
                href_lines.append(check['DISCOVERYNAME'].astype(str).values.tolist()[0])
        else:
            stars_data_dict[i] = dict(zip(df.columns, dummy_star(sorted_stars_shortnames[i]).values.tolist()[0]))
            RA_DEC.append([float("NaN"), float("NaN")])

    separation_degrees, separation_AU = get_separation_AU(primary_parallax, RA_DEC)

    texpath = system_tex_path + "/" + sorted_stars_shortnames[0] + ".tex"
    imgpath = system_tex_path + "/" + sorted_stars_shortnames[0] + ".jpg"

    writelines_targetfiles(columns_by_file, system_df, head_target_text, tail_target_text, texpath, sorted_stars_shortnames, stars_data_dict, href_lines, separation_AU)
    image_to_latex(imgpath, sorted_stars_shortnames, df)
    aladin_line = add_aladin_coordinates(stars_data_dict, separation_degrees, targetfiles_path)
    create_comments_files(comments_path, sorted_stars_shortnames[0])


    single_main_line = r"\input{targetfiles/" + sorted_stars_shortnames[0] + "/" + sorted_stars_shortnames[0] + ".tex}\n" + r"\clearpage" + "\n"

    return single_main_line, aladin_line


def add_aladin_coordinates(stars_data_dict, separation_degrees, targetfiles_path):  # writes single system star coordinates to Aladin's script
    RAs, DECs, shortnames = [], [], []
    max_sep = np.array(separation_degrees)*2/60   #max_sep sono secondi d'arco (sa)
    max_sep[0] = 6
    for i in range(len(stars_data_dict)):
        RAs.append(stars_data_dict[i]['RA2000'])
        DECs.append(stars_data_dict[i]['DEC2000'])
        shortnames.append(stars_data_dict[i]['SHORTNAME'])

    max_sep = np.max(np.nan_to_num(max_sep))
    max_sep = str(int(max_sep.round(0)))
    script_line = "get Simbad " + RAs[0] + " " + DECs[0] + ";"
    for i in range(1, len(shortnames)):
        script_line = script_line + "draw tag(" + RAs[i] + ", " + DECs[i] + ", " + shortnames[i] + "); "
    script_line = script_line + "zoom " + max_sep + "arcmin; sync; save " + targetfiles_path + shortnames[0] + "/" + shortnames[0] + "_2MASS.jpg;\n"

    return script_line


def write_main_latex_file(main_tex_path, single_system_lines):  # writes the main.tex file with all the calls to single systems files
    f = open(main_tex_path, 'w')
    f.writelines(header_main_file())
    f.writelines(single_system_lines)
    f.writelines(footer_main_file())
    f.close()

    return


def read_sample_target_tex():
    head_target_text = []
    with open('sample_files/targetfile_sample_head.tex', "r") as file:  # r=scrittura (sovrascrive), r+ = read/write
        lines = file.readlines()
        for line in lines:
            head_target_text.append(line)
    tail_target_text = []
    with open('sample_files/targetfile_sample_tail.tex', "r") as file:  # r=scrittura (sovrascrive), r+ = read/write
        lines = file.readlines()
        for line in lines:
            tail_target_text.append(line)
    return head_target_text, tail_target_text


def header_main_file():
    x = []
    x.append(r"\documentclass[12pt]{article}")
    x.append(r"\usepackage{graphicx, hyperref, booktabs, longtable, float}")
    x.append(r"\usepackage{gensymb}")
    x.append(r"\setlength{\textwidth}{200mm}")
    x.append(r"\setlength{\textheight}{240mm}")
    x.append(r"\setlength{\topmargin}{-15mm}")
    x.append(r"\setlength{\oddsidemargin}{-20mm}")
    x.append(r"\setlength{\evensidemargin}{-20mm}")
    x.append(r"\setlength{\unitlength}{1mm}")
    x.append(r"\usepackage{amsmath}")

    x.append(r"\begin{document}")
    x.append(r"\begin{center}")
    x.append(r"{\bf GUCDs Benchmark Systems} \\" + "\n")
    x.append(r"\end{center}" + "\n")

    x.append(r"\noindent")
    x.append(r"\begin{center}")
    x.append(r"Compiler: Samuel Nale Di Schiena\\")
    x.append(r"Collaborators: R. L. Smart, B. Bucciarelli" + "\n")
    x.append(r"\vspace{1cm}")
    x.append(r"\noindent")
    x.append(r"{\bf Questions / comments to \\")
    x.append(r"samuel.naledischiena@edu.unito.it \\")
    x.append(r"richard.smart@inaf.it}")
    x.append(r"\end{center}")
    x.append("\n")
    x.append(r"\input{summary}" + "\n")
    x.append(r"\input{collaborators}" + "\n")

    testo = '\n'.join(x)
    return testo


def footer_main_file():
    x = []
    x.append(r"\newpage")
    x.append(r"\bibliographystyle{plain}")
    x.append(r"\bibliography{refs.bib}" + "\n\n")
    x.append(r"\end{document}")

    testo = '\n'.join(x)
    return testo


def create_single_tex_path(targetfiles_path, primary_star):
    system_tex_path = targetfiles_path + primary_star

    access_rights = 0o755  # define the access rights

    if not os.path.isdir(system_tex_path):
        os.makedirs(system_tex_path, access_rights)

    return system_tex_path


def create_comments_files(comments_path, starname): # creates empty comments file
    system_comment_path = comments_path + "/" + starname + ".tex"
    if os.path.isfile(system_comment_path):
        pass
    else:
        try:
            with open(system_comment_path, 'w') as f:
                f.write('\nNo comment yet\n')
        except OSError:
            pass
        else:
            pass

    return


def complete_pdf(base_path_array, all_main_lines):  #creates directory for the full RA pdf
    if os.path.isdir("latex_files/Full_RA"):
        try:
            shutil.rmtree("latex_files/Full_RA")
            print("Directory 'latex_files/Full_RA' deleted")
        except OSError:
            print("Creation of the directory 'latex_files/Full_RA' failed")
            raise OSError
    try:
        os.makedirs("latex_files/Full_RA")  # meglio fare if directory does not exist
    except OSError:
        print("Creation of the directory 'latex_files/Full_RA' failed")
        raise OSError

    print("Generating the complete PDF file:")
    for item in base_path_array:
        shutil.copytree(item, "latex_files/Full_RA", dirs_exist_ok=True)

    write_main_latex_file("latex_files/Full_RA/main.tex", all_main_lines)
    copy_files_and_zip_folder("latex_files/Full_RA/")
    os.chdir("latex_files/Full_RA")
    os.system("pdflatex -interaction=nonstopmode main.tex")
    os.rename('main.pdf', 'GaiaUCDs_benchmark_systems.pdf')
    shutil.copy2("GaiaUCDs_benchmark_systems.pdf", "../GaiaUCDs_benchmark_systems.pdf")

    return
