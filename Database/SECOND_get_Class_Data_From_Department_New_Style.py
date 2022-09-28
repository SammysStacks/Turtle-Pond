# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:15:48 2020

@author: Sam

Need to install the following via command line:
    pip3 install openpyxl
    pip install webdriver-manager
    python -m pip install -U selenium

Program takes around 5 minutes to run
"""


# Split the Code Name
import re
# Write to JSON Database
import json
# Navigate Webpages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

course_URLs = [\
"https://catalog.caltech.edu/current/2022-23/",\
]

    
def write_Data(data, class_Code, class_Name, class_Units, class_Term, class_Prereqs, class_Description):
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
        print("\tClass Code has Multiple Numbers (Handled): ", class_Code_Info, class_Code)
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
                    data[class_Code]['class_Term'] = class_Term
                    data[class_Code]['class_Description'] = class_Description
                    # Some Info is Not Present Here
                    data[class_Code]['class_Prereqs'] = class_Prereqs
                    data[class_Code]['course_Evaluation_Info'] = {
                        'first': {'class_Hours': "NA", 'class_Rating': "NA", 'course_Eval_URL': "NA"},
                        'second': {'class_Hours': "NA", 'class_Rating': "NA", 'course_Eval_URL': "NA"},
                        'third': {'class_Hours': "NA", 'class_Rating': "NA", 'course_Eval_URL': "NA"},
                    }
                
                # Write Info to JSON Database for Updated Input
                # If Units Not Present
                if data[class_Code]['class_Units'] in ["+", "NA", "", " ", "."]:
                    data[class_Code]['class_Units'] = re.sub(' +', ' ', class_Units) # Single Spaces Only
                # If Full Name Present
                if len(data[class_Code]['class_Name']) < len(re.sub(' +', ' ', class_Name)):
                    data[class_Code]['class_Name'] = re.sub(' +', ' ', class_Name)   # Single Spaces Only
                # If NA
                if data[class_Code]['class_Term'] in ["NA", "", " ", "."]:
                    data[class_Code]['class_Term'] = class_Term
                # If Prereqs Not Present
                if data[class_Code]['class_Prereqs'] in ["+", "NA", "", " ", ".", "Prerequisites: NA"]:
                    data[class_Code]['class_Prereqs'] = re.sub(' +', ' ', class_Prereqs) # Single Spaces Only
                # Add Another Term
                if class_Term != "NA":
                    for term in class_Term.split(", "):
                        if term.lower() not in data[class_Code]['class_Term'].lower():
                            data[class_Code]['class_Term'] += ", " + term
                # If NA
                if data[class_Code]['class_Description'] in ["NA", "", " ", "."] or data[class_Code]['class_Description'].startswith("For course description,"):
                    data[class_Code]['class_Description'] = class_Description

    # Return Back to Loop
    return data

    
with open('registars_Data.json') as JSON_File:
    data = json.load(JSON_File)
        
    for URL in course_URLs:
        try:
            print("Getting Class Info for: ", URL)
            # Open a Chrome Browser (in Terminal) to Run Code
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get(URL)
            course_Pages = driver.find_elements(By.XPATH, "//ul[contains(@class,'catalog-sidebar-menu-block__level-3')]//li[contains(@class,'catalog-sidebar-menu-block__level-3__item')]//a")
            # No Info on Page
            if len(course_Pages) == 0:
                driver.close()
                print("No Info on Page: ", URL)
                continue
            # Loop Through Departments
            for pageInd in range(len(course_Pages)):
                # Navigate to the deparment page
                department = course_Pages[pageInd]
                print("Moving to " + department.text)
                driver.execute_script("arguments[0].click();", department)
                # Recover course pages (after page reload)
                course_Pages = driver.find_elements(By.XPATH, "//ul[contains(@class,'catalog-sidebar-menu-block__level-3')]//li[contains(@class,'catalog-sidebar-menu-block__level-3__item')]//a")

                class_Info_List = driver.find_elements(By.XPATH, "//div[contains(@class,'course-description2 ') and not(contains(@class,'course-description2--not-offered'))]")
                # Loop Through Info on Page
                for current_Class in class_Info_List:
                    # Get Info for Class
                    class_Code = current_Class.find_element(By.XPATH, ".//div[contains(@class,'course-description2__label')]").text
                    class_Name = current_Class.find_element(By.XPATH, ".//h3[contains(@class,'course-description2__title')]").text
                    class_Units, class_Term_to_Edit = current_Class.find_elements(By.XPATH, ".//span[contains(@class,'course-description2__units-and-terms__item')]")
                    class_Units, class_Term_to_Edit = class_Units.text, class_Term_to_Edit.text
                    class_Description = current_Class.find_element(By.XPATH, ".//div[contains(@class,'course-description2__description course-description2__general-text')]").text
                    try:
                        class_Instructors = current_Class.find_element(By.XPATH, ".//div[contains(@class,'course-description2__instructors course-description2__general-text')]").text
                    except:
                        class_Instructors = "NA"
                    try:
                        class_Prereqs = current_Class.find_element(By.XPATH, ".//div[contains(@class,'course-description2__prerequisites')]").text
                    except:
                        class_Prereqs = "Prerequisites: NA"
                    
                    # Add Instructor to Description
                    if class_Instructors in ["NA", " ", ".", " .", ""]:
                        class_Instructors = ""
                    else:
                        class_Instructors = " " + class_Instructors
                    class_Description = class_Description + class_Instructors
                    
                    # Get Units in Parenthesis Form
                    try: 
                        class_Units = re.search('\(([^)]+)', class_Units).group(1)
                    # Or Just at Least Get the Total Units
                    except:
                        class_Units_List = re.search(r'\d+', class_Units)
                        if class_Units_List != None:
                            class_Units = class_Units_List[0]
                    if not bool(re.search(r'\d', class_Units)):
                        class_Units = "NA"
                        
                    
                    # Format Class Term
                    class_Term = ""
                    if class_Term_to_Edit != "":
                        # Get the CLass Term     
                        class_Term_to_Edit = class_Term_to_Edit.upper()
                        if "FIRST" in class_Term_to_Edit:
                            class_Term += "first, "
                        if "SECOND" in class_Term_to_Edit:
                            class_Term += "second, "
                        if "THIRD" in class_Term_to_Edit:
                            class_Term += "third, "
                        if len(class_Term) > 0:
                            class_Term = class_Term[0:-2]
                    if class_Term == "":
                        class_Term = "NA"
                    
                    #print("Description: ", class_Description)
                    #print("code: ", class_Code, " name: ", class_Name, " units: ", class_Units, " term: ", class_Term)
                    #print("")
                    
                    data = write_Data(data, class_Code, class_Name, class_Units, class_Term, class_Prereqs, class_Description)
                    
            print("Closing")
            driver.close()
        except Exception as e:
            print(e)
            driver.close()
            print("\n\nError Getting Data From: ", URL)
            
with open('department_Data_Current.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

