# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:15:48 2020

@author: Sam

Need to install the following via command line:
    pip3 install openpyxl
    pip install webdriver-manager
    python -m pip install -U selenium
    
Time to run: ~4.5 Hours
"""

# General Modules
import sys
# Split the Code Name
import re
# Write to JSON Database
import json

# Define New Data Dictionary
new_Data = {}
    
with open('courses_And_Ratings.json') as JSON_File:
    data = json.load(JSON_File)
    
    # Remove acb classes that are in the wrong term
    for class_Code in data:
        # For Each Course in the Dictionary, get the section info
        course_Dict = data[class_Code]
        section_Info = course_Dict["section_Info"]
        course_Evaluation_Info = course_Dict["course_Evaluation_Info"]
        # Loop through the terms to see if there are any blanks
        badTerms = []
        goodTerms = ""
        for class_Term in section_Info:
            # Record the terms with dummy information
            if section_Info[class_Term] == {'01': {'section_Grading': 'NA', 'section_Instructor': 'NA', 'section_Loc': ['A'], 'section_Time': ['A']}}:
                badTerms.append(class_Term)
            else:
                goodTerms = goodTerms + class_Term + ", "
        # if not all are dummy, delete the bad ones (if all are dummy, we really dont know)
        if len(badTerms) != len(section_Info):
            for class_Term in badTerms:
                del section_Info[class_Term]
                del course_Evaluation_Info[class_Term]
        # Specify the New Class Terms
        course_Dict["class_Term"] = goodTerms[:-2]

            
with open('courses_culled.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

