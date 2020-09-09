# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:15:48 2020

@author: Sam

Need to install the following via command line:
    pip3 install openpyxl
    pip install webdriver-manager
    python -m pip install -U selenium
"""

# General Modules
import sys
# Split the Code Name
import re
# Write to JSON Database
import json
# Navigate Webpages
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
  

course_URLs = [\
"https://catalog.caltech.edu/current/ae",\
"https://catalog.caltech.edu/current/an",\
"https://catalog.caltech.edu/current/acm",\
"https://catalog.caltech.edu/current/am",\
"https://catalog.caltech.edu/current/aph",\
"https://catalog.caltech.edu/current/art",\
"https://catalog.caltech.edu/current/ay",\
"https://catalog.caltech.edu/current/bmb",\
"https://catalog.caltech.edu/current/be",\
"https://catalog.caltech.edu/current/bi",\
"https://catalog.caltech.edu/current/bem",\
"https://catalog.caltech.edu/current/che",\
"https://catalog.caltech.edu/current/ch",\
"https://catalog.caltech.edu/current/ce",\
"https://catalog.caltech.edu/current/cns",\
"https://catalog.caltech.edu/current/cs",\
"https://catalog.caltech.edu/current/cms",\
"https://catalog.caltech.edu/current/cds",\
"https://catalog.caltech.edu/current/ec",\
"https://catalog.caltech.edu/current/ee",\
"https://catalog.caltech.edu/current/est",\
"https://catalog.caltech.edu/current/e",\
"https://catalog.caltech.edu/current/en",\
"https://catalog.caltech.edu/current/esl",\
"https://catalog.caltech.edu/current/ese",\
"https://catalog.caltech.edu/current/f",\
"https://catalog.caltech.edu/current/fs",\
"https://catalog.caltech.edu/current/ge",\
"https://catalog.caltech.edu/current/h",\
"https://catalog.caltech.edu/current/hps",\
"https://catalog.caltech.edu/current/hum",\
"https://catalog.caltech.edu/current/ids",\
"https://catalog.caltech.edu/current/ist",\
"https://catalog.caltech.edu/current/isp",\
"https://catalog.caltech.edu/current/l",\
"https://catalog.caltech.edu/current/law",\
"https://catalog.caltech.edu/current/ms",\
"https://catalog.caltech.edu/current/ma",\
"https://catalog.caltech.edu/current/me",\
"https://catalog.caltech.edu/current/mede",\
"https://catalog.caltech.edu/current/mu",\
"https://catalog.caltech.edu/current/nb",\
"https://catalog.caltech.edu/current/pva",\
"https://catalog.caltech.edu/current/pl",\
"https://catalog.caltech.edu/current/pe",\
"https://catalog.caltech.edu/current/ph",\
"https://catalog.caltech.edu/current/ps",\
"https://catalog.caltech.edu/current/psy",\
"https://catalog.caltech.edu/current/sec",\
"https://catalog.caltech.edu/current/ss",\
"https://catalog.caltech.edu/current/sa",\
"https://catalog.caltech.edu/current/vc",\
"https://catalog.caltech.edu/current/wr",\
]
    
#course_URLs = ["https://catalog.caltech.edu/current/bi"]
# Ch 213A
# Problem with Units (Ae 251, Ae 241)


    
def write_Data(data, class_Code, class_Name, class_Units, prereqs, class_Term, class_Description):
    class_Code = re.sub(' +', ' ', class_Code) # Remove Double Spaces
    # Decompress Class Code for Each Class
    class_Code_Info = re.split('(\d+)', class_Code)
    class_Depts = class_Code_Info[0].replace(" ","").split("/")
    class_Nums = [class_Code_Info[1].replace(" ","")]
    class_Levels = "-" # Holder for NO Class Level Listed
    if len(class_Code_Info) == 3:
        class_Levels = class_Code_Info[2].replace(" ","").lower()
        if class_Levels == "":
            class_Levels = "-"
    elif len(class_Code_Info) > 3:
        print("Class Code has Multiple Numbers (Handled): ", class_Code_Info, class_Code, "\n")
        class_Depts = class_Code_Info[0].replace(" ","").split("/")
        class_Nums = "".join(class_Code_Info[1:-1]).replace(" ","").split("/")
        class_Levels = class_Code_Info[-1].replace(" ","")
        if class_Levels == "":
            class_Levels = "-"
        
    
    # For Each Class Get Class Code
    for class_Dept in class_Depts:
        for class_Level in class_Levels:
            if class_Level == "-":
                class_Level = ""
            else:
                class_Level = class_Level
            for class_Num in class_Nums:
                class_Code = class_Dept + " " + class_Num + class_Level
                # See if Class Already in Dictionary
                previous_Input = data.get(class_Code, None)
                if previous_Input == None:
                     # Write Info to JSON Database for NEW Input
                    data[class_Code] = {}
                    data[class_Code]['class_Code'] = re.sub(' +', ' ', class_Code)   # Single Spaces Only
                    data[class_Code]['class_Units'] = re.sub(' +', ' ', class_Units)
                    data[class_Code]['class_Name'] = re.sub(' +', ' ', class_Name)
                    data[class_Code]['section_Info'] = {
                        'first': {"01": {"section_Instructor": "NA", "section_Time": ["A"], "section_Loc": ["A"], "section_Grading": "NA"}}, 
                        'second': {"01": {"section_Instructor": "NA", "section_Time": ["A"], "section_Loc": ["A"], "section_Grading": "NA"}}, 
                        'third': {"01": {"section_Instructor": "NA", "section_Time": ["A"], "section_Loc": ["A"], "section_Grading": "NA"}}
                    }
                    # Some Info is Not Present Here
                    data[class_Code]['class_Term'] = class_Term
                    data[class_Code]['class_Prereqs'] = prereqs
                    data[class_Code]['class_Description'] = class_Description
                
                # Write Info to JSON Database for Updated Input
                # If Units Not Present
                if data[class_Code]['class_Units'] in ["+", "NA", "", " "]:
                    data[class_Code]['class_Units'] = re.sub(' +', ' ', class_Units) # Single Spaces Only
                # If Full Name Present
                if len(data[class_Code]['class_Name']) < len(re.sub(' +', ' ', class_Name)):
                    data[class_Code]['class_Name'] = re.sub(' +', ' ', class_Name)   # Single Spaces Only
                # If NA
                if data[class_Code]['class_Prereqs'] in ["NA", "", " "]:
                    data[class_Code]['class_Prereqs'] = prereqs
                # If NA
                if data[class_Code]['class_Term'] in ["NA", "", " "]:
                    data[class_Code]['class_Term'] = class_Term
                # Add Another Term
                for term in class_Term.split(", "):
                    if term.lower() not in data[class_Code]['class_Term'].lower():
                        data[class_Code]['class_Term'] += ", " + term
                # If NA
                if data[class_Code]['class_Description'] in ["NA", "", " "] or data[class_Code]['class_Description'].startswith("For course description,"):
                    data[class_Code]['class_Description'] = class_Description
                #print(data[class_Code],"\n")

    # Return Back to Loop
    return data

    
with open('registars_Data.json') as JSON_File:
    data = json.load(JSON_File)
        
    sheet_row = 1
    for URL in course_URLs:
        try:
            print("Getting Class Info for: ", URL)
            # Open a Chrome Browser (in Terminal) to Run Code
            driver = webdriver.Chrome(executable_path='./chromedriver')
            driver.get(URL)
            course_Page = driver.find_elements_by_xpath("//div[contains(@class,'sidebar-layout__rich-text') and contains(@class,'rich-text')]")
            # No Info on Page
            if len(course_Page) == 0:
                driver.close()
                print("No Info on Page: ", URL)
                continue
            # Loop Through Info on Page
            class_Info_List = course_Page[0].find_elements_by_tag_name('p')
            for current_Class in class_Info_List:
                #print("Start",current_Class.text[0:15])
                class_Code_and_Name_List = current_Class.find_elements_by_tag_name('strong')
                # If there is no Bold letters, it is just a general message on page
                if len(class_Code_and_Name_List) == 0:
                    print("\nThe URL Was: ", URL)
                    print("And There was No Class Name, but there was the Following: ",  current_Class.text)
                    print("The Section Was Skipped \n")
                    continue
                # Extract Class Code and Name
                class_Code_and_Name = ""
                for code in  class_Code_and_Name_List:
                    class_Code_and_Name += code.text + " "
                class_Code_and_Name = re.sub(' +', ' ', class_Code_and_Name) # Single Spaces Only
                class_Code = class_Code_and_Name.split(".")[0]
                class_Name = class_Code_and_Name.split(". ")[1].replace(".","")
                # Extract Class Units (Units are NEVER in BOLD)
                class_Units_and_Term_Total = current_Class.find_elements_by_tag_name('em')
                class_Units_and_Term = []
                for tag in class_Units_and_Term_Total:
                    # It isnt part of the Units if it is in Bold
                    parent_Tag = tag.find_element_by_xpath('..').tag_name
                    if parent_Tag != "strong":
                        class_Units_and_Term.append(tag)
                # Initialize Variables
                prereqs = "NA"
                class_Term = ""
                class_Units = "NA"
                # Extract Prereqs, Term, and Units
                for i, emphasis_Info in enumerate(class_Units_and_Term):
                    # Getting Class Units and Term
                    emphasis_Info_Text = emphasis_Info.text
                    if i == 0:
                        # Get Units in Parenthesis Form
                        try: 
                            class_Units = re.search('\(([^)]+)', emphasis_Info_Text).group(1)
                        # Or Just at Least Get the Total Units
                        except:
                            class_Units_List = re.search(r'\d+', emphasis_Info_Text)
                            if class_Units_List != None:
                                class_Units = class_Units_List[0]
                    # Check if There is a Prereq Given WITH Information
                    if 'Prerequisite' in emphasis_Info_Text:
                        #print("Trying to Get Prereqs from ", emphasis_Info.text)
                        prereqs = emphasis_Info_Text
                        #print("Got Class Prereqs")
                    if class_Term != "":
                        # Get the CLass Term     
                        big_Emphasis_Info_Text = emphasis_Info_Text.upper()
                        if "FIRST" in big_Emphasis_Info_Text:
                            class_Term += "first, "
                        if "SECOND" in big_Emphasis_Info_Text:
                            class_Term += "second, "
                        if "THIRD" in big_Emphasis_Info_Text:
                            class_Term += "third, "
                        if len(class_Term) > 0:
                            class_Term = class_Term[0:-2]
                if prereqs != "NA":
                    #print("prereqs found: " + prereqs + "; Getting Description")
                    class_Description = "".join(current_Class.text.split(prereqs)[1:])[1:]
                elif class_Units_and_Term == []:
                    #print("No Prereqs, Units, or Term found; Getting Description via class Name")
                    class_Description = "".join(current_Class.text.split(class_Name)[1:])[2:]
                else:
                    #print("Getting Description via NA prereqs: ", prereqs)
                    class_Description = "".join(current_Class.text.split(class_Units_and_Term[0].text)[1:])[1:]
                #print("Description: ", class_Description + "\n")
                #print("code ", class_Code, " name ", class_Name, " units: ", class_Units, " reqs ", prereqs, " term: ", class_Term)
                
                data = write_Data(data, class_Code, class_Name, class_Units, prereqs, class_Term, class_Description)
                sheet_row += 1
            print("Closing")
            driver.close()
        except Exception as e:
            print(e)
            driver.close()
            print("\n\nError Getting Data From: ", URL)
            
with open('department_data_Old_Style.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

