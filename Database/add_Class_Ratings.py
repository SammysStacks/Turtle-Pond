# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:15:48 2020

@author: Sam

Need to install the following via command line:
    pip3 install openpyxl
    pip install webdriver-manager
    python -m pip install -U selenium
    
Time to run: ~1.5 Hours
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


# Must Match the Write_Data Term 'URL_Term' Order
course_URLs = [\
# Spring
"https://access.caltech.edu/tqfr/reports/list_divisions?survey_id=40&term_id=522", \
# Winter
"https://access.caltech.edu/tqfr/reports/list_divisions?survey_id=39&term_id=521", \
# Fall
"https://access.caltech.edu/tqfr/reports/list_divisions?survey_id=38&term_id=520", \
]


    
def write_Data(data, class_Code, course_Hours, rating, course_Eval_URL, URL_Term):
    # Get Class Term
    if URL_Term == 2:
        link_Term = "first"
    elif URL_Term == 1:
        link_Term = "second"
    elif URL_Term == 0:
        link_Term = "third"
        
    
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
    # Remove Trailing Zeros from Class Nums
    for i in range(len(class_Nums)):
        while class_Nums[i][0] == "0":
            class_Nums[i] = class_Nums[i][1:] # Remove the First Zero
        
    
    # For Each Class Get Class Code
    for class_Dept in class_Depts:
        for class_Level in class_Levels:
            if class_Level == "-":
                class_Level = ""
            else:
                class_Level = class_Level
            for class_Num in class_Nums:
                class_Code = class_Dept + " " + class_Num + class_Level
                print("code:", class_Code)
                # See if Class Already in Dictionary
                previous_Input = data.get(class_Code, None)
                if previous_Input == None:
                     continue
                
                # Write Info to JSON Database for Updated Input
                # If Units Not Present
                if data[class_Code]['course_Evaluation_Info'][link_Term]['class_Hours'] in ["+", "NA", "", " "]:
                    data[class_Code]['course_Evaluation_Info'][link_Term]['class_Hours'] = re.sub(' +', ' ', course_Hours) # Single Spaces Only
                # If Full Name Present
                if data[class_Code]['course_Evaluation_Info'][link_Term]['class_Rating'] in ["+", "NA", "", " "]:
                    data[class_Code]['course_Evaluation_Info'][link_Term]['class_Rating'] = re.sub(' +', ' ', rating)   # Single Spaces Only
                # If NA
                if data[class_Code]['course_Evaluation_Info'][link_Term]['course_Eval_URL'] in ["NA", "", " "]:
                    data[class_Code]['course_Evaluation_Info'][link_Term]['course_Eval_URL'] = course_Eval_URL
                #print(data[class_Code],"\n")
                #print(course_Hours, rating)

    # Return Back to Loop
    return data

    
