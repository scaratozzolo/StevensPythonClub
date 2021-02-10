from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import mystevenscreds as creds
# import importlib.util
# spec = importlib.util.spec_from_file_location("mystevenscreds", "C:/Users/Scott/OneDrive/Stevens/Python Club/mystevenscreds.py")
# creds = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(creds)


# class_codes = ["10157"]
class_codes = ["test"]*10

driver = webdriver.Chrome(executable_path="chromedriver.exe")
driver.get("https://mystevens.stevens.edu/sso/webselfservices.php")

driver.find_element_by_id("username").send_keys(creds.user)
driver.find_element_by_id("password").send_keys(creds.password)

driver.find_element_by_name("_eventId_proceed").click()

# try:
#     push_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "push-label")))
# finally:
#     driver.quit()
#
# print("here")
# push_div.find_elements_by_tag_name("button").click()

while True:

    if driver.title == "Web Self Services | myStevens":
        break


driver.get("https://mystevens.stevens.edu/sso/web4student.php")

ActionChains(driver).move_to_element(driver.find_element_by_id("menuHeading3")).perform()
driver.find_element_by_xpath("//a[@title='Drop and Add Classes']").click()


input_table = driver.find_elements_by_class_name("dataentrytable")[-1]
input_rows = input_table.find_elements_by_tag_name("tr")[1:]

input_rows_dict = {i:input_rows[i].find_elements_by_xpath(".//input[@name='Callnum']") for i in range(len(input_rows))}


row_codes_dict = {i//5:class_codes[i:i+5] for i in range(0, len(class_codes), 5)}

for j, inputs in input_rows_dict.items():

    for k, code in enumerate(row_codes_dict[j]):
        inputs[k].send_keys(code)


driver.find_element_by_xpath("//input[@title='Submit']").click()

print("Course Codes submitted, check the page for any issues")
