from __future__ import print_function, division
import pandas as pd
import numpy as np
import os
import shutil
from numpy import arccos, cos, sin
# from utils.python_to_latex import write_main_latex_file


def set_divisions():    #gets in input the number of desired divisions in RA
    print("###############################################")
    print("#                                             #")
    print("#        Gaia UCDs benchmark systems          #")
    print("#        samuelnale@gmail.com,  2022          #")
    print("#                                             #")
    print("###############################################")
    print()
    print("Check the README.txt")
    print()
    print(r"Hey! Remember to manually delete old RA folders inside /latex_files. Be careful to not delete the comments instead!")
    print("Also remember to manually add the comment files inside the proper folder before zipping it.\n")
    mark = True
    while mark:
        divisions = input("Dividing systems by primary RA.\nHow many partitions do you want? ")
        try:
            int(divisions)
            mark = False
        except ValueError:
            print("Come on, this is not a number!\n")

    return int(divisions)


def set_aladin_yes_or_no():     # gets in input if you want to run or not the Aladin's script
    test = True
    aladin_yes_or_no = True
    print()
    while test:
        yes_no = input("Do you want to execute automatically the Aladin's images scripts?\nIf YES all the latex_files/targetfiles folders will be reset [Y/N] ")
        if yes_no == "Y" or yes_no == "y":
            print("Aladin's scripts will be run!\n")
            test = False
        elif yes_no == "N" or yes_no == "n":
            print("Aladin's scripts WON'T be run!\n")
            aladin_yes_or_no = False
            test = False
        else:
            print("Please, type only Y or N\n")

    return aladin_yes_or_no


def link_related_dfstars(dfstars):      #links every star checking if they are companions to others to any degree of separation,
                                        #rejecting systems with more than N stars (by default N=10)
    listed_df = dfstars.values.tolist()
    for i in range(len(listed_df)):
        listed_df[i] = [j for j in listed_df[i] if j != "0"]

    final_listed_stars = []
    stars = listed_df[:].copy()  # 1173:1180
    iterator = 0

    for i in range(len(stars)):
        tok = False
        if stars[i] == ["0"]:
            continue
        else:
            final_listed_stars.append(stars[i])
            stars[i] = ["0"]
            while tok is False:
                tok = True
                for j in range(len(stars)):
                    if (stars[j] != ["0"]) and (
                            len(list(set(final_listed_stars[iterator] + stars[j]))) < len(final_listed_stars[iterator] + stars[j])):
                        final_listed_stars[iterator] = list(set(final_listed_stars[iterator] + stars[j]))
                        stars[j] = ["0"]
                        tok = False
            iterator = iterator + 1
    rejected_systems(final_listed_stars)
    final_listed_stars = [x for x in final_listed_stars if len(x) < 11]
    print("Total number of merged systems:", len(final_listed_stars))

    return final_listed_stars


def rejected_systems(final_listed_stars):       # writes on a file the "strange" systems with more than N stars
    unwanted = [x for x in final_listed_stars if len(x) > 10]   # N=10 by default, change it to match the previous function
    with open("rejected_systems.txt", "w") as file:
        for line in unwanted:
            file.write(f"{line}\n\n")
    print("Number of rejected systems:", len(unwanted), "(written in 'rejected_systems.txt')")

    return


def create_directories(division, divisions, aladin_yes_or_no):  # creates output directories latex_files/etc
    base_path = "latex_files/RA_" + str(int(division*360/divisions)) + "-" + str(int(division*360/divisions+360/divisions)) + "/"
    targetfiles_path = base_path + "targetfiles/"
    main_tex_path = base_path + "main.tex"
    index_path = base_path + "index_file.tex"
    comments_path = base_path + "comments/"

    for path in [base_path, comments_path]:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError:
                print("Creation of the directory %s failed" % path)
                raise OSError

    if (os.path.isdir(targetfiles_path)) and (aladin_yes_or_no == True):  # if /targetfiles exists, deletes it and creates an empty one
        try:
            shutil.rmtree(targetfiles_path)
            print("Directory %s deleted" % targetfiles_path)

            try:
                os.makedirs(targetfiles_path)  # meglio fare if directory does not exist
            except IOError as err:
                print(err)
                print(err.args)
                print(err.filename)
                print("Creation of the directory %s failed" % targetfiles_path)
                # raise OSError
        except OSError:
            print("Creation of the directory %s failed" % targetfiles_path)
            raise OSError
    elif (os.path.isdir(targetfiles_path) == False):
        try:
            os.makedirs(targetfiles_path)  # meglio fare if directory does not exist
        except IOError as err:
            print(err, ",", err.args, ",", err.targetfiles_path)
            print("Creation of the directory %s failed" % targetfiles_path)

    return base_path, main_tex_path, targetfiles_path, comments_path, index_path


