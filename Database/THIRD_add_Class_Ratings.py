# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:15:48 2020

@author: Sam

Need to install the following via command line:
    pip3 install openpyxl
    pip install webdriver-manager
    python -m pip install -U selenium
    
Time to run: ~0.5 Hours per link For Slow Internet
Time to run: ~12 Minutes per link For Fast Internet (Page Navigation is Slowest Step)

Works Best in Chrome (in Dock for Macs, not pop up)
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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Most Recent Ones Should be Near Top
course_URLs = [\
# Spring
("https://access.caltech.edu/tqfr/reports/list_divisions?survey_id=47&term_id=548", "third"),  # 2022
("https://access.caltech.edu/tqfr/reports/list_divisions?survey_id=43&term_id=528", "third"),  # 2021
# Winter
("https://access.caltech.edu/tqfr/reports/list_divisions?survey_id=46&term_id=547", "second"), # 2022
("https://access.caltech.edu/tqfr/reports/list_divisions?survey_id=42&term_id=527", "second"), # 2021
# Fall
("https://access.caltech.edu/tqfr/reports/list_divisions?survey_id=45&term_id=546", "first"),  # 2022
#("https://access.caltech.edu/tqfr/reports/list_divisions?survey_id=41&term_id=526", "first"),  # 2021
]
    
badLinks = []



def write_Data(data, class_Code, course_Hours, rating, course_Eval_URL, link_Term):      
    
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
                #print("code:", class_Code)
                # See if Class Already in Dictionary (Dont add New Class Just for a Rating; Maybe it is Not Offered)
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
        
    for URL_Term_Term in course_URLs:
        URL = URL_Term_Term[0]
        Link_Term = URL_Term_Term[1]
        try:
            print("Getting Class Info for: ", URL)
            # Open a Chrome Browser (in Terminal) to Run Code
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get(URL)
            # Login
            login_Form = driver.find_elements(By.XPATH, "//body//div[contains(@id,'container')]//div[contains(@id,'contents')]//section[contains(@id,'main')]//form[contains(@id, 'login_form')]")[0]
            login_Form.find_elements(By.XPATH, "//input[contains(@name,'login')]")[0].send_keys("ssolomon")
            login_Form.find_elements(By.XPATH, "//input[contains(@name,'password')]")[0].send_keys("SAMthegreat11!!")
            login = login_Form.find_elements(By.XPATH, "//input[contains(@type,'submit')]")[0]
            driver.execute_script("arguments[0].click();", login)
            # Get Table Information with Class Catagories
            department_Evals = driver.find_elements(By.XPATH, "//table[contains(@class,'tablediv')]//tbody//tr//td[contains(@class,'questiondiv')]//a")
            # No Info on Page
            if len(department_Evals) == 0:
                driver.close()
                print("No Info on Page: ", URL)
                continue
            
            # Loop through Catagories (BBE)
            for evalInd in range(len(department_Evals)):
                department_Evals = driver.find_elements(By.XPATH, "//table[contains(@class,'tablediv')]//tbody//tr//td[contains(@class,'questiondiv')]//a")
                course_Division = department_Evals[evalInd]
                # Find Department in Division (Bioengineering)
                driver.execute_script("arguments[0].click();", course_Division)
                course_Departments = driver.find_elements(By.XPATH, "//table[contains(@class,'tablediv')]//tbody//tr//td[contains(@class,'questiondiv')]//a")
                for courseDepartmentInd in range(len(course_Departments)):
                    course_Departments = driver.find_elements(By.XPATH, "//table[contains(@class,'tablediv')]//tbody//tr//td[contains(@class,'questiondiv')]//a")
                    course_Department = course_Departments[courseDepartmentInd]
                    # print("Department:", course_Department.text)
                    # Find Classes in Departmnet
                    driver.execute_script("arguments[0].click();", course_Department)
                    currentClassRows = driver.find_elements(By.XPATH, "//table[contains(@class,'tablediv')]//tbody//tr")
                    for rowInd in range(len(currentClassRows)):
                        classRow = currentClassRows[rowInd]
                        if "0.00 ± 0.00" in classRow.text or 'Offering Response Rate Surveys Score' in classRow.text or 'NOT SURVEYED' in classRow.text:
                            continue
                        
                        # Find Course Score
                        course_Score = classRow.text.split(" ± ")
                        if len(course_Score) > 1:
                            course_Score = course_Score[0].split(" ")[-1] + " ± " + course_Score[1]
                        else:
                            continue
                        
                        # Move into Course Survey Page
                        courseElement = classRow.find_element(By.XPATH, ".//td[contains(@class,'questiondiv')]//a")
                        course_Code = courseElement.text.split(" Section")[0]
                        driver.execute_script("arguments[0].click();", courseElement)
                        # Wait for the page to load
                        try:
                            element_present = EC.presence_of_element_located((By.XPATH, ".//td[contains(text(),'±')]"))
                            WebDriverWait(driver, 30).until(element_present)
                        except TimeoutException:
                            print("\tTimed out waiting for page to load")
                        
                        # Get Course Evaluation URL
                        course_Eval_URL = driver.current_url
                        
                        # Get Median Class Hours
                        try:
                            # get Hours Element
                            course_Hours_Table = driver.find_element(By.XPATH, ".//h2[contains(text(),'Hours/Week')]/following-sibling::table")
                            course_Average_Text = course_Hours_Table.find_element(By.XPATH, ".//td[contains(text(),'Course Average')]")
                            course_Hours_Full_Text = course_Average_Text.find_element(By.XPATH, "..").text
                            # Find Highest Percentage
                            course_Hours_List = [e for e in re.split("[^0-9]", course_Hours_Full_Text) if e != '']
                            course_Hours_Max_Percent = max(map(int, course_Hours_List))
                            # Find Hours for the Percentage
                            columns_In = len(course_Hours_Full_Text.split(str(course_Hours_Max_Percent))[0].split("%"))
                            course_Hours = course_Hours_Table.find_elements(By.XPATH, ".//tr[contains(@class,'header')]//th")[columns_In].text                            
                        except Exception:
                            print("\tNo Hours found in the URL:", course_Eval_URL)
                            #print("No Class Hours")
                            course_Hours = "NA"
                        
                        # Get Course Overall Rating
                        rating_Header = driver.find_element(By.XPATH, ".//td[contains(text(),'±')]")
                        rating = rating_Header.text.split(" ± ")
                        if len(rating) > 1:
                            rating = rating[0] + " ± " + rating[1].split(" ")[-1]
                            #print("Rating", rating)
                        else:
                            #print("No Score in Class Page ... WHY?")
                            rating = "NA"
                            
                        # Write Data
                        data = write_Data(data, course_Code, course_Hours, course_Score, course_Eval_URL, Link_Term)
                        
                        # Return Back to Previous Page
                        driver.back()
                        # Wait for the page to load
                        try:
                            element_present = EC.presence_of_element_located((By.XPATH, "//table[contains(@class,'tablediv')]//tbody//tr"))
                            WebDriverWait(driver, 30).until(element_present)
                        except TimeoutException:
                            print("\tTimed out waiting for page to load")
                            # Reset current classes
                        currentClassRows = driver.find_elements(By.XPATH, "//table[contains(@class,'tablediv')]//tbody//tr")

                    driver.back()
                driver.back()
            print("Closing")
            driver.close()
        except Exception as e:
            print(e)
            badLinks.append((Link_Term, URL, e))
            driver.close()
            print("\n\nError Getting Data From: ", URL)

print(badLinks)
            
with open('courses_And_Ratings.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

