from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# import mystevenscreds as creds
import importlib.util
spec = importlib.util.spec_from_file_location("mystevenscreds", "C:/Users/Scott/OneDrive/Stevens/Python Club/mystevenscreds.py")
creds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(creds)


class_codes = ["10157"]


driver = webdriver.Chrome(executable_path="chromedriver.exe")
driver.get("https://mystevens.stevens.edu/sso/webselfservices.php")

user_input = driver.find_element_by_id("username")
password_input = driver.find_element_by_id("password")
user_input.send_keys(creds.user)
password_input.send_keys(creds.password)

driver.find_element_by_name("_eventId_proceed").click()



while True:

    if driver.title == "Web Self Services | myStevens":
        break

driver.get("https://mystevens.stevens.edu/sso/web4student.php")

ActionChains(driver).move_to_element(driver.find_element_by_id("menuHeading3")).perform()
driver.find_element_by_xpath("//a[@title='Drop and Add Classes']").click()


input_table = driver.find_elements_by_class_name("dataentrytable")[-1]
input_rows = input_table.find_elements_by_tag_name("tr")[1:]
input_row_1 = input_rows[0].find_elements_by_xpath(".//input[@name='Callnum']")
input_row_2 = input_rows[1].find_elements_by_xpath(".//input[@name='Callnum']")

row_1_codes = class_codes[0:5]
row_2_codes = class_codes[5:]

for i, code in enumerate(row_1_codes):
    input_row_1[i].send_keys(code)

for i, code in enumerate(row_2_codes):
    input_row_1[i].send_keys(code)


driver.find_element_by_xpath("//input[@title='Submit']").click()


print("Course Codes submitted, check the page for any issues")
