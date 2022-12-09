# gaiaUCDs

NOTE: /Data files are missing, you can find the ones I've used there: https://drive.google.com/drive/folders/1XGBTtp4AsmOkBsOjV2KRX8ACVCfgvcvW?usp=share_link
Download and copy them inside the Data folder where there are the matching .txt
 
First of all, please DO NOT move or rename the "basic" files and folders.
Probably this program will work only under Linux OS.

#################### Description ####################

[0] The main file is "main.py" (unbelievable). To run the program, "python main.py". The "config.py" is service only file. Other python files are inside /utils/.

--------------------------------------------------

[1] /setup/ folder: "data_files.txt" contains the names of the files in which there is the necessary data. Write the file names there (case sensitive) along with the extension.
The program can accept any number of "example.fits" or "example.csv" files, just be sure they have no columns with the same name.
Finally, "refs.bib" and "summary.tex" are there just to be copied inside the generated directories.

--------------------------------------------------

[2] The program will generate many folders. Every /latex_files/RA_X_Y/ will contain the LaTeX files (just add the necessary comments files) ready to be zipped for OverLeaf or whatever.
Folder /aladin_scripts/ will contain every Aladin's script: you can launch them manually if needed (point [4]).

--------------------------------------------------

[3] The columns you want in the final LaTeX PDF have to be written in the /Data/ folder, inside a text file with the same name of the relative .fits, just with a .txt extension.
The structure of the file should be:
	columnName, approximation, dataType, columnNameError
Approximation is an integer number > 0 (relevant only for float data), dataType is a letter (i=integer, f=float, s=string), columnNameError is the column error associated to the columnName and is optional.
NOTA BENE: if a column has an associated error, you also have to add a row for the column error! Example:
	Parallax, 2, F, ParallaxError
	ParallaxError, 2, F
	
[3.1] The principal Master file will not read the columnNameError. You will have to edit manually the first part of "utils/latex_table_code.py", because it is more complex than the secondary files and cannot be fully automated very easily.

--------------------------------------------------

[4] /sample_files/ folder: here there are the sample files for the final single targetfiles. You can carefully edit the "targetfile_sample_head.txt". You can edit or add code to the "targetfile_sample_tail.txt" as you want but please DO NOT MOVE ALREADY PRESENT LINES, otherwise you will also need to edit the Python code in the "utils/latex_table_code.py" file

--------------------------------------------------

[5] On the Aladin's 2MASS images script: the program will automatically create and run it, but it does not always work (it can surely be improved). Just CTRL+C to stop the current script and try to run it manually from the GaiaUCD directory with ./aladin_script/script_name.sh
Disclaimer: the script is SLOW.



For any question/suggestion write me at: samuelnale@gmail.com (or samuel.naledischiena@edu.unito.it)
Bye!
