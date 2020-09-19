# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:15:48 2020

@author: Sam

Need to install the following via command line:
    pip3 install openpyxl
    pip install webdriver-manager
    python -m pip install -U selenium
    
Takes around 45 minutes (+/- 15 per page)
"""

# General Modules
import sys
# Split the Code Name
import re
# Write to JSON Database
import json
# Navigate Webpages
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
    
course_URLs = [\
"http://schedules.caltech.edu/FA2020-21.html",\
"http://schedules.caltech.edu/WI2019-20.html", \
"http://schedules.caltech.edu/SP2019-20.html", \
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
        # Open a Chrome Browser (in Terminal) to Run Code
        print("Getting Class Info for: ", URL)
        driver = webdriver.Chrome(executable_path='./chromedriver')
        driver.get(URL)
        # Get Course HTML Elements
        course_Body_List = driver.find_elements_by_xpath("//table//tbody//tr//td[contains(@rowspan,'2')][contains(@width,'132')]//font[contains(@face,'verdana')]//parent::td//parent::tr")
        course_Header_List = driver.find_elements_by_xpath("//table//tbody//tr[contains(@valign,'top')]//td[contains(@width,'113')]//a[contains(@target,'_parent')]//font[contains(@face,'verdana')]//parent::a//parent::td//parent::tr")
        header_Hash = 0
        add_First = False

        # Loop Through Every Class Section in Every Course
        section_Info = {}
        for section in course_Body_List:
            # Initialize New Variables for Course
            new_Course = True
            previous_Section = class_Section
            class_Section = "NA"; section_Instructor = "NA"; section_Time = "NA";
            section_Loc = "NA"; section_Grading = "NA"
            
            # Extract Class Information from the Section
            course_Body = section.find_elements_by_tag_name('td')
            for course in course_Body:
                element_Width = course.get_attribute('width')
                if element_Width == "42":
                    class_Section = course.text
                elif element_Width == "184":
                    section_Instructor = course.text
                elif element_Width == "135":
                    section_Time = course.text
                elif element_Width == "94":
                    section_Loc = course.text
                elif element_Width == "132":
                    section_Grading = course.text
                    
            # If Class Section is Missing, then Data Belongs to Previous Section
            if class_Section in ["NA", "", " "]:
                # This is NOT a New Course Section to Add!! It Belongs to the Last One
                new_Course = False
                class_Section = previous_Section
                # If there was an Instructor, it is Just The Rest of the Name
                if section_Instructor not in ["NA", "", " "]:
                    section_Info[class_Section]['section_Instructor'] += section_Instructor
                # If there is a New Time, It is New Information
                elif section_Time not in ["NA", "", " ", "A"]:
                    section_Info[class_Section]['section_Time'].append(section_Time)
                    section_Info[class_Section]['section_Loc'].append(section_Loc)
                # If there is No New Time, But Loc -> It is Really an Extension of the Previous location
                elif section_Loc not in ["NA", "", " ", "A"]:
                    section_Info[class_Section]['section_Loc'][-1] += section_Loc
                # if section_Grading != "NA", It doesnt matter as it is just always the same
                
            # If First in Section (NOTE: I have seen mess ups with labeling the first '011'. ugh)
            # Also Some Sections are MISSING! So NOT ALL Start with 01
            if new_Course and (class_Section.startswith("01") or (int(class_Section) <= int(previous_Section))):
                # Write Previus Section
                if add_First:
                    header_Hash += 1
                    data = write_Data(data, class_Code, class_Units, class_Name, section_Info, URL)
                    # Prepare for next Course
                    section_Info = {}
                else:
                    add_First = True
                # Get the Class Header Information
                course_Header = course_Header_List[header_Hash].find_elements_by_tag_name('td')
                #print(course_Header_List[header_Hash].text)
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
                    
            # Compile Section Data
            if new_Course:
                section_Info[class_Section] = {}
                section_Info[class_Section]['section_Instructor'] = section_Instructor
                section_Info[class_Section]['section_Time'] = [section_Time]
                section_Info[class_Section]['section_Loc'] = [section_Loc]
                section_Info[class_Section]['section_Grading'] = section_Grading  
            #print(section.text)
        
        header_Hash += 1
        data = write_Data(data, class_Code, class_Units, class_Name, section_Info, URL)
        driver.close()
    except Exception as e:
        driver.close()
        print("\n\nError Getting Data From: ", URL)
        print(e)

print("Finished: ", len(data.keys()))
with open('registars_Data.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

