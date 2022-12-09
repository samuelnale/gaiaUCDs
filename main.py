import os

from utils.functions import *
from utils.primary_star_name import *
from utils.python_to_latex import *
from utils import global_variables
from config import data_files, data_columns


def main(df, dfstars, divisions, columns_by_file, aladin_yes_or_no):
    create_script_dir()
    print("\nNumber of filtered columns:", len(df.columns))
    listed_dfstars = link_related_dfstars(dfstars)
    #listed_dfstars = listed_dfstars[0:5]      # HEY! Keep this commented if you want the full dataset
    print("\nSplitting dataset by RA...")
    stars_by_magnitude, df, system_dfs_list = sort_by_magnitude(listed_dfstars, df)
    divided_systems_list = divide_systems_by_RA(divisions, stars_by_magnitude, df)

    head_target_text, tail_target_text = read_sample_target_tex()

    i, starting_point = 0, 0
    all_main_lines, base_path_array = [], []
    for division in range(divisions):
        print("--- RA subset number", division, "---")
        main_lines, all_aladin_lines = [], []
        base_path, main_tex_path, targetfiles_path, comments_path = create_directories(division, divisions, aladin_yes_or_no)
        base_path_array.append(base_path)
        #commentslist = open(base_path + "comments_list.txt", "w")
        script_name = create_aladin_script(division, divisions, targetfiles_path, len(divided_systems_list[division]))

        for system in divided_systems_list[division]:
            print(i)
            system_tex_path = create_single_tex_path(targetfiles_path, system[0])
            single_main_line, aladin_line = generate_tex_targetfile(system_tex_path, system, df, columns_by_file, system_dfs_list[i], head_target_text, tail_target_text, comments_path, targetfiles_path)
            #commentslist.write(system[0] + ".tex\n")
            main_lines.append(single_main_line)
            all_main_lines.append(single_main_line)
            all_aladin_lines.append(aladin_line)
            i = i + 1
        replace_comments(comments_path)
        #commentslist.close()

        write_main_latex_file(main_tex_path, main_lines)

        write_aladin_script(script_name, all_aladin_lines, aladin_yes_or_no)

        copy_files_and_zip_folder(base_path)

        print("\n\n############################################\n\n")

    complete_pdf(base_path_array, all_main_lines)


if __name__ == '__main__':
    divisions, aladin_yes_or_no = set_divisions(), set_aladin_yes_or_no()
    # delete_targetfiles()
    df, dfstars, columns_by_file = global_variables.initialize_dataframe(data_columns, data_files)
    main(df, dfstars, divisions, columns_by_file, aladin_yes_or_no)