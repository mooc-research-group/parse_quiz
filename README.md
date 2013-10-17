parse_quiz
==========

This Python script takes Coursera quiz and survey data exports and outputs the responses to a formatted .csv file.


About
-----

Coursera provides data exports for quizzes (and for any surveys implemented as quizzes). The responses, however, are exported to an unstructured data .txt file which is difficult to use for data analysis. This Python script parses through the unstructured .txt file responses and outputs the results to a more useful .csv format. The following two input files are required: "Quiz XML.txt" and "Detailed Quiz Responses.txt". Results are outputted to "Parsed Quiz Responses.csv". Example input files and resulting output are provided.

Files
-----

#### XML.txt

This input file contains the quiz's raw XML, which this script uses to get the questions and set up the .csv file header.
* In Coursera's admin toolbar, go to "Content" > "Section Manager"
* Find the desired quiz and click "edit item" (if a warning appears, press "Continue")
* Click "Edit Raw XML"
* Copy the all of the displayed XML text and save it as "Quiz XML.txt" in the same directory as "parse_quiz.py"

#### Detailed Quiz Responses.txt

This input file contains all the quiz responses, which this script parses to populate the rows of the .csv file.
* In Coursera's admin toolbar, go to "Data" > "Detailed Quiz Responses"
* Select the desired quiz from the dropdown and click "Export" (it may take a while for Coursera to process the request)
* Once the data export is ready, it will appear under "Job Status" where you can then click on "Results"
* Download "Detailed Quiz Responses.txt" to the same directory as "parse_quiz.py"

#### parse_quiz.py

Run this file to generate "Parsed Quiz Responses.csv"
* "XML.txt" and "Detailed Quiz Responses.txt" must be in the same directory as "parse_quiz.py"
* The following Python libraries must be installed: glob, csv, re, bs4

License
-------

Licensed under GPLv3. See LICENSE file for more details.