def create_script_dir():    #creates the directory for the aladin's scripts: aladin_scripts/
    if os.path.isdir("aladin_scripts"):  # if /targetfiles exists, deletes it and creates an empty one
        try:
            shutil.rmtree("aladin_scripts")
            print("Directory aladin_scripts deleted")
        except OSError:
            print("Creation of the directory aladin_scripts failed")
            raise OSError

    try:
        os.makedirs("aladin_scripts")
    except OSError:
        print("Creation of the directory 'aladin_scripts' failed")
        raise OSError
    return


def get_separation_AU(primary_parallax, RA_DEC):    # calculates the separation in AU between the primary star and the secondaries
    primary_parallax = primary_parallax/1000    #arcsec
    separation_AU = [0]
    separation_degrees = [0]
    for i in range(1, len(RA_DEC)):
        theta = arccos(sin(RA_DEC[0][1]) * sin(RA_DEC[i][1]) + cos(RA_DEC[0][1]) * cos(RA_DEC[i][1]) * cos(RA_DEC[0][0] - RA_DEC[i][0]))
        theta = theta * 3600    #arcsec
        sepAU = theta / primary_parallax
        separation_degrees.append(theta)
        separation_AU.append(np.around(sepAU, 1))

    return separation_degrees, separation_AU


def create_aladin_script(division, divisions, targetfiles_path, division_len):  #creates the .sh file containing Aladin's script
    script_name = []
    cap = int(np.ceil(division_len/95))
    for i in range(cap):
        script_name.append("aladin_scripts/aladin_RA_" + str(int(division*360/divisions)) + "-" + str(int(division * 360 / divisions + 360 / divisions)) + "_" + str(i) + ".sh")
        with open(script_name[i], "w") as aladin_file:
            aladin_file.write(
                r'echo "reset; get hips(CDS/P/2MASS/color); sync; get hips(CDS/I/350/gaiaedr3); sync; get hips(CDS/II/246/out); sync; zoom 6arcmin; sync;  reverse;  sync; save ' + targetfiles_path + 'test.jpg' + '\n')
    return script_name


def write_aladin_script(script_name, all_aladin_lines, aladin_yes_or_no):   #writes the Aladin's scripts in .sh files
    x = 95
    final_list = lambda all_aladin_lines, x: [all_aladin_lines[i:i + x] for i in range(0, len(all_aladin_lines), x)]
    splitted_lines = final_list(all_aladin_lines, x)

    for i in range(len(splitted_lines)):
        print("\nWriting Aladin script n.", i, " - ", script_name[i])
        with open(script_name[i], "a") as aladin_file:
            for line in splitted_lines[i]:
                aladin_file.write(line)
            aladin_file.write(r'quit" | java -jar AladinBeta.jar -nogui')
        os.system("chmod +x " + script_name[i])

        if aladin_yes_or_no:
            print("\nExecuting script '" + script_name[i] + "' - this will take some time...")
            os.system("./" + script_name[i])

    return


def copy_files_and_zip_folder(base_path):   # copies the necessary LaTeX files for compiling
    shutil.copy2("setup/refs.bib", base_path)
    shutil.copy2("setup/summary.tex", base_path)
    shutil.copy2("setup/summary.tex", base_path)
    shutil.copy2("setup/legend.tex", base_path)
    #command = "zip -r -j latex_files/Benchmark_" + str(division) + ".zip latex_files/"+str(division)
    #os.system(command)
    return


def replace_comments(comments_path):
    print("Copying comments files...")
    with open('manual_comments/comments_list.txt', 'r') as file:
        lines = file.read().splitlines()

    for i in range(len(lines)):
        if os.path.exists(comments_path + lines[i]):
            shutil.copy2('manual_comments/' + lines[i], comments_path + lines[i])

    return


def delete_targetfiles():
    directory = "latex_files/"
    if os.path.isdir(directory):
        test = True
        aladin_yes_or_no = True
        while test:
            yes_no = input("CAREFUL! Do you want to delete all the /targetfiles directories? [Y/N] ")
            if yes_no == "Y" or yes_no == "y":
                print("/targetfiles folders will be deleted\n")
                for i in [f.path for f in os.scandir(directory) if f.is_dir()]:
                    print(i + "/targetfiles")
                    print(os.path.isdir(i + "/targetfiles"))
                    print()

                    try:
                        shutil.rmtree(i + "/targetfiles")
                    except FileNotFoundError:
                        print("Impossible to delete", i + "/targetfiles")
                test = False
            elif yes_no == "N" or yes_no == "n":
                print("/targetfiles folders WON'T be deleted\n")
                test = False
            else:
                print("Please, type only Y or N\n")

    return
