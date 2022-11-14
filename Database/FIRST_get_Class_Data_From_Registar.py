# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:15:48 2020

@author: Sam

Need to install the following via command line:
    pip install openpyxl webdriver-manager selenium
    
Takes around 45 minutes (+/- 15 per page), Internet Speed Dependant
"""

# Basic Modules
import re         # Split Strings
import sys        # System
import linecache  # Error Printing
# Write to JSON Database
import json
# Navigate Webpages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
    
course_URLs = [\
"http://schedules.caltech.edu/FA2022-23.html", \
"http://schedules.caltech.edu/WI2022-23.html", \
"http://schedules.caltech.edu/SP2021-22.html",   
]


def write_Data(data, class_Code, class_Units, class_Name, section_Info, URL):
    # Get Class Term
    if URL.split("/")[-1][0] == "F":
        class_Term = "first"
    elif URL.split("/")[-1][0] == "W":
        class_Term = "second"
    elif URL.split("/")[-1][0] == "S":
        class_Term = "third"
    
    class_Code = re.sub(' +', ' ', class_Code) # Single Spaces Only
    # Decompress Class Code for Each Class
    class_Code_Info = re.split('(\d+)', class_Code)
    class_Depts = class_Code_Info[0].replace(" ","").split("/")
    class_Num = class_Code_Info[1].replace(" ","")
    while class_Num[0] == "0":
        class_Num = class_Num[1:] # Remove the First Zero
    class_Levels = "-" # Holder for NO Class Level Listed
    if len(class_Code_Info) == 3:
        class_Levels = class_Code_Info[2].replace(" ","").lower()
        if class_Levels == "":
            class_Levels = "-"
    elif len(class_Code_Info) > 3:
        print("Error in Decomposing Class Code: ", class_Code_Info, class_Code, "\n")
        exit()
    
    # For Each Class Get Class Code
    for class_Dept in class_Depts:
        for class_Level in class_Levels:
            if class_Level == "-":
                class_Level = ""
            else:
                class_Level = class_Level
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
                data[class_Code]['section_Info'][class_Term] = section_Info
                data[class_Code]['class_Term'] = class_Term
                # Some Info is Not Present Here
                data[class_Code]['class_Prereqs'] = "NA"
                data[class_Code]['class_Description'] = "NA"
                data[class_Code]['course_Evaluation_Info'] = {
                        'first': {'class_Hours': "NA", 'class_Rating': "NA", 'course_Eval_URL': "NA"},
                        'second': {'class_Hours': "NA", 'class_Rating': "NA", 'course_Eval_URL': "NA"},
                        'third': {'class_Hours': "NA", 'class_Rating': "NA", 'course_Eval_URL': "NA"},
                    }
            # Write Info to JSON Database for Updated Input
            # If Units Not Present
            if data[class_Code]['class_Units'] in ["+", "NA", "", " "]:
                data[class_Code]['class_Units'] = re.sub(' +', ' ', class_Units) # Single Spaces Only
            # If Full Name Present
            if len(data[class_Code]['class_Name']) < len(re.sub(' +', ' ', class_Name)):
                data[class_Code]['class_Name'] = re.sub(' +', ' ', class_Name)   # Single Spaces Only
            # Add Another Term
            if class_Term.lower() not in data[class_Code]['class_Term'].lower():
                data[class_Code]['class_Term'] += ", " + class_Term
            # Add section_Infoif Needed
            if data[class_Code]['section_Info'][class_Term] == {"01": {"section_Instructor": "NA", "section_Time": ["A"], "section_Loc": ["A"], "section_Grading": "NA"}}:
                data[class_Code]['section_Info'][class_Term] = section_Info
            #print(data[class_Code],"/n")

    # Return Back to Loop
    return data
    

# Initialize Variables to Get Data
class_Section = "01"
class_Number = 0
data = {}
# Get Data From Registar Website
for URL in course_URLs:
    try:
        
        # ----------- Open Selenium Driver and Compile Data Tags ----------- #
        
        # Open a Chrome Browser (in Terminal) to Run Code
        print("Getting Class Info for: ", URL)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(URL)
        # Get Course HTML Elements
        course_Body_List = driver.find_elements(By.XPATH, "//table//tbody//tr//td[contains(@rowspan,'2')][contains(@width,'132')]//font[contains(@face,'verdana')]//parent::td//parent::tr")
        course_Header_List = driver.find_elements(By.XPATH, "//table//tbody//tr[contains(@valign,'top')]//td[contains(@width,'113')]//a[contains(@target,'_parent')]//font[contains(@face,'verdana')]//parent::a//parent::td//parent::tr")
        cancelledClasses = driver.find_elements(By.XPATH, "//table//tbody//tr//td[contains(@width,'524')]//font[contains(@face,'verdana')]//i[contains(text(), 'cancelled')][not(contains(text(),'ection'))]")
        totalSections = len(course_Body_List)
        header_Hash = 1
        cancelledHash = 0
        
        # ---------------------------------------------------------------#

        # Loop Through Every Class Section in Every Course
        section_Info = {}
        for sectionNum, section in enumerate(course_Body_List):
            
            # ------------ Compile Section Header and Write Data ----------- #
            
            # If we are Moving onto Next Header
            if sectionNum == totalSections - 1 or section.location['y'] > course_Header_List[header_Hash].location['y']:
                # Get the Class Header Information
                course_Header = course_Header_List[header_Hash-1].find_elements(By.TAG_NAME, 'td')
                # From the Header Information, Extract the Class Code/Units/Name
                class_Code = "NA"; class_Units = "NA"; class_Name = "NA";
                for course in course_Header:
                    element_Width= course.get_attribute('width')
                    if element_Width == "113":
                        class_Code_RAW = course.text
                        class_Code = " ".join(re.split(r'(^[^\d]+)', class_Code_RAW)[1:]) # Add Space Before Class #
                    elif element_Width == "80":
                        class_Units = course.text
                    elif element_Width == "524":
                        class_Name = course.text
                
                # Write Data; Skip Classes that are Canceled (Should be 18 apart, dont go over 70)
                if cancelledHash >= len(cancelledClasses) or cancelledClasses[cancelledHash].location['y'] - course_Header_List[header_Hash-1].location['y'] > 18*3:
                    data = write_Data(data, class_Code, class_Units, class_Name, section_Info, URL)
                # Iterate the canceled classes
                while cancelledHash != len(cancelledClasses) and cancelledClasses[cancelledHash].location['y'] - course_Header_List[header_Hash-1].location['y'] < 0:
                    cancelledHash += 1
                # Prepare for next Course
                section_Info = {}
                header_Hash += 1
                        
            # ---------------------------------------------------------------#
                
            # -------------- Get Section Info for Each Section ------------- #
            
            # Initialize New Variables for Course
            new_Course = True
            previous_Section = class_Section
            class_Section = "NA"; section_Instructor = "NA"; section_Time = "NA";
            section_Loc = "NA"; section_Grading = "NA"
            
            # Extract Class Information from the Section
            course_Body = section.find_elements(By.TAG_NAME, 'td')
            for course in course_Body:
                element_Width = course.get_attribute('width')
                # Reduce Options
                itemText = course.text
                if itemText in ["NA", "", " "]:
                    itemText = "NA"
                # Find the Correct Label
                if element_Width == "42":
                    class_Section = itemText
                elif element_Width == "184":
                    section_Instructor = itemText
                elif element_Width == "135":
                    section_Time = itemText
                elif element_Width == "94":
                    section_Loc = itemText
                elif element_Width == "132":
                    section_Grading = itemText
            
            # ---------------------------------------------------------------#
            
            # ----------- Compile Section Info under One Format ------------ #
                    
            # If Class Section is Missing, then Data Belongs to Previous Section
            if class_Section in ["NA", "", " "]:
                # This is NOT a New Course Section to Add!! It Belongs to the Last One
                new_Course = False
                class_Section = previous_Section
                # If there was an Instructor, it is Just The Rest of the Name
                if section_Instructor not in ["NA", "", " "]:
                    section_Info[class_Section]['section_Instructor'] += section_Instructor
                # If there is a New Time, It is New Information
                if section_Time not in ["NA", "", " ", "A"]:
                    if section_Info[class_Section]['section_Time'][-1].endswith(" - "):
                        section_Info[class_Section]['section_Time'][-1] += section_Time
                    else:
                        section_Info[class_Section]['section_Time'].append(section_Time)
                    # If the New Location is Useful
                    if section_Loc not in ["NA", "", " ", "A"]:
                        # If the Old Location Wasnt Useful
                        if section_Info[class_Section]['section_Loc'] not in ["NA", "", " ", "A"]:
                            section_Info[class_Section]['section_Loc'] = section_Loc
                        # If New Location, Add it as List
                        else:
                            section_Info[class_Section]['section_Loc'].append(section_Loc)
                # If there is No New Time, But Loc -> It is Really an Extension of the Previous location
                elif section_Loc not in ["NA", "", " ", "A"]:
                    section_Info[class_Section]['section_Loc'] += section_Loc
                # if section_Grading != "NA", It doesnt matter as it is just always the same
            # It is a New Course, so Compile Section Data
            else:
                section_Info[class_Section] = {}
                section_Info[class_Section]['section_Instructor'] = section_Instructor
                section_Info[class_Section]['section_Time'] = [section_Time]
                section_Info[class_Section]['section_Loc'] = [section_Loc]
                section_Info[class_Section]['section_Grading'] = section_Grading 
            
            # ---------------------------------------------------------------#
                        
        driver.close()
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
        print(e)
        sys.exit()

print("Finished: ", len(data.keys()))
with open('registars_Data.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