with open('department_Data_Current.json') as JSON_File:
    data = json.load(JSON_File)
        
    for URL_Term, URL in enumerate(course_URLs):
        try:
            print("Getting Class Info for: ", URL)
            # Open a Chrome Browser (in Terminal) to Run Code
            driver = webdriver.Chrome(executable_path='./chromedriver')
            driver.get(URL)
            # Login
            login_Form = driver.find_elements_by_xpath("//body//div[contains(@id,'container')]//div[contains(@id,'contents')]//section[contains(@id,'main')]//form[contains(@id, 'login_form')]")[0]
            login_Form.find_elements_by_xpath("//input[contains(@name,'login')]")[0].send_keys("")
            login_Form.find_elements_by_xpath("//input[contains(@name,'password')]")[0].send_keys("")
            login = login_Form.find_elements_by_xpath("//input[contains(@type,'submit')]")[0]
            driver.execute_script("arguments[0].click();", login)
            # Get Table Information with Class Catagories
            department_Evals = driver.find_elements_by_xpath("//table[contains(@class,'tablediv')]//tbody//tr//td[contains(@class,'questiondiv')]//a")
            # No Info on Page
            if len(department_Evals) == 0:
                driver.close()
                print("No Info on Page: ", URL)
                continue
            
            # Loop through Catagories (BBE)
            i  = 0
            for i in range(len(department_Evals)):
                department_Evals = driver.find_elements_by_xpath("//table[contains(@class,'tablediv')]//tbody//tr//td[contains(@class,'questiondiv')]//a")
                course_Division = department_Evals[i]
                # Find Department in Division (Bioengineering)
                driver.execute_script("arguments[0].click();", course_Division)
                course_Departments = driver.find_elements_by_xpath("//table[contains(@class,'tablediv')]//tbody//tr//td[contains(@class,'questiondiv')]//a")
                for j in range(len(course_Departments)):
                    course_Departments = driver.find_elements_by_xpath("//table[contains(@class,'tablediv')]//tbody//tr//td[contains(@class,'questiondiv')]//a")
                    course_Department = course_Departments[j]
                    print("Department:", course_Department.text)
                    # Find Classes in Departmnet
                    driver.execute_script("arguments[0].click();", course_Department)
                    current_Courses = driver.find_elements_by_xpath("//table[contains(@class,'tablediv')]//tbody//tr")
                    for k in range(len(current_Courses)):
                        current_Courses = driver.find_elements_by_xpath("//table[contains(@class,'tablediv')]//tbody//tr")
                        current_Course = current_Courses[k]
                        if "0.00 ± 0.00" in current_Course.text:
                            continue
                        
                        # Find Course Score
                        course_Score = current_Course.text.split(" ± ")
                        if len(course_Score) > 1:
                            course_Score = course_Score[0].split(" ")[-1] + " ± " + course_Score[1]
                            print("Score:", course_Score)
                        else:
                            print("No Score", current_Course.text)
                            print("")
                            continue
                        
                        # Move into Course Survey Page
                        current_Course = current_Course.find_elements_by_xpath(".//td[contains(@class,'questiondiv')]//a")[0]
                        course_Code = current_Course.text.split(" Section")[0]
                        driver.execute_script("arguments[0].click();", current_Course)
                        
                        # Get Course Evaluation URL
                        course_Eval_URL = driver.current_url
                        
                        # Get Median Class Hours
                        try:
                            # get Hours Element
                            course_Hours_Table = driver.find_element_by_xpath(".//h2[contains(text(),'Hours/Week')]/following-sibling::table")
                            course_Average_Text = course_Hours_Table.find_element_by_xpath(".//td[contains(text(),'Course Average')]")
                            course_Hours_Full_Text = course_Average_Text.find_element_by_xpath("..").text
                            # Find Highest Percentage
                            course_Hours_List = [e for e in re.split("[^0-9]", course_Hours_Full_Text) if e != '']
                            course_Hours_Max_Percent = max(map(int, course_Hours_List))
                            # Find Hours for the Percentage
                            columns_In = len(course_Hours_Full_Text.split(str(course_Hours_Max_Percent))[0].split("%"))
                            course_Hours = course_Hours_Table.find_elements_by_xpath(".//tr[contains(@class,'header')]//th")[columns_In].text                            
                        except Exception as e:
                            print(e)
                            print("No Class Hours")
                            course_Hours = "NA"
                        
                        # Get Course Overall Rating                        
                        rating_Header = driver.find_element_by_xpath(".//td[contains(text(),' ± ')]")
                        rating_Row = rating_Header
                        rating = rating_Row.text.split(" ± ")
                        if len(rating) > 1:
                            rating = rating[0] + " ± " + rating[1].split(" ")[-1]
                            print("Rating", rating)
                        else:
                            print("No Score in Class Page ... WHY?")
                            rating = "NA"
                            
                        # Write Data
                        data = write_Data(data, course_Code, course_Hours, rating, course_Eval_URL, URL_Term)
                        
                        # Return Back to Previous Page
                        driver.back()
                        print("")

                    driver.back()
                driver.back()
            print("Closing")
            driver.close()
        except Exception as e:
            print(e)
            driver.close()
            print("\n\nError Getting Data From: ", URL)
            
with open('courses_And_Ratings.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

